#!/bin/bash
clear
echo "=================================================="
echo "      กำลังติดตั้ง theIGO Auto-Rejoin (V2)          "
echo "=================================================="

# ขอสิทธิ์เข้าถึงพื้นที่จัดเก็บข้อมูล
termux-setup-storage
sleep 2

# อัปเดตแพ็กเกจของ Termux และลงเครื่องมือที่จำเป็น
pkg update -y && pkg upgrade -y
pkg install -y python curl tsu procps psmisc

# ตั้งค่าชื่อบัญชีและชื่อโปรเจกต์บน GitHub
GH_USER="azcvyhnb-cpu"
GH_REPO="Rejoin-The-IGO"
TARGET_DIR="/storage/emulated/0/Download"

mkdir -p "$TARGET_DIR"

echo "[+] กำลังดาวน์โหลดไฟล์จาก GitHub ($GH_USER/$GH_REPO)..."
curl -Ls "https://raw.githubusercontent.com/$GH_USER/$GH_REPO/main/requirements.txt" -o "$TARGET_DIR/requirements.txt"
curl -Ls "https://raw.githubusercontent.com/$GH_USER/$GH_REPO/main/rejoin.py" -o "$TARGET_DIR/rejoin.py"
curl -Ls "https://raw.githubusercontent.com/$GH_USER/$GH_REPO/main/Heartbeat.lua" -o "$TARGET_DIR/Heartbeat.lua"

# ติดตั้งไลบรารี Python
pip install -r "$TARGET_DIR/requirements.txt"

# คัดลอกไฟล์ Heartbeat.lua ไปยังโฟลเดอร์ Autoexecute ของ Executor ทุกค่ายอัตโนมัติ
for exec_dir in \
    "/storage/emulated/0/Delta/Autoexecute" \
    "/storage/emulated/0/Fluxus/Autoexecute" \
    "/storage/emulated/0/Codex/Autoexecute" \
    "/storage/emulated/0/Arceus X/Autoexecute" \
    "/storage/emulated/0/VegaX/Autoexecute" \
    "/sdcard/Delta/Autoexecute" \
    "/sdcard/Fluxus/Autoexecute" \
    "/sdcard/Codex/Autoexecute" \
    "/sdcard/Arceus X/Autoexecute"; do
    if [ -d "$exec_dir" ]; then
        cp -f "$TARGET_DIR/Heartbeat.lua" "$exec_dir/Heartbeat.lua"
        echo "[✓] คัดลอก Heartbeat.lua ไปยัง $exec_dir สำเร็จ!"
    fi
done

chmod +x "$TARGET_DIR/rejoin.py"

echo "=================================================="
echo "[✓] ติดตั้ง theIGO เสร็จสมบูรณ์พร้อมใช้งาน!"
echo "คัดลอกคำสั่งด้านล่างนี้ไปรันได้เลย:"
echo 'su -c "export PATH=$PATH:/data/data/com.termux/files/usr/bin && export TERM=xterm-256color && cd /storage/emulated/0/Download && python ./rejoin.py"'
echo "=================================================="
