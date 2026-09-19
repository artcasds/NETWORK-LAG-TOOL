<p align="center">
  <img src="bener.jpg" width="100%" alt="Network Lag Tool"/>
</p>

<h1 align="center">⚡ NETWORK LAG TOOL</h1>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20Termux-green?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/license-MIT-red?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/version-1.0-orange?style=for-the-badge"/>
</p>

<p align="center">
  Multi-protocol network stress testing tool with device scanning, vendor identification, and real-time packet monitoring.
</p>

---

## ⚙️ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Network Scan** | Scan entire /24 subnet, detect live hosts, open ports, MAC vendor, and device names |
| 📡 **UDP Flood** | High-speed UDP packet flooding with 20 threads |
| 🔵 **ICMP Flood** | Raw socket ICMP ping flood |
| 🔴 **TCP SYN Flood** | Half-open connection flood |
| 🌐 **HTTP Flood** | HTTP GET request spam with randomized User-Agent |
| ⚡ **Multi-Protocol** | All attack modes simultaneously |
| 🎲 **Custom Packet** | Random payload UDP+TCP mixed flood |
| 🏷️ **MAC Vendor Lookup** | Identify device manufacturer from MAC address |
| 📛 **Device Name Resolution** | NetBIOS + DNS hostname detection |
| 🎨 **Braille ASCII Art** | Custom braille terminal banner |

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/network-lag-tool.git
cd network-lag-tool

# Install dependencies
pip install -r requirements.txt

# Run
python network_lag.py
```

### Termux (Android)

```bash
pkg install python
pip install colorama
python network_lag.py
```

## 🚀 Usage

```
  [x] select option : 01    ← Network Scan
  [x] select option : 02    ← UDP Flood
  [x] select option : 05    ← HTTP Flood
  [x] select option : 00    ← Exit
```

### Scan Output Example

```
  SCAN RESULT
  Subnet  : 192.168.1.0/24
  Local   : 192.168.1.4 (ini IP lo)

  192.168.1.1  [ROUTER] 38:E1:AA:68:08:79
    53/tcp  DNS
    80/tcp  HTTP
    443/tcp  HTTPS
  192.168.1.2  46:26:1E:1A:91:40
    no port open
  192.168.1.3  Samsung Galaxy S24  CA:6D:19:53:F0:5B
    no port open

  Total   : 3 host aktif
```

## 📋 Menu

| Code | Mode | Description |
|------|------|-------------|
| `01` | Scan IP | Scan subnet + device info (name, vendor, ports) |
| `02` | UDP Flood | Random UDP packets to target |
| `03` | ICMP Flood | Raw socket ping flood (requires admin) |
| `04` | TCP SYN Flood | Half-open TCP connection flood |
| `05` | HTTP Flood | HTTP GET request spam |
| `06` | Multi-Protocol | All modes simultaneously |
| `07` | Custom Packet | Random UDP+TCP mixed payload |
| `00` | Exit | Quit |

## 🛡️ Supported MAC Vendors

| Vendor | Devices |
|--------|---------|
| Apple | iPhone, Mac, iPad, AirPods |
| Samsung | Galaxy series, Smart TV |
| Xiaomi | Redmi, POCO, Mi series |
| Huawei | phones, routers |
| TP-Link | routers, adapters |
| Asus | routers, ROG series |
| Sony | PlayStation, Xperia |
| Oppo | Find, Reno series |
| VMware | virtual machines |
| Raspberry Pi | SBC devices |

## ⚡ Cross-Platform

| Feature | Windows | Linux | Termux |
|---------|---------|-------|--------|
| All flood modes | ✅ | ✅ | ✅ |
| Network scan | ✅ | ✅ | ✅ |
| MAC vendor lookup | ✅ | ✅ | ✅ |
| NetBIOS name | ✅ | ❌ | ✅ |
| ICMP raw socket | admin only | root | root |

## ⚠️ Disclaimer

This tool is for **authorized network testing only**. Use only on networks and devices you own or have explicit permission to test. Unauthorized use is illegal.

## 📄 License

MIT License — do whatever you want.

---

<p align="center">
  Made with 💀 by <a href="https://github.com/artcasds">YOGGS</a>
</p>
