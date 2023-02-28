FROM opensearchproject/opensearch:2.2.1

RUN /usr/share/opensearch/bin/opensearch-plugin install -b https://github.com/aparo/opensearch-learning-to-rank/releases/download/2.2.1/ltr-2.0.0-os2.2.1.zip
