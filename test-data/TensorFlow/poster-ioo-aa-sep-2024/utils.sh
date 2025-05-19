
# Define color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Function to check if a file exists and is a PDF
function file_exists_and_is_pdf() {
    local FILE=$1
    # Check if the file exists
    if [ -f "$FILE" ]; then
        # Check if the file is a PDF
        if [[ $(file --mime-type -b "$FILE") == "application/pdf" ]]; then
            # If the file is a PDF, print a success message in green
            echo -e "${GREEN}File $FILE exists and is a PDF.${NC}"
        else
            # If the file is not a PDF, print an error message in red and exit with a non-zero status
            echo -e "${RED}Error: File $FILE exists but is not a PDF.${NC}"
            exit 1
        fi
    else
        # If the file does not exist, print an error message in red and exit with a non-zero status
        echo -e "${RED}Error: File $FILE does not exist.${NC}"
        exit 1
    fi
}

# Function to check if a file exists and is not empty
function file_exists_and_is_not_empty() {
    local FILE=$1
    # Check if the file exists
    if [ -f "$FILE" ]; then
        # Check if the file is not empty
        if [ -s "$FILE" ]; then
            # If the file exists and is not empty, print a success message in green
            echo -e "${GREEN}File $FILE exists and is not empty.${NC}"
        else
            # If the file exists but is empty, print an error message in red and exit with a non-zero status
            echo -e "${RED}Error: File $FILE exists but is empty.${NC}"
            exit 1
        fi
    else
        # If the file does not exist, print an error message in red and exit with a non-zero status
        echo -e "${RED}Error: File $FILE does not exist.${NC}"
        exit 1
    fi
}


# Function to check if a file exists
function file_exists() {
    local FILE=$1
    # Check if the file exists
    if [ -f "$FILE" ]; then
        # If the file exists, print a success message in green
        echo -e "${GREEN}File $FILE exists.${NC}"
    else
        # If the file does not exist, print an error message in red and exit with a non-zero status
        echo -e "${RED}Error: File $FILE does not exist.${NC}"
        exit 1
    fi
}


# Function to check if a shell command exists
function command_exists() {
    local COMMAND=$1
    # Check if the command exists
    if command -v "$COMMAND" >/dev/null 2>&1; then
        # If the command exists, print a success message in green
        echo -e "${GREEN}Command $COMMAND exists.${NC}"
    else
        # If the command does not exist, print an error message in red and exit with a non-zero status
        echo -e "${RED}Error: Command $COMMAND does not exist.${NC}"
        exit 1
    fi
}





# Function to print a happy smile emoji
function print_happy_smile() {
    echo -e "\xF0\x9F\x98\x8A"
}

# Function to print a sad smile emoji
function print_sad_smile() {
    echo -e "\xF0\x9F\x98\x9E"
}

# Function to print a heart emoji
function print_heart() {
    echo -e "\xE2\x99\xA5"
}

# Function to print a thumbs up emoji
function print_thumbs_up() {
    echo -e "\xF0\x9F\x91\x8D"
}

# Function to print a thumbs down emoji
function print_thumbs_down() {
    echo -e "\xF0\x9F\x91\x8E"
}


