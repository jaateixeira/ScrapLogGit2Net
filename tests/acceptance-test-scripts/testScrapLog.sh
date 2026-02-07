#!/bin/bash
echo "Is scrapLog.py doing what is suposed to do?"
echo "This tests scrapLog.py by executing it againt input files in ./test-data/"
echo "part of the ScrapLogGit2Net open-source project"
echo "Developed by Jose Teixeira <jose.teixeira@abo.fi> "

GREEN=$(tput setaf 2)
RED=$(tput setaf 1)
NC=$(tput sgr0)


# TEST CASE 1
# Input with 3 commits but not edges associating developers 


echo "" 
echo "Testing with test-data/TensorFlow/tensorFlowGitLog-3-commits-0-edges.IN"
echo "./scrapLog.py  -r test-data/TensorFlow/tensorFlowGitLog-3-commits-0-edges.IN > testResults.tmp"


./scrapLog.py  -r test-data/TensorFlow/tensorFlowGitLog-3-commits-0-edges.IN > testResults.tmp
#echo "Output should contain ERROR collaboration tuplesList is empty !!"
#expectedLastLine="ERROR collaboration tuplesList is empty"
expectedLastLine="FATAL ERROR: Network have less than two nodes"

# Define the file to read
file="testResults.tmp"

# Check if the file exists
if [ ! -f "$file" ]; then
    echo "Error: File $file not found."
    exit 1
fi
# Check if the file contains the specific error message
if grep -q $expectedLastLine "$file"; then
    echo "Success: The error message was found."
        echo "${GREEN}TESTCASE 1 passed${NC}"
else
    echo "Failure: The error message was not found."
    echo "${RED}TESTCASE 1 did not pass${NC}"
    echo "ScrapLog should result in  $expectedLastLine"§
    exit 1
fi

echo 
rm testResults.tmp



# TEST CASE 2
# Input with 3 commits and one edge associating developers
# lawrencews@google.com and olupton@nvidia.com co-edited tensorflow/core/lib/gtl/array_slice.h


echo "" 
echo "Testing with test-data/TensorFlow/tensorFlowGitLog-3-commits-1-edges.IN"
echo "./scrapLog.py  -r test-data/TensorFlow/tensorFlowGitLog-3-commits-1-edge.IN > testResults.tmp"


./scrapLog.py  -r test-data/TensorFlow/tensorFlowGitLog-3-commits-1-edge.IN > testResults.tmp

# Define the file to read
file="testResults.tmp"

cat $file

# Check if the file exists
if [ ! -f "$file" ]; then
    echo "Error: File $file not found."
    exit 1
fi
# Check if the file contains the specific error message
if grep -q 'Network nodes (developers): 2' "$file"; then
    echo "Success: The error message was found."
        echo "${GREEN}TESTCASE 2.1 passed${NC}"
else
    echo "Failure: The error message was not found."
    echo "${RED}TESTCASE 2-1 did not pass${NC}"
    echo "ScrapLog sould result in  'Number of unique collaborations (i.e., network edges)[1]'"
    exit 1
fi


echo ""

# Test if tensorFlowGitLog-3-commits-1-edge.NetworkFile.graphML was created
echo ""

GraphMLFILE="tensorFlowGitLog-3-commits-1-edge.NetworkFile.graphML"
if test -f "$GraphMLFILE"; then
    echo "${GREEN}TESTCASE 2.2 - $GraphMLFILE exists ${NC}"
else
    echo "${RED}TESTCASE 2.2 did not pass${NC}"
    echo "$GraphMLFILE not created" 
fi

GraphMLHeader='<?xml version="1.0" encoding="UTF-8"?>
<!-- This file was created by scraplog.py script for OSS SNA research purposes --> '

# Test if GraphML have correct header
actualHeader=$(head -2 $GraphMLFILE)

echo ""
#echo actualHeader=$actualHeader
#echo GraphMLHeader=$GraphMLHeader


if [ "$actualHeader" == "$GraphMLHeader" ]; then 
   echo "${GREEN}TESTCASE 2.3 - $GraphMLFILE have a good header${NC}"
else 
   echo "${RED}TESTCASE 2.3 did not pass${NC}"
   echo "$GraphMLFILE with wrong header" 
fi



# Test if nodes are correct
echo ""

if grep -q '<data key="d0">olupton@nvidia.com</data>' "$GraphMLFILE"; then
    echo "${GREEN}TESTCASE 2.4 - $GraphMLFILE have the olupton@nvidia.com node as expected${NC}"
else 
    echo "${RED}TESTCASE 2.4 did not pass${NC}"
fi

echo "" 

if grep -q '<data key="d0">lawrencews@google.com</data>' "$GraphMLFILE"; then
    echo "${GREEN}TESTCASE 2.5 - $GraphMLFILE have the lawrencews@google.com node as expected${NC}"
else 
    echo "${RED}TESTCASE 2.5 did not pass${NC}"
fi


echo "" 
# Test if edges are correct


if grep -q '<edge id="e0" source="0" target="1"/>' "$GraphMLFILE"; then
    echo "${GREEN}TESTCASE 2.6 - $GraphMLFILE have the the expected edge connecting two nodes${NC}"
else 
    echo "${RED}TESTCASE 2.6 did not pass${NC}"
    echo '   expecting <edge id="e0" source="0" target="1"/>'
    echo "   please check check the edges in  tensorFlowGitLog-3-commits-1-edge.NetworkFile.graphML"
    
fi


echo "" 
# Test if the graphML files closes with the right footer 

cmdOutput=$(tail -1  $GraphMLFILE)


if [ "$cmdOutput" == '</graph></graphml>' ]; then
    echo "${GREEN}TESTCASE 2.7 - $GraphMLFILE ends in the proper way with </graphml>${NC}"
else 
    echo "${RED}TESTCASE 2.7 did not pass - Wrong ending of $GraphMLFILE ${NC}"
fi



# TEST CASE 3
# Input with the tensorFlowGitLog-first-trimester-2024.IN


echo "" 
echo "Testing with tensorFlowGitLog-first-trimester-2024.IN - 32659 lines"
echo "Should capture colllaboration between during first trimester 2024 in TensorFlow "
echo "Should also filter the bots and emails listed in test-configurations/TensorFlowBots.txt"
# Not passing configurations as they can evolve over time 
echo "./scrapLog.py  -r test-data/TensorFlow/tensorFlowGitLog-first-trimester-2024.IN > testResults.tmp"


./scrapLog.py  -r test-data/TensorFlow/tensorFlowGitLog-first-trimester-2024.IN > testResults.tmp

echo""

if grep -q 'Total commit blocks found: 4431' testResults.tmp; then
    echo "${GREEN}TESTCASE 3.1 - Scrapped changelog blocks [4431] as expected${NC}"
else 
    echo "${RED}TESTCASE 3.1 did not pass - unexpected number of changelog blocks${NC}"
fi


echo""

if grep -q 'Files affected: 8467' testResults.tmp; then
    echo "${GREEN}TESTCASE 3.2 - number of changed files [8467] as expected${NC}"
else 
    echo "${RED}TESTCASE 3.2 did not pass - unexpected number of changed files${NC}"
fi



echo""

if grep -q 'Network nodes (developers): 256' testResults.tmp; then
    echo "${GREEN}TESTCASE 3.3 - number of nodes [279] as expected${NC}"
else 
    echo "${RED}TESTCASE 3.3 did not pass - unexpected number of nodes${NC}"
fi

echo""

if grep -q 'Network edges (collaborations): 3363' testResults.tmp; then
    echo "${GREEN}TESTCASE 3.4 - number of edges [3363] as expected${NC}"
else 
    echo "${RED}TESTCASE 3.4 did not pass - unexpected number of edges ${NC}"
fi





rm testResults.tmp
#rm $GraphMLFILE



