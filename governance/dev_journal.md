# 12 of March 

Goals: 
* One more test case
* Improve visualizations
* Implement export to a file
* unit test cases 
* Write acceptance tests


Achievements: 
* One more test file 


=== New RAW log 
==Henning Becker;hebecker@google.com;Thu Apr 11 12:29:17 2024 -0700==
third_party/xla/xla/service/gpu/llvm_gpu_backend/BUILD
third_party/xla/xla/service/gpu/llvm_gpu_backend/gpu_backend_lib.cc

==Eugene Zhulenev;ezhulenev@google.com;Thu Apr 11 11:38:22 2024 -0700==
third_party/xla/third_party/tsl/tsl/concurrency/async_value.h
third_party/xla/xla/literal.cc
third_party/xla/xla/literal.h

==Yang Chen;yangchen@google.com;Thu Apr 11 11:30:06 2024 -0700==
tensorflow/core/kernels/data/experimental/index_flat_map_dataset_op.cc
tensorflow/python/data/experimental/kernel_tests/BUILD
tensorflow/python/data/experimental/kernel_tests/index_flat_map_test.py

==guozhong.zhuang;guozhong.zhuang@intel.com;Thu Apr 11 11:43:23 2024 -0700==
tensorflow/core/BUILD
tensorflow/core/common_runtime/mkl_layout_pass.cc
tensorflow/core/kernels/mkl/BUILD
tensorflow/core/kernels/mkl/mkl_deprecated_ops.cc
tensorflow/core/ops/array_ops.cc
tensorflow/core/ops/math_ops.cc
tensorflow/core/ops/nn_ops.cc

==Kuangyuan Chen;chky@google.com;Thu Apr 11 11:02:12 2024 -0700==
third_party/xla/xla/pjrt/transpose.cc

==Blake Hechtman;blakehechtman@google.com;Thu Apr 11 09:55:57 2024 -0700==
third_party/xla/xla/layout_util.cc
third_party/xla/xla/layout_util.h
third_party/xla/xla/service/BUILD
third_party/xla/xla/service/computation_layout.cc
third_party/xla/xla/service/layout_assignment.cc
third_party/xla/xla/service/layout_assignment_test.cc
third_party/xla/xla/shape_layout.cc
third_party/xla/xla/shape_layout.h

==Changhui Lin;changhuilin@google.com;Thu Apr 11 09:44:24 2024 -0700==
third_party/xla/xla/pjrt/event_pool.cc
third_party/xla/xla/pjrt/event_pool.h

==Eugene Zhulenev;ezhulenev@google.com;Thu Apr 11 09:16:48 2024 -0700==
third_party/xla/xla/pjrt/c/pjrt_c_api_gpu_test.cc
third_party/xla/xla/pjrt/c/pjrt_c_api_helpers.cc
third_party/xla/xla/pjrt/c/pjrt_c_api_helpers.h
third_party/xla/xla/pjrt/c/pjrt_c_api_test.cc
third_party/xla/xla/pjrt/c/pjrt_c_api_test_base.cc
third_party/xla/xla/pjrt/c/pjrt_c_api_test_base.h
third_party/xla/xla/pjrt/c/pjrt_c_api_wrapper_impl.cc
third_party/xla/xla/pjrt/host_callback_test.cc
third_party/xla/xla/pjrt/pjrt_c_api_client.cc
third_party/xla/xla/pjrt/pjrt_c_api_client.h
third_party/xla/xla/pjrt/pjrt_client.h
third_party/xla/xla/pjrt/pjrt_future.h
third_party/xla/xla/pjrt/pjrt_stream_executor_client.cc

==Kyle Lucke;klucke@google.com;Thu Apr 11 07:21:10 2024 -0700==
tensorflow/c/experimental/stream_executor/stream_executor_test.cc
third_party/xla/xla/stream_executor/stream_executor_pimpl.cc

==Pearu Peterson;pearu.peterson@gmail.com;Thu Apr 11 06:30:51 2024 -0700==
third_party/xla/xla/python/xla_client.py
third_party/xla/xla/service/elemental_ir_emitter.cc
third_party/xla/xla/tests/complex_unary_op_samples.h
third_party/xla/xla/tests/complex_unary_op_test.cc
third_party/xla/xla/tests/generate_complex_unary_op_samples.py

