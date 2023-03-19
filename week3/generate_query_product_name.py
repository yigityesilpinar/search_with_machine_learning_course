import pandas as pd
import os
import xml.etree.ElementTree as ET

output_file_name = r"datasets/fasttext/query_product_name.csv"
directory = r"datasets/product_data/products/"

skus = []
names = []
product_files = os.listdir(directory)
for filename in product_files:
    if filename.endswith(".xml"):
        with open(os.path.join(directory, filename)) as xml_file:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            for child in root:
                sku = child.find("sku").text
                name = child.find("name").text
                skus.append(sku)
                names.append(name)

products_df = pd.DataFrame(list(zip(skus, names)), columns=["sku", "name"]).astype(
    {"sku": "int64", "name": "string"}
)
queries_file_name = r"datasets/train.csv"
queries_df = pd.read_csv(queries_file_name)[["sku", "query"]].astype(
    {"sku": "int64", "query": "string"}
)
merged_df = queries_df.merge(products_df, on="sku", how="left")
merged_df = merged_df.drop(["sku"], axis=1)
merged_df = merged_df[merged_df["name"].map(pd.notnull)]
merged_df.to_csv(output_file_name, escapechar="\\", index=False)
