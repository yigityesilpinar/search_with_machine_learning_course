
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

