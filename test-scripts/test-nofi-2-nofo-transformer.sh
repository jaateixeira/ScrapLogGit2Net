#!/bin/bash
echo "Is ./transform-nofi-2-nofo-GraphML.py doing what is supposed to do?"
echo "This tests ./transform-nofi-2-nofo-GraphML.py by executing it against graphML test files in ./test-data/"
echo "part of the ScrapLogGit2Net open-source project"
echo "Developed by Jose Teixeira <jose.teixeira@abo.fi> "
echo -e "\n"


echo -e "\t Testing validGraphmlXMLfile() and command_exits() functions"


GREEN=$(tput setaf 2)
RED=$(tput setaf 1)
NC=$(tput sgr0)



# Fuction that validates if a fiven XML file is valid 
validGraphmlXMLfile() {
    # First check if file exists
    if ! test -f $1; then
	echo -e "\t File $1 does not exist."
	false 
	return 
    fi

    if ! xmllint --schema http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd $1 >> /dev/null ; then
	echo -e "\t File $1 is not a valid graphml xml file"
	echo -e "\t It does no comply with with schema at http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd"
	false 
	return 
    fi

    true 
    return 
}


# Unit test for function validGraphmlXMLfile()
ValidGraphmlXMLfile="test-data/2-org-with-2-developers-each-with-only-two-engaging-in-one-inter-firm-cooperation-relationship.graphML"

if ! validGraphmlXMLfile $ValidGraphmlXMLfile ; then
   echo "Error: $ValidGraphmlXMLfile should be a valid graphml xml file according to schema"
   echo "Error: Unit test for validGraphmlXMLfile() did not pass"
   false 
   exit 
fi



echo -e "\t\t validGraphmlXMLfile() passed test"


# FUCTION that checks if a given command exists / is isntalled. 
command_exists()
{
  command -v "$1" >/dev/null 2>&1
}




# Unit test for function exists()

commandThatExists="bash"
if ! command_exists $commandThatExists ; then
   echo "Error: $commandThatExists should be installed"
   echo "Error: Unit test for exists() did not pass"
   false 
   exit 

fi 

echo -e "\t\t command_exists() passed test"


echo -e "${GREEN}\n \t functions passed unit tests${NC}"


echo -e "\n \t Cheking now for the grep and xmllint dependencies"




# Checking if dependencies for the test script exit 
if command_exists grep; then
  echo -e '\t\t grep exists!'
else
    echo 'ERROR: Your system does not have grep'
    exit 
fi

if command_exists xmllint; then
  echo -e '\t\t xmllint exists!'
else
    echo 'ERROR Your system does not have xmllint'
    exit
fi



echo -e "${GREEN}\n \t Dependencies grep and xmllint are met${NC}"



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


if ! validGraphmlXMLfile $TC1OUTFILE ; then
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
echo "TC2: Checking now if the test case 2 have the  right output"
echo "\t Inter-organizational network should have one edge with weight=1 between two nodes only"
echo ""


TC2OUTFILE=2-org-with-2-developers-each-all-in-inter-firm-cooperation-relationships-transformed-to-nofo.graphML




echo ""
echo -e "\t Testing if $TC2OUTFILE is a valid under the graphML xml schema"
echo ""


if ! validGraphmlXMLfile $TC2OUTFILE ; then
    echo "ERROR: $TC2OUTFILE is not a valid XML graphML file"
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




###########################################################################################################
# TEST CASE 3
# Transforms a 5 nodes pentagon star, 5 dev, 3, org, all connected in star format, where weights shoould be 4, 2,2. 
# test-data/5-pentagon-with-star.graphML 
###########################################################################################################
TC3FILE=test-data/5-pentagon-with-star.graphML 

if [ ! -f "$TC3FILE" ]; then
    echo "ERROR $TC3FILE does not exist."
    exit 
fi


echo ""
echo "TC3: Testing with $TC3FILE"
cmd="./formatAndViz-nofi-GraphML.py -pl  $TC3FILE"
echo $cmd

echo ""
echo "TC3: Showing original network"
./formatAndViz-nofi-GraphML.py -pl  $TC3FILE & 
sleep 1

echo "TC3: transforming it"
./transform-nofi-2-nofo-GraphML.py  -v  $TC3FILE --show  

sleep 1
echo "TC2: You should now see only one edge between two nodes with a weight of 3, as three developers from the two organizations worked together"


echo ""
echo "TC3: Checking now if the test case 3 have the  right output"
echo "\t Inter-organizational network should have one edge with weight=1 between two nodes only"
echo ""


TC3OUTFILE=5-pentagon-with-star-transformed-to-nofo.graphML




echo ""
echo -e "\t Testing if $TC3OUTFILE is a valid under the graphML xml schema"
echo ""


if ! validGraphmlXMLfile $TC3OUTFILE ; then
    echo "ERROR: $TC3OUTFILE is not a valid XML graphML file"
    exit 
fi





echo "" 
echo -e "\t checking now if the  $TC3OUTFILE have the expected content" 
echo ""

if [ ! -f "$TC3OUTFILE" ]; then
    echo "ERROR: $TC3OUTFILE does not exist."
    exit 
fi




expectedString=\<data\ key=\"d0\"\>4\<\/data\>
echo -e "\t Expected String="$expectedString

if grep -q  $expectedString "$TC3OUTFILE" ; then
    echo ""
    echo "${GREEN}TESTCASE 3 passed${NC}"
    echo -e "\t" $expectedString "is in the output inter-org network as expected"
    echo ""
else
    
       echo "echo ${RED}TESTCASE 3 did not pass${NC}"
       echo $expectedString should be in $TC3OUTFILE
       exit
       
fi 




echo "Removing inter-organizational network that resulted from transformation"
rm  $TC3OUTFILE
echo ""
