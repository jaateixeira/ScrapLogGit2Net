#!/bin/bash
# =============================================================================
# test_extension_filtering.sh
# Tests the --include-extensions (-ie) and --exclude-extensions (-xe)
# arguments of ScrapLogGit2Net (scrapLog.py).
#
# Test input files use real developer identities and file paths from the
# TensorFlow git log (March 2024).
#
# Test cases:
#   TC1 — include only .py
#         Thai Nguyen + TensorFlower share a .py file → connected
#         Dan Suh + Matt Callanan touch only .cc/.h → must NOT appear
#
#   TC2 — include .py and .cc
#         Thai Nguyen has commits with both .py and .cc → connected to others
#         Dmitri Gribenko touches only .bzl → must NOT appear
#
#   TC3 — exclude .bzl
#         Peter Hawkins has a .bzl-only commit (invisible) + a .cc/.h commit (visible)
#         Dmitri Gribenko touches only .bzl → must NOT appear
#         Gunhyun Park has .bzl (excluded) + .mlir (passes through) → appears via .mlir
#
#   TC4 — include .cc and .h, then exclude .h  (net: .cc only)
#         Henning Becker + Benjamin Chetioui both edited ir_emitter_triton.cc → connected
#         .h-only connections must NOT appear
#
#   TC5 — include .py and .cc, then exclude .cc  (net: .py only)
#         Thai Nguyen has a .py commit + a .cc commit; only .py survives
#         Thai Nguyen + TensorFlower share quantize_model*.py → connected
#         Matt Callanan only has .cc → must NOT appear
#
# part of the ScrapLogGit2Net open-source project
# Developed by Jose Teixeira <jose.teixeira@abo.fi>
# =============================================================================

echo "Testing --include-extensions (-ie) and --exclude-extensions (-xe)"
echo "Test data: ./test-data/ExtensionFiltering/"
echo "part of the ScrapLogGit2Net open-source project"
echo "Developed by Jose Teixeira <jose.teixeira@abo.fi>"

GREEN=$(tput setaf 2)
RED=$(tput setaf 1)
NC=$(tput sgr0)

# -----------------------------------------------------------------------------
# Temp directory
# -----------------------------------------------------------------------------
mkdir -p temp_dir_test_extension_filtering
TEMP_DIR=temp_dir_test_extension_filtering
echo "TEMP_DIR=$TEMP_DIR"

# -----------------------------------------------------------------------------
# Tracking
# -----------------------------------------------------------------------------
TESTS_FAILED=0
FAILED_TESTS=()

# -----------------------------------------------------------------------------
# Helpers — mirrors the existing ScrapLogGit2Net test suite
# -----------------------------------------------------------------------------

compare_xml_structure() {
    local actual_file=$1
    local expected_pattern=$2
    local test_name=$3

    EXPECTED_FILE="$TEMP_DIR/${test_name}_expected.xml"
    echo "$expected_pattern" > "$EXPECTED_FILE"

    ACTUAL_STRUCTURE="$TEMP_DIR/${test_name}_actual_structure.txt"
    EXPECTED_STRUCTURE="$TEMP_DIR/${test_name}_expected_structure.txt"

    if command -v xmlstarlet &> /dev/null; then
        xmlstarlet el "$actual_file" | sort > "$ACTUAL_STRUCTURE"
        xmlstarlet el "$EXPECTED_FILE" | sort > "$EXPECTED_STRUCTURE"
    else
        echo "${RED}Warning: xmlstarlet not found. Falling back to basic diff.${NC}"
        grep -o '<[^>]*>' "$actual_file" | sort -u > "$ACTUAL_STRUCTURE"
        grep -o '<[^>]*>' "$EXPECTED_FILE" | sort -u > "$EXPECTED_STRUCTURE"
    fi

    echo "${RED}XML Structure Comparison for $test_name:${NC}"
    diff -u "$EXPECTED_STRUCTURE" "$ACTUAL_STRUCTURE" || true
    echo
    echo "${RED}Files saved to:${NC}"
    echo "  Expected : $EXPECTED_FILE"
    echo "  Actual   : $actual_file"
    echo
    echo "${RED}To compare manually:${NC}"
    echo "  xmldiff --formatter diff $EXPECTED_FILE $actual_file"
    echo "  colordiff -y $EXPECTED_FILE $actual_file"
}

