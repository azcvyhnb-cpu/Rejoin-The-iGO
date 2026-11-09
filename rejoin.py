#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
theIGO - Roblox Auto-Rejoin (Ultimate Edition)
แก้ปัญหา Error Code: 524 ไม่ยอมปิดแอป และแก้ปัญหาค้างหน้าโหลดก่อนเข้าหน้าหลัก Roblox
"""

import os
import re
import sys
import json
import time
import glob
import subprocess
from datetime import datetime

CONFIG_FILE = "/storage/emulated/0/Download/theigo_config.json"

DEFAULT_CONFIG = {
    "package_name": "com.roblox.client",
    "place_id": "",
    "private_server_code": "",
    "boot_timeout": 60,        # เวลารอโหลดเข้าแพลตฟอร์ม/เข้าแมพสูงสุด (วินาที) ถ้าเกินจะบังคับ Kill ทันที
    "heartbeat_timeout": 25,   # เวลารอสัญญาณชีพตอนอยู่ในแมพ (วินาที)
    "check_interval": 4,       # ความถี่ในการเช็คสถานะ (วินาที)
    "cooldown_after_kill": 6   # เวลาพักหลัง Kill แอป เพื่อเคลียร์เซสชันป้องกัน Error 524 (วินาที)
}

WORKSPACES = [
    "/storage/emulated/0/Delta/Workspace",
    "/storage/emulated/0/Fluxus/Workspace",
    "/storage/emulated/0/Codex/Workspace",
    "/storage/emulated/0/Arceus X/Workspace",
    "/storage/emulated/0/VegaX/Workspace",
    "/sdcard/Delta/Workspace",
    "/sdcard/Fluxus/Workspace",
    "/sdcard/Codex/Workspace",
    "/sdcard/Arceus X/Workspace"
]

class C:
    G = "\033[92m"
    Y = "\033[93m"
    R = "\033[91m"
    B = "\033[96m"
    W = "\033[0m"

def log(msg, color=C.W):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{now}] {msg}{C.W}")

def sh(cmd):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=12)
        return res.stdout.strip()
    except Exception:
        return ""

def parse_input_link(raw_input):
    """แยก Place ID และ Private Server Code อัตโนมัติหากผู้ใช้ว่างลิงก์เต็ม"""
    raw_input = raw_input.strip()
    place_match = re.search(r"games/(\d+)", raw_input) or re.search(r"placeId=(\d+)", raw_input, re.I)
    code_match = re.search(r"privateServerLinkCode=([a-zA-Z0-9_-]+)", raw_input, re.I) or re.search(r"linkCode=([a-zA-Z0-9_-]+)", raw_input, re.I)

    if place_match:
        pid = place_match.group(1)
        pcode = code_match.group(1) if code_match else ""
        return pid, pcode
    return raw_input, ""

def load_config():
    cfg = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                cfg.update(saved)
        except Exception:
            pass

    if not cfg.get("place_id"):
        print(f"{C.B}======================================================{C.W}")
        print(f"{C.G}         ตั้งค่าเริ่มต้น theIGO Auto-Rejoin             {C.W}")
        print(f"{C.B}======================================================{C.W}")
        raw_place = input("1. ใส่เลข Place ID (หรือวางลิงก์ VIP Server เต็มได้เลย): ").strip()
        pid, extracted_code = parse_input_link(raw_place)
        cfg["place_id"] = pid

        if extracted_code:
            cfg["private_server_code"] = extracted_code
            log(f"ดึงข้อมูลสำเร็จ -> Place ID: {pid} | VIP Code: {extracted_code}", C.G)
        else:
            ps = input("2. ใส่ Private Server Link Code (ถ้าเข้าเซิร์ฟธรรมดา กด Enter ข้าม): ").strip()
            cfg["private_server_code"] = ps

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
        print(f"{C.B}======================================================{C.W}\n")
    return cfg

def get_hb_path():
    for w in WORKSPACES:
        if os.path.exists(w):
            return os.path.join(w, "heartbeat.json")
    found = glob.glob("/storage/emulated/0/*/Workspace")
    if found:
        return os.path.join(found[0], "heartbeat.json")
    return "/storage/emulated/0/Delta/Workspace/heartbeat.json"

def is_app_running(pkg):
    return bool(sh(f"pidof {pkg}"))

def detect_ui_error():
    """
    สแกนข้อความบนหน้าจอ Android โดยตรงด้วย uiautomator
    ดักจับ Error Code: 524 และ Join Error ทันทีแม้สคริปต์ Lua ยังไม่ทำงาน
    """
    xml = sh("uiautomator dump /sdcard/theigo_ui.xml >/dev/null 2>&1 && cat /sdcard/theigo_ui.xml")
    if not xml:
        return False, ""
    error_patterns = [
        "Error Code: 524",
        "Join Error",
        "You do not have permission to join",
        "Error Code: 277",
        "Error Code: 267",
        "Error Code: 279",
        "Disconnected",
        "Connection attempt failed"
    ]
    for pat in error_patterns:
        if pat.lower() in xml.lower():
            return True, pat
    return False, ""

def force_kill_roblox(pkg, hb_path, cooldown=6):
    log(f"กำลังบังคับปิดแอป {pkg} และเคลียร์สถานะค้าง...", C.R)
    sh(f"am force-stop {pkg}")
    sh(f"killall -9 {pkg} 2>/dev/null")
    sh(f"pkill -9 -f {pkg} 2>/dev/null")

    # ลบไฟล์ Heartbeat เก่าทิ้งทั้งหมด เพื่อป้องกันเวลาเก่าค้างทำให้ไม่ยอมรีสตาร์ทตอนค้างหน้าโหลด
    folder = os.path.dirname(hb_path)
    for fname in ["heartbeat.json", "heartbeat.txt"]:
        fpath = os.path.join(folder, fname)
        if os.path.exists(fpath):
            try:
                os.remove(fpath)
            except Exception:
                sh(f"rm -f '{fpath}'")

    log(f"หน่วงเวลา {cooldown} วินาที ให้เซิร์ฟเวอร์เคลียร์เซสชัน (ป้องกัน Error 524)...", C.Y)
    time.sleep(cooldown)

def launch_roblox(pkg, place_id, ps_code=""):
    log("กำลังเปิดแอป Roblox และเชื่อมต่อเข้าสู่แมพ...", C.B)
    sh("input keyevent KEYCODE_WAKEUP")

    if str(place_id).startswith("http"):
        url = place_id
    elif ps_code:
        url = f"roblox://placeID={place_id}&linkCode={ps_code}"
    else:
        url = f"roblox://placeID={place_id}"

    sh(f"am start -W -a android.intent.action.VIEW -d '{url}' -f 0x10008000 {pkg}")

def check_heartbeat(hb_path):
    if not os.path.exists(hb_path):
        return False, 9999, "WAITING"
    try:
        age = time.time() - os.path.getmtime(hb_path)
        with open(hb_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        status = str(data.get("status", "UNKNOWN"))
        if status.startswith("ERROR"):
            return False, age, status
        return True, age, status
    except Exception:
        return False, 9999, "READ_ERR"

def main():
    os.system("clear")
    log("======================================================", C.B)
    log("     theIGO AUTO-REJOIN (FIX ERROR 524 & FREEZE)      ", C.G)
    log("======================================================", C.B)

    if "--reset" in sys.argv and os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
        log("รีเซ็ตการตั้งค่าเดิมเรียบร้อย!", C.Y)

    cfg = load_config()
    pkg = cfg["package_name"]
    place_id = cfg["place_id"]
    ps_code = cfg.get("private_server_code", "")
    boot_timeout = int(cfg.get("boot_timeout", 60))
    hb_timeout = int(cfg.get("heartbeat_timeout", 25))
    interval = int(cfg.get("check_interval", 4))
    cooldown = int(cfg.get("cooldown_after_kill", 6))

    hb_path = get_hb_path()
    log(f"ตรวจจับไฟล์สถานะที่: {hb_path}", C.G)
    log("หากต้องการเปลี่ยนแมพในรอบถัดไป ให้รัน: python ./rejoin.py --reset", C.Y)

    force_kill_roblox(pkg, hb_path, cooldown)
    launch_roblox(pkg, place_id, ps_code)

    boot_start = time.time()
    in_game = False
    loop_count = 0

    while True:
        time.sleep(interval)
        loop_count += 1

        # 1. เช็คว่าตัวแอป Roblox เด้งหลุดปิดตัวเองไปหรือไม่
        if not is_app_running(pkg):
            print()
            log("[!] ตรวจพบแอป Roblox ปิดตัวลงเอง! กำลังสั่งเปิดใหม่...", C.R)
            force_kill_roblox(pkg, hb_path, cooldown)
            launch_roblox(pkg, place_id, ps_code)
            boot_start = time.time()
            in_game = False
            continue

        # 2. อ่านไฟล์สถานะ Heartbeat จากในเกม
        alive, age, status = check_heartbeat(hb_path)

        if status.startswith("ERROR"):
            print()
            log(f"[!] ตรวจพบ Error จากในเกม ({status})! กำลัง Kill และเข้าใหม่ทันที...", C.R)
            force_kill_roblox(pkg, hb_path, cooldown)
            launch_roblox(pkg, place_id, ps_code)
            boot_start = time.time()
            in_game = False
            continue

        # 3. สแกนหน้าจอจับ Error 524 / Join Error ทุกๆ 3 รอบ (ประมาณ 12 วินาที)
        if (not in_game) and (loop_count % 3 == 0):
            has_ui_err, err_text = detect_ui_error()
            if has_ui_err:
                print()
                log(f"[!] ตรวจพบหน้าต่าง '{err_text}' ค้างบนหน้าจอ! สั่ง Kill แอปทันที...", C.R)
                force_kill_roblox(pkg, hb_path, cooldown)
                launch_roblox(pkg, place_id, ps_code)
                boot_start = time.time()
                in_game = False
                continue

        # 4. แยกเช็คเวลา Timeout ระหว่าง "กำลังโหลดเข้าแอป" กับ "อยู่ในแมพแล้ว"
        if alive and age <= hb_timeout:
            if not in_game:
                print()
                log("[✓] โหลดเข้าแมพสำเร็จ! ระบบเฝ้าระวัง theIGO ทำงานปกติ", C.G)
                in_game = True
            else:
                print(f"\r{C.G}[✓] สถานะปกติ | อัปเดตล่าสุดเมื่อ {int(age)} วินาทีที่แล้ว   {C.W}", end="")
        else:
            if not in_game:
                # ดักอาการค้างหน้าโหลดตอนกดเข้าแพลตฟอร์ม Roblox แล้วยังไม่ถึงหน้าหลัก/เข้าแมพไม่ได้
                elapsed_boot = int(time.time() - boot_start)
                print(f"\r{C.Y}[...] กำลังรอโหลดเข้าแพลตฟอร์ม/แมพ ({elapsed_boot}/{boot_timeout} วินาที)   {C.W}", end="")
                if elapsed_boot >= boot_timeout:
                    print()
                    log(f"[X] ค้างหน้าโหลดนานเกิน {boot_timeout} วินาที! สั่ง Kill แอปแล้วดึงเข้าใหม่...", C.R)
                    force_kill_roblox(pkg, hb_path, cooldown)
                    launch_roblox(pkg, place_id, ps_code)
                    boot_start = time.time()
                    in_game = False
            else:
                print()
                log(f"[X] เกมค้างหรือขาดการติดต่อเกิน {hb_timeout} วินาที! กำลัง Rejoin...", C.R)
                force_kill_roblox(pkg, hb_path, cooldown)
                launch_roblox(pkg, place_id, ps_code)
                boot_start = time.time()
                in_game = False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        log("หยุดการทำงานของ theIGO เรียบร้อย", C.Y)
        sys.exit(0)
