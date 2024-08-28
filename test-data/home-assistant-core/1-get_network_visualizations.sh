if [ ! "$BASH_VERSION" ] ; then
    echo "Please do not use sh to run this script ($0), just execute it directly" 1>&2
    exit 1
fi



if [ ! "$BASH_VERSION" ] ; then
    exec /bin/bash "$0" "$@"
fi


source config.cfg
source utils.sh 

echo  e "Invoking the $FFV_NO_FI_GRAPHML_SCRIPT with save_graphML so we can later transform it"

CMD="$FFV_NO_FI_GRAPHML_SCRIPT  $INPUT pl oi $COMPANIES_TO_IGNORE save_graphML" 


echo e "Excecutiong:\n  $CMD \n"

eval $CMD

echo e "TESTED" "Worked" "\n"

echo e "Filtered file saved at $FILTERED_FILE" "\n"


du sh $INPUT
du sh $FILTERED_FILE


