from nltk import word_tokenize, pos_tag
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

stemmer = PorterStemmer()


def transform_name(product_name):
    tokens = word_tokenize(product_name.lower())
    english_stopwords = stopwords.words("english")
    tokens_without_stopwords = [
        token for token in tokens if not token in english_stopwords
    ]
    pos_tags = pos_tag(tokens_without_stopwords)
    target_tag_types = [
        "DT",
        "EX",
        "FW",
        "IN",
        "JJ",
        "JJR",
        "JJS",
        "NN",
        "NNP",
        "NNPS",
        "NNS",
        "PDT",
        "RB",
        "RBR",
        "RBS",
        "RP",
        "SYM",
        "UH",
        "VB",
        "VBD",
        "VBG",
        "VBN",
        "VBP",
        "VBZ",
    ]
    tokens_filtered_by_tag_type = [
        tag[0] for tag in pos_tags if tag[1] in target_tag_types
    ]
    stemmed_tokens = [stemmer.stem(token) for token in tokens_filtered_by_tag_type]
    transformed_product_name = " ".join(stemmed_tokens)
    return transformed_product_name
