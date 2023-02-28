# A simple loop that can be run to check on counts for our two indices as you are indexing.  Ctrl-c to get out.
while [ true ];
do
  echo "Queries:"
  curl -k -XGET "http://localhost:9200/_cat/count/bbuy_queries";
  echo "Products:"
  curl -k -XGET "http://localhost:9200/_cat/count/bbuy_products";
  sleep 60;
done