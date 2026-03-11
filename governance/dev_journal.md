# 11 of March 

Goals: 
* Fixing the algorithm and visualizations
* Fix the time conversions 
* Implement export to a file
* unit test cases 
* Write acceptance tests

DONE: 
* Fixing the algorithm and visualizations
* Fix the time conversions 

Checking now for  test-data/TensorFlow/tensorFlowGitLog-temporal-3-developers-6-commits-thee-files.IN
```
./scrapLog.py -r  test-data/TensorFlow/tensorFlowGitLog-temporal-3-developers-6-commits-thee-files.IN   --type-of-network=inter_individual_graph_temporal -vv
```

### Raw git log 


== 1 Johannes Reifferscheid ;jreiffers@google.com;Tue Jan 7 06:30:42 2024 -0800==

third_party/xla/xla/service/gpu/fusions/BUILD
third_party/xla/xla/service/gpu/fusions/fusions.cc
third_party/xla/xla/service/gpu/fusions/scatter.cc

== NA Giulio C.n;57756052+giuliocn@users.noreply.github.com;Tue Jan 2 14:18:00 2024 +0100==

== 2 Johannes Reifferscheid;jreiffers@google.com;Tue Jan 6 04:03:16 2024 -0800==
third_party/xla/xla/service/gpu/fusions/BUILD
third_party/xla/xla/service/gpu/fusions/fusions.cc
third_party/xla/xla/service/gpu/fusions/scatter.cc


== 3 Adrian Kuegel;akuegel@google.com;Mon Jan 5 23:20:59 2024 -0800==
tensorflow/compiler/jit/xla_activity_logging_listener.cc
tensorflow/core/BUILD
tensorflow/core/kernels/gpu_utils.cc
tensorflow/core/platform/BUILD
tensorflow/core/platform/logger.h


==Adrian Kuegel;akuegel@google.com;Mon Jan 3 23:44:42 2024 -0800==
third_party/xla/xla/debug_options_flags.cc
third_party/xla/xla/service/gpu/fusions/fusions.cc
third_party/xla/xla/service/gpu/fusions/scatter.cc

==Dragan Mladjenovic;Dragan.Mladjenovic@amd.com;Tue Jan 1 03:51:03 2024 -0800==
third_party/xla/xla/stream_executor/rocm/rocm_driver.cc

### Expected output 

T0,Tue Jan 1 03:51:03 2024 , no edges 
T1, Mon Jan 1 on Jan 3 23:44:42 2024, no edges 
T2, Jan 2 03:51:03 2024 -0800==, no edges
T3, Tue Jan 2 04:03:16 2024 -0800==, jreiffers@google.com <-->  akuegel@google.com
T4, Tue Jan 2 14:18:00 2024, no edges 
T4, Tue Jan 2 06:30:42 2024 -0800==, jreiffers@google.com <-->  akuegel@google.com



---------------------------

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