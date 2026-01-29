#!/bin/bash


source config.cfg

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color


# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}


# Function to test configuration
test_config() {
    echo -e "${CYAN}=== Testing Configuration Variables ===${NC}"
    echo ""

    # Test the first 4 variables for file existence and execution
    local file_vars=("SCRAPLOG_SCRIPT" "FFV_NO_FI_GRAPHML_SCRIPT" "TRANSFORM_GRAPHML_SCRIPT" )

    for var_name in "${file_vars[@]}"; do
        local file_path="${!var_name}"

        echo -e "${BLUE}Testing ${var_name}: ${NC}"
        echo -e "  Path: ${YELLOW}${file_path}${NC}"

        # Test 1: Check if file exists
        if [[ -f "$file_path" ]]; then
            echo -e "  File exists: ${GREEN}✓${NC}"
        else
            echo -e "  File exists: ${RED}✗${NC}"
            echo -e "  ${RED}ERROR: File not found!${NC}"
            continue
        fi

        # Test 2: Check if it's executable
        if [[ -x "$file_path" ]]; then
            echo -e "  Is executable: ${GREEN}✓${NC}"
        else
            echo -e "  Is executable: ${RED}✗${NC}"
            echo -e "  ${YELLOW}WARNING: File is not executable. Consider running 'chmod +x ${file_path}'${NC}"
        fi

        # Test 3: Check if it's a Python file
        if [[ "$file_path" == *.py ]] || head -n 1 "$file_path" 2>/dev/null | grep -q "^#!.*python"; then
            echo -e "  Python file: ${GREEN}✓${NC}"
        else
            echo -e "  Python file: ${YELLOW}?${NC}"
            echo -e "  ${YELLOW}Note: This may not be a Python script${NC}"
        fi

        echo ""
    done

    # Display the last 2 variables with color
    echo -e "${CYAN}=== Displaying Configuration Variables ===${NC}"
    echo ""

    echo -e "${MAGENTA}TOP10_ORG:${NC}"
    echo -e "${GREEN}${TOP10_ORG}${NC}"
    echo ""

    echo -e "${MAGENTA}COMPANIES_TO_IGNORE:${NC}"
    echo -e "${GREEN}${COMPANIES_TO_IGNORE}${NC}"
    echo ""

    echo -e "${CYAN}=== Configuration Test Complete ===${NC}"
}



check_dir_writable() {
    local dir_path="$1"

    if [[ -z "$dir_path" ]]; then
        echo -e "${RED}Error: No directory path provided${NC}"
        return 1
    fi

    if [[ ! -d "$dir_path" ]]; then
        echo -e "${RED}Error: Directory '$dir_path' does not exist${NC}"
        return 1
    fi

    if [[ ! -w "$dir_path" ]]; then
        echo -e "${RED}Error: Directory '$dir_path' is not writable${NC}"
        return 1
    fi

    echo -e "${GREEN}Success: Directory '$dir_path' exists and is writable${NC}"
    return 0
}