==Krasimir Georgiev;krasimir@google.com;Thu Apr 11 05:59:02 2024 -0700==
third_party/llvm/generated.patch
third_party/llvm/workspace.bzl
third_party/triton/llvm_integration/cl623185214.patch
third_party/triton/llvm_integration/series.bzl
third_party/xla/third_party/triton/llvm_integration/cl623185214.patch
third_party/xla/third_party/triton/llvm_integration/series.bzl

==Tom Cobley;cobley@google.com;Thu Apr 11 04:33:20 2024 -0700==
third_party/xla/xla/pjrt/cpu/BUILD
third_party/xla/xla/pjrt/cpu/gloo_collectives_test.cc

==Shanbin Ke;ske@nvidia.com;Thu Apr 11 03:30:07 2024 -0700==
third_party/xla/xla/service/gpu/BUILD
third_party/xla/xla/service/gpu/cudnn_fused_mha_rewriter.cc
third_party/xla/xla/service/gpu/cudnn_workspace_rewriter.cc
third_party/xla/xla/service/gpu/cudnn_workspace_rewriter.h
third_party/xla/xla/service/gpu/gpu_fused_mha_runner.cc
third_party/xla/xla/service/gpu/gpu_fused_mha_runner.h
third_party/xla/xla/service/gpu/ir_emitter_unnested.cc
third_party/xla/xla/service/gpu/nvptx_compiler.cc
third_party/xla/xla/service/gpu/runtime/fused_mha_thunk.cc
third_party/xla/xla/service/gpu/runtime/fused_mha_thunk.h
third_party/xla/xla/stream_executor/cuda/cuda_dnn.cc
third_party/xla/xla/stream_executor/cuda/cuda_dnn.h
third_party/xla/xla/stream_executor/dnn.h

==Shawn Wang;shawnw@nvidia.com;Thu Apr 11 02:55:18 2024 -0700==
third_party/xla/xla/service/gpu/gpu_executable.cc
third_party/xla/xla/service/gpu/nccl_clique_key.cc
third_party/xla/xla/service/gpu/nccl_clique_key.h
third_party/xla/xla/service/gpu/nccl_clique_key_test.cc
third_party/xla/xla/service/gpu/runtime/command_buffer_cmd.cc
third_party/xla/xla/service/gpu/runtime/command_buffer_cmd.h
third_party/xla/xla/service/gpu/runtime/command_buffer_cmd_test.cc
third_party/xla/xla/service/gpu/runtime/nccl_collective_thunk.cc
third_party/xla/xla/service/gpu/runtime/nccl_collective_thunk.h
third_party/xla/xla/service/gpu/runtime/thunk.cc
third_party/xla/xla/service/gpu/runtime/thunk.h
third_party/xla/xla/stream_executor/command_buffer.h

==Sergey Kozub;sergeykozub@google.com;Thu Apr 11 01:59:09 2024 -0700==
third_party/xla/xla/service/gpu/llvm_gpu_backend/BUILD
third_party/xla/xla/service/gpu/llvm_gpu_backend/gpu_backend_lib.cc

==Dimitar (Mitko) Asenov;dasenov@google.com;Thu Apr 11 01:38:42 2024 -0700==
third_party/xla/xla/service/gpu/stream_executor_util.cc
third_party/xla/xla/service/gpu/stream_executor_util_test.cc

==Jinliang Wei;jlwei@google.com;Thu Apr 11 00:04:32 2024 -0700==
third_party/xla/xla/service/hlo_value_semantics_analysis.cc
third_party/xla/xla/service/hlo_value_semantics_analysis.h
third_party/xla/xla/service/hlo_value_semantics_analysis_test.cc

==Adrian Kuegel;akuegel@google.com;Wed Apr 10 23:40:00 2024 -0700==
third_party/xla/xla/hlo/ir/hlo_computation.cc
third_party/xla/xla/hlo/ir/hlo_instructions.cc
third_party/xla/xla/hlo/ir/hlo_instructions.h

==Eugene Zhulenev;ezhulenev@google.com;Wed Apr 10 23:15:44 2024 -0700==
third_party/xla/xla/pjrt/BUILD
third_party/xla/xla/pjrt/pjrt_future.cc
third_party/xla/xla/pjrt/pjrt_future.h
third_party/xla/xla/pjrt/pjrt_future_test.cc

