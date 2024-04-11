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
echo "Last line of output shoul be:"
echo "Output should be ERROR collaboration tuplesList is empty !!"
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
echo "Last line of output shoul be:"
echo "Output should be"
lastline=$(tail -n1 testResults.tmp)
expectedLastLine="ERROR "

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
