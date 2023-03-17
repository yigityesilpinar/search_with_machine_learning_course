import argparse
import xml.etree.ElementTree as ET
import pandas as pd
import csv
from tqdm import tqdm
import time
import dask.dataframe as dd
from transform_query import transform_query

tqdm.pandas()
categories_file_name = r"datasets/product_data/categories/categories_0001_abcat0010000_to_pcmcat99300050000.xml"

queries_file_name = r"datasets/train.csv"
output_file_name = r"datasets/fasttext/labeled_queries.txt"

parser = argparse.ArgumentParser(description="Process arguments.")
general = parser.add_argument_group("general")
general.add_argument(
    "--min_queries",
    default=1,
    help="The minimum number of queries per category label (default is 1)",
)
general.add_argument(
    "--max_rows",
    help="Limit the rows used from training data, only to be used during development",
)
general.add_argument("--output", default=output_file_name, help="the file to output to")

args = parser.parse_args()
output_file_name = args.output

if args.min_queries:
    min_queries = int(args.min_queries)

max_rows = None
if args.max_rows:
    max_rows = int(args.max_rows)



# The root category, named Best Buy with id cat00000, doesn't have a parent.
root_category_id = "cat00000"

tree = ET.parse(categories_file_name)
root = tree.getroot()

# Parse the category XML file to map each category id to its parent category id in a dataframe.
categories = []
parents = []
for child in root:
    id = child.find("id").text
    cat_path = child.find("path")
    cat_path_ids = [cat.find("id").text for cat in cat_path]
    leaf_id = cat_path_ids[-1]
    if leaf_id != root_category_id:
        categories.append(leaf_id)
        parents.append(cat_path_ids[-2])
parents_df = pd.DataFrame(
    list(zip(categories, parents)), columns=["category", "parent"]
)


# Read the training data into pandas, only keeping queries with non-root categories in our category tree.
if max_rows:
    queries_df = pd.read_csv(queries_file_name, nrows=max_rows)[["category", "query"]]
else:
    queries_df = pd.read_csv(queries_file_name)[["category", "query"]]

queries_df = queries_df[queries_df["category"].isin(categories)]


def log_time(message, operation):
    print(message)
    start_time = time.time()
    operation()
    print(f"--- {(time.time() - start_time):.2f} seconds ---")


if __name__ == "__main__":
    # IMPLEMENT ME: Convert queries to lowercase, and optionally implement other normalization, like stemming.
    def transform_queries_in_dataset():
        global queries_df
        ddata = dd.from_pandas(queries_df["query"], npartitions=30)
        queries_df["query"] = ddata.map_partitions(
            lambda df: df.progress_map(transform_query)
        ).compute(scheduler="processes")
        queries_df = queries_df[queries_df["query"].map(pd.notnull)]

    log_time(
        message=f"--- Transforming {len(queries_df)} queries  ---",
        operation=transform_queries_in_dataset,
    )

    # IMPLEMENT ME: Roll up categories to ancestors to satisfy the minimum number of queries per category.
    if min_queries > 1:

        def roll_up_categories_to_ancestors():
            global queries_df
            while True:
                category_query_counts_df = (
                    queries_df.groupby(["category"])
                    .size()
                    .reset_index(name="num_queries")
                )
                categories_under_threshold = category_query_counts_df[
                    category_query_counts_df["num_queries"] < min_queries
                ]["category"].unique()

                if categories_under_threshold.any():
                    extended_by_parents = queries_df.merge(
                        parents_df, on="category", how="left"
                    )
                    extended_by_parents["parent"].loc[pd.isnull] = root_category_id
                    extended_df = extended_by_parents.merge(
                        category_query_counts_df, on="category", how="left"
                    )
                    extended_df.loc[
                        extended_df["num_queries"] < min_queries, "category"
                    ] = extended_df["parent"]
                    queries_df = extended_df.drop(["parent", "num_queries"], axis=1)
                else:
                    break

        log_time(
            message=f"--- Rolling up categories of {len(queries_df)} queries  ---",
            operation=roll_up_categories_to_ancestors,
        )

    # Create labels in fastText format.
    queries_df["label"] = "__label__" + queries_df["category"]

    # Output labeled query data as a space-separated file, making sure that every category is in the taxonomy.
    queries_df = queries_df[queries_df["category"].isin(categories)]
    queries_df["output"] = queries_df["label"] + " " + queries_df["query"]
    queries_df[["output"]].to_csv(
        output_file_name,
        header=False,
        sep="|",
        escapechar="\\",
        quoting=csv.QUOTE_NONE,
        index=False,
    )
