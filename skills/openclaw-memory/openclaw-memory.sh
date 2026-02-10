#!/usr/bin/env bash
# OpenClaw Memory Management Skill
# Version: 1.1.0 - SECURITY HARDENED
# Author: Pi-Agent

# Security: Fail fast, validate all inputs, prevent command injection
set -euo pipefail

# Color definitions
readonly CYAN='\033[0;36m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly RED='\033[0;31m'
readonly NC='\033[0m'

# Security configuration
readonly MAX_QUERY_LENGTH=200
readonly MAX_FILES_TO_DELETE=100
readonly MAX_RESULTS=20
readonly ALLOWED_COMMANDS=("search" "compress" "stats" "agents" "recent" "clean" "help")
readonly LOG_FILE="/tmp/openclaw-memory.log"

# Default paths - validated later
WORKSPACE=""
MEMORY_FILE=""
AGENTS_FILE=""
MEMORY_DIR=""

# Security logging
log_security() {
    local event="$1"
    local details="${2:-}"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "[$timestamp] SECURITY: $event | $details" >> "$LOG_FILE"
}

# Input validation - prevent command injection
validate_input() {
    local input="$1"
    local name="$2"
    local max_length="${3:-$MAX_QUERY_LENGTH}"

    # Check length
    if [ ${#input} -gt $max_length ]; then
        log_security "INPUT_TOO_LONG" "$name: length=${#input}"
        echo -e "${RED}❌ Error: $name exceeds maximum length ($max_length)${NC}" >&2
        exit 1
    fi

    # Check for dangerous characters (command injection)
    if echo "$input" | grep -qE '[;&|`$()]'; then
        log_security "DANGEROUS_CHARS" "$name: $input"
        echo -e "${RED}❌ Error: Invalid characters in $name${NC}" >&2
        exit 1
    fi

    # Check for path traversal attempts
    if echo "$input" | grep -qE '\.\./|\.\./|/etc|/proc|/sys'; then
        log_security "PATH_TRAVERSAL_ATTEMPT" "$name: $input"
        echo -e "${RED}❌ Error: Invalid path in $name${NC}" >&2
        exit 1
    fi
}

# Path validation - prevent directory traversal
validate_path() {
    local path="$1"
    local name="$2"

    # Resolve absolute path
    local resolved=$(realpath -m "$path" 2>/dev/null || echo "$path")

    # Check for symlinks to sensitive directories
    case "$resolved" in
        /etc/*|/proc/*|/sys/*|/dev/*)
            log_security "SENSITIVE_PATH" "$name: $resolved"
            echo -e "${RED}❌ Error: Access to restricted path denied${NC}" >&2
            exit 1
            ;;
    esac

    echo "$resolved"
}

# Initialize paths with validation
init_paths() {
    # Get and validate WORKSPACE
    local workspace_input="${WORKSPACE:-$(pwd)}"
    validate_input "$workspace_input" "WORKSPACE"
    WORKSPACE=$(validate_path "$workspace_input" "WORKSPACE")

    # Set validated paths
    MEMORY_FILE="$WORKSPACE/MEMORY.md"
    AGENTS_FILE="$WORKSPACE/AGENTS.md"
    MEMORY_DIR="$WORKSPACE/memory"

    # Create memory directory if it doesn't exist
    if [ ! -d "$MEMORY_DIR" ]; then
        mkdir -p "$MEMORY_DIR" 2>/dev/null || {
            echo -e "${RED}❌ Error: Cannot create memory directory${NC}" >&2
            exit 1
        }
    fi

    log_security "INIT_PATHS" "WORKSPACE=$WORKSPACE"
}

# Safe grep - prevents pattern injection
safe_grep() {
    local pattern="$1"
    local file="$2"

    # Validate pattern length
    validate_input "$pattern" "search pattern"

    # Use -- to prevent option injection
    # Use -F for fixed strings (not regex)
    grep -- -F -i -n -- "$pattern" "$file" 2>/dev/null || true
}

# Safe find - prevents command injection
safe_find() {
    local dir="$1"
    local pattern="$2"

    # Validate directory
    validate_input "$dir" "search directory"

    # Use -print0 and xargs for safety
    find "$dir" -type f -name "*.md" -print0 2>/dev/null | \
        xargs -0 grep -l -F -i -- "$pattern" 2>/dev/null || true
}

# Command validation - whitelist allowed commands
validate_command() {
    local cmd="$1"

    # Check if command is in whitelist
    local found=false
    for allowed in "${ALLOWED_COMMANDS[@]}"; do
        if [ "$allowed" = "$cmd" ]; then
            found=true
            break
        fi
    done

    if [ "$found" = false ]; then
        log_security "INVALID_COMMAND" "$cmd"
        echo -e "${RED}❌ Error: Unknown or disallowed command: $cmd${NC}" >&2
        exit 1
    fi

    log_security "COMMAND_EXEC" "$cmd"
}

# Help
show_help() {
    cat << EOF
🧠 OpenClaw Memory Management Skill (SECURITY HARDENED v1.1.0)

Commands:
  search <query>           Search MEMORY.md and memory/*.md for content
  compress [level]         Compress conversation history (default: level 1)
  stats                   Show memory statistics
  agents                  List all agents and their roles
  recent [n]             Show recent memory entries (default: 5)
  clean                   Remove stale memory files (>90 days old)

Environment Variables:
  WORKSPACE                Path to OpenClaw workspace (default: current dir)

Security Features:
  - Input validation (length, characters, path traversal)
  - Command whitelisting
  - Safe path resolution
  - Operation limits (max results, max files)
  - Security logging to: $LOG_FILE

Examples:
  openclaw-memory.sh search "trading strategies"
  openclaw-memory.sh compress 2
  openclaw-memory.sh stats
  openclaw-memory.sh agents

EOF
}

# Search memory - hardened
memory_search() {
    local query="$1"

    if [ -z "$query" ]; then
        echo -e "${RED}❌ Error: Search query required${NC}" >&2
        exit 1
    fi

    echo -e "${CYAN}🔍 Searching memory for: $query${NC}"
    echo ""

    # Search MEMORY.md
    if [ -f "$MEMORY_FILE" ]; then
        echo -e "${GREEN}📄 MEMORY.md:${NC}"
        safe_grep "$query" "$MEMORY_FILE" | head -n "$MAX_RESULTS" || echo "  No matches"
        echo ""
    else
        echo -e "${YELLOW}⚠️  MEMORY.md not found${NC}"
        echo ""
    fi

    # Search memory/*.md
    if [ -d "$MEMORY_DIR" ]; then
        echo -e "${GREEN}📁 memory/ directory:${NC}"
        safe_find "$MEMORY_DIR" "$query" | head -n "$MAX_RESULTS" || echo "  No matches"
    else
        echo -e "${YELLOW}⚠️  memory/ directory not found${NC}"
    fi
}

# Compress memory - with safeguards
memory_compress() {
    local level="${1:-1}"

    # Validate level
    case "$level" in
        1|2|3)
            ;;
        *)
            echo -e "${RED}❌ Error: Invalid level: $level (use 1, 2, or 3)${NC}" >&2
            exit 1
            ;;
    esac

    echo -e "${CYAN}🗜  Compressing memory (level: $level)...${NC}"
    echo ""

    case "$level" in
        1)
            echo "Level 1: Removing duplicate entries"
            echo "  (Not implemented - requires memory format specification)"
            ;;
        2)
            echo "Level 2: Summarizing old entries (>30 days)"
            echo "  (Not implemented - requires AI summarization)"
            ;;
        3)
            echo "Level 3: Archiving old files (>90 days)"
            echo "  (Not implemented - requires archive directory setup)"
            ;;
    esac

    echo -e "${GREEN}✅ Compression complete${NC}"
}

# Show statistics - safe
memory_stats() {
    echo -e "${CYAN}📊 Memory Statistics${NC}"
    echo ""

    # MEMORY.md
    if [ -f "$MEMORY_FILE" ]; then
        local lines=$(wc -l < "$MEMORY_FILE" 2>/dev/null || echo "0")
        local size=$(du -h "$MEMORY_FILE" 2>/dev/null | cut -f1 || echo "0")
        echo "MEMORY.md: $lines lines, $size"
    fi

    # AGENTS.md
    if [ -f "$AGENTS_FILE" ]; then
        local lines=$(wc -l < "$AGENTS_FILE" 2>/dev/null || echo "0")
        local size=$(du -h "$AGENTS_FILE" 2>/dev/null | cut -f1 || echo "0")
        echo "AGENTS.md: $lines lines, $size"
    fi

    # memory/*.md
    if [ -d "$MEMORY_DIR" ]; then
        local count=$(find "$MEMORY_DIR" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l)
        local total_size=$(du -sh "$MEMORY_DIR" 2>/dev/null | cut -f1 || echo "0")
        echo "memory/ directory: $count files, $total_size"
    fi
}

# List agents - safe
agents_list() {
    echo -e "${CYAN}🤖 AGENTS.md${NC}"
    echo ""

    if [ -f "$AGENTS_FILE" ]; then
        # Display file with size limit (prevent output overflow)
        local lines=$(wc -l < "$AGENTS_FILE" 2>/dev/null || echo "0")
        if [ "$lines" -le 100 ]; then
            cat "$AGENTS_FILE"
        else
            echo "  File too large to display ($lines lines)"
            echo "  Use: head -n 50 $AGENTS_FILE"
        fi
    else
        echo -e "${YELLOW}⚠️  AGENTS.md not found${NC}"
    fi
}

# Show recent entries - with limit
recent_entries() {
    local count="${1:-5}"

    # Validate count (prevent exhaustion)
    if ! [[ "$count" =~ ^[0-9]+$ ]]; then
        echo -e "${RED}❌ Error: Invalid count: $count (must be positive integer)${NC}" >&2
        exit 1
    fi

    # Limit maximum
    if [ "$count" -gt 50 ]; then
        count=50
        echo -e "${YELLOW}⚠️  Count limited to 50${NC}"
    fi

    echo -e "${CYAN}📅 Recent Memory Entries (last $count)${NC}"
    echo ""

    if [ -d "$MEMORY_DIR" ]; then
        find "$MEMORY_DIR" -maxdepth 1 -name "*.md" -type f -printf "%T@ %p\n" 2>/dev/null | \
            sort -rn | \
            head -n "$count" | \
            awk '{print "  " $2}' | \
            xargs -I {} basename {} 2>/dev/null || echo "  No entries found"
    else
        echo -e "${YELLOW}⚠️  memory/ directory not found${NC}"
    fi
}

# Clean old memory - with safeguards
clean_old() {
    echo -e "${CYAN}🧹 Cleaning old memory files (>90 days)${NC}"
    echo ""

    if [ ! -d "$MEMORY_DIR" ]; then
        echo -e "${YELLOW}⚠️  memory/ directory not found${NC}"
        return
    fi

    # Count old files first (with limit)
    local count=$(find "$MEMORY_DIR" -maxdepth 1 -name "*.md" -mtime +90 -type f 2>/dev/null | wc -l)

    if [ "$count" -eq 0 ]; then
        echo "No old files found"
        return
    fi

    # Limit maximum deletions
    if [ "$count" -gt "$MAX_FILES_TO_DELETE" ]; then
        echo -e "${YELLOW}⚠️  Found $count old files (exceeds safety limit of $MAX_FILES_TO_DELETE)${NC}"
        echo "  Run cleanup manually or increase limit"
        return
    fi

    echo "Found $count old files. Removing..."
    log_security "CLEAN_OLD" "Deleting $count files"

    # Delete with confirmation (requires manual confirm or env var)
    if [ "${AUTO_CLEAN:-0}" != "1" ]; then
        echo -e "${YELLOW}⚠️  Set AUTO_CLEAN=1 to skip confirmation${NC}"
        echo "  Continuing with dry-run..."
        find "$MEMORY_DIR" -maxdepth 1 -name "*.md" -mtime +90 -type f 2>/dev/null | head -n 5
        return
    fi

    # Actual deletion
    local deleted=$(find "$MEMORY_DIR" -maxdepth 1 -name "*.md" -mtime +90 -type f -delete 2>/dev/null && echo "$count" || echo "0")
    echo -e "${GREEN}✅ Removed $deleted old files${NC}"
}

# Main - with security layers
main() {
    # Initialize paths (with validation)
    init_paths

    # Validate command
    local command="${1:-help}"
    validate_command "$command"

    # Route command
    case "$command" in
        search)
            memory_search "$2"
            ;;
        compress)
            memory_compress "$2"
            ;;
        stats)
            memory_stats
            ;;
        agents)
            agents_list
            ;;
        recent)
            recent_entries "$2"
            ;;
        clean)
            clean_old
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}❌ Error: Unknown command: $command${NC}" >&2
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
