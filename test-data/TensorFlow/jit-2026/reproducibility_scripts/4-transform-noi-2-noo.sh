#!/bin/bash
# ##########################################################
# 4-transform-noi-2-noo.sh - Transforms network of individuals into networks of firms
# finds .graphml files then invokes transform-nofi-2-nofo-GraphML.py from the ScrapLogGit2Net project
# ##########################################################

if [ ! "$BASH_VERSION" ] ; then
    echo "Please do not use sh to run this script ($0), just execute it directly" 1>&2
    exit 1
fi



if [ ! "$BASH_VERSION" ] ; then
    exec /bin/bash "$0" "$@"
fi


source config.cfg
source config.cfg
source utils.sh


test_config



echo FFV_NO_FI_GRAPHML_SCRIPT=$FFV_NO_FI_GRAPHML_SCRIPT
echo TRANSFORM_GRAPHML_SCRIPT=$TRANSFORM_GRAPHML_SCRIPT
echo DIR_4_MINED_NETWORKS_NOFI_GRAPHML=$DIR_4_MINED_NETWORKS_NOFI_GRAPHML
echo DIR_4_MINED_NETWORKS_NOFO_GRAPHML=$DIR_4_MINED_NETWORKS_NOFO_GRAPHML



    # Check and handle directory
    if ! check_or_create_directory "$DIR_4_MINED_NETWORKS_NOFO_GRAPHML"; then
        echo ""
        print_error "Directory check failed. Exiting script."
        exit 1
    fi


echo ""
echo -e "${MAGENTA} Let's tranform the network then${NC}"
echo ""



# Find all files with extension .IN.NetworkFile.graphML
echo "🔍 Searching for .graphML files in $DIR_4_MINED_NETWORKS_NOFI_GRAPHML"
files=($(find $DIR_4_MINED_NETWORKS_NOFI_GRAPHML -type f -name "*.graphML" 2>/dev/null | sort))

# Check if any files were found
if [[ ${#files[@]} -eq 0 ]]; then
    echo "❌ No .graphML files found in current directory or subdirectories."
    exit 1
fi

echo "✅ Found ${#files[@]} ..graphML file(s):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"


# Display files with numbers
for i in "${!files[@]}"; do
    printf "  [%2d] %s\n" "$((i+1))" "${files[i]}"
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Please select files to process:"
echo "   • Enter numbers separated by spaces (e.g., '1 3 5')"
echo "   • Enter 'a' or 'all' to select all files"
echo "   • Enter 'q' or 'quit' to exit"
echo ""

# Function to validate selection
validate_selection() {
    local selection="$1"

    # Check for quit
    if [[ "$selection" =~ ^[qQ](uit)?$ ]]; then
        echo "Exiting..."
        exit 0
    fi

    # Check for all
    if [[ "$selection" =~ ^[aA](ll)?$ ]]; then
        selected_files=("${files[@]}")
        return 0
    fi

    # Parse numbers
    selected_files=()
    for num in $selection; do
        # Check if it's a valid number
        if ! [[ "$num" =~ ^[0-9]+$ ]]; then
            echo "❌ '$num' is not a valid number. Please enter numbers only."
            return 1
        fi

        # Check if number is in range
        if (( num < 1 || num > ${#files[@]} )); then
            echo "❌ '$num' is out of range (1-${#files[@]})."
            return 1
        fi

        # Add file to selection (adjust for 0-based index)
        selected_files+=("${files[$((num-1))]}")
    done

    # Remove duplicates
    # shellcheck disable=SC2207
    selected_files=($(printf "%s\n" "${selected_files[@]}" | sort -u))

    return 0
}

# Get user input with validation loop
while true; do
    read -p "➤ Enter your selection: " -r user_input

    if validate_selection "$user_input"; then
        break
    fi
done

echo ""
echo "✅ Selected ${#selected_files[@]} file(s) for processing:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Display selected files
for i in "${!selected_files[@]}"; do
    printf "  [%2d] %s\n" "$((i+1))" "${selected_files[i]}"
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""


# Process confirmation
if [[ ${#selected_files[@]} -gt 0 ]]; then
    read -p "🚀 Start processing these files? (y/N): " -n 1 -r confirm
    echo ""

    if [[ $confirm =~ ^[Yy]$ ]]; then
        # Process each file
        for file in "${selected_files[@]}"; do
            echo "⏳ Processing: $file"

            # Generate output filename
            # Remove .IN.NetworkFile.graphML and add .out.graphML
            base_name="${file%.graphML}"
            output_file="${base_name}.nofo.graphML"

            echo "   → Output will be: $output_file"




            # For demonstration,
            echo "   → Command: python3 $TRANSFORM_GRAPHML_SCRIPT --top-firms-only --filter-by-org  --show $file "


            if  $TRANSFORM_GRAPHML_SCRIPT  -v  --show  "$file" ; then
                 echo "   ✅ Successfully processed $file"
                 echo "   See $output_file"
                 echo ""
                 echo "   You can add to repo with: "
                 echo "   git add $output_file"
             else
                 echo "   ❌ Failed to process $file"
            fi

            exit

            echo



            viz_question="Do you want to visualize $file vs. $output_file before and after deanonymizing via GitHub REST API? "


            echo "Do you want to visualize both the networks before and after deanonymizing via GitHub REST API?"
            echo "You should not longer see so many developers affiliated with 'user'"


            # First check if visualization script exists
if [[ ! -f "$FFV_NO_FI_GRAPHML_SCRIPT" ]]; then
    echo -e "${RED}✗ Visualization script not found: $FFV_NO_FI_GRAPHML_SCRIPT${NC}"
    # Optionally ask if they want to continue without visualization
    if ask_yes_no "Continue processing without visualization?" "y"; then
        VISUALIZE_BOTH=false
    fi
else
    echo -e "${GREEN}✓ Visualization script available${NC}"
    echo -e "${BLUE}Script: ${YELLOW}$FFV_NO_FI_GRAPHML_SCRIPT${NC}"
    echo ""

    # Now ask about visualization
    if ask_yes_no "Do you want to visualize both the networks before and after deanonymizing via GitHub REST API?" "n"; then
        VISUALIZE_BOTH=true
        echo -e "Visualization will be performed on both input and output files."
        echo -e "\"$file\" vs. \"$output_file"

        $FFV_NO_FI_GRAPHML_SCRIPT --plot --legend $file &
        $FFV_NO_FI_GRAPHML_SCRIPT --plot --legend $output_file &

    else
        VISUALIZE_BOTH=false
        echo "Skipping visualization."
    fi
fi





        done

        echo "🎉 Processing complete!"
    else
        echo "❌ Processing cancelled."
    fi
else
    echo "⚠️  No files selected."
fi

# Optional: Save selection to a file for batch processing
# echo "💾 Saving selection to 'selected_files.txt'..."
# printf "%s\n" "${selected_files[@]}" > selected_files.txt
