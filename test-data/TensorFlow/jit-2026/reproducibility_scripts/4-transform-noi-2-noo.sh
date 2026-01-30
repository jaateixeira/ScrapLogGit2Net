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
            echo "   → Command: python3 $TRANSFORM_GRAPHML_SCRIPT --top-firms-only --filter-by-org --show $file -o $output_file"

            if python3 "$TRANSFORM_GRAPHML_SCRIPT" -v --show "$file" -o "$output_file"; then
                echo "   ✅ Successfully processed $file"
                echo "   See $output_file"
                echo ""
                echo "   You can add to repo with: "
                echo "   git add $output_file"
            else
                echo "   ❌ Failed to process $file"
            fi
        done  # Close the for loop
    else
        echo "❌ Processing cancelled by user."
    fi  # Close the inner if statement
else
    echo "⚠️  No files selected for processing."
fi  # Close the outer if statement


print_info " Checking if $output_file was created"


        # Test 1: Check if output file exists
        if [[ -f "$output_file" ]]; then
            echo "   → Command: python3 $TRANSFORM_GRAPHML_SCRIPT --top-firms-only --filter-by-org  --show $file  -o $output_file "
            print_success "$output_file successfully created by transforming "
        else

            print_error "ERROR: File not found!"
            exit
        fi

      copy_with_confirmation $output_file $DIR_4_MINED_NETWORKS_NOFO_GRAPHML

      ls $DIR_4_MINED_NETWORKS_NOFO_GRAPHML


    # Test 2: Test if file was copied
        if [[ -f "${DIR_4_MINED_NETWORKS_NOFO_GRAPHML}/$output_file" ]]; then
            print_success "$output_file successfully copied to $DIR_4_MINED_NETWORKS_NOFO_GRAPHML"
        else
            print_error "ERROR: File not found!"
            echo -e "Not in ${DIR_4_MINED_NETWORKS_NOFO_GRAPHML}/$output_file"
            exit
        fi

    du -sh "${DIR_4_MINED_NETWORKS_NOFO_GRAPHML}/$output_file"