==Clive Verghese;cliveverghese@google.com;Wed Apr 10 22:39:11 2024 -0700==
tensorflow/core/profiler/BUILD
third_party/xla/third_party/tsl/tsl/profiler/backends/cpu/BUILD
third_party/xla/third_party/tsl/tsl/profiler/backends/cpu/threadpool_listener.cc
third_party/xla/third_party/tsl/tsl/profiler/backends/cpu/threadpool_listener.h
third_party/xla/third_party/tsl/tsl/profiler/backends/cpu/threadpool_listener_state.cc
third_party/xla/third_party/tsl/tsl/profiler/backends/cpu/threadpool_listener_state.h
third_party/xla/third_party/tsl/tsl/profiler/lib/BUILD
third_party/xla/third_party/tsl/tsl/profiler/lib/context_types.cc
third_party/xla/third_party/tsl/tsl/profiler/lib/context_types.h
third_party/xla/third_party/tsl/tsl/profiler/utils/BUILD
third_party/xla/third_party/tsl/tsl/profiler/utils/preprocess_xplane.cc
third_party/xla/third_party/tsl/tsl/profiler/utils/preprocess_xplane.h
third_party/xla/third_party/tsl/tsl/profiler/utils/preprocess_xplane_test.cc
third_party/xla/third_party/tsl/tsl/profiler/utils/xplane_schema.cc
third_party/xla/third_party/tsl/tsl/profiler/utils/xplane_schema.h
third_party/xla/xla/backends/profiler/cpu/BUILD
third_party/xla/xla/backends/profiler/cpu/host_tracer.cc

==Gunhyun Park;gunhyun@google.com;Wed Apr 10 22:08:55 2024 -0700==
third_party/xla/xla/client/xla_builder_test.cc
third_party/xla/xla/service/shape_inference_test.cc

==Tongfei Guo;tongfei@google.com;Wed Apr 10 21:48:00 2024 -0700==
third_party/xla/xla/hlo/utils/hlo_sharding_util.cc
third_party/xla/xla/hlo/utils/hlo_sharding_util.h
third_party/xla/xla/service/BUILD
third_party/xla/xla/service/algebraic_simplifier.cc
third_party/xla/xla/service/algebraic_simplifier_test.cc
third_party/xla/xla/service/spmd/gather_scatter_handler.cc

==Emilio Cota;ecg@google.com;Wed Apr 10 21:27:49 2024 -0700==
third_party/xla/xla/hlo/ir/hlo_computation.cc
third_party/xla/xla/hlo/ir/hlo_computation.h

==Zixuan Jiang;zixuanjiang@google.com;Wed Apr 10 21:15:29 2024 -0700==
third_party/xla/xla/client/BUILD
third_party/xla/xla/client/xla_builder.cc
third_party/xla/xla/client/xla_builder.h
third_party/xla/xla/client/xla_builder_test.cc

==Kyle Lucke;klucke@google.com;Wed Apr 10 16:41:44 2024 -0700==
tensorflow/c/experimental/stream_executor/stream_executor.cc
third_party/xla/xla/backends/interpreter/executor.h
third_party/xla/xla/backends/interpreter/platform.cc
third_party/xla/xla/stream_executor/cuda/cuda_executor.cc
third_party/xla/xla/stream_executor/cuda/cuda_platform.cc
third_party/xla/xla/stream_executor/gpu/gpu_executor.h
third_party/xla/xla/stream_executor/host/host_executor.cc
third_party/xla/xla/stream_executor/host/host_executor.h
third_party/xla/xla/stream_executor/host/host_platform.cc
third_party/xla/xla/stream_executor/rocm/rocm_executor.cc
third_party/xla/xla/stream_executor/rocm/rocm_platform.cc
third_party/xla/xla/stream_executor/stream_executor_internal.h
third_party/xla/xla/stream_executor/stream_executor_pimpl.cc
third_party/xla/xla/stream_executor/stream_executor_pimpl.h
third_party/xla/xla/stream_executor/tpu/tpu_executor.cc
third_party/xla/xla/stream_executor/tpu/tpu_executor.h
third_party/xla/xla/stream_executor/tpu/tpu_executor_c_api.h
third_party/xla/xla/stream_executor/tpu/tpu_platform.cc

==Kyle Lucke;klucke@google.com;Wed Apr 10 16:03:12 2024 -0700==
third_party/xla/xla/service/gpu/BUILD
third_party/xla/xla/service/gpu/mock_nccl_topo_config.h
third_party/xla/xla/service/gpu/mock_nccl_utils.cc
third_party/xla/xla/service/gpu/mock_nccl_utils.h
third_party/xla/xla/service/gpu/mock_nccl_utils_default.cc
third_party/xla/xla/service/gpu/mock_nccl_xml.cc
third_party/xla/xla/service/gpu/mock_nccl_xml.h
third_party/xla/xla/service/gpu/mock_nccl_xml_test.cc

==Gunhyun Park;gunhyun@google.com;Wed Apr 10 15:54:09 2024 -0700==
third_party/xla/xla/client/xla_builder_test.cc
third_party/xla/xla/service/shape_inference.cc
third_party/xla/xla/service/shape_inference_test.cc

==Yunlong Liu;yunlongl@google.com;Wed Apr 10 15:25:42 2024 -0700==
third_party/xla/xla/pjrt/BUILD
third_party/xla/xla/pjrt/c/CHANGELOG.md
third_party/xla/xla/pjrt/c/pjrt_c_api.h
third_party/xla/xla/pjrt/c/pjrt_c_api_wrapper_impl.cc
third_party/xla/xla/pjrt/c/pjrt_c_api_wrapper_impl.h
third_party/xla/xla/pjrt/host_memory_spaces.cc
third_party/xla/xla/pjrt/host_memory_spaces.h
third_party/xla/xla/pjrt/pjrt_c_api_client.cc
third_party/xla/xla/pjrt/pjrt_c_api_client.h
third_party/xla/xla/pjrt/pjrt_client.h
third_party/xla/xla/python/ifrt/memory.cc
third_party/xla/xla/python/ifrt/mock.h
third_party/xla/xla/python/ifrt_proxy/client/client.cc
third_party/xla/xla/python/ifrt_proxy/client/client_test.cc
third_party/xla/xla/python/ifrt_proxy/client/memory.h
third_party/xla/xla/python/ifrt_proxy/common/ifrt_service.proto
third_party/xla/xla/python/ifrt_proxy/server/ifrt_backend.cc
third_party/xla/xla/python/ifrt_proxy/server/ifrt_backend_test.cc
third_party/xla/xla/python/pjrt_ifrt/pjrt_array.cc
third_party/xla/xla/python/pjrt_ifrt/pjrt_client.cc
third_party/xla/xla/python/py_device.cc
third_party/xla/xla/python/py_device_list.cc
third_party/xla/xla/python/py_memory_space.cc

==Gunhyun Park;gunhyun@google.com;Wed Apr 10 14:36:46 2024 -0700==
third_party/xla/xla/client/xla_builder_test.cc
third_party/xla/xla/service/shape_inference_test.cc

==Gunhyun Park;gunhyun@google.com;Wed Apr 10 14:26:33 2024 -0700==
third_party/xla/xla/client/xla_builder_test.cc

==Yang Sheng;yang.sheng@intel.com;Wed Apr 10 14:03:14 2024 -0700==
.bazelrc
tensorflow/opensource_only.files
third_party/gpus/crosstool/BUILD.sycl.tpl
third_party/gpus/crosstool/clang/bin/crosstool_wrapper_driver_sycl.tpl
third_party/gpus/crosstool/sycl_cc_toolchain_config.bzl.tpl
third_party/gpus/find_sycl_config.py
third_party/gpus/rocm/build_defs.bzl.tpl
third_party/gpus/rocm_configure.bzl
third_party/gpus/sycl/BUILD
third_party/gpus/sycl/BUILD.tpl
third_party/gpus/sycl/build_defs.bzl.tpl
third_party/gpus/sycl_configure.bzl
third_party/xla/.bazelrc
third_party/xla/third_party/tsl/.bazelrc
third_party/xla/third_party/tsl/opensource_only.files
third_party/xla/third_party/tsl/third_party/gpus/crosstool/BUILD.sycl.tpl
third_party/xla/third_party/tsl/third_party/gpus/crosstool/clang/bin/crosstool_wrapper_driver_sycl.tpl
third_party/xla/third_party/tsl/third_party/gpus/crosstool/sycl_cc_toolchain_config.bzl.tpl
third_party/xla/third_party/tsl/third_party/gpus/find_sycl_config.py
third_party/xla/third_party/tsl/third_party/gpus/rocm/build_defs.bzl.tpl
third_party/xla/third_party/tsl/third_party/gpus/rocm_configure.bzl
third_party/xla/third_party/tsl/third_party/gpus/sycl/BUILD
third_party/xla/third_party/tsl/third_party/gpus/sycl/BUILD.tpl
third_party/xla/third_party/tsl/third_party/gpus/sycl/build_defs.bzl.tpl
third_party/xla/third_party/tsl/third_party/gpus/sycl_configure.bzl
third_party/xla/third_party/tsl/workspace2.bzl
third_party/xla/xla/stream_executor/build_defs.bzl

