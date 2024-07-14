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



echo "Cropping the margins"
 input.pdf

CMD="pdf-crop-margins -v -p 0 -a -1 $FOCAL_ORG.pdf"
echo $CMD
eval $CMD
echo ""


echo "Showing the result"

CMD="okular $FOCAL_ORG""_cropped.pdf"
echo $CMD
eval $CMD
echo ""



echo "Listing the destination Figures folder"

CMD="ls $OVERLEAF_FIGURES_FOLDERS" 
echo $CMD
eval $CMD
echo ""



# Copying the figure pdf file
CMD="cp -iv $FOCAL_ORG""_cropped.pdf $OVERLEAF_FIGURES_FOLDERS" 
echo $CMD
eval $CMD
echo ""


echo "Adding to version control"
cd $OVERLEAF_FIGURES_FOLDERS

echo $PWD
echo "I moved to $PWD"
echo ""

CMD="git add $FOCAL_ORG""_cropped.pdf"
echo $CMD
eval $CMD
echo ""


CMD="git commit $FOCAL_ORG""_cropped.pdf -m '4-deploy-to-overlead.sh added pdfFigure for $FOCAL_ORG'"
echo $CMD
eval $CMD
echo ""

CMD="git push"
echo $CMD
eval $CMD
echo ""


echo "back to origin" 
cd - 







