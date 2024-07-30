#!/bin/bash


if [ ! "$BASH_VERSION" ] ; then
    echo "Please do not use sh to run this script ($0), just execute it directly" 1>&2
    exit 1
fi



if [ ! "$BASH_VERSION" ] ; then
    exec /bin/bash "$0" "$@"
fi


source config.cfg


du -sh $INPUT

echo -r "Taking $FOCAL_ORG as the focal firm we are analysing" "\n"

echo -r "The top 10 org in the case are: $TOP10_ORG" "\n"


echo "-pr -> for ploting the graph and showing the legend" 

echo -e "TESTED" "\n"

echo "-oi -> Do not consider affiliations gmail,ee,hotmail,outlook,yahoo,qq,users,163,gmx"

echo -e "TESTED" "\n"


echo "org_list_top_only -> Considering top 10 rganizations" 

echo -e "TESTED"  "\n"


echo "With ../../../../formatFilterAndViz-nofi-GraphML.py  ../../icis-2024-wp-networks-graphML/tensorFlowGitLog-all-till-12-Apri-2024.NetworkFile.graphML -pl   -oi gmail,ee,hotmail,outlook,yahoo,qq,users,163,gmx  -ot top10" 

echo "I could find the top 10 organizations  google,intel,nvidia,arm,ibm,amd,microsoft,huawei,amazon,naver" 


echo -e "Then I run "

echo "../../../../formatFilterAndViz-nofi-GraphML.py  ../../icis-2024-wp-networks-graphML/tensorFlowGitLog-all-till-12-Apri-2024.NetworkFile.graphML -pl   -oi gmail,ee,hotmail,outlook,yahoo,qq,users,163,gmx  -oo google,intel,nvidia,arm,ibm,amd,microsoft,huawei,amazon,naver,chromium"

echo "I have a issue because chromoum is not on the legend"

echo "when we need to run wth --legend-type Top10+1 and --legend_extra-roganizations" 

echo "../../../../formatFilterAndViz-nofi-GraphML.py  ../../icis-2024-wp-networks-graphML/tensorFlowGitLog-all-till-12-Apri-2024.NetworkFile.graphML -pl   -oi gmail,ee,hotmail,outlook,yahoo,qq,users,163,gmx  -oo google,intel,nvidia,arm,ibm,amd,microsoft,huawei,amazon,naver,chromium  --legend_type=top10+1"


echo "got issues  then tried with   -le LEGEND_EXTRA_ORGANIZATION"

echo "../../../../formatFilterAndViz-nofi-GraphML.py  ../../icis-2024-wp-networks-graphML/tensorFlowGitLog-all-till-12-Apri-2024.NetworkFile.graphML -pl   -oi gmail,ee,hotmail,outlook,yahoo,qq,users,163,gmx  -oo google,intel,nvidia,arm,ibm,amd,microsoft,huawei,amazon,naver,chromium  --legend_type=top10+1 --legend_extra_organizations chromium " 

echo "I also run into provlems " 


echo "That should be fixed. "

echo "And then with:" 
echo "../../../../formatFilterAndViz-nofi-GraphML.py  ../../icis-2024-wp-networks-graphML/tensorFlowGitLog-all-till-12-Apri-2024.NetworkFile.graphML -pl   -oi gmail,ee,hotmail,outlook,yahoo,qq,users,163,gmx  -oo google,intel,nvidia,arm,ibm,amd,microsoft,huawei,amazon,naver,chromium  --legend_type=top10+1 -le --legend_extra_organizations chromium " 

echo "I got the following almost done: 

With top10+1 as legend type -> show the 10 organizations with most nodes
And add the extra organization
Here the extra organization is the first element of the list of -le LEGEND_EXTRA_ORGANIZATIONS
"

echo -e "Then I fixed the code  and worked" "\n"

echo  -e "So to get the filterd network I just need to invoke the abover commend with  --save_graphML so we can transform it"

CMD="../../../../formatFilterAndViz-nofi-GraphML.py  $INPUT -pl   -oi gmail,ee,hotmail,outlook,yahoo,qq,users,163,gmx  -oo $TOP10_ORG,$FOCAL_ORG  --legend_type=top10+1 --org_list_and_neighbours_only chromium --legend_extra_organizations $FOCAL_ORG --save_graphML" 


echo -e "Excecutiong:\n  $CMD \n"

eval $CMD

echo -e "TESTED" "Worked" "\n"

echo -e "Filtered file saved at $FILTERED_FILE" "\n"


du -sh $INPUT
du -sh $FILTERED_FILE

echo -e "Let's now transform the network \n"

grep chromium $FILTERED_FILE
../../../../formatFilterAndViz-nofi-GraphML.py ../../icis-2024-wp-networks-graphML/tensorFlowGitLog-all-till-12-Apri-2024.NetworkFile.graphML -pl -oi gmail,ee,hotmail,outlook,yahoo,qq,users,163,gmx
