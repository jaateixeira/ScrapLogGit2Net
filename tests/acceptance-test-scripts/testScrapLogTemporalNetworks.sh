#!/bin/bash
echo "Is scrapLogTemporalNetworks.py doing what is supposed to do in temporal networks mode?"
echo "This tests scrapLog.py by executing it against input files in ./test-data/"
echo "The input test files are:"
ls --color "test-data/TensorFlow/tensorFlowGitLog-temporal"*
echo "part of the ScrapLogGit2Net open-source project"
echo "Developed by Jose Teixeira <jose.teixeira@abo.fi> "

GREEN=$(tput setaf 2)
RED=$(tput setaf 1)
NC=$(tput sgr0)



assert_str_in_file() {
    local expected="$1"
    local file="$2"

    if grep -qF "$expected" "$file"; then
        echo "${GREEN}✓ Found: '$expected' in $file${NC}"
        return 0
    else
        echo "${RED}✗ Failed: '$expected' NOT found in $file${NC}"
        return 1
    fi
}


# TEST CASE 1
# Input with 2 developers all commiting the same file.
# Should result in only one edge

TC1_input_file="test-data/TensorFlow/tensorFlowGitLog-temporal-2-developers-3-commits-same-file.IN"
TC1_command="./scrapLog.py -r  $TC1_input_file --type-of-network=inter_individual_graph_temporal"


echo "" 
echo "Testing with $TC1_input_file"
echo "$TC1_command"


$TC1_command

TC1_output_file="tensorFlowGitLog-temporal-2-developers-3-commits-same-file.temporal.graphml.zip"

# Check if the file exists
if [ ! -f "$TC1_output_file" ]; then
    echo "Error: File $TC1_output_file not found."
    exit 1
fi

expected_pattern=('<graph edgedefault="undirected">
    <node id="dasenov@google.com" />
    <node id="ddunleavy@google.com" />
    <edge source="dasenov@google.com" target="ddunleavy@google.com" id="0">
      <data key="d0">2024-01-03T04:05:02-08:00</data>
    </edge>
  </graph>')

echo expected_pattern="${expected_pattern[0]}"

if zgrep -z -q -F "${expected_pattern[0]}" $TC1_output_file; then
     echo "Success: exported graphML.zip file had expected content"
        echo "${GREEN}TESTCASE 1 passed${NC}"
else
     echo "${RED}TESTCASE 1 did not pass${NC}"
    echo "ScrapLog should result in  ${expected_pattern[0]}"
fi

rm -v $TC1_output_file

exit




