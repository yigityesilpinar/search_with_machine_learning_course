
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
	./index-data.sh

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