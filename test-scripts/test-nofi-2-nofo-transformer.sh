#!/bin/bash
echo "Is ./transform-nofi-2-nofo-GraphML.py doing what is supposed to do?"
echo "This tests ./transform-nofi-2-nofo-GraphML.py by executing it against graphML input files in ./test-data/"
echo "part of the ScrapLogGit2Net open-source project"
echo "Developed by Jose Teixeira <jose.teixeira@abo.fi> "

# Checking if dependencies exit 
exists()
{
  command -v "$1" >/dev/null 2>&1
}



if exists grep; then
  echo 'grep exists!'
else
    echo 'ERROR: Your system does not have grep'
    exit 
fi

if exists xmllint; then
  echo 'xmllint exists!'
else
    echo 'ERROR Your system does not have xmllint'
    exit
fi



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
 


echo ""
echo "Checking now if the test case 1 have the  right output"
echo "\t Inter-organizational network should have one edge with weight=1 between two nodes only"
echo ""


TC1OUTFILE=2-org-with-2-developers-each-with-only-two-engaging-in-one-inter-firm-cooperation-relationship-transformed-to-nofo.graphML




expectedString="data" 


echo ""
echo -e "\t Testing if $TC1OUTFILE is a valid under the graphML xml schema"
echo ""


if ! xmllint --schema http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd $TC1OUTFILE ; then
    echo "ERROR: $TC1OUTFILE is not a valid XML graphML file"
    exit 
fi





echo "" 
echo -e "\t checking now if the  $TC1OUTFILE have the expected content" 
echo ""

if [ ! -f "$TC1OUTFILE" ]; then
    echo "ERROR: $TC1OUTFILE does not exist."
    exit 
fi


expectedString=\<data\ key=\"d0\"\>1\<\/data\>
echo "Expected String="$expectedString

if grep -q \<data\ key=\"d0\"\>1\<\/data\>  "$TC1OUTFILE" ; then
    echo "${GREEN}TESTCASE 1 passed${NC}"
    echo $expectedString "is in the output inter-org network as expected" 
else
       echo "echo ${RED}TESTCASE 1 did not pass${NC}"
       echo $expectedString should be in $TC1OUTFILE
       exit
       
fi 


sleep 1
echo "Removing inter-organizational network that resulted from transformation"
rm  $TC1OUTFILE





# TEST CASE 2
# Transforms a small network where there should be only one inter-organizational edge with a weight of 3. 
# test-data/2-org-with-2-developers-each-all-in-inter-firm-cooperation-relationships.graphML

TC2FILE=test-data/2-org-with-2-developers-each-all-in-inter-firm-cooperation-relationships.graphML

if [ ! -f "$TC2FILE" ]; then
    echo "ERROR $TC2FILE does not exist."
    exit 
fi


echo ""
echo "TC2: Testing with $TC2FILE"
cmd="./formatAndViz-nofi-GraphML.py -pl  $TC2FILE"
echo $cmd

echo ""
echo "TC2: Showing original network"
./formatAndViz-nofi-GraphML.py -pl  $TC2FILE & 
sleep 1

echo "TC2: transforming it"
./transform-nofi-2-nofo-GraphML.py  -v  $TC2FILE --show  

sleep 1
echo "TC2: You should now see only one edge between two nodes with a weight of 3, as three developers from the two organizations worked together"


echo ""
echo "TC2: Checking now if the test case 1 have the  right output"
echo "\t Inter-organizational network should have one edge with weight=1 between two nodes only"
echo ""


TC2OUTFILE=2-org-with-2-developers-each-all-in-inter-firm-cooperation-relationships-transformed-to-nofo.graphML




echo ""
echo -e "\t Testing if $TC2OUTFILE is a valid under the graphML xml schema"
echo ""


if ! xmllint --schema http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd $TC2OUTFILE ; then
    echo "ERROR: $TC1OUTFILE is not a valid XML graphML file"
    exit 
fi





echo "" 
echo -e "\t checking now if the  $TC2OUTFILE have the expected content" 
echo ""

if [ ! -f "$TC2OUTFILE" ]; then
    echo "ERROR: $TC2OUTFILE does not exist."
    exit 
fi


expectedString=\<data\ key=\"d0\"\>3\<\/data\>
echo -e "\t Expected String="$expectedString

if grep -q \<data\ key=\"d0\"\>3\<\/data\>  "$TC2OUTFILE" ; then
    echo "${GREEN}TESTCASE 2 passed${NC}"
    echo -e "\t" $expectedString "is in the output inter-org network as expected" 
else
       echo "echo ${RED}TESTCASE 2 did not pass${NC}"
       echo $expectedString should be in $TC2OUTFILE
       exit
       
fi 


sleep 1
echo "Removing inter-organizational network that resulted from transformation"
rm  $TC2OUTFILE

