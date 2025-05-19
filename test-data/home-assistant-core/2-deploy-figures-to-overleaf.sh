1#!/bin/bash


if [ ! "$BASH_VERSION" ] ; then
    echo "Please do not use sh to run this script ($0), just execute it directly" 1>&2
    exit 1
fi



if [ ! "$BASH_VERSION" ] ; then
    exec /bin/bash "$0" "$@"
fi


source config.cfg
source utils.sh 
echo -e "\n Figures should be in Figures folder\n"
#FIGURE_TO_DEPLOY=Figures/all-known-org.pdf
FIGURE_TO_DEPLOY=Figures/NetOfOrg.pdf


file_exists_and_is_not_empty "$FIGURE_TO_DEPLOY"

command_exists "pdf-crop-margins"


CMD="du -sh $FIGURE_TO_DEPLOY"
echo $CMD
eval $CMD
echo ""



CMD="file $FIGURE_TO_DEPLOY"
echo $CMD
eval $CMD
echo ""

echo "Cropping the margins"
CMD="pdf-crop-margins -v -p 0 -a -1 $FIGURE_TO_DEPLOY -o  $FIGURE_TO_DEPLOY""_cropped.pdf"


FILE=$FIGURE_TO_DEPLOY
# Ask the user if they want to crop the white-space margins of the figure
read -p "Do you want to crop the white-space margins of the figure $FILE? (y/n) " choice

# Perform the selected action
case $choice in
    [Yy]* )
        # Call the function to check if the file exists and is a PDF
        if file_exists_and_is_pdf "$FILE"; then
            # If the file exists and is a PDF, crop the white-space margins using pdf-crop-margins
	    echo -e $CMD
	    eval $CMD	    
            echo -e "${GREEN}White-space margins of $FILE have been cropped.${NC}"
        else
            # If the file does not exist or is not a PDF, print an error message in red
            echo -e "${RED}Error: File $FILE does not exist or is not a PDF.${NC}"
	    echo ""
        fi
        ;;
    [Nn]* )
        # Do nothing
        echo "White-space margins of $FILE have not been cropped."
        ;;
    * )
        # If the user entered an invalid choice, print an error message in red
        echo -e "${RED}Error: Invalid choice.${NC}"
        ;;
esac



echo "Showing the result"


CMD="okular $FIGURE_TO_DEPLOY""_cropped.pdf"
echo $CMD
eval $CMD
echo ""



echo "Listing the destination Figures folder"

CMD="ls $OVERLEAF_FIGURES_FOLDERS" 
echo $CMD
eval $CMD
echo ""




# Copying the figure pdf file
CMD="cp -iv $FIGURE_TO_DEPLOY""_cropped.pdf $OVERLEAF_FIGURES_FOLDERS" 
echo $CMD
eval $CMD
echo ""



file_exists_and_is_not_empty "$FIGURE_TO_DEPLOY"
echo Checking if  "$OVERLEAF_FOLDER"/"$FIGURE_TO_DEPLOY"_cropped.pdf exists 
file_exists_and_is_not_empty "$OVERLEAF_FOLDER"/"$FIGURE_TO_DEPLOY"_cropped.pdf


echo "Adding to version control"
cd $OVERLEAF_FIGURES_FOLDERS

echo $PWD
echo "I moved to $PWD"
echo ""

cd ..
echo $PWD
echo "I moved to Overlead project root"
echo ""


file_exists_and_is_not_empty $FIGURE_TO_DEPLOY""_cropped.pdf

CMD="git add $FIGURE_TO_DEPLOY""_cropped.pdf"
echo $CMD
eval $CMD
echo ""





CMD="git commit $FIGURE_TO_DEPLOY""_cropped.pdf -m '4-deploy-to-overlead.sh added pdfFigure for $FIGURE_TO_DEPLOY'"
echo $CMD
eval $CMD
echo ""

CMD="git push"
echo $CMD
eval $CMD
echo ""



echo "back to origin" 
cd - 

echo "DONE"
print_happy_smile