==Subhankar Shah;subhankarshah@google.com;Wed Apr 10 13:14:16 2024 -0700==
third_party/xla/xla/service/memory_space_assignment/memory_space_assignment.cc
third_party/xla/xla/service/memory_space_assignment/memory_space_assignment.proto
third_party/xla/xla/service/memory_space_assignment/memory_space_assignment_test.cc

==Gunhyun Park;gunhyun@google.com;Wed Apr 10 12:51:44 2024 -0700==
third_party/xla/xla/client/xla_builder_test.cc

==Gunhyun Park;gunhyun@google.com;Wed Apr 10 12:36:28 2024 -0700==
third_party/xla/xla/client/xla_builder_test.cc

==Kyle Lucke;klucke@google.com;Wed Apr 10 12:24:55 2024 -0700==
third_party/xla/xla/stream_executor/rocm/rocm_executor.cc

==Gunhyun Park;gunhyun@google.com;Wed Apr 10 12:15:10 2024 -0700==
third_party/xla/xla/client/xla_builder_test.cc

==Gunhyun Park;gunhyun@google.com;Wed Apr 10 12:03:15 2024 -0700==
third_party/xla/xla/client/xla_builder_test.cc
third_party/xla/xla/service/shape_inference_test.cc

==Ce Zheng;zce@google.com;Wed Apr 10 11:42:33 2024 -0700==
third_party/xla/xla/python/ifrt/device.h
third_party/xla/xla/python/py_device_list.cc

==Gunhyun Park;gunhyun@google.com;Wed Apr 10 11:38:53 2024 -0700==
third_party/xla/xla/client/xla_builder_test.cc
third_party/xla/xla/service/shape_inference.cc
third_party/xla/xla/service/shape_inference_test.cc

```
bash-3.2$ ./scrapLog.py -r  test-data/TensorFlow/tensorFlowGitLog-temporal-10-developers-coediting-the-same-files.IN    --type-of-network=inter_individual_graph_temporal 
```

=== Juxtapose between Raw log and Table with edges
All seem right.

DONE: 
New test files test-data/TensorFlow/tensorFlowGitLog-temporal-10-developers-coediting-the-same-files.IN

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

5 
==  Johannes Reifferscheid ;jreiffers@google.com;Tue Jan 8 06:30:42 2024 -0800==

third_party/xla/xla/service/gpu/fusions/BUILD
third_party/xla/xla/service/gpu/fusions/fusions.cc
third_party/xla/xla/service/gpu/fusions/scatter.cc

4 == NA Giulio C.n;57756052+giuliocn@users.noreply.github.com;Tue Jan 7 14:18:00 2024 +0100==

3 ==  Johannes Reifferscheid;jreiffers@google.com;Tue Jan 6 04:03:16 2024 -0800==
third_party/xla/xla/service/gpu/fusions/BUILD
third_party/xla/xla/service/gpu/fusions/fusions.cc
third_party/xla/xla/service/gpu/fusions/scatter.cc


2 == Adrian Kuegel;akuegel@google.com;Mon Jan 5 23:20:59 2024 -0800==
tensorflow/compiler/jit/xla_activity_logging_listener.cc
tensorflow/core/BUILD
tensorflow/core/kernels/gpu_utils.cc
tensorflow/core/platform/BUILD
tensorflow/core/platform/logger.h


1==Adrian Kuegel;akuegel@google.com;Mon Jan 3 23:44:42 2024 -0800==
third_party/xla/xla/debug_options_flags.cc
third_party/xla/xla/service/gpu/fusions/fusions.cc
third_party/xla/xla/service/gpu/fusions/scatter.cc

0==Dragan Mladjenovic;Dragan.Mladjenovic@amd.com;Tue Jan 1 03:51:03 2024 -0800==
third_party/xla/xla/stream_executor/rocm/rocm_driver.cc

### Expected output 

T0, Jan 1  2024 , no edges 
T1, Jan 3  2024 , no edges 
T2, Jan 5  2024 , no edges
T3, Jan 6  2024 , jreiffers@google.com <-->  akuegel@google.com
T4, Jan 7  2024 , no edges 
T5, Jan 8  2024 , jreiffers@google.com <-->  akuegel@google.com



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