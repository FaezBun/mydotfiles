# Path : Dalam Music Dir
# Usage : Automation script untuk tolak file (music) ke dalam server 
# Pastikan dah install rsync

#!/bin/bash

# --- SETTING ---
DEST_USER="f8un99"                
DEST_IP="192.168.0.100"           
DEST_DIR="/DATA/Media/Music"      

echo "--- Memulakan hantaran lagu... ---"

# --no-g --no-p (supaya dia tak gaduh pasal owner/group lama)
# --temp-dir (paksa dia buat temp file dalam folder Music server)
rsync -rvz --no-g --no-p --ignore-existing \
    --temp-dir="$DEST_DIR" \
    --include="*/" \
    --include="**/*.flac" \
    --include="**/*.mp3" \
    --exclude="*" \
    ./ "$DEST_USER@$DEST_IP:$DEST_DIR/"

if [ $? -eq 0 ]; then
    echo "--- ALHAMDULILLAH: Menjadi pun! ---"
else
    echo "--- MASIH ERROR? Cuba check password atau firewall. ---"
fi
