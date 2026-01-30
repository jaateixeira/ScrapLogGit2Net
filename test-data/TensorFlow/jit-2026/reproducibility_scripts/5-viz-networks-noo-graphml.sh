#!/bin/bash

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


echo FFV_NO_FO_GRAPHML_SCRIPT=$FFV_NO_FO_GRAPHML_SCRIPT
echo DIR_4_MINED_NETWORKS_NOFO_GRAPHML=$DIR_4_MINED_NETWORKS_NOFO_GRAPHML



print_info "Checking if $DIR_4_MINED_NETWORKS_NOFO_GRAPHML is a directory"
print_info "It's where we will look for networks of organizations to visualize"

# Check if directory exists
if [[ -d "$DIR_4_MINED_NETWORKS_NOFO_GRAPHML" ]]; then
  print_success "Directory exists: $DIR_4_MINED_NETWORKS_NOFO_GRAPHML"
  else
    {
    print_error  "$DIR_4_MINED_NETWORKS_NOFO_GRAPHM does not exist"
    exit 1
    }
fi


print_info "Checking if $DIR_4_MINED_NETWORKS_NOFO_GRAPHML is a directory"
print_info "It's where we will look for networks of organizations to visualize"

# Check if directory exists
if [[ -d "$DIR_4_MINED_NETWORKS_NOFO_GRAPHML" ]]; then
  print_success "Directory exists: $DIR_4_MINED_NETWORKS_NOFO_GRAPHML"
  else
    {
    print_error  "$DIR_4_MINED_NETWORKS_NOFO_GRAPHM does not exist"
    exit 1
    }
fi



echo ""
print_success "FFV_NO_FO_GRAPHML_SCRIPT=$FFV_NO_FO_GRAPHML_SCRIPT DIR_4_MINED_NETWORKS_NOFO_GRAPHML=$DIR_4_MINED_NETWORKS_NOFO_GRAPHML"
echo ""





print_info "Listing $DIR_4_MINED_NETWORKS_NOFO_GRAPHML"
ls  $DIR_4_MINED_NETWORKS_NOFO_GRAPHML



# CMD="$FFV_NO_FO_GRAPHML_SCRIPT  --legent --show  --filter_by_org=$COMPANIES_TO_IGNORE --top_firm_only=$TOP10_ORG  $network_file"


# Function to check if visualization script exists
check_visualization_script() {
    if [[ ! -f "$FFV_NO_FO_GRAPHML_SCRIPT" ]]; then
        print_error "❌ ERROR: Visualization script not found at: $FFV_NO_FO_GRAPHML_SCRIPT"
        echo "Please update the FFV_NO_FO_GRAPHML_SCRIPT variable in this script."
        exit 1
    fi

    # Check if it's a Python script and executable
    if [[ "$FFV_NO_FO_GRAPHML_SCRIPT" == *.py ]] && ! command -v python3 &> /dev/null; then
        print_error "❌ ERROR: python3 is required but not installed"
        exit 1
    fi
}

