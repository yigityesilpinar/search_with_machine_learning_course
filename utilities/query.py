# A simple client for querying driven by user input on the command line.  Has hooks for the various
# weeks (e.g. query understanding).  See the main section at the bottom of the file
from opensearchpy import OpenSearch
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import argparse
import json
from getpass import getpass
from urllib.parse import urljoin
import pandas as pd
import logging
from fasttext.FastText import _FastText
from typing import Callable

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(levelname)s:%(message)s')

# expects clicks and impressions to be in the row
def create_prior_queries_from_group(
        click_group):  # total impressions isn't currently used, but it mayb worthwhile at some point
    click_prior_query = ""
    # Create a string that looks like:  "query": "1065813^100 OR 8371111^89", where the left side is the doc id and the right side is the weight.  In our case, the number of clicks a document received in the training set
    if click_group is not None:
        for item in click_group.itertuples():
            try:
                click_prior_query += "%s^%.3f  " % (item.doc_id, item.clicks / item.num_impressions)

            except KeyError as ke:
                pass  # nothing to do in this case, it just means we can't find priors for this doc
    return click_prior_query


# expects clicks from the raw click logs, so value_counts() are being passed in
def create_prior_queries(doc_ids, doc_id_weights,
                         query_times_seen):  # total impressions isn't currently used, but it mayb worthwhile at some point
    click_prior_query = ""
    # Create a string that looks like:  "query": "1065813^100 OR 8371111^89", where the left side is the doc id and the right side is the weight.  In our case, the number of clicks a document received in the training set
    click_prior_map = ""  # looks like: '1065813':100, '8371111':809
    if doc_ids is not None and doc_id_weights is not None:
        for idx, doc in enumerate(doc_ids):
            try:
                wgt = doc_id_weights[doc]  # This should be the number of clicks or whatever
                click_prior_query += "%s^%.3f  " % (doc, wgt / query_times_seen)
            except KeyError as ke:
                pass  # nothing to do in this case, it just means we can't find priors for this doc
    return click_prior_query


# Hardcoded query here.  Better to use search templates or other query config.
def create_query(user_query, click_prior_query, filters, sort="_score", sortDir="desc", size=10, source=None, use_synoyms=False):
    name_field = "name.synonyms" if use_synoyms else "name"
    query_obj = {
        'size': size,
        "sort": [
            {sort: {"order": sortDir}}
        ],
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "must": [

                        ],
                        "should": [  #
                            {
                                "match": {
                                    name_field: {
                                        "query": user_query,
                                        "fuzziness": "1",
                                        "prefix_length": 2,
                                        # short words are often acronyms or usually not misspelled, so don't edit
                                        "boost": 0.01
                                    }
                                }
                            },
                            {
                                "match_phrase": {  # near exact phrase match
                                    "name.hyphens": {
                                        "query": user_query,
                                        "slop": 1,
                                        "boost": 50
                                    }
                                }
                            },
                            {
                                "multi_match": {
                                    "query": user_query,
                                    "type": "phrase",
                                    "slop": "6",
                                    "minimum_should_match": "2<75%",
                                    "fields": [f"{name_field}^10", "name.hyphens^10", "shortDescription^5",
                                               "longDescription^5", "department^0.5", "sku", "manufacturer", "features",
                                               "categoryPath"]
                                }
                            },
                            {
                                "terms": {
                                    # Lots of SKUs in the query logs, boost by it, split on whitespace so we get a list
                                    "sku": user_query.split(),
                                    "boost": 50.0
                                }
                            },
                            {  # lots of products have hyphens in them or other weird casing things like iPad
                                "match": {
                                    "name.hyphens": {
                                        "query": user_query,
                                        "operator": "OR",
                                        "minimum_should_match": "2<75%"
                                    }
                                }
                            }
                        ],
                        "minimum_should_match": 1,
                        "filter": filters  #
                    }
                },
                "boost_mode": "multiply",  # how _score and functions are combined
                "score_mode": "sum",  # how functions are combined
                "functions": [
                    {
                        "filter": {
                            "exists": {
                                "field": "salesRankShortTerm"
                            }
                        },
                        "gauss": {
                            "salesRankShortTerm": {
                                "origin": "1.0",
                                "scale": "100"
                            }
                        }
                    },
                    {
                        "filter": {
                            "exists": {
                                "field": "salesRankMediumTerm"
                            }
                        },
                        "gauss": {
                            "salesRankMediumTerm": {
                                "origin": "1.0",
                                "scale": "1000"
                            }
                        }
                    },
                    {
                        "filter": {
                            "exists": {
                                "field": "salesRankLongTerm"
                            }
                        },
                        "gauss": {
                            "salesRankLongTerm": {
                                "origin": "1.0",
                                "scale": "1000"
                            }
                        }
                    },
                    {
                        "script_score": {
                            "script": "0.0001"
                        }
                    }
                ]

            }
        }
    }
    if click_prior_query is not None and click_prior_query != "":
        query_obj["query"]["function_score"]["query"]["bool"]["should"].append({
            "query_string": {
                # This may feel like cheating, but it's really not, esp. in ecommerce where you have all this prior data,  You just can't let the test clicks leak in, which is why we split on date
                "query": click_prior_query,
                "fields": ["_id"]
            }
        })
    if user_query == "*" or user_query == "#":
        # replace the bool
        try:
            query_obj["query"] = {"match_all": {}}
        except:
            print("Couldn't replace query for *")
    if source is not None:  # otherwise use the default and retrieve all source
        query_obj["_source"] = source
    return query_obj

