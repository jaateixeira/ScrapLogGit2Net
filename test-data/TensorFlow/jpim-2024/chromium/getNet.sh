echo "Analysing network" ../../icis-2024-wp-networks-graphML/tensorFlowGitLog-al
l-till-12-Apri-2024.NetworkFile.graphML

echo "-pr -> for ploting the graph and showing the legend" 

echo "TESTED"

echo "-oi -> Do not consider affiliations gmail,ee,hotmail,outlook,yahoo,qq,users,163,gmx"

echo "TESTED"


echo "org_list_top_only -> Considering top 10 rganizations" 

echo "TESTE D" 

echo  "Fine" 

echo With ../../../../formatFilterAndViz-nofi-GraphML.py  ../../icis-2024-wp-networks-graphML/tensorFlowGitLog-all-till-12-Apri-2024.NetworkFile.graphML -pl   -oi gmail,ee,hotmail,outlook,yahoo,qq,users,163,gmx  -ot top10

echo "I could find the top 10 organizations  google,intel,nvidia,arm,ibm,amd,microsoft,huawei,amazon,naver" 


echo "now I should run "

echo "../../../../formatFilterAndViz-nofi-GraphML.py  ../../icis-2024-wp-networks-graphML/tensorFlowGitLog-all-till-12-Apri-2024.NetworkFile.graphML -pl   -oi gmail,ee,hotmail,outlook,yahoo,qq,users,163,gmx  -oo google,intel,nvidia,arm,ibm,amd,microsoft,huawei,amazon,naver,chromium"

echo "I have a issue because chromoum is not on the legend"

echo "when we need to run wth --legend-type Top10+1 and --legend_extra-roganizations 

echo "../../../../formatFilterAndViz-nofi-GraphML.py  ../../icis-2024-wp-networks-graphML/tensorFlowGitLog-all-till-12-Apri-2024.NetworkFile.graphML -pl   -oi gmail,ee,hotmail,outlook,yahoo,qq,users,163,gmx  -oo google,intel,nvidia,arm,ibm,amd,microsoft,huawei,amazon,naver,chromium  --legend_type=top10+1 "


echo "got issues  then tried with   -le LEGEND_EXTRA_ORGANIZATION

echo "../../../../formatFilterAndViz-nofi-GraphML.py  ../../icis-2024-wp-networks-graphML/tensorFlowGitLog-all-till-12-Apri-2024.NetworkFile.graphML -pl   -oi gmail,ee,hotmail,outlook,yahoo,qq,users,163,gmx  -oo google,intel,nvidia,arm,ibm,amd,microsoft,huawei,amazon,naver,chromium  --legend_type=top10+1 --legend_extra_organizations chromium " 

echo "I also run into provlems "


echo That should be fixed. 

echo And then with 
echo "../../../../formatFilterAndViz-nofi-GraphML.py  ../../icis-2024-wp-networks-graphML/tensorFlowGitLog-all-till-12-Apri-2024.NetworkFile.graphML -pl   -oi gmail,ee,hotmail,outlook,yahoo,qq,users,163,gmx  -oo google,intel,nvidia,arm,ibm,amd,microsoft,huawei,amazon,naver,chromium  --legend_type=top10+1 -le --legend_extra_organizations chromium " 

echo I got the following almost done 


With top10+1 as legend type -> show the 10 organizations with most nodes
And add the extra organization
Here the extra organization is the first element of the list of -le LEGEND_EXTRA_ORGANIZATIONS


Then I fixed the coed and worked 
