
echo "Analysing network" ../../icis-2024-wp-networks-graphML/tensorFlowGitLog-all-till-12-Apri-2024.NetworkFile.graphML

echo "-plr -> Plot the results with the legend on the right "

echo "-oi -> Do not consider affiliations gmail,ee,hotmail,outlook,yahoo,qq,users,163,gmx"

echo "-on gatech -> Consider only gatech and the ones they work with"

echo "-lt top10+1 -> legent type is the top10 + 1"

echo "-to top10+1 -> consider only the top 10 organizations with most nodes"

echo ""
echo "Note: Because the -to is only passed at the end, we are considering only gatech and its neighbours"
echo 


../../../../formatAndViz-nofi-GraphML.py  ../../icis-2024-wp-networks-graphML/tensorFlowGitLog-all-till-12-Apri-2024.NetworkFile.graphML -plrs -oi gmail,ee,hotmail,outlook,yahoo,qq,users,163,gmx -on gatech -lt top10+1 -to top10+1 -le gatech 

# ../../../../formatAndViz-nofi-GraphML.py ../../icis-2024-wp-networks-graphML/tensorFlowGitLog-all-till-12-Apri-2024.NetworkFile.graphML -plr -oi gmail,ee,hotmail,outlook,yahoo,qq,users,163,gmx -on gatech
