#!/bin/bash

source config.cfg


echo "Moving to the overleaf project root folder where main.tex is expected"

CMD="cd $OVERLEAF_FOLDER"
echo $CMD 
eval $CMD
echo ""


echo "I am at PWD=$PWD"


OVERLEAF_FIGURES_FOLDERS=/home/apolinex/rep_clones/floss_sna_team/TensorFlowSocialStructure/tensorflowsna-open-coopetition-triple-helix-non-commercial/Figures/noo/




echo "Testing if $FOCAL_ORG pdf figure is there"

CMD="du -sh $OVERLEAF_FIGURES_FOLDERS$FOCAL_ORG""_cropped.pdf"
echo $CMD
eval $CMD
echo ""



echo "Now check than main exists" 

MAIN_FILE=main.tex


CMD="du -sh main.tex & file main.tex"
echo $CMD
eval $CMD
echo ""


# Check if the file is provided
if [ -z $MAIN_FILE ]; then
    echo "main.tex missing"
    exit 1
fi

echo "File is provided"

# LaTeX code to be inserted
FIGURE_CODE="\n\\begin{figure}[h!]\n\\centering\n\\includegraphics[width=0.8\\textwidth]{./Figures/noo/$FOCAL_ORG""_cropped.pdf}\n\\caption{$FOCAL_ORG inter-organizational network deployed by ScrapLog}\n\\label{fig:noo_$FOCAL_ORG}\n\\end{figure}\n"

echo "FIGURE_CODE=$FIGURE_CODE"
echo ""

echo "running sed to add the code"

echo "----- "

#echo sed -i "/\\subsection{BOT added figures}/a $FIGURE_CODE" "$MAIN_FILE"
#sed -i "/\\subsection{BOT added figures}/a $FIGURE_CODE" "$MAIN_FILE"


echo  $FIGURE_CODE >> "$MAIN_FILE"

echo "-----"
echo ""

# Use sed to insert the figure code after the specified line
#CMD="sed -i /\\subsection{BOT added figures}/a $FIGURE_CODE" "$MAIN_FILE"

echo $CMD
eval $CMD
echo ""


echo "Figure code inserted into $MAIM_FILE"
echo ""


echo "Testing if there with grep "

CMD="grep fig:$FOCAL_ORG $MAIN_FILE" 

echo $CMD
eval $CMD
echo ""


echo "back to origin" 
cd - 

echo "DONE"


