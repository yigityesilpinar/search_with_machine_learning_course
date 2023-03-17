from nltk import regexp_tokenize
from nltk.stem import PorterStemmer
import re

stemmer = PorterStemmer()


def transform_query(query):
    query_without_special_chars = re.sub("[^0-9a-zA-Z]+", " ", query.lower())
    query_with_normalized_spaces = " ".join(query_without_special_chars.split())
    tokens = regexp_tokenize(query_with_normalized_spaces, pattern="\s+", gaps=True)
    stemmed_tokens = [stemmer.stem(token) for token in tokens]
    transformed_product_name = " ".join(stemmed_tokens)
    if not transformed_product_name:
        return None
    return transformed_product_name