validate_xml() {
    local xml_file=$1
    local expected_pattern=$2
    local test_name=$3

    EXPECTED_PATTERN_FILE="$TEMP_DIR/${test_name}_expected_pattern.xml"
    echo "$expected_pattern" > "$EXPECTED_PATTERN_FILE"

    if ! xmllint --noout "$xml_file" 2>/dev/null; then
        echo "${RED}Error: Invalid XML in $xml_file${NC}"
        compare_xml_structure "$xml_file" "$expected_pattern" "$test_name"
        return 1
    fi

    if ! grep -q -F "$(echo "$expected_pattern" | tr -d '[:space:]')" \
            <(tr -d '[:space:]' < "$xml_file"); then
        echo "${RED}Error: Expected XML pattern not found in $xml_file${NC}"
        echo "Expected pattern:"
        echo "$expected_pattern"
        echo "Actual XML:"
        cat "$xml_file"
        compare_xml_structure "$xml_file" "$expected_pattern" "$test_name"
        return 1
    fi

    return 0
}

# Assert a node is NOT present in the output.
# Used to confirm developers who only touched filtered-out extensions
# do not appear as collaborators in the network.
assert_node_absent() {
    local xml_file=$1
    local node_id=$2
    local test_name=$3

    if grep -q "\"$node_id\"" "$xml_file"; then
        echo "${RED}Error [$test_name]: node '$node_id' should be absent but was found.${NC}"
        echo "Actual XML:"
        cat "$xml_file"
        return 1
    fi
    return 0
}

# Assert an edge between two nodes is NOT present.
# Used to confirm that collaboration through an excluded file type
# does not leak into the network.
assert_edge_absent() {
    local xml_file=$1
    local source=$2
    local target=$3
    local test_name=$4

    if grep -q \
        "source=\"$source\" target=\"$target\"\|source=\"$target\" target=\"$source\"" \
        "$xml_file"; then
        echo "${RED}Error [$test_name]: edge '$source' <-> '$target' should be absent but was found.${NC}"
        echo "Actual XML:"
        cat "$xml_file"
        return 1
    fi
    return 0
}

# =============================================================================
# TC1 — include only .py
#
# Input:
#   thaink@google.com       → quantize_model.py
#   gardener@tensorflow.org → quantize_model_test.py
#   dansuh@google.com       → attrs_and_constraints.h + nchw_convolution_to_nhwc.cc
#   mpcallanan@google.com   → data_service_client.cc
#
# Expected: Thai + TensorFlower connected; Dan + Matt absent.
# =============================================================================
echo ""
echo "────────────────────────────────────────────────────────────────────"
echo "TESTCASE 1 — include only .py"

TC1_input="test-data/ExtensionFiltering/extfilter-tc1-include-py-only.IN"
TC1_output="extfilter-tc1-include-py-only.NetworkFile.graphML"
TC1_cmd="./scrapLog.py -r $TC1_input -t inter_individual_graph_unweighted --include-only-with-file-extensions .py"

echo "Command: $TC1_cmd"
$TC1_cmd

if [ ! -f "$TC1_output" ]; then
    echo "${RED}Error: output file $TC1_output not found.${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    FAILED_TESTS+=("TC1")
    exit
else
    TC1_xml="$TEMP_DIR/tc1.xml"
    cp "$TC1_output" "$TC1_xml"

    TC1_expected=$(cat << 'EOF'
<node id="thaink@google.com"/>
<node id="gardener@tensorflow.org"/>
<edge source="thaink@google.com" target="gardener@tensorflow.org"
EOF
)
    TC1_passed=true

    if ! validate_xml "$TC1_xml" "$TC1_expected" "TC1"; then TC1_passed=false; fi
    if ! assert_node_absent "$TC1_xml" "dansuh@google.com"     "TC1"; then TC1_passed=false; fi
    if ! assert_node_absent "$TC1_xml" "mpcallanan@google.com" "TC1"; then TC1_passed=false; fi

    $TC1_passed && echo "${GREEN}TESTCASE 1 passed${NC}" || {
        TESTS_FAILED=$((TESTS_FAILED + 1)); FAILED_TESTS+=("TC1")
    }
    rm -f "$TC1_output"
fi

echo
echo

exit

# =============================================================================
# TC2 — include .py and .cc
#
# Input:
#   thaink@google.com     → quantize_model.cc + .h  (commit 1)
#   thaink@google.com     → quantize_model.py        (commit 2)
#   kramerb@google.com    → tensorflow/.../BUILD      (BUILD only)
#   mpcallanan@google.com → data_service_client.cc
#   dmitrig@google.com    → workspace.bzl             (.bzl only)
#
# Expected: Thai + Matt connected via .cc; Dmitri + Kramer absent.
# =============================================================================
echo ""
echo "────────────────────────────────────────────────────────────────────"
echo "TESTCASE 2 — include .py and .cc"

