import fasttext
import pandas as pd
import numpy as np
from functools import reduce
from normalize_query_product_name import transform_name


input_file_name = r"datasets/fasttext/query_product_name.csv"
query_name_df = pd.read_csv(input_file_name)[["query", "name"]]

grouped_df = query_name_df.groupby("query")
product_title_model_path = r"datasets/fasttext/title_model.bin"
grouped_df.get_group("macbook")

product_title_model = fasttext.load_model(product_title_model_path)


def get_similarity(query, product_name):
    try:
        names = grouped_df.get_group(query)["name"].values
        vectors = []
        for name in names:
            normalized_name = transform_name(name)
            vector = product_title_model.get_sentence_vector(normalized_name)
            vectors.append(vector)
        query_vector = reduce(lambda a, b: np.mean([a, b], axis=0), vectors)
        normalized_product_name = transform_name(product_name)
        input_product_vector = product_title_model.get_sentence_vector(
            normalized_product_name
        )
        cosine_similarity = np.dot(query_vector, input_product_vector) / (
            np.linalg.norm(query_vector) * np.linalg.norm(input_product_vector)
        )
        return cosine_similarity
    except KeyError:
        print(f"\nNo data is avilable for query: {query}")
        return 0


# # click: 3108172, query: macbook
# product_name = 'Apple® - MacBook® Air - Intel® Core™ i5 Processor - 11.6" Display - 2GB Memory - 64GB Flash Storage'

if __name__ == "__main__":
    query_prompt = "\nEnter your query (type 'Exit' to exit or hit ctrl-c):"
    product_name_prompt = (
        "\nEnter the product name (type 'Exit' to exit or hit ctrl-c):"
    )
    while True:
        query = input(query_prompt).rstrip()
        if query.lower() == "exit":
            exit(0)
        product_name = input(product_name_prompt).rstrip()
        if query.lower() == "exit":
            exit(0)
        cosine_similarity = get_similarity(query, product_name)
        print(f"\nCosine similarity is: {cosine_similarity}")
