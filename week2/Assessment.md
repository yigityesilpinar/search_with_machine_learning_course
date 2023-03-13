# Week2 - Project Assessment

## 1. For classifying product names to categories:

#### a) What precision (P@1) were you able to achieve?

**0.972 - 0.974**

#### b) What fastText parameters did you use?

`-lr 1.0 -epoch 25 -wordNgrams 2`

#### c) How did you transform the product names?

No transformation applied using "transform_name" method. When tested with transformation, achieved lower scores (~0.95).

#### d) How did you prune infrequent category labels, and how did that affect your precision?

Utilising pandas. Removing the category rows that has less than **min_products** products.

It had a huge impact, without pruning: 0.603, with prining: 0.97 - 0.972

#### e) How did you prune the category tree, and how did that affect your precision?

Utilising pandas. Replacing with the **nearest_parent** category that has more than **min_products** products.

It had a smaller impact comparing to pruning (but we are extending our category dictionary), always falling back to ancestors at depth 1: 0.909, final solution: 0.972 - 0.974

## 2. For deriving synonyms from content:

#### a) What were the results for your best model in the tokens used for evaluation?

Product Types

```
headphones:

headphon 0.848862
earbud 0.780217
ear 0.730387
earpollut 0.691522
yurbud 0.686955
phones 0.682976
cancelling 0.653936
over 0.639882
earphon 0.638961
piiq 0.635533
```

```
laptop:

notebook 0.767502
netbook 0.656412
bags 0.653984
ultrabook 0.636491
zenbook 0.627366
omnibook 0.620251
lifebook 0.613478
ibook 0.611688
briefcas 0.608474
t2060 0.602118
```

```
freezer:

freezerless 0.890927
refriger 0.803499
refrigerators 0.779358
refrigerator 0.774626
freez 0.770645
by 0.713044
cu 0.665524
side 0.658299
satina 0.657314
frost 0.648286
```

Brands

```
nintendo:

ds 0.968273
wii 0.932205
3ds 0.810575
nintendog 0.808966
gam 0.74554
xbox 0.720017
playstat 0.719159
psp 0.69107
360 0.676576
```

```
whirlpool:

maytag 0.775183
frigidair 0.771827
biscuit 0.750548
ge 0.721097
ingli 0.694863
hotpoint 0.687357
kitchenaid 0.676704
bisque 0.659302
electrolux 0.639224
amana 0.638293
```

```
kodak:

easyshar 0.856131
m341 0.711334
c813 0.684549
playsport 0.681347
m1063 0.677522
m763 0.676062
playtouch 0.670581
m340 0.66795
m550 0.663166
```

Models

```
ps2:

playstat 0.814385
ps3 0.729845
xbox 0.720434
gamecub 0.707921
guides 0.701105
psp 0.690421
gba 0.675813
gamecube 0.675015
guid 0.672131
adventur 0.66446
```

```
razr:

motorola 0.803692
droid 0.719096
cliphang 0.705777
cliq 0.704293
nokia 0.703014
r225 0.678673
phone 0.674843
startac 0.67105
cell 0.668403
ccm 0.660618
```

```
stratocaster:

telecaster 0.886299
fretboard 0.81337
strat 0.7886
starcaster 0.777565
fender 0.765122
squier 0.755677
tremolo 0.72126
thinlin 0.71435
whammy 0.710852
hss 0.69354
```

Other

```
holiday:

nobr 0.671777
stock 0.660111
congratul 0.587655
reindeer 0.585895
kwanzaa 0.583799
hallmark 0.578288
navidad 0.567146
perfectli 0.566057
slaphappi 0.554414
stardol 0.554159
```

```
plasma:

panel 0.700569
flat 0.688087
edtv 0.686464
tv 0.684522
hdtv 0.650581
ultravis 0.646992
viera 0.640964
kuro 0.639569
xbr 0.633605
ambilight 0.611085
```

```
leather:

reclin 0.682314
berklin 0.639976
dolan 0.627329
sofa 0.621712
faux 0.608956
armless 0.605202
case 0.604042
folio 0.566838
theaterseatstor 0.555563
sleev 0.552663
```

#### b) What fastText parameters did you use?

`-minCount 7 -epoch 25`, minCount 7 mostly to keep "nespresso", it had 8 occurences.

#### c) How did you transform the product names?

using **nltk word_tokenize, pos_tag, stopwords and stem**

## 3. For integrating synonyms with search:

#### a) How did you transform the product names (if different than previously)?

Same as level 2, using **nltk word_tokenize, pos_tag, stopwords and stem**

#### b) What threshold score did you use?

**0.75**

#### c) Were you able to find the additional results by matching synonyms?

Yes (you can see in "query_results.json" and "query_results_with_synonyms.json")

- "earbuds" => 1205 to 5852
- "nespresso" => 8 to 265
- "dslr" => 2837 to 7359

## 4. For classifying reviews:

#### a) What precision (P@1) were you able to achieve?

**0.88**

#### b) What fastText parameters did you use?

`-lr 1.0 -epoch 25 -wordNgrams 2`

#### c) How did you transform the review content?

No transformations. Tried only title or only comments, did not increase the precision.

#### d) How did you transform the review content?

Transforming rating to a different scale “positive”, “negative”, and “neutral” helped. P@1 is increased from **0.671** to **0.88**
