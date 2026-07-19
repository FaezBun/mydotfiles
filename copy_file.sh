#!/bin/bash

# --- SETTING ---
# Menggunakan $HOME/a untuk merujuk kepada ~/a/
SOURCE_DIR="$HOME/a/"
DEST_USER="f8un99"
DEST_IP="192.168.0.100"
DEST_DIR="/DATA/Media/Music"

echo "--- Memulakan hantaran lagu dari $SOURCE_DIR ke $DEST_IP... ---"

# Menggunakan $SOURCE_DIR sebagai punca data
rsync -rvz --no-g --no-p --ignore-existing \
    --temp-dir="$DEST_DIR" \
    --include="*/" \
    --include="**/*.flac" \
    --include="**/*.mp3" \
    --exclude="*" \
    "$SOURCE_DIR" "$DEST_USER@$DEST_IP:$DEST_DIR/"

if [ $? -eq 0 ]; then
    echo "--- ALHAMDULILLAH: Menjadi pun! ---"
else
    echo "--- MASIH ERROR? Cuba check password atau firewall. ---"
fi
