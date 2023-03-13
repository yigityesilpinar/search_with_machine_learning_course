import argparse
import fasttext
import os
import csv

ROOT_DIR = os.path.dirname(os.path.abspath("__file__"))
MODEL_PATH = os.path.join(ROOT_DIR, 'datasets/fasttext/title_model.bin')
TOP_WORDS_PATH = os.path.join(ROOT_DIR, 'datasets/fasttext/top_words.txt')
OUTPUT_CSV = os.path.join(ROOT_DIR, 'datasets/fasttext/synonyms.csv')

model = fasttext.load_model(path=MODEL_PATH)

parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--threshold", default=0.75, type=float, help="The minimum NN score to accept word neighbor word as a synonym (range between 0 - 1)")
args = parser.parse_args()

with open(TOP_WORDS_PATH) as top_words_file:
    csv_lines=[]
    for line in top_words_file:
        word = line.rstrip()
        nearest_neighbors = model.get_nearest_neighbors(word)
        filtered_neighbor_words = [nearest_neighbor[1] for nearest_neighbor in nearest_neighbors if nearest_neighbor[0] > args.threshold]
        if len(filtered_neighbor_words):
            csv_lines.append(tuple([word] + filtered_neighbor_words))
    with open(OUTPUT_CSV, "wt") as synonyms_file:
        writer = csv.writer(synonyms_file, delimiter=",")
        writer.writerows(csv_lines)