verify_and_visualize_graphml() {
    local input_file="$1"  # The original .IN.TXT file path

    echo -e "${CYAN}════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}        Verify & Visualize GraphML Output${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════${NC}"

    # Check if input file was provided
    if [[ -z "$input_file" ]]; then
        echo -e "${RED}✗ ERROR: No input file provided${NC}"
        return 1
    fi

    local input_name=$(basename "$input_file")
    echo -e "${BLUE}Input file: ${YELLOW}$input_name${NC}"

    # Generate expected GraphML filename
    #
    local base_name="${input_file}"


    # Alternative:  scrapLog.py creates files in output directory
    local graphml_file="./${input_name%.TXT}.NetworkFile.graphML"



    echo -e "${BLUE}Expected GraphML: ${YELLOW}$(basename "$graphml_file")${NC}"
    echo -e "${BLUE}Full path: ${CYAN}$graphml_file${NC}"
    echo ""

    # Step 1: Check if GraphML file exists
    echo -e "${MAGENTA}Step 1: Checking if GraphML file exists...${NC}"

    if [[ ! -f "$graphml_file" ]]; then
        echo -e "${RED}✗ GraphML file not found: $graphml_file${NC}"

        # Look for similar files
        echo -e "${YELLOW} exit with as file to be produced by ScrapLog was not found ${NC}"
        return 1
    else
        echo -e "${GREEN}✓ GraphML file found${NC}"
    fi

    # Step 2: Check if it's a valid GraphML file
    echo ""
    echo -e "${MAGENTA}Step 2: Validating GraphML file...${NC}"

    local file_size=$(du -h "$graphml_file" 2>/dev/null | cut -f1 || echo "unknown")
    local line_count=$(wc -l < "$graphml_file" 2>/dev/null || echo "0")

    echo -e "${BLUE}Size: ${YELLOW}$file_size${NC}, ${BLUE}Lines: ${YELLOW}$line_count${NC}"

    # Check for GraphML signature
    if head -5 "$graphml_file" 2>/dev/null | grep -iq "<graphml"; then
        echo -e "${GREEN}✓ Valid GraphML file (contains <graphml> tag)${NC}"

        # Count nodes and edges if possible
        local node_count=$(grep -c "<node " "$graphml_file" 2>/dev/null || echo "0")
        local edge_count=$(grep -c "<edge " "$graphml_file" 2>/dev/null || echo "0")

        echo -e "${BLUE}Nodes: ${GREEN}$node_count${NC}, ${BLUE}Edges: ${GREEN}$edge_count${NC}"

        # Check if file has content
        if [[ $node_count -eq 0 ]]; then
            echo -e "${YELLOW}⚠ Warning: Graph has 0 nodes (might be empty)${NC}"
        fi
    else
        echo -e "${RED}✗ Not a valid GraphML file (missing <graphml> tag)${NC}"

        # Show first few lines for debugging
        echo -e "${YELLOW}First 3 lines:${NC}"
        head -3 "$graphml_file" 2>/dev/null | while IFS= read -r line; do
            echo -e "${YELLOW}  $line${NC}"
        done
        return 1
    fi

    # Step 3: Ask about visualization
    echo ""
    echo -e "${MAGENTA}Step 3: Visualization Options${NC}"

    # Check if visualization script exists
    if [[ ! -f "$FFV_NO_FI_GRAPHML_SCRIPT" ]]; then
        echo -e "${RED}✗ Visualization script not found: $FFV_NO_FI_GRAPHML_SCRIPT${NC}"
        return 1
    fi

    echo -e "${GREEN}✓ Visualization script available${NC}"
    echo -e "${BLUE}Script: ${YELLOW}$FFV_NO_FI_GRAPHML_SCRIPT${NC}"
    echo ""

    echo -e "${BLUE}Visualization options:${NC}"
    echo -e "  ${GREEN}[1]${NC} Basic visualization"
    echo -e "  ${GREEN}[2]${NC} With legend (--legend)"
    echo -e "  ${GREEN}[3]${NC} With plot (--plot)"
    echo -e "  ${GREEN}[4]${NC} With legend and plot (--legend --plot)"
    echo -e "  ${GREEN}[s]${NC} Skip visualization"
    echo -e "  ${GREEN}[q]${NC} Quit"
    echo ""

    while true; do
        echo -e  "${BLUE}Select option (1-4, s, q): ${NC}"
        read -r option

        case "$option" in
            1)
                viz_command="python3 \"$FFV_NO_FI_GRAPHML_SCRIPT\" \"$graphml_file\""
                break
                ;;
            2)
                viz_command="python3 \"$FFV_NO_FI_GRAPHML_SCRIPT\" --legend \"$graphml_file\""
                break
                ;;
            3)
                viz_command="python3 \"$FFV_NO_FI_GRAPHML_SCRIPT\" --plot \"$graphml_file\""
                break
                ;;
            4)
                viz_command="python3 \"$FFV_NO_FI_GRAPHML_SCRIPT\" --legend --plot \"$graphml_file\""
                break
                ;;
            s|S)
                echo -e "${YELLOW}⚠ Skipping visualization${NC}"
                copy_with_confirmation "$graphml_file" "$DIR_4_MINED_NETWORKS_NOFI_GRAPHML"
                return 0
                ;;
            q|Q)
                echo -e "${YELLOW}⚠ Exiting${NC}"
                return 0
                ;;
            *)
                echo -e "${RED}✗ Invalid option. Please try again.${NC}"
                ;;
        esac
    done

    echo ""
    echo -e "${MAGENTA}Step 4: Running Visualization${NC}"
    echo -e "${BLUE}Command:${NC}"
    echo -e "${YELLOW}$viz_command${NC}"
    echo ""

    echo -e "${BLUE}Run visualization? (y/n): ${NC}"
    read -r confirm

    if [[ ! "$confirm" =~ ^[Yy]([Ee][Ss])?$ ]]; then
        echo -e "${YELLOW}⚠ Visualization cancelled${NC}"
        return 0
    fi

    echo -e "${CYAN}Starting visualization...${NC}"

    # Run the visualization command
    if eval "$viz_command"; then
        echo -e "${GREEN}✓ Visualization completed successfully${NC}"

    else
        local exit_code=$?
        echo -e "${RED}✗ Visualization failed with exit code: $exit_code${NC}"
        return $exit_code
    fi


      echo -e "${GREEN}✓ processed, visualized, time to copy  to final destination as in config.cfg${NC}"

  copy_with_confirmation "$graphml_file" "$DIR_4_MINED_NETWORKS_NOFI_GRAPHML"


}


