.DEFAULT_GOAL := start

.PHONY: start
start:
	docker-compose -f docker/docker-compose.yml up

.PHONY: stop
stop:
	docker-compose -f docker/docker-compose.yml down

.PHONY: build-local-dashboard-image
build-local-dashboard-image:
	docker build -f docker/local-opensearch-dashboard-disabled-security.dockerfile -t local-opensearch-dashboard-disabled-security:latest ./docker

.PHONY: build-local-opensearch-learning-to-rank
build-local-opensearch-learning-to-rank:
	docker build -f docker/local-opensearch-learning-to-rank.dockerfile -t local-opensearch-learning-to-rank:latest ./docker

.PHONY: index
index:
	./index-data.sh -r -p `pwd`/week2/conf/bbuy_products.json

.PHONY: delete
delete:
	./delete-indexes.sh

.PHONY: count
count:
	./count-tracker.sh

.PHONY: track_index_products
track_index_products:
	tail -f logs/index_products.log

.PHONY: track_index_queries
track_index_queries:
	tail -f logs/index_queries.log

.PHONY: ltr
ltr: 
	./ltr-end-to-end.sh -y

.PHONY: generate
generate: 
	python `pwd`/week2/createContentTrainingData.py --label id --min_products 500 --output `pwd`/datasets/fasttext/labeled_products.txt

.PHONY: shuffle
shuffle: 
	bash -c "shuf `pwd`/datasets/fasttext/labeled_products.txt  --random-source=<(seq 99999) > `pwd`/datasets/fasttext/shuffled_labeled_products.txt"

.PHONY: normalize
normalize: 
	cat `pwd`/datasets/fasttext/shuffled_labeled_products.txt |sed -e "s/\([.\!?,'/()]\)/ \1 /g" | tr "[:upper:]" "[:lower:]" | sed "s/[^[:alnum:]_]/ /g" | tr -s ' ' > `pwd`/datasets/fasttext/normalized_labeled_products.txt

.PHONY: split
split: 
	head -10000 `pwd`/datasets/fasttext/normalized_labeled_products.txt > `pwd`/datasets/fasttext/training_data.txt && \
	tail -10000 `pwd`/datasets/fasttext/normalized_labeled_products.txt > `pwd`/datasets/fasttext/test_data.txt
	wc `pwd`/datasets/fasttext/test_data.txt
	wc `pwd`/datasets/fasttext/training_data.txt

.PHONY: train
train: 
	fasttext supervised -input `pwd`/datasets/fasttext/training_data.txt -output `pwd`/datasets/fasttext/model -lr 1.0 -epoch 25 -wordNgrams 2

.PHONY: test_model
test_model: 
	fasttext test `pwd`/datasets/fasttext/model.bin `pwd`/datasets/fasttext/test_data.txt

.PHONY: predict
predict: 
	fasttext predict `pwd`/datasets/fasttext/model.bin -

.PHONY: run
run: generate shuffle normalize split train test_model

.PHONY: generate_synonyms_data
generate_synonyms_data:
	python `pwd`/week2/createContentTrainingData.py --label name --transform --output `pwd`/datasets/fasttext/products.txt

.PHONY: normalize_synonyms_data
normalize_synonyms_data: 
	cat `pwd`/datasets/fasttext/products.txt | sed -e "s/\([.\!?,'/()]\)/ \1 /g" | tr "[:upper:]" "[:lower:]" | sed "s/[^[:alnum:]]/ /g" | tr -s ' ' > `pwd`/datasets/fasttext/normalized_products.txt

.PHONY: train_synonyms
train_synonyms: 
	fasttext skipgram -input `pwd`/datasets/fasttext/normalized_products.txt -output `pwd`/datasets/fasttext/title_model -minCount 7 -epoch 25

.PHONY: predict_synonyms
predict_synonyms: 
	fasttext nn `pwd`/datasets/fasttext/title_model.bin

.PHONY: top_words
top_words: 
	cat `pwd`/datasets/fasttext/normalized_products.txt | tr " " "\n" | grep "...." | sort | uniq -c | sort -nr | head -1000 | grep -oE '[^ ]+$'' > `pwd`/datasets/fasttext/top_words.txt

.PHONY: top_words_synonyms
top_words_synonyms: 
	python `pwd`/week2/generateSynonyms.py

.PHONY: run_synonyms
run_synonyms: generate_synonyms_data normalize_synonyms_data train_synonyms top_words top_words_synonyms

.PHONY: copy_synonyms_to_container
copy_synonyms_to_container: 
	docker cp `pwd`/datasets/fasttext/synonyms.csv opensearch-node1:/usr/share/opensearch/config/synonyms.csv

.PHONY: shell
shell:
	@docker-compose -f docker/docker-compose.yml  exec opensearch-node1 /bin/bash

.PHONY: generate_reviews_data
generate_reviews_data:
	python week2/createReviewLabels.py

.PHONY: shuffle_reviews_data
shuffle_reviews_data: 
	bash -c "shuf datasets/fasttext/output_reviews.fasttext  --random-source=<(seq 99999) > datasets/fasttext/shuffled_output_reviews.fasttext"

.PHONY: normalize_reviews_data
normalize_reviews_data: 
	cat `pwd`/datasets/fasttext/shuffled_output_reviews.fasttext |sed -e "s/\([.\!?,'/()]\)/ \1 /g" | tr "[:upper:]" "[:lower:]" | sed "s/[^[:alnum:]_]/ /g" | tr -s ' ' > `pwd`/datasets/fasttext/normalized_output_reviews.fasttext

.PHONY: split_reviews_data
split_reviews_data: 
	head -10000 `pwd`/datasets/fasttext/normalized_output_reviews.fasttext > `pwd`/datasets/fasttext/reviews_training_data.txt && \
	tail -10000 `pwd`/datasets/fasttext/normalized_output_reviews.fasttext > `pwd`/datasets/fasttext/reviews_test_data.txt
	wc `pwd`/datasets/fasttext/reviews_test_data.txt
	wc `pwd`/datasets/fasttext/reviews_training_data.txt

.PHONY: train_reviews
train_reviews: 
	fasttext supervised -input `pwd`/datasets/fasttext/reviews_training_data.txt -output `pwd`/datasets/fasttext/reviews_model -lr 1.0 -epoch 25 -wordNgrams 2

.PHONY: test_reviews_model
test_reviews_model: 
	fasttext test `pwd`/datasets/fasttext/reviews_model.bin `pwd`/datasets/fasttext/reviews_test_data.txt

.PHONY: predict_reviews
predict_reviews: 
	fasttext predict `pwd`/datasets/fasttext/reviews_model.bin -

.PHONY: run_reviews
run_reviews: generate_reviews_data shuffle_reviews_data normalize_reviews_data split_reviews_data train_reviews test_reviews_model