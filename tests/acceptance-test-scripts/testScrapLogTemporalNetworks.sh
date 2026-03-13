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

expected_pattern=$(cat << 'EOF'
<graph edgedefault="undirected">
    <node id="dasenov@google.com" />
    <node id="ddunleavy@google.com" />
    <edge source="dasenov@google.com" target="ddunleavy@google.com" id="0">
      <data key="d0">2024-01-03T04:05:02-08:00</data>
    </edge>
  </graph>
EOF
)

echo "expected_pattern=\"$expected_pattern\""

# Unzip and test with regular grep
if gunzip -c "$TC1_output_file" | grep -q -F "$expected_pattern"; then
     echo "Success: exported graphML.zip file had expected content"
        echo "${GREEN}TESTCASE 1 passed${NC}"
else
     echo "${RED}TESTCASE 1 did not pass${NC}"
    echo "ScrapLog should result in: $expected_pattern"
fi

rm -v "$TC1_output_file"

echo
echo

# TEST CASE 2
# Input with 2 developers all commiting the same file.
# Should result in only one edge

TC2_input_file="test-data/TensorFlow/tensorFlowGitLog-temporal-2-developers-3-commits-two-files.IN
"
TC2_command="./scrapLog.py -r  $TC2_input_file --type-of-network=inter_individual_graph_temporal"


echo ""
echo "Testing with $TC2_input_file"
echo "$TC2_command"


$TC2_command

TC2_output_file="tensorFlowGitLog-temporal-2-developers-3-commits-two-files.temporal.graphml.zip"

# Check if the file exists
if [ ! -f "$TC2_output_file" ]; then
    echo "Error: File $TC2_output_file not found."
    exit 1
fi

expected_pattern=$(cat << 'EOF'
<graph edgedefault="undirected">
    <node id="dasenov@google.com" />
    <node id="ddunleavy@google.com" />
    <edge source="dasenov@google.com" target="ddunleavy@google.com" id="0">
      <data key="d0">2024-01-03T04:05:02-08:00</data>
    </edge>
  </graph>
EOF
)

echo "expected_pattern=\"$expected_pattern\""

# Unzip and test with regular grep
if gunzip -c "$TC2_output_file" | grep -q -F "$expected_pattern"; then
     echo "Success: exported graphML.zip file had expected content"
        echo "${GREEN}TESTCASE 2 passed${NC}"
else
     echo "${RED}TESTCASE 2 did not pass${NC}"
    echo "ScrapLog should result in: $expected_pattern"
fi

rm -v "$TC2_output_file"


echo
echo

# TEST CASE 3
# Input with 3 developers with two of them commiting the same files.
# Should result in only two edges

TC3_input_file="test-data/TensorFlow/tensorFlowGitLog-temporal-3-developers-6-commits-thee-files.IN"

TC3_command="./scrapLog.py -r  $TC3_input_file --type-of-network=inter_individual_graph_temporal"


echo ""
echo "Testing with $TC3_input_file"
echo "$TC3_command"


$TC3_command

TC3_output_file="tensorFlowGitLog-temporal-3-developers-6-commits-thee-files.temporal.graphml.zip"

# Check if the file exists
if [ ! -f "$TC3_output_file" ]; then
    echo "Error: File $TC3_output_file not found."
    exit 1
fi

expected_pattern=$(cat << 'EOF'
<graph edgedefault="undirected">
    <node id="akuegel@google.com" />
    <node id="jreiffers@google.com" />
    <edge source="akuegel@google.com" target="jreiffers@google.com" id="0">
      <data key="d0">2024-01-06T04:03:16-08:00</data>
    </edge>
    <edge source="akuegel@google.com" target="jreiffers@google.com" id="1">
      <data key="d0">2024-01-08T06:30:42-08:00</data>
    </edge>
  </graph>
EOF
)

echo "expected_pattern=\"$expected_pattern\""

# Unzip and test with regular grep
if gunzip -c "$TC3_output_file" | grep -q -F "$expected_pattern"; then
     echo "Success: exported graphML.zip file had expected content"
        echo "${GREEN}TESTCASE 3 passed${NC}"
else
     echo "${RED}TESTCASE 3 did not pass${NC}"
    echo "ScrapLog should result in: $expected_pattern"
fi

rm -v "$TC3_output_file"

echo
echo

# TEST CASE 4
# Input with circa 10  developers all commiting many files
# Should result in only one edge

TC4_input_file="test-data/TensorFlow/tensorFlowGitLog-temporal-10-developers-coediting-the-same-files.IN
"

TC4_command="./scrapLog.py -r  $TC4_input_file --type-of-network=inter_individual_graph_temporal"


echo ""
echo "Testing with $TC4_input_file"
echo "$TC4_command"


$TC4_command

TC4_output_file="tensorFlowGitLog-temporal-10-developers-coediting-the-same-files.temporal.graphml.zip"

# Check if the file exists
if [ ! -f "$TC4_output_file" ]; then
    echo "Error: File $TC4_output_file not found."
    exit 1
fi

expected_pattern=$(cat << 'EOF'
<graph edgedefault="undirected">
    <node id="yunlongl@google.com" />
    <node id="zce@google.com" />
    <node id="ezhulenev@google.com" />
    <node id="gunhyun@google.com" />
    <node id="zixuanjiang@google.com" />
    <node id="akuegel@google.com" />
    <node id="ecg@google.com" />
    <node id="klucke@google.com" />
    <node id="ske@nvidia.com" />
    <node id="blakehechtman@google.com" />
    <node id="tongfei@google.com" />
    <node id="hebecker@google.com" />
    <node id="sergeykozub@google.com" />
    <edge source="yunlongl@google.com" target="zce@google.com" id="0">
      <data key="d0">2024-04-10T15:25:42-07:00</data>
    </edge>
    <edge source="yunlongl@google.com" target="ezhulenev@google.com" id="0">
      <data key="d0">2024-04-10T23:15:44-07:00</data>
    </edge>
    <edge source="yunlongl@google.com" target="ezhulenev@google.com" id="1">
      <data key="d0">2024-04-11T09:16:48-07:00</data>
    </edge>
    <edge source="gunhyun@google.com" target="zixuanjiang@google.com" id="0">
      <data key="d0">2024-04-10T21:15:29-07:00</data>
    </edge>
    <edge source="gunhyun@google.com" target="zixuanjiang@google.com" id="1">
      <data key="d0">2024-04-10T22:08:55-07:00</data>
    </edge>
    <edge source="akuegel@google.com" target="ecg@google.com" id="0">
      <data key="d0">2024-04-10T23:40:00-07:00</data>
    </edge>
    <edge source="klucke@google.com" target="ske@nvidia.com" id="0">
      <data key="d0">2024-04-11T03:30:07-07:00</data>
    </edge>
    <edge source="blakehechtman@google.com" target="tongfei@google.com" id="0">
      <data key="d0">2024-04-11T09:55:57-07:00</data>
    </edge>
    <edge source="hebecker@google.com" target="sergeykozub@google.com" id="0">
      <data key="d0">2024-04-11T12:29:17-07:00</data>
    </edge>
  </graph>
EOF
)

echo "expected_pattern=\"$expected_pattern\""

# Unzip and test with regular grep
if gunzip -c "$TC4_output_file" | grep -q -F "$expected_pattern"; then
     echo "Success: exported graphML.zip file had expected content"
        echo "${GREEN}TESTCASE 4 passed${NC}"
else
     echo "${RED}TESTCASE 4 did not pass${NC}"
    echo "ScrapLog should result in: $expected_pattern"
fi

rm -v "$TC4_output_file"

echo
echo