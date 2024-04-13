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
echo "Testing with test-data/tensorFlowGitLog-3-commits-0-edges.IN" 
echo "./scrapLog.py  -r test-data/tensorFlowGitLog-3-commits-0-edges.IN >> testResults.tmp"


./scrapLog.py  -r test-data/tensorFlowGitLog-3-commits-0-edges.IN >> testResults.tmp
#echo "Last line of output shoul be:"
#echo "Output should be ERROR collaboration tuplesList is empty !!"
lastline=$(tail -n1 testResults.tmp)
expectedLastLine="ERROR collaboration tuplesList is empty"

#echo lastline=[$lastline]
#echo expextedLastLine=[$expectedLastLine]

# Test if "ERROR collaboration tuplesList is empty" is on the last line of the scrapLog STDOUT 

echo 
if [[  "$lastline" =~ "$expectedLastLine" ]]; then
    echo "${GREEN}TESTCASE 1 passed${NC}"
else
    echo "${RED}TESTCASE 1 did not pass${NC}"
    echo "ScrapLog should end with 'ERROR collaboration tuplesList is empty expected'"
    
fi

echo 
rm testResults.tmp



# TEST CASE 2
# Input with 3 commits and one edge associating developers
# lawrencews@google.com and olupton@nvidia.com co-edited tensorflow/core/lib/gtl/array_slice.h


echo "" 
echo "Testing with test-data/tensorFlowGitLog-3-commits-1-edges.IN" 
echo "./scrapLog.py  -r test-data/tensorFlowGitLog-3-commits-1-edge.IN >> testResults.tmp"


./scrapLog.py  -r test-data/tensorFlowGitLog-3-commits-1-edge.IN >> testResults.tmp
#echo "Last line of output shoul be:"
#echo "Output should be"
lastline=$(tail -n1 testResults.tmp)
expectedLastLine="Number of unique collaborations (i.e., network edges)[1]"

echo ""
#echo lastline=[$lastline]
#echo expextedLastLine=[$expectedLastLine]

# Test if the number of unique collaborations is only one on the last line of the scrapLog STDOUT 

echo 
if [[  "$lastline" =~ "$expectedLastLine" ]]; then
    echo "${GREEN}TESTCASE 2.1 - last line test passed${NC}"
else
    echo "${RED}TESTCASE 2.1 did not pass${NC}"
    echo "ScrapLog should end with 'ERROR collaboration tuplesList is empty expected'"
    
fi

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
   echo "${GREEN}TESTCASE 2.3 - $GraphMLFILE have a good header"
else 
   echo "${RED}TESTCASE 2.3 did not pass${NC}"
   echo "$GraphMLFILE with wrong header" 
fi



# Test if nodes are correct
echo ""

if grep -q '<data key="d0">olupton@nvidia.com</data>' "$GraphMLFILE"; then
    echo "${GREEN}TESTCASE 2.4 - $GraphMLFILE have the olupton@nvidia.com node as expected"
else 
    echo "${RED}TESTCASE 2.4 did not pass${NC}"
fi

echo "" 

if grep -q '<data key="d0">lawrencews@google.com</data>' "$GraphMLFILE"; then
    echo "${GREEN}TESTCASE 2.5 - $GraphMLFILE have the lawrencews@google.com node as expected"
else 
    echo "${RED}TESTCASE 2.5 did not pass${NC}"
fi


echo "" 
# Test if edges are correct

if grep -q '<edge id="e0" source="0" target="1"/>' "$GraphMLFILE"; then
    echo "${GREEN}TESTCASE 2.6 - $GraphMLFILE have the the expected edge connecting two nodes"
else 
    echo "${RED}TESTCASE 2.6 did not pass${NC}"
fi


echo "" 
# Test if the graphML files closes with the right footer 

cmdOutput=$(tail -1  $GraphMLFILE)


if [ "$cmdOutput" == '</graph></graphml>' ]; then
    echo "${GREEN}TESTCASE 2.7 - $GraphMLFILE ends in the proper way with </graphml>"
else 
    echo "${RED}TESTCASE 2.7 did not pass - Wrong ending of $GraphMLFILE ${NC}"
fi



lastline=$(tail -n1 testResults.tmp)



rm testResults.tmp
rm $GraphMLFILE