ask_yes_no() {
    local question="$1"
    local default="$2"  # "y" or "n"
    local prompt

    # Set prompt based on default value
    if [[ "$default" == "y" ]]; then
        prompt="[Y/n]"
    elif [[ "$default" == "n" ]]; then
        prompt="[y/N]"
    else
        prompt="[y/n]"
    fi

    while true; do
        read -p "$question $prompt: " -n 1 -r answer
        echo ""

        # Handle Enter key (use default)
        if [[ -z "$answer" ]]; then
            answer="$default"
        fi

        case "$answer" in
            [Yy]* ) return 0 ;;  # Yes = true
            [Nn]* ) return 1 ;;  # No = false
            * ) echo "Please answer yes (y) or no (n)." ;;
        esac
    done
}


# Function to check and handle directory
check_or_create_directory() {
    local dir_path="$1"

    print_info "Checking directory: $dir_path"

    # Check if directory exists
    if [[ -d "$dir_path" ]]; then
        print_success "Directory exists: $dir_path"

        # Check if it's readable
        if [[ ! -r "$dir_path" ]]; then
            print_warning "Directory exists but is not readable"
        fi

        # Check if it's writable
        if [[ ! -w "$dir_path" ]]; then
            print_warning "Directory exists but is not writable"
        fi

        # List contents (optional)
        if [[ -r "$dir_path" ]]; then
            local file_count=$(find "$dir_path" -maxdepth 1 -type f 2>/dev/null | wc -l)
            local dir_count=$(find "$dir_path" -maxdepth 1 -type d 2>/dev/null | wc -l)
            ((dir_count--))  # Subtract the directory itself

            print_info "Directory contains: $file_count files, $dir_count subdirectories"

            if [[ $file_count -gt 0 ]]; then
                if ask_yes_no "Show first 5 files?" "n"; then
                    echo "Files in directory:"
                    find "$dir_path" -maxdepth 1 -type f 2>/dev/null | head -5
                fi
            fi
        fi

        return 0
    else
        print_warning "Directory does not exist: $dir_path"

        # Ask user if they want to create it
        if ask_yes_no "Would you like to create this directory now?" "y"; then
            print_info "Creating directory: $dir_path"

            # Try to create directory
            if mkdir -p "$dir_path"; then
                print_success "Directory created successfully: $dir_path"

                # Set permissions (optional)
                if ask_yes_no "Set directory permissions to 755 (rwxr-xr-x)?" "y"; then
                    if chmod 755 "$dir_path"; then
                        print_success "Permissions set to 755"
                    else
                        print_warning "Could not set permissions (continuing anyway)"
                    fi
                fi

                return 0
            else
                print_error "Failed to create directory: $dir_path"
                print_error "Please check your permissions or disk space"
                return 1
            fi
        else
            print_error "User chose not to create directory. Exiting."
            return 1
        fi
    fi
}


