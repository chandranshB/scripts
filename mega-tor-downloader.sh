#!/usr/bin/env bash
set -euo pipefail

# ——— Configurable defaults ———
MAX_RETRIES=10            # how many times to try before giving up
RETRY_DELAY=10            # seconds to sleep before retrying after a Tor restart
LOG_DIR="$HOME/Downloads/mega-tor-logs"

usage() {
  cat <<EOF
Usage: $0 [-u <MEGA_URL>] [-d <DEST_DIR>]... [-h]

Options:
  -u URL        MEGA public folder URL (e.g. https://mega.nz/folder/XYZ#key)
  -d DIR        Destination directory (can be passed multiple times)
  -r N          Max retries (default $MAX_RETRIES)
  -w SEC        Wait between retries (default $RETRY_DELAY)
  -h            Show this help and exit

If no -u or -d are provided, you will be prompted interactively.
EOF
  exit 1
}

# ——— Parse flags ———
declare -a DESTS=()
while getopts "u:d:r:w:h" opt; do
  case $opt in
    u) MEGA_URL="$OPTARG" ;;
    d) DESTS+=("$OPTARG") ;;
    r) MAX_RETRIES="$OPTARG" ;;
    w) RETRY_DELAY="$OPTARG" ;;
    h|*) usage ;;
  esac
done

# ——— Interactive prompts, if needed ———
if [ -z "${MEGA_URL-}" ]; then
  read -rp "🔗 Enter the MEGA public folder link: " MEGA_URL
fi
if [ "${#DESTS[@]}" -eq 0 ]; then
  read -rp "📦 Enter one or more download locations (space‑separated): " -a DESTS
fi

# ——— Prepare logs and destinations ———
mkdir -p "$LOG_DIR"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG_FILE="$LOG_DIR/mega-tor-$TIMESTAMP.log"

for dir in "${DESTS[@]}"; do
  mkdir -p "$dir"
done

echo "🧅 Starting Tor service..."
sudo systemctl start tor

# Trap CTRL‑C to clean up
cleanup() {
  echo -e "\n🛑 Interrupted. You can resume later."
  exit 1
}
trap cleanup SIGINT SIGTERM

attempt=0
while (( attempt < MAX_RETRIES )); do
  attempt=$(( attempt + 1 ))
  echo -e "\n🔄 [Attempt $attempt/$MAX_RETRIES] Trying new Tor route at $(date)"
  sudo systemctl restart tor
  sleep 2  # give Tor a moment to bootstrap

  # Download to each destination in turn
  for DEST in "${DESTS[@]}"; do
    echo "➡️  Downloading to: $DEST"
    torsocks megadl --path "$DEST" "$MEGA_URL" 2>&1 | tee -a "$LOG_FILE"
    exit_code=${PIPESTATUS[0]}

    if [ $exit_code -eq 0 ]; then
      echo "✅ Download succeeded to $DEST"
      # continue to next DEST, but if you only want one DEST, you can break here.
    else
      echo "❌ Download to $DEST failed (exit code $exit_code). See $LOG_FILE"
    fi
  done

  # Check if at least one ran cleanly
  if ! grep -Eq "exit code [1-9]" "$LOG_FILE"; then
    echo -e "\n🎉 All downloads completed successfully!"
    exit 0
  fi

  # If we hit a rate‑limit (509) or any other error, wait and retry
  echo "⚠️  Encountered errors. Waiting $RETRY_DELAY seconds before retry..."
  sleep "$RETRY_DELAY"
done

echo "🚨 Reached max retries ($MAX_RETRIES). Please check $LOG_FILE for details."
exit 2
