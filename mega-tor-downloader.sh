#!/bin/bash
set -euo pipefail

# ========== CONFIG ==========
MEGA_URL="https://mega.nz/folder/<YOUR-FOLDER-NAEM> also, the decryption key is required too. the text after #"
DEST_DIR="$HOME/Downloads/mega-tor"
LOG_FILE="tor-mega.log"
# ============================

echo "Follow me on https://github.com/chandranshB"

mkdir -p "$DEST_DIR"

echo "📦 Download location: $DEST_DIR"
echo "e Starting Tor service..."
sudo systemctl start tor

function download_with_tor() {
  echo -e "\n🔄 Trying new Tor route at $(date)..."
  torsocks megadl --path "$DEST_DIR" "$MEGA_URL" 2>&1 | tee "$LOG_FILE"
}

while true; do
  download_with_tor

  if grep -q "509" "$LOG_FILE"; then
    echo "⚠️  Hit MEGA 509 quota, restarting Tor to get a new IP..."
    sudo systemctl restart tor
    sleep 10
  else
    echo "✅ Download completed or exited without rate limit."
    break
  fi
done

echo -e "\n🎉 All done! Files saved to: $DEST_DIR"