# Function to find and display nofo.graphML files
find_and_display_files() {
    print_info "🔍 Searching for .nofo.graphML files..."

    # Find all nofo.graphML files (case insensitive)
    mapfile -t all_files < <(find $DIR_4_MINED_NETWORKS_NOFO_GRAPHML -type f -iname "*.nofo.graphML" | head -$MAX_FILES)

    if [[ ${#all_files[@]} -eq 0 ]]; then
        print_error "❌ No .nofo.graphML files found in current directory or subdirectories."
        echo "Make sure you're in the correct directory."
        exit 1
    fi

    print_success "✅ Found ${#all_files[@]} .nofo.graphML file(s):"
    echo ""

    # Display files with numbers
    for i in "${!all_files[@]}"; do
        printf "  ${GREEN}%2d${NC}) %s\n" $((i+1)) "${all_files[$i]}"
    done

    # Check if there are more files than we're showing
    total_files=$(find . -type f -iname "*.nofo.graphML" | wc -l)
    if [[ $total_files -gt $MAX_FILES ]]; then
        echo_yellow "⚠️  Note: Found $total_files files total, showing first $MAX_FILES"
    fi

    echo ""
}

# Function for user selection
select_files() {
    local -n files_ref=$1
    local -n selected_ref=$2

    print_info "📋 SELECTION MENU"
    echo "------------------------------------------------"
    echo "Enter your choice:"
    echo "  • Single number (e.g., '1') for one file"
    echo "  • Multiple numbers separated by spaces (e.g., '1 3 5')"
    echo "  • Range using hyphen (e.g., '1-5')"
    echo "  • 'all' or '*' for all files"
    echo "  • 'q' or 'quit' to exit"
    echo "------------------------------------------------"

    while true; do
        read -p "Your selection: " selection

        # Handle quit
        if [[ "$selection" =~ ^[Qq](uit)?$ ]]; then
            echo_yellow "👋 Exiting..."
            exit 0
        fi

        # Handle "all" or "*"
        if [[ "$selection" == "all" || "$selection" == "*" ]]; then
            selected_ref=("${files_ref[@]}")
            print_success "✅ Selected all ${#selected_ref[@]} files"
            break
        fi

        # Parse the selection
        local temp_selected=()
        local valid_selection=true

        # Split by spaces or commas
        IFS=', ' read -ra choices <<< "$selection"

        for choice in "${choices[@]}"; do
            # Check for range (e.g., 1-5)
            if [[ "$choice" =~ ^([0-9]+)-([0-9]+)$ ]]; then
                start=${BASH_REMATCH[1]}
                end=${BASH_REMATCH[2]}

                if [[ $start -ge 1 && $end -le ${#files_ref[@]} && $start -le $end ]]; then
                    for ((i=start; i<=end; i++)); do
                        temp_selected+=("${files_ref[$((i-1))]}")
                    done
                else
                    print_error "❌ Invalid range: $choice (valid: 1-${#files_ref[@]})"
                    valid_selection=false
                fi

            # Check for single number
            elif [[ "$choice" =~ ^[0-9]+$ ]]; then
                if [[ $choice -ge 1 && $choice -le ${#files_ref[@]} ]]; then
                    temp_selected+=("${files_ref[$((choice-1))]}")
                else
                    print_error "❌ Invalid number: $choice (valid: 1-${#files_ref[@]})"
                    valid_selection=false
                fi

            # Handle empty or invalid input
            elif [[ -n "$choice" ]]; then
                print_error "❌ Invalid input: '$choice'"
                valid_selection=false
            fi
        done

        # Remove duplicates
        if [[ ${#temp_selected[@]} -gt 0 ]]; then
            selected_ref=($(printf "%s\n" "${temp_selected[@]}" | sort -u))
        fi

        # Check if we have valid selections
        if [[ $valid_selection == true && ${#selected_ref[@]} -gt 0 ]]; then
            print_success "✅ Selected ${#selected_ref[@]} file(s):"
            for file in "${selected_ref[@]}"; do
                echo "  • $file"
            done
            break
        elif [[ ${#selected_ref[@]} -eq 0 ]]; then
            print_error "❌ No valid files selected. Please try again."
        fi
    done
}

# Function to visualize files
visualize_files() {
    local selected_files=("$@")

    print_info "🚀 Starting visualization of ${#selected_files[@]} file(s)..."
    echo ""

    for network_file in "${selected_files[@]}"; do
        print_success "📊 Visualizing: $network_file"

        # Build the command
        CMD="$FFV_NO_FO_GRAPHML_SCRIPT --legend --show \"$network_file\""

        print_info "   Command: $CMD"
        echo ""

        # Execute the command
        if eval "$CMD"; then
            print_success "   ✅ Successfully visualized: $network_file"
        else
            print_error "   ❌ Failed to visualize: $network_file"
            exit 1
        fi

        echo ""
        echo "---"
        echo ""
    done

    print_success "🎉 Visualization complete!"
}

# Main script execution
main() {
    # Check if visualization script exists
    check_visualization_script

    # Find and display files
    find_and_display_files

    # User selects files
    declare -a selected_files
    select_files all_files selected_files

    # Confirm before proceeding
    echo ""
    read -p "🚀 Proceed with visualization? (y/N): " -n 1 -r confirm
    echo ""

    if [[ $confirm =~ ^[Yy]$ ]]; then
        visualize_files "${selected_files[@]}"
    else
        echo_yellow "❌ Visualization cancelled."
    fi
}

# Run the main function
main