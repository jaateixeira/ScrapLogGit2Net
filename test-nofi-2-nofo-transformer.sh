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



echo ""
echo "Testing with test-data/TensorFlow/2-org-with-2-developers-each-with-only-two-engaging-in-one-inter-firm-cooperation-relationship.graphML"
cmd="./formatAndViz-nofi-GraphML.py -pls  test-data/2-org-with-2-developers-each-with-only-two-engaging-in-one-inter-firm-cooperation-relationship.graphML"
echo $cmd

echo ""
echo "Showing original network"
./formatAndViz-nofi-GraphML.py -pls  test-data/2-org-with-2-developers-each-with-only-two-engaging-in-one-inter-firm-cooperation-relationship.graphML
sleep 1

echo "transforming it"
./transform-nofi-2-nofo-GraphML.py  -v  test-data/2-org-with-2-developers-each-with-only-two-engaging-in-one-inter-firm-cooperation-relationship.graphML


sleep 1
echo "You should now see only one edge between two nodes"
./formatAndViz-nofo-GraphML.py -v  2-org-with-2-developers-each-with-only-two-engaging-in-one-inter-firm-cooperation-relationship-filtered.graphML