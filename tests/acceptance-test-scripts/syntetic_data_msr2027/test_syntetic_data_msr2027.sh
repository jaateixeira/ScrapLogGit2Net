#!/bin/bash
# =============================================================================
# test_syntetic_data_msr2027.sh
# Acceptance test on the synthetic project of the MSR 2027 tool paper
# (running example, Table "Synthetic project"). Checks that scrapLog.py and
# transform_nofi_2_nofo_graphml.py produce exactly the networks described in
# the paper, which were computed by hand.
#
# Input: test-data/syntetic_data_msr2027/syntetic_data_msr2027.IN
#   (the git log written by test-data/syntetic_data_msr2027/make_toy_log.sh)
#
# Five developers, three companies, nine commits, five files:
#   Jan 3  Ana  (alpha.com) core/scheduler.c, core/memory.c
#   Jan 8  Bob  (alpha.com) core/scheduler.c
#   Jan 15 Cleo (beta.org)  core/scheduler.c, net/driver.c
#   Jan 22 Dan  (beta.org)  net/driver.c
#   Feb 2  Eli  (gamma.io)  net/driver.c, docs/guide.md
#   Feb 12 Bob  (alpha.com) docs/guide.md
#   Feb 20 Ana  (alpha.com) core/memory.c        (only Ana: no tie, no self-loop)
#   Mar 5  Eli  (gamma.io)  tests/test_core.c    (only Eli: no tie)
#   Mar 11 Dan  (beta.org)  net/driver.c
#
# A contact (i, j, t) is made when a developer edits a file that another
# developer edited before; t is the time of the later edit. Hand-computed:
#   Jan 8  bob-ana                 (scheduler.c)
#   Jan 15 cleo-ana, cleo-bob      (scheduler.c)
#   Jan 22 dan-cleo                (driver.c)
#   Feb 2  eli-cleo, eli-dan       (driver.c)
#   Feb 12 bob-eli                 (guide.md)
#   Mar 11 dan-cleo, dan-eli       (driver.c)
#   -> 9 contacts, 7 developer pairs; cleo-dan and dan-eli have weight 2.
# Organizations (ties inside a company dropped, weight = developer pairs):
#   alpha-beta 2 (ana-cleo, bob-cleo), beta-gamma 2 (cleo-eli, dan-eli),
#   alpha-gamma 1 (bob-eli).
#
# Test cases:
#   TC1 unweighted network of individuals (default -t)
#   TC2 weighted network of individuals
#   TC3 temporal network of individuals (contact sequence)
#   TC4 network of organizations (transform_nofi_2_nofo_graphml.py on TC1)
#   TC5 same input gives byte-identical output (TC1-TC3 run twice)
#
# Run from the repository root:
#   bash tests/acceptance-test-scripts/syntetic_data_msr2027/test_syntetic_data_msr2027.sh
# Needs python with the scraplog dependencies, and xmllint.
#
# part of the ScrapLogGit2Net open-source project
# =============================================================================

echo "Testing scrapLog.py on the synthetic project of the MSR 2027 paper"
echo "Test data: ./test-data/syntetic_data_msr2027/"

GREEN=$(tput setaf 2 2>/dev/null || true)
RED=$(tput setaf 1 2>/dev/null || true)
NC=$(tput sgr0 2>/dev/null || true)

INPUT=test-data/syntetic_data_msr2027/syntetic_data_msr2027.IN
if [ ! -f "$INPUT" ] || [ ! -f scrapLog.py ]; then
    echo "${RED}Run this script from the repository root ($INPUT not found).${NC}"
    exit 1
fi

TEMP_DIR=temp_dir_test_syntetic_data_msr2027
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"
echo "TEMP_DIR=$TEMP_DIR"

TESTS_FAILED=0
FAILED_TESTS=()

fail() {
    echo "${RED}FAIL [$1]: $2${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    FAILED_TESTS+=("$1")
}

pass() {
    echo "${GREEN}PASS [$1]${NC}"
}

# Print a GraphML network (plain or zipped) in a canonical, sorted text form:
#   node <e-mail or id> <affiliation or ->
#   edge <a> <b> <weight or time or ->     (a < b; one line per parallel edge)
# Nodes are named by their e-mail attribute when they have one, else by id.
canonical_network() {
    python - "$1" <<'EOF'
import io, sys, zipfile
import networkx as nx

path = sys.argv[1]
if zipfile.is_zipfile(path):
    with zipfile.ZipFile(path) as archive:
        source = io.BytesIO(archive.read(archive.namelist()[0]))
else:
    source = path
g = nx.read_graphml(source, force_multigraph=True)

def name(n):
    return g.nodes[n].get('e-mail', n)

lines = [f"node {name(n)} {g.nodes[n].get('affiliation', '-')}" for n in g.nodes]
for u, v, d in g.edges(data=True):
    a, b = sorted((name(u), name(v)))
    lines.append(f"edge {a} {b} {d.get('weight', d.get('time', '-'))}")
print("\n".join(sorted(lines)))
EOF
}

# check_network <test name> <graphml file> <expected canonical text>
check_network() {
    local test_name=$1 file=$2 expected=$3
    if [ ! -f "$file" ]; then
        fail "$test_name" "output file $file was not written"
        return
    fi
    if python -c "import zipfile, sys; sys.exit(0 if zipfile.is_zipfile(sys.argv[1]) else 1)" "$file"; then
        mkdir -p "$TEMP_DIR/${test_name}_unzipped"
        unzip -o -q "$file" -d "$TEMP_DIR/${test_name}_unzipped"
        xml_file=$(ls "$TEMP_DIR/${test_name}_unzipped"/* | head -n 1)
    else
        xml_file=$file
    fi
    if ! xmllint --noout "$xml_file"; then
        fail "$test_name" "$xml_file is not well-formed XML"
        return
    fi
    echo "$expected" | LC_ALL=C sort > "$TEMP_DIR/${test_name}_expected.txt"
    canonical_network "$file" | LC_ALL=C sort > "$TEMP_DIR/${test_name}_actual.txt"
    if diff -u "$TEMP_DIR/${test_name}_expected.txt" "$TEMP_DIR/${test_name}_actual.txt"; then
        pass "$test_name"
    else
        fail "$test_name" "network differs from the hand-computed one (diff above: - expected, + actual)"
    fi
}

# run <test name> <command...>: run a command, log its output, fail on non-zero exit
run() {
    local test_name=$1
    shift
    if ! "$@" > "$TEMP_DIR/${test_name}.log" 2>&1; then
        fail "$test_name" "command failed: $* (see $TEMP_DIR/${test_name}.log)"
        return 1
    fi
}

# =============================================================================
echo ""
echo "TC1 — unweighted network of individuals"
TC1_OUT=$TEMP_DIR/syntetic.NetworkFile.graphML
if run TC1 python scrapLog.py -r "$INPUT" -o "$TC1_OUT"; then
    check_network TC1 "$TC1_OUT" "node ana@alpha.com alpha
node bob@alpha.com alpha
node cleo@beta.org beta
node dan@beta.org beta
node eli@gamma.io gamma
edge ana@alpha.com bob@alpha.com -
edge ana@alpha.com cleo@beta.org -
edge bob@alpha.com cleo@beta.org -
edge bob@alpha.com eli@gamma.io -
edge cleo@beta.org dan@beta.org -
edge cleo@beta.org eli@gamma.io -
edge dan@beta.org eli@gamma.io -"
fi

# =============================================================================
echo ""
echo "TC2 — weighted network of individuals"
TC2_OUT=$TEMP_DIR/syntetic.WeightedNetwork.graphML
if run TC2 python scrapLog.py -r "$INPUT" -t inter_individual_graph_weighted -o "$TC2_OUT"; then
    check_network TC2 "$TC2_OUT" "node ana@alpha.com alpha
node bob@alpha.com alpha
node cleo@beta.org beta
node dan@beta.org beta
node eli@gamma.io gamma
edge ana@alpha.com bob@alpha.com 1
edge ana@alpha.com cleo@beta.org 1
edge bob@alpha.com cleo@beta.org 1
edge bob@alpha.com eli@gamma.io 1
edge cleo@beta.org dan@beta.org 2
edge cleo@beta.org eli@gamma.io 1
edge dan@beta.org eli@gamma.io 2"
fi

# =============================================================================
echo ""
echo "TC3 — temporal network of individuals (9 contacts)"
TC3_OUT=$TEMP_DIR/syntetic.temporal.graphml.zip
if run TC3 python scrapLog.py -r "$INPUT" -t inter_individual_graph_temporal -o "$TC3_OUT"; then
    check_network TC3 "$TC3_OUT" "node ana@alpha.com -
node bob@alpha.com -
node cleo@beta.org -
node dan@beta.org -
node eli@gamma.io -
edge ana@alpha.com bob@alpha.com 2024-01-08T10:00:00+00:00
edge ana@alpha.com cleo@beta.org 2024-01-15T10:00:00+00:00
edge bob@alpha.com cleo@beta.org 2024-01-15T10:00:00+00:00
edge cleo@beta.org dan@beta.org 2024-01-22T10:00:00+00:00
edge cleo@beta.org eli@gamma.io 2024-02-02T10:00:00+00:00
edge dan@beta.org eli@gamma.io 2024-02-02T10:00:00+00:00
edge bob@alpha.com eli@gamma.io 2024-02-12T10:00:00+00:00
edge cleo@beta.org dan@beta.org 2024-03-11T10:00:00+00:00
edge dan@beta.org eli@gamma.io 2024-03-11T10:00:00+00:00"
fi

# =============================================================================
echo ""
echo "TC4 — network of organizations (from the TC1 network)"
TC4_PREFIX=$TEMP_DIR/syntetic-nofo
rm -f "$TC4_PREFIX".*
if [ -f "$TC1_OUT" ] && run TC4 python transform_nofi_2_nofo_graphml.py "$TC1_OUT" -o "$TC4_PREFIX"; then
    TC4_OUT=$(ls "$TC4_PREFIX"* 2>/dev/null | head -n 1)
    check_network TC4 "${TC4_OUT:-$TC4_PREFIX.graphML}" "node alpha -
node beta -
node gamma -
edge alpha beta 2
edge alpha gamma 1
edge beta gamma 2"
elif [ ! -f "$TC1_OUT" ]; then
    fail TC4 "skipped: TC1 produced no network"
fi

# =============================================================================
echo ""
echo "TC5 — same input gives byte-identical output"
TC5_OK=1
# The second run writes files with the same names into another folder: the
# temporal zip stores the file name inside the archive.
AGAIN_DIR=$TEMP_DIR/again
mkdir -p "$AGAIN_DIR"
for args in "-t inter_individual_graph_unweighted|$TC1_OUT" \
            "-t inter_individual_graph_weighted|$TC2_OUT" \
            "-t inter_individual_graph_temporal|$TC3_OUT"; do
    options=${args%%|*}
    first=${args##*|}
    second=$AGAIN_DIR/$(basename "$first")
    # shellcheck disable=SC2086  # options are split on purpose
    if ! run TC5 python scrapLog.py -r "$INPUT" $options -o "$second"; then
        TC5_OK=0
    elif ! cmp -s "$first" "$second"; then
        echo "${RED}$first and $second differ${NC}"
        TC5_OK=0
    fi
done
if [ "$TC5_OK" -eq 1 ]; then
    pass TC5
else
    fail TC5 "a second run did not reproduce the same bytes"
fi

# =============================================================================
echo ""
echo "────────────────────────────────────────────────────────────────────"
if [ "$TESTS_FAILED" -eq 0 ]; then
    echo "${GREEN}All 5 test cases passed.${NC}"
    exit 0
else
    echo "${RED}$TESTS_FAILED test case(s) failed: ${FAILED_TESTS[*]}${NC}"
    echo "Outputs and logs are in $TEMP_DIR/"
    exit 1
fi