TC2_input="test-data/ExtensionFiltering/extfilter-tc2-include-py-and-cc.IN"
TC2_output="extfilter-tc2-include-py-and-cc.NetworkFile.graphML"
TC2_cmd="./scrapLog.py -r $TC2_input -t inter_individual_graph_unweighted -ie .py .cc"

echo "Command: $TC2_cmd"
$TC2_cmd

if [ ! -f "$TC2_output" ]; then
    echo "${RED}Error: output file $TC2_output not found.${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    FAILED_TESTS+=("TC2")
else
    TC2_xml="$TEMP_DIR/tc2.xml"
    cp "$TC2_output" "$TC2_xml"

    TC2_expected=$(cat << 'EOF'
<node id="thaink@google.com"/>
<node id="mpcallanan@google.com"/>
EOF
)
    TC2_passed=true

    if ! validate_xml "$TC2_xml" "$TC2_expected" "TC2"; then TC2_passed=false; fi
    if ! assert_node_absent "$TC2_xml" "dmitrig@google.com"  "TC2"; then TC2_passed=false; fi
    if ! assert_node_absent "$TC2_xml" "kramerb@google.com"  "TC2"; then TC2_passed=false; fi

    $TC2_passed && echo "${GREEN}TESTCASE 2 passed${NC}" || {
        TESTS_FAILED=$((TESTS_FAILED + 1)); FAILED_TESTS+=("TC2")
    }
    rm -f "$TC2_output"
fi

echo
echo

# =============================================================================
# TC3 — exclude .bzl
#
# Input:
#   phawkins@google.com  → four .bzl files only          (commit 1 — all excluded)
#   phawkins@google.com  → BUILD + jax_jit.cc/.h + ...  (commit 2 — .cc/.h survive)
#   dmitrig@google.com   → workspace.bzl                 (.bzl only)
#   slebedev@google.com  → ir_emitter_unnested.cc + kernel_arguments.cc/.h
#   gunhyun@google.com   → workspace.bzl (excluded) + ops.mlir (survives)
#
# Expected: Peter appears via commit 2; Dmitri absent entirely;
#           Peter-Dmitri edge from commit 1 must not appear.
# =============================================================================
echo ""
echo "────────────────────────────────────────────────────────────────────"
echo "TESTCASE 3 — exclude .bzl"

TC3_input="test-data/ExtensionFiltering/extfilter-tc3-exclude-bzl.IN"
TC3_output="extfilter-tc3-exclude-bzl.NetworkFile.graphML"
TC3_cmd="./scrapLog.py -r $TC3_input -t inter_individual_graph_unweighted -xe .bzl"

echo "Command: $TC3_cmd"
$TC3_cmd

if [ ! -f "$TC3_output" ]; then
    echo "${RED}Error: output file $TC3_output not found.${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    FAILED_TESTS+=("TC3")
else
    TC3_xml="$TEMP_DIR/tc3.xml"
    cp "$TC3_output" "$TC3_xml"

    TC3_expected=$(cat << 'EOF'
<node id="phawkins@google.com"/>
<node id="slebedev@google.com"/>
EOF
)
    TC3_passed=true

    if ! validate_xml "$TC3_xml" "$TC3_expected" "TC3"; then TC3_passed=false; fi
    if ! assert_node_absent "$TC3_xml" "dmitrig@google.com"  "TC3"; then TC3_passed=false; fi
    if ! assert_edge_absent "$TC3_xml" \
        "phawkins@google.com" "dmitrig@google.com" "TC3"; then TC3_passed=false; fi

    $TC3_passed && echo "${GREEN}TESTCASE 3 passed${NC}" || {
        TESTS_FAILED=$((TESTS_FAILED + 1)); FAILED_TESTS+=("TC3")
    }
    rm -f "$TC3_output"
fi

echo
echo

# =============================================================================
# TC4 — include .cc and .h, then exclude .h  (net: .cc only)
#
# Input:
#   hebecker@google.com    → fusion_emitter.cc + indexing_map.cc/.h + ir_emitter_triton.cc
#   bchetioui@google.com   → gemm_fusion.cc + ir_emitter_triton.cc + softmax_rewriter_triton.cc
#   tsilytskyi@google.com  → kernel.h + kernel_spec.cc/.h
#   kanvi.khanna@intel.com → change_op_data_type.cc + onednn_matmul_rewriter.cc
#
# Expected: Becker + Chetioui connected via ir_emitter_triton.cc;
#           Tsilytskyi does NOT connect to Becker (no shared .cc).
# =============================================================================
echo ""
echo "────────────────────────────────────────────────────────────────────"
echo "TESTCASE 4 — include .cc .h then exclude .h  (net: .cc only)"

TC4_input="test-data/ExtensionFiltering/extfilter-tc4-include-cc-h-exclude-h.IN"
TC4_output="extfilter-tc4-include-cc-h-exclude-h.NetworkFile.graphML"
TC4_cmd="./scrapLog.py -r $TC4_input -t inter_individual_graph_unweighted -ie .cc .h -xe .h"

echo "Command: $TC4_cmd"
$TC4_cmd

if [ ! -f "$TC4_output" ]; then
    echo "${RED}Error: output file $TC4_output not found.${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    FAILED_TESTS+=("TC4")
else
    TC4_xml="$TEMP_DIR/tc4.xml"
    cp "$TC4_output" "$TC4_xml"

    TC4_expected=$(cat << 'EOF'
<node id="hebecker@google.com"/>
<node id="bchetioui@google.com"/>
<edge source="hebecker@google.com" target="bchetioui@google.com"
EOF
)
    TC4_passed=true

    if ! validate_xml "$TC4_xml" "$TC4_expected" "TC4"; then TC4_passed=false; fi
    # kernel.h excluded — Tsilytskyi must not connect to Becker via .h alone
    if ! assert_edge_absent "$TC4_xml" \
        "tsilytskyi@google.com" "hebecker@google.com" "TC4"; then TC4_passed=false; fi

    $TC4_passed && echo "${GREEN}TESTCASE 4 passed${NC}" || {
        TESTS_FAILED=$((TESTS_FAILED + 1)); FAILED_TESTS+=("TC4")
    }
    rm -f "$TC4_output"
fi

echo
echo

# =============================================================================
# TC5 — include .py and .cc, then exclude .cc  (net: .py only)
#
# Input:
#   thaink@google.com          → quantize_model.cc + .h  (commit 1 — .cc excluded)
#   thaink@google.com          → quantize_model.py       (commit 2 — survives)
#   gardener@tensorflow.org    → quantize_model_test.py  (survives)
#   mpcallanan@google.com      → data_service_client.cc  (excluded)
#   dansuh@google.com          → attrs_and_constraints.h + nchw*.cc  (both excluded)
#
# Expected: Thai + TensorFlower connected via .py;
#           Matt absent; Dan absent; Thai-Matt edge absent.
# =============================================================================
echo ""
echo "────────────────────────────────────────────────────────────────────"
echo "TESTCASE 5 — include .py .cc then exclude .cc  (net: .py only)"

TC5_input="test-data/ExtensionFiltering/extfilter-tc5-include-py-cc-exclude-cc.IN"
TC5_output="extfilter-tc5-include-py-cc-exclude-cc.NetworkFile.graphML"
TC5_cmd="./scrapLog.py -r $TC5_input -t inter_individual_graph_unweighted -ie .py .cc -xe .cc"

echo "Command: $TC5_cmd"
$TC5_cmd

if [ ! -f "$TC5_output" ]; then
    echo "${RED}Error: output file $TC5_output not found.${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    FAILED_TESTS+=("TC5")
else
    TC5_xml="$TEMP_DIR/tc5.xml"
    cp "$TC5_output" "$TC5_xml"

    TC5_expected=$(cat << 'EOF'
<node id="thaink@google.com"/>
<node id="gardener@tensorflow.org"/>
<edge source="thaink@google.com" target="gardener@tensorflow.org"
EOF
)
    TC5_passed=true

    if ! validate_xml "$TC5_xml" "$TC5_expected" "TC5"; then TC5_passed=false; fi
    if ! assert_node_absent "$TC5_xml" "mpcallanan@google.com" "TC5"; then TC5_passed=false; fi
    if ! assert_node_absent "$TC5_xml" "dansuh@google.com"     "TC5"; then TC5_passed=false; fi
    if ! assert_edge_absent "$TC5_xml" \
        "thaink@google.com" "mpcallanan@google.com" "TC5"; then TC5_passed=false; fi

    $TC5_passed && echo "${GREEN}TESTCASE 5 passed${NC}" || {
        TESTS_FAILED=$((TESTS_FAILED + 1)); FAILED_TESTS+=("TC5")
    }
    rm -f "$TC5_output"
fi

# =============================================================================
# Summary
# =============================================================================
echo ""
echo "════════════════════════════════════════════════════════════════════"
if [ $TESTS_FAILED -eq 0 ]; then
    echo "${GREEN}ALL TESTS PASSED (5/5)${NC}"
    exit 0
else
    echo "${RED}FAILED: ${FAILED_TESTS[*]}  ($TESTS_FAILED/5 failed)${NC}"
    echo
    echo "${RED}Intermediate files for inspection: $TEMP_DIR/${NC}"
    echo "  *_expected.xml  — what the test expected"
    echo "  tc*.xml         — actual output from scrapLog.py"
    exit 1
fi
