# theIGO - Roblox Auto-Rejoin (Ultimate Edition)

ระบบ Auto-Rejoin สำหรับ Roblox บน Android (Termux + Root) แก้ปัญหาค้างหน้าโหลดและตรวจจับ Error 524 อัตโนมัติ

## คุณสมบัติเด่น
- **ตรวจจับ Error 524 ทันที:** สแกนหน้าจอและสถานะในเกม หากขึ้น `Join Error (Error Code: 524)` จะสั่งบังคับปิดแอป (Force Stop + Kill) และหน่วงเวลาเคลียร์เซสชันก่อนเข้าใหม่อัตโนมัติ
- **แก้ค้างหน้าโหลดก่อนเข้าหน้าหลัก:** มีระบบจับเวลาแยกช่วงเปิดแอป (`boot_timeout`) หากค้างหน้าโลโก้หรือหมุนเข้าเกมไม่ได้เกินเวลาที่กำหนด จะรีสตาร์ทแอปให้ทันที
- **รองรับลิงก์ VIP Server เต็มรูปแบบ:** ใส่ได้ทั้งเลข Place ID, โค้ด Private Server หรือวางลิงก์ VIP Server แบบเต็มได้เลย

---

## คำสั่งติดตั้งและรันใช้งาน (Termux)

### 1. เปลี่ยน Repository ของ Termux (ทำเฉพาะครั้งแรก)
```bash
termux-change-repo
curl -Ls [https://raw.githubusercontent.com/Garnt024020806/theIGO/main/setup.sh](https://raw.githubusercontent.com/Garnt024020806/theIGO/main/setup.sh) | bash
su -c "export PATH=$PATH:/data/data/com.termux/files/usr/bin && export TERM=xterm-256color && cd /storage/emulated/0/Download && python ./rejoin.py"

---

### ไฟล์ที่ 2: `requirements.txt`[span_10](start_span)[span_10](end_span)

```text
requests>=2.31.0
colorama>=0.4.6