class QueryClassification:
    def __init__(self, model: _FastText, threshold: int, label_prefix: str, transform_query: Callable[..., str], prediction_count:int):
        self.model = model 
        self.threshold = threshold
        self.label_prefix = label_prefix
        self.transform_query = transform_query
        self.prediction_count = prediction_count

def search(client, user_query, index="bbuy_products", sort="_score", sortDir="desc", source=None, use_synonyms=False, print_results=False, print_query=False, query_classification:QueryClassification=None, boost_mode=False, category_path_ids_boost=0.001, category_leaf_boost = 0.002):
    #### W3: classify the query
    #### W3: create filters and boosts
    # Note: you may also want to modify the `create_query` method above
    all_predictions = []
    predictions_over_threshold = []
    if query_classification:
        labels, scores = query_classification.model.predict(query_classification.transform_query(user_query), k=query_classification.prediction_count)
        for idx, label_with_prefix in enumerate(labels):
            score = scores[idx]
            label = label_with_prefix[len(query_classification.label_prefix) :]
            all_predictions.append({
                "category": label,
                "score": score
            })
            if score >= query_classification.threshold:
                predictions_over_threshold.append({
                    "category": label,
                    "score": score
                })
        # nothing bigger than threshold, fallback to first n categories sum to reach the threshold
        if not predictions_over_threshold:
            sum_index = 0
            sum_score = 0
            for score in scores:
                sum_index = sum_index + 1
                sum_score += score
                if sum_score >= query_classification.threshold:
                    predictions_over_threshold = all_predictions[:sum_index]
                    break
                


    filters = None
    categories_over_threshold =[prediction["category"] for prediction in predictions_over_threshold]
    if categories_over_threshold and not boost_mode:
        filters = [
            {
                "bool": {
                    "must": {"terms": {"categoryPathIds": categories_over_threshold }},
                    "should": {"terms": {"categoryLeaf": categories_over_threshold}},
                }
            }
        ]
    query_obj = create_query(user_query, click_prior_query=None, filters=filters, sort=sort, sortDir=sortDir, source=source, use_synoyms=use_synonyms)

    if categories_over_threshold and boost_mode:
        query_obj["query"]["function_score"]["query"]["bool"]["should"].extend(
            [
                {"terms": {"categoryPathIds": categories_over_threshold, "boost": category_path_ids_boost}},
                {"terms": {"categoryLeaf": categories_over_threshold, "boost": category_leaf_boost}},
            ]
        )
    if print_query:
        print(json.dumps(query_obj, indent=2))  
    response = client.search(query_obj, index=index)
    if response and response['hits']['hits'] and len(response['hits']['hits']) > 0:
        if print_results:
            print(json.dumps(response, indent=2))
    return response, predictions_over_threshold, all_predictions


if __name__ == "__main__":
    host = 'localhost'
    port = 9200
    auth = ('admin', 'admin')  # For testing only. Don't store credentials in code.
    parser = argparse.ArgumentParser(description='Build LTR.')
    general = parser.add_argument_group("general")
    general.add_argument("-i", '--index', default="bbuy_products",
                         help='The name of the main index to search')
    general.add_argument('--host', default="localhost",
                         help='The OpenSearch host name')
    general.add_argument("--synonyms",
                         help='If set, queries will match against synonyms of product names', action="store_true", default=False)
    general.add_argument("--classification",
                         help='If set, query classification will be used in search', action="store_true", default=False)
    general.add_argument("--boost",
                        help='If set, query classification will be in boost mode instead of filter', action="store_true", default=False)
    general.add_argument("-p", '--port', type=int, default=9200,
                         help='The OpenSearch port')
    general.add_argument('--user',
                         help='The OpenSearch admin.  If this is set, the program will prompt for password too. If not set, use default of admin/admin')
    args = parser.parse_args()

    if len(vars(args)) == 0:
        parser.print_usage()
        exit()

    host = args.host
    port = args.port
    if args.user:
        password = getpass()
        auth = (args.user, password)

    base_url = "http://{}:{}/".format(host, port)
    opensearch = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_compress=True,  # enables gzip compression for request bodies
        use_ssl=False,
    )
    index_name = args.index
    query_prompt = "\nEnter your query (type 'Exit' to exit or hit ctrl-c):"
    query_classification = None
    if args.classification:
        import os
        import fasttext
        import sys

        sys.path.append(os.path.abspath(os.path.join(".")))
        from week3.transform_query import transform_query as _transform_query

        query_classification_model_file_path = (
            r"datasets/fasttext/labeled_queries_model.bin"
        )
        query_classification_model = fasttext.load_model(
            query_classification_model_file_path
        )
        query_classification_prefix = "__label__"
        query_classification_score_threshold = 0.5
        query_classification = QueryClassification(
            model=query_classification_model,
            threshold=query_classification_score_threshold,
            label_prefix=query_classification_prefix,
            transform_query=_transform_query,
            prediction_count=3,
        )
    while True:
        line = input(query_prompt).rstrip()
        query = line.rstrip()
        if query.lower() == "exit":
            exit(0)
        search(
            client=opensearch,
            user_query=query,
            index=index_name,
            source=["name", "shortDescription"],
            use_synonyms=args.synonyms,
            print_results=True,
            query_classification=query_classification,
            boost_mode=args.boost,
        )