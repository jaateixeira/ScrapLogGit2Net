#!/bin/bash

source config.cfg


echo "Testing if $FOCAL_ORG pdf figure is there"

CMD="du -sh $FOCAL_ORG.pdf"
echo $CMD
eval $CMD
echo ""



CMD="file $FOCAL_ORG.pdf"
echo $CMD
eval $CMD
echo ""


echo "Listing the destination Figures folder"

CMD="ls $OVERLEAF_FIGURES_FOLDERS" 
echo $CMD
eval $CMD
echo ""



# Copying the figure pdf file
CMD="cp -i $FOCAL_ORG.pdf $OVERLEAF_FIGURES_FOLDERS" 
echo $CMD
eval $CMD
echo ""




