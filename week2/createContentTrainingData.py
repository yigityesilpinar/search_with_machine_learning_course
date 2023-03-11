import argparse
import multiprocessing
import glob
from tqdm import tqdm
import os
import xml.etree.ElementTree as ET
from pathlib import Path
import pandas as pd
import numpy as np
from nltk import word_tokenize, pos_tag
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer


# Directory for product data
directory = r'datasets/product_data/products/'

parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--input", default=directory,  help="The directory containing product data")
general.add_argument("--output", default="datasets/fasttext/output.fasttext", help="the file to output to")
general.add_argument("--label", default="id", help="id is default and needed for downsteam use, but name is helpful for debugging")
general.add_argument("--transform", default=False, help="if set, do transformations on product name using nltk", action="store_true" )

# IMPLEMENT: Setting min_products removes infrequent categories and makes the classifier's task easier.
general.add_argument("--min_products", default=0, type=int, help="The minimum number of products per category (default is 0).")

args = parser.parse_args()

def transform_name(product_name):
    if args.transform:
        tokens = word_tokenize(product_name.lower())
        english_stopwords = stopwords.words("english")
        tokens_without_stopwords = [token for token in tokens if not token in english_stopwords]
        pos_tags = pos_tag(tokens_without_stopwords)
        # https://stackoverflow.com/questions/15388831/what-are-all-possible-pos-tags-of-nltk
        target_tag_types = ["DT", "EX", "FW", "IN","JJ","JJR", "JJS","NN", "NNP", "NNPS", "NNS", "PDT", "RB", "RBR", "RBS", "RP", "SYM", "UH", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]
        tokens_filtered_by_tag_type = [tag[0] for tag in pos_tags if tag[1] in target_tag_types]
        stemmer = PorterStemmer()
        stemmed_tokens = [stemmer.stem(token) for token in tokens_filtered_by_tag_type]
        transformed_product_name = " ".join(stemmed_tokens)
        return transformed_product_name
    # IMPLEMENT
    return product_name

output_file = args.output
path = Path(output_file)
output_dir = path.parent
if os.path.isdir(output_dir) == False:
        os.mkdir(output_dir)

ROOT_DIR = os.path.dirname(os.path.abspath("__file__"))
CATEGORIES_FILE_PATH = os.path.join(ROOT_DIR, 'datasets/product_data/categories/categories_0001_abcat0010000_to_pcmcat99300050000.xml')
tree = ET.parse(CATEGORIES_FILE_PATH)
root = tree.getroot()

category_to_parents = {}
for child in root:
    catPath = child.find('path')
    idArray = [cat.find('id').text for cat in catPath]
    category_to_parents[idArray[-1]] = idArray[:-1]

if args.input:
    directory = args.input
# IMPLEMENT: Track the number of items in each category and only output if above the min
min_products = args.min_products
names_as_labels = False
if args.label == 'name':
    names_as_labels = True


def get_replacement_parent_category(category, unique_categories_with_min_products):
    if category in category_to_parents:
        parent_categories = category_to_parents[category]
        for nearest_parent in reversed(parent_categories):
            if nearest_parent in unique_categories_with_min_products:
                return nearest_parent
    return None

def _label_filename(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    labels = []
    for child in root:
        # Check to make sure category name is valid and not in music or movies
        if (child.find('name') is not None and child.find('name').text is not None and
            child.find('categoryPath') is not None and len(child.find('categoryPath')) > 0 and
            child.find('categoryPath')[len(child.find('categoryPath')) - 1][0].text is not None and
            child.find('categoryPath')[0][0].text == 'cat00000' and
            child.find('categoryPath')[1][0].text != 'abcat0600000'):
              # Choose last element in categoryPath as the leaf categoryId or name
              if names_as_labels:
                  cat = child.find('categoryPath')[len(child.find('categoryPath')) - 1][1].text.replace(' ', '_')
              else:
                  cat = child.find('categoryPath')[len(child.find('categoryPath')) - 1][0].text
              # Replace newline chars with spaces so fastText doesn't complain
              name = child.find('name').text.replace('\n', ' ')
              if names_as_labels:
                  labels.append((transform_name(cat), transform_name(name)))
              else: 
                  labels.append((cat, transform_name(name)))
    return labels

if __name__ == '__main__':
    files = glob.glob(f'{directory}/*.xml')
    print("Writing results to %s" % output_file)
    with multiprocessing.Pool() as p:
        all_labels = tqdm(p.imap(_label_filename, files), total=len(files))
        with open(output_file, 'w') as output:
            all_rows = []
            for label_list in all_labels:
                all_rows.extend(label_list)
            df = pd.DataFrame(all_rows, columns=["Category", "Name"])
            if min_products:
                df_valid_category = df[
                    df.groupby("Category")["Category"].transform("size") >= min_products
                ]
                unique_categories_with_min_products = list(set(df_valid_category.groupby("Category")["Category"].transform(lambda x: x)))
                df["Category"] = df.groupby("Category")["Category"].transform(lambda x: x if (x.count() >= min_products) else get_replacement_parent_category(x.values[0], unique_categories_with_min_products))
                df = df[df["Category"].map(pd.notnull)]
            if not names_as_labels:
                df["Category"] = df["Category"].map("__label__{}".format)
            np.savetxt(output_file, df.values, fmt="%s")
