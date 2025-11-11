#!/bin/bash
set -euo pipefail

# DEFAULTS

TARGET_DIR=""
OUTPUT_FL=""
PREFIX_FL="Description.md"
SUFFIX_FL="Conclusion.md"
ITEM_PREFIX=""
DOC_NAME=""
ADD_PREFIX=false
ADD_SUFFIX=false
FIX_LINKS=false
SEPARATOR=$'\n--------------------------------------------------------------------------------\n'

function usage() {
cat <<EOF
Usage: $0 [OPTIONS]

Options:
  -t, --target-dir=<dir>      Target directory containing input markdown files
  -o, --output-fl=<file>      Output markdown file
  -p, --item-prefix=<prefix>  Prefix for document items (e.g. REQ, DD, TC, INF, WI, ...)
  -N, --doc-name=<name>       Name/title for the concatenated document
  -P, --add-prefix            Add prefix markdown file (Description.md)
  -S, --add-suffix            Add suffix markdown file (Conclusion.md)
  -s, --separator=<sep>       Separator string (default: horizontal line)
  -F, --fix-links             Rewrite Markdown links in the output file
  -h, --help                  Show this help message

Example:
  $0 --target-dir=./EDS/ --output-fl=./EDS.md --item-prefix=DD --add-prefix --add-suffix --fix-links --doc-name="Element Design Specification"

EOF
}

function parse_args() {
    for arg in "$@"; do
        case $arg in
            -t=*|--target-dir=*)
                TARGET_DIR="${arg#*=}"
                ;;
            -o=*|--output-fl=*)
                OUTPUT_FL="${arg#*=}"
                ;;
            -p=*|--item-prefix=*)
                ITEM_PREFIX="${arg#*=}"
                ;;
            -N=*|--doc-name=*)
                DOC_NAME="${arg#*=}"
                ;;
            -s=*|--separator=*)
                SEPARATOR="${arg#*=}"
                ;;
            -P|--add-prefix)
                ADD_PREFIX=true
                ;;
            -S|--add-suffix)
                ADD_SUFFIX=true
                ;;
            -F|--fix-links)
                FIX_LINKS=true
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                echo "Unknown argument: $arg"
                usage
                exit 1
                ;;
        esac
    done

    if [[ -z "$TARGET_DIR" || -z "$OUTPUT_FL" || -z "$ITEM_PREFIX" || -z "$DOC_NAME" ]]; then
        echo "[ ERROR ]: Missing required arguments"
        usage
        exit 1
    fi

    if [[ ! -d "$TARGET_DIR" ]]; then
        echo "[ NOK ]: Target directory '$TARGET_DIR' not found"
        exit 1
    fi
}

function print_section_header() {
    local file="$1"
    local dir="${2:-}"
    local name
    local title
    name=$(basename "$file" | cut -d '.' -f 1 | tr '_' ' ')
    if [ ! -z "$dir" ]; then
        title=$(head -n 1 "${dir}/${file}")
    else
        title=$(head -n 1 "${file}")
    fi
    echo "# [ $name ]: ${title#\# }"
    echo
}

function build_output() {
    echo "[ ... ]: Building document body"
    {
        echo "# $DOC_NAME"
        echo

        if $ADD_PREFIX && [[ -f "$TARGET_DIR/$PREFIX_FL" ]]; then
            print_section_header "$PREFIX_FL" "$TARGET_DIR"
#           cat "$TARGET_DIR/$PREFIX_FL"
            tail -n +2 "$TARGET_DIR/$PREFIX_FL"
            echo "$SEPARATOR"
        fi

        for file in $(ls "$TARGET_DIR"/"$ITEM_PREFIX"*.md 2>/dev/null | sort -V); do
            [[ -e "$file" ]] || continue
            print_section_header "$file"
#           cat "$file"
            tail -n +2 "$file"
            echo "$SEPARATOR"
        done

        if $ADD_SUFFIX && [[ -f "$TARGET_DIR/$SUFFIX_FL" ]]; then
            print_section_header "$SUFFIX_FL" "$TARGET_DIR"
#           cat "$TARGET_DIR/$SUFFIX_FL"
            tail -n +2 "$TARGET_DIR/$SUFFIX_FL"
        fi
    } > "$OUTPUT_FL"

    echo "[ OK ]: Built $OUTPUT_FL from $TARGET_DIR"
}

#######################################
# [ NOTE ]: Fix Markdown links in output file (repo-root relative)
# - If target is dir2:
#   ./file.md    → ./dir2/file.md
#   ../dir3/file.md → ./dir3/file.md
#######################################
function fix_links() {
    local file="$1"
    local target_dir
    target_dir="$(basename "$TARGET_DIR")"

    echo "[ ... ]: Reworking links in $file ..."

    # Rewrite links inside the target dir
    sed -i -E "s#\]\(\s*\./([^)]*)\)#](./${target_dir}/\1)#g" "$file"

    # Rewrite links to sibling dirs
    for sibling in $(find "$(dirname "$TARGET_DIR")" -maxdepth 1 -type d -not -name "$target_dir" -printf "%f\n"); do
        sed -i -E "s#\]\(\s*\.\./${sibling}/([^)]*)\)#](./${sibling}/\1)#g" "$file"
    done

    echo "[ OK ]: Links rewritten in $file"
}

function display_banner() {
    cat<<EOF
    ___________________________________________________________________________

      *                      *  Dynamic DOX Builder  *                       *
    ___________________________________________________________________________
                    Regards, the Alveare Solutions #!/Society -x

EOF
    return $?
}

function main() {
    display_banner
    parse_args "$@"
    build_output
    if $FIX_LINKS; then
        fix_links "$OUTPUT_FL"
    fi
}

# MISCELLANEOUS

main "$@"

# CODE DUMP

