# 11 of March 

Goals: 
* Fixing the algorithm and visualizations
* Implement export to a file
* unit test cases 
* Write acceptance tests

```
./scrapLog.py -r  test-data/TensorFlow/tensorFlowGitLog-temporal-2-developers-3-commits-two-files.IN  --type-of-network=inter_individual_graph_temporal -vv
```


Gives 
📈 BASIC STATISTICS:
  • Graph type:      TemporalMultiGraph
  • Directed:        False
  • Total nodes:     2
  • Total edges:     2
  • Snapshots:       1
  • Time attributes: Not found in edges

Should not 
Graph type 
Total edges 2 





# 10 of March 

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


# Observation 
22:13 - For 1 edge visualizations owrk. 

Now other git log 
```
./scrapLog.py -r  test-data/TensorFlow/tensorFlowGitLog-temporal-2-developers-3-commits-two-files.IN  --type-of-network=inter_individual_graph_temporal -vv
```

#### Raw git log
==Dimitar (Mitko) Asenov;dasenov@google.com;Wed Jan 3 04:05:02 2024 -0800==
third_party/xla/xla/tests/BUILD
tensorflow/core/kernels/gpu_utils.cc
tensorflow/core/platform/logger.h

==David Dunleavy;ddunleavy@google.com;Tue Jan 2 11:19:35 2024 -0800==
third_party/xla/xla/tests/BUILD

==David Dunleavy;ddunleavy@google.com;Tue Jan 2 07:34:17 2024 -0800==
third_party/xla/xla/tests/BUILD
tensorflow/core/kernels/gpu_utils.cc

### Expected output 

T0, Tue Jan 2 07:34:17 2024, No edges 
T1, Tue Jan 2 11:19:35 2024, No edges, sam developer 
T2, Wed Jan 3 04:05:02 2024, dasenov@google.com -> ddunleavy@google.com

# Observation 
We are getting two edges: 
→ NEW relational edge betweendasenov@google.com and others ddunleavy@google.com with timestamp='Wed Jan 3 04:05:02 2024 -0800'
→ NEW relational edge betweendasenov@google.com and others ddunleavy@google.com with timestamp='Wed Jan 3 04:05:02 2024 -0800'

# TODO tomorrow. Should be one edge only