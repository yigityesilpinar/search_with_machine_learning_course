# Week3 - Project Assessment

## 1. For query classification:

#### a) How many unique categories did you see in your rolled up training data when you set the minimum number of queries per category to 1000? To 10000?

```
1000 -> 387
10000 -> 69
```

#### b) What were the best values you achieved for R@1, R@3, and R@5? You should have tried at least a few different models, varying the minimum number of queries per category, as well as trying different fastText parameters or query normalization. Report at least 2 of your runs.
```
--min_queries 10000
train -500000
test -100000

-lr 0.5 -epoch 25 -wordNgrams 2
P@1     0.639
R@1     0.639
P@3     0.278
R@3     0.834
P@5     0.178
R@5     0.889

-lr 0.7 -epoch 25 -wordNgrams 4

P@1     0.564
R@1     0.564
P@3     0.194
R@3     0.582
P@5     0.118
R@5     0.59
```

```
--min_queries 1000
-lr 0.5 -epoch 25 -wordNgrams 2
P@1     0.572
R@1     0.572
P@3     0.256
R@3     0.768
P@5     0.166
R@5     0.831
```
## 2, For integrating query classification with search:

#### a) Give 2 or 3 examples of queries where you saw a dramatic positive change in the results because of filtering. Make sure to include the classifier output for those queries.

```
Query: "lcd tv"
Predictions: Best Buy > TV & Home Theater > TVs > All Flat-Panel TVs ---> 0.98
Comment: much better relevancy in top 10 results, e.g Adapter for Apple® iPad® is removed.
```
```
Query: "Ipad"
Predictions: Best Buy > Computers & Tablets > Tablets & iPad > iPad ---> 0.66
Comment: much better relevancy in top 10 results, all are actuall ipads, instead of accessories. 
```
```
Query: "camera"
Predictions:
Best Buy > Cameras & Camcorders > Digital Cameras > Point & Shoot Cameras > Fun & Basic Cameras ---> 0.31
Best Buy > Cameras & Camcorders > Digital SLR Cameras > DSLR Body & Lens ---> 0.17
Best Buy > Cameras & Camcorders > Digital Cameras > Point & Shoot Cameras ---> 0.15
Comment: much better relevancy in top 10 results, all are actuall cameras, instead of accessories. 
```
#### b) Give 2 or 3 examples of queries where filtering hurt the results, either because the classifier was wrong or for some other reason. Again, include the classifier output for those queries.
```
Query: "lollipop"
Predictions: Best Buy > Computers & Tablets > Desktop & All-in-One Computers ---> 0.73
Comment: no results for filter mode, boost mode results are irrelevant.
```
```
Query: "Bed"
Predictions: Best Buy > Appliances ---> 0.98
Comment: mostly irrelevant results.
```
```
Query: "queen"
Predictions: 
Best Buy > Movies & Music > Movies & TV Shows ---> 0.31
Best Buy > Video Games > Pre-Owned & Refurbished > Pre-Owned Games ---> 0.18
Best Buy > Movies & Music > Music > Rock ---> 0.12
Comment: no results for filter mode, boost mode didn't change the results.
```