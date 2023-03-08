## Environment

Local environment with:
opensearch:2.2.1
opensearch-dashboards:2.2.1
ltr-2.0.0-os2.2.1

## Results

`./ltr-end-to-end.sh -y -m 0 -c quantiles`

```
Simple MRR is 0.279
LTR Simple MRR is 0.441
Hand tuned MRR is 0.423
LTR Hand Tuned MRR is 0.462

Simple p@10 is 0.121
LTR simple p@10 is 0.168
Hand tuned p@10 is 0.171
LTR hand tuned p@10 is 0.193
Simple better: 454      LTR_Simple Better: 647  Equal: 17
HT better: 559  LTR_HT Better: 709      Equal: 20
```

`After click prior feature`

```
Simple MRR is 0.279
LTR Simple MRR is 0.621
Hand tuned MRR is 0.423
LTR Hand Tuned MRR is 0.718

Simple p@10 is 0.121
LTR simple p@10 is 0.309
Hand tuned p@10 is 0.171
LTR hand tuned p@10 is 0.362
Simple better: 478      LTR_Simple Better: 624  Equal: 16
HT better: 568  LTR_HT Better: 695      Equal: 25
```

## Comments for performance evaluation

See evaluation output images at "week1/out" and "week1/out/wo_prior_clicks"

### Before prior clicks
LTR results seem to be better. For the query "Ipad", hello world template seems to perform better (more real devices on higher positions).


### After prior clicks

"Ipad" query case seems to be improved. In general results look good but there are some strange results e.g a tv mount is number one for the "lcd tv" query.

