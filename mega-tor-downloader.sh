#!/usr/bin/env bash
#
# This script automates downloading a MEGA public folder to one or more
# destinations, using Tor to bypass IP-based download quotas by rotating
# the IP address upon failure. It only retries downloads for destinations
# that have not yet succeeded.

set -euo pipefail

# --- Configuration ---
# Default values for options that can be overridden by flags.
MAX_RETRIES=10
RETRY_DELAY=10
LOG_DIR="$HOME/Downloads/mega-tor-logs"

# --- Helper Functions ---

# Function for color-coded and timestamped logging.
log() {
  local type="$1"
  local msg="$2"
  # ANSI color codes
  local color_red="\033[0;31m"
  local color_green="\033[0;32m"
  local color_yellow="\033[0;33m"
  local color_blue="\033[0;34m"
  local color_reset="\033[0m"
  local timestamp

  timestamp=$(date "+%Y-%m-%d %H:%M:%S")

  case "$type" in
    SUCCESS)
      echo -e "${color_green}[$timestamp] [SUCCESS] $msg${color_reset}"
      ;;
    ERROR)
      # Direct error messages to stderr
      echo -e "${color_red}[$timestamp] [ERROR]   $msg${color_reset}" >&2
      ;;
    WARN)
      echo -e "${color_yellow}[$timestamp] [WARN]    $msg${color_reset}"
      ;;
    INFO)
      echo -e "${color_blue}[$timestamp] [INFO]    $msg${color_reset}"
      ;;
    *)
      # Default log format without color
      echo "[$timestamp] $msg"
      ;;
  esac
}

# Displays usage information and exits.
usage() {
  cat <<EOF
Usage: $0 [-u <MEGA_URL>] [-d <DEST_DIR>]... [-h]

Downloads a MEGA public folder, using Tor to rotate IPs on rate limits.

Options:
  -u URL        MEGA public folder URL (e.g. https://mega.nz/folder/XYZ#key)
  -d DIR        Destination directory (can be passed multiple times)
  -r N          Max retries for failed downloads (default: $MAX_RETRIES)
  -w SEC        Seconds to wait between retries (default: $RETRY_DELAY)
  -h            Show this help message and exit

If -u or -d are not provided, you will be prompted to enter them.
EOF
  exit 1
}

# Checks for required dependencies and exits if any are missing.
check_deps() {
  log "INFO" "Checking for required tools..."
  local missing_deps=false
  for cmd in megadl torsocks systemctl sudo; do
    if ! command -v "$cmd" &> /dev/null; then
      log "ERROR" "Required command '$cmd' is not installed or not in PATH."
      missing_deps=true
    fi
  done
  if $missing_deps; then
    exit 1
  fi
  log "SUCCESS" "All required tools are present."
}

# --- Main Script Logic ---
main() {
  # --- Parse Command-Line Arguments ---
  local MEGA_URL=""
  # Use an array to store destination directories
  local -a DESTS=()
  while getopts "u:d:r:w:h" opt; do
    case $opt in
      u) MEGA_URL="$OPTARG" ;;
      d) DESTS+=("$OPTARG") ;;
      r) MAX_RETRIES="$OPTARG" ;;
      w) RETRY_DELAY="$OPTARG" ;;
      h|*) usage ;;
    esac
  done

  # --- Interactive Prompts (if arguments not provided) ---
  if [[ -z "$MEGA_URL" ]]; then
    read -rp "🔗 Enter the MEGA public folder link: " MEGA_URL
  fi
  if [[ ${#DESTS[@]} -eq 0 ]]; then
    read -rp "📦 Enter one or more download locations (space-separated): " -a DESTS
  fi

  # --- Input Validation ---
  if ! [[ "$MEGA_URL" =~ ^https://mega\.nz/folder/ ]]; then
    log "ERROR" "Invalid MEGA URL provided. It must start with 'https://mega.nz/folder/'."
    exit 1
  fi
  if [[ ${#DESTS[@]} -eq 0 ]]; then
    log "ERROR" "No destination directories provided."
    exit 1
  fi
  if [[ $EUID -eq 0 ]]; then
    log "ERROR" "This script should not be run as root. It will ask for sudo password when needed."
    exit 1
  fi

  # --- Setup ---
  check_deps
  log "INFO" "Refreshing sudo credentials..."
  sudo -v # Cache sudo credentials to avoid repeated prompts within the loop.

  mkdir -p "$LOG_DIR"
  local timestamp
  timestamp=$(date +%Y%m%d-%H%M%S)
  local LOG_FILE="$LOG_DIR/mega-tor-$timestamp.log"
  touch "$LOG_FILE"
  log "INFO" "Log file created at: $LOG_FILE"

  for dir in "${DESTS[@]}"; do
    log "INFO" "Ensuring destination directory exists: $dir"
    mkdir -p "$dir"
  done

  # Check if Tor is already running so we can restore the state on exit.
  local was_tor_active=false
  if systemctl is-active --quiet tor; then
    was_tor_active=true
    log "INFO" "Tor service is already active. It will not be stopped on exit."
  fi

  # --- Cleanup Trap ---
  # This function runs on script interruption (CTRL-C) or termination.
  cleanup() {
    log "WARN" "Script interrupted. Cleaning up..."
    # Only stop Tor if the script started it.
    if ! $was_tor_active; then
      log "INFO" "Stopping Tor service because it was not active before script execution."
      sudo systemctl stop tor &>/dev/null || true
    fi
    exit 1
  }
  trap cleanup SIGINT SIGTERM

  # --- Download Loop ---
  # This array will hold the list of destinations that still need a successful download.
  local -a pending_dests=( "${DESTS[@]}" )
  local attempt=0

  while (( ${#pending_dests[@]} > 0 && attempt < MAX_RETRIES )); do
    attempt=$(( attempt + 1 ))
    log "INFO" "Starting attempt $attempt/$MAX_RETRIES for ${#pending_dests[@]} remaining destination(s)."
    log "INFO" "Restarting Tor to get a new IP address..."
    sudo systemctl restart tor
    sleep 3 # Give Tor a moment to establish a new circuit.

    local -a failed_this_round=()
    # Iterate over only the destinations that have not yet completed.
    for dest in "${pending_dests[@]}"; do
      log "INFO" "Downloading to: $dest"
      # We append all output (stdout and stderr) to the log file.
      if torsocks megadl --path "$dest" "$MEGA_URL" &>> "$LOG_FILE"; then
        log "SUCCESS" "Download to '$dest' completed."
      else
        local exit_code=$?
        log "WARN" "Download to '$dest' failed (exit code: $exit_code). Will retry."
        # If a download fails, add it to the list for the next round.
        failed_this_round+=("$dest")
      fi
    done

    # The new list of pending destinations is the list of failures from this round.
    pending_dests=( "${failed_this_round[@]}" )

    # If there are still pending downloads and we haven't reached the max retries, wait.
    if (( ${#pending_dests[@]} > 0 && attempt < MAX_RETRIES )); then
      log "WARN" "Waiting $RETRY_DELAY seconds before the next attempt..."
      sleep "$RETRY_DELAY"
    fi
  done

  # --- Final Status ---
  log "INFO" "--------------------------------------------------"
  if (( ${#pending_dests[@]} == 0 )); then
    log "SUCCESS" "All downloads completed successfully!"
    exit 0
  else
    log "ERROR" "Reached max retries ($MAX_RETRIES). The following downloads failed:"
    for dest in "${pending_dests[@]}"; do
      log "ERROR" "  - $dest"
    done
    log "ERROR" "Check the log file for details: $LOG_FILE"
    exit 2
  fi
}

# Run the main function, passing all script arguments to it.
main "$@"
