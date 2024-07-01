#!/bin/bash
echo "Is ./transform-nofi-2-nofo-GraphML.py doing what is supposed to do?"
echo "This tests ./transform-nofi-2-nofo-GraphML.py by executing it against graphML input files in ./test-data/"
echo "part of the ScrapLogGit2Net open-source project"
echo "Developed by Jose Teixeira <jose.teixeira@abo.fi> "

GREEN=$(tput setaf 2)
RED=$(tput setaf 1)
NC=$(tput sgr0)


# TEST CASE 1
# Transforms a small network where there should be only one inter-organizational edge
# 2-org-with-2-developers-each-with-only-two-engaging-in-one-inter-firm-cooperation-relationship.graphML

TC1FILE=test-data/2-org-with-2-developers-each-with-only-two-engaging-in-one-inter-firm-cooperation-relationship.graphML

if [ ! -f "$TC1FILE" ]; then
    echo "$TC1FILE does not exist."
    exit 
fi


echo ""
echo "Testing with test-data/TensorFlow/2-org-with-2-developers-each-with-only-two-engaging-in-one-inter-firm-cooperation-relationship.graphML"
cmd="./formatAndViz-nofi-GraphML.py -pl  $TC1FILE"
echo $cmd

echo ""
echo "Showing original network"
./formatAndViz-nofi-GraphML.py -pl  $TC1FILE &
sleep 1


echo "transforming it"
./transform-nofi-2-nofo-GraphML.py  -v  $TC1FILE --show 

sleep 1
echo "You should now see only one edge between two nodes"





#lastline=$(tail -n1 testResults.tmp)
#expectedLastLine="ERROR collaboration tuplesList is empty"

#echo lastline=[$lastline]
#echo expextedLastLine=[$expectedLastLine]



#echo 
#if [[  "$lastline" =~ "$expectedLastLine" ]]; then
#    echo "${GREEN}TESTCASE 1 passed${NC}"
#else
#    echo "${RED}TESTCASE 1 did not pass${NC}"
#    echo "ScrapLog should end with 'ERROR collaboration tuplesList is empty expected'"
    
#fi





TC1OUTFILE=2-org-with-2-developers-each-with-only-two-engaging-in-one-inter-firm-cooperation-relationship-transformed-to-nofo.graphML

sleep 1
echo "Removing inter-organizational network that resulted from transformation"
rm  $TC1OUTFILE

