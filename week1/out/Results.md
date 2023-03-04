## Environment

Local environment with:
opensearch:2.2.1
opensearch-dashboards:2.2.1
ltr-2.0.0-os2.2.1

## Results

`./ltr-end-to-end.sh -y -m 0 -c quantiles`

```
Simple MRR is 0.319
LTR Simple MRR is 0.484
Hand tuned MRR is 0.408
LTR Hand Tuned MRR is 0.462

Simple p@10 is 0.119
LTR simple p@10 is 0.151
Hand tuned p@10 is 0.152
LTR hand tuned p@10 is 0.160
Simple better: 461      LTR_Simple Better: 582  Equal: 20
HT better: 556  LTR_HT Better: 644      Equal: 22
```

`After click prior feature`

```
Simple MRR is 0.319
LTR Simple MRR is 0.681
Hand tuned MRR is 0.408
LTR Hand Tuned MRR is 0.718

Simple p@10 is 0.119
LTR simple p@10 is 0.270
Hand tuned p@10 is 0.152
LTR hand tuned p@10 is 0.294
Simple better: 397 LTR_Simple Better: 647 Equal: 19
HT better: 578 LTR_HT Better: 619 Equal: 25
```

## Comments for performance evaluation

See evaluation output images at "week1/out" and "week1/out/wo_prior_clicks"

### Before prior clicks
LTR results seem to be better. For the query "Ipad", hello world template seems to perform better (more real devices on higher positions).


### After prior clicks

"Ipad" query case seems to be improved. In general results look good but there are some strange results e.g a tv mount is number one for the "lcd tv" query.

