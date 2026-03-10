10 of March 

Goals: 
* Fixing the algorithm and visualizations
* unit test cases 
* Write acceptance tests

```
./scrapLog.py -r  test-data/TensorFlow/tensorFlowGitLog-temporal-2-developers-3-commits-same-file.IN --type-of-network=inter_individual_graph_temporal -vv
```

### Raw git log 
==Dimitar (Mitko) Asenov;dasenov@google.com;Wed Jan 3 04:05:02 2024 -0800==
third_party/xla/xla/tests/BUILD

==David Dunleavy;ddunleavy@google.com;Tue Jan 2 11:19:35 2024 -0800==
third_party/xla/xla/tests/BUILD

==David Dunleavy;ddunleavy@google.com;Tue Jan 2 07:34:17 2024 -0800==
third_party/xla/xla/tests/BUILD

### Expected output 
T0, Jan 2 07:34:17 2024, no edges 
T1, Tue Jan 2 11:19:35 2024, no edges because same person 
T2, Wed Jan 3 04:05:02 2024, asenov@google.com -- ddunleavy@google.com


# Obsevations 