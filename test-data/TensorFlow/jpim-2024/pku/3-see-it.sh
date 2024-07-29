#!/bin/bash

if [ ! "$BASH_VERSION" ] ; then
    echo "Please do not use sh to run this script ($0), just execute it directly" 1>&2
    exit 1
fi



if [ ! "$BASH_VERSION" ] ; then
    exec /bin/bash "$0" "$@"
fi


source config.cfg

../../../../formatFilterAndViz-nofo-GraphML.py -l tensorFlowGitLog-all-till-12-Apri-2024.NetworkFile-filtered-transformed-to-nofo.graphML -ff $FOCAL_ORG -v


