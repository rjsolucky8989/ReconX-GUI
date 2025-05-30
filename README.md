
# ReconX GUI – Automated Red‑Team Recon Engine

![ReconX](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Version](https://img.shields.io/badge/version-1.7.0--gui-blueviolet)

> GUI-based automated reconnaissance tool built for red teamers and penetration testers.

---

## 🚀 Features

- Modern PyQt5-based interface
- Supports 12 essential recon modules:
  - WHOIS
  - Subfinder
  - DNSRecon
  - dig
  - httpx
  - nuclei
  - nmap 
  - feroxbuster
- Multi-module execution with progress tracking
- Live output logging per tool
- Exported results with individual logs
- Dark theme UI
- Cross-platform with Linux-first compatibility

---

## 🖼️ GUI Preview

> ![Sample GUI Screenshot](https://via.placeholder.com/800x400.png?text=GUI+Screenshot+Placeholder)

---

## 🔧 Requirements

### 🐍 Python Version

- Python **3.8+** (recommended: Python 3.10 or later)

### 📦 Python Libraries

Install via pip:

```bash
pip install -r requirements.txt
```

**requirements.txt:**

```
PyQt5
termcolor
```

### 🔨 External Tools Required

Ensure the following recon tools are installed and in your system’s `$PATH`:

- `whois`
- `subfinder`
- `dnsrecon`
- `dig`
- `httpx`
- `nuclei`
- `nmap`
- `feroxbuster`

You can install them using package managers like `apt`, `brew`, or directly from their GitHub releases.

---

## 💻 Running the Tool

### Standard Usage

```bash
python3 reconx_gui1.py
```

### Headless (Server/No GUI)

```bash
xvfb-run -a python3 reconx_gui1.py
```

> ❗ If you're running on Linux without a GUI, you must use `xvfb-run`.

---

## 🧪 How to Use

1. **Set Target** – Use the “Set Target” button to input a domain or IP.
2. **Choose Modules** – Check one or more modules from the left panel.
3. **Run Recon** – Click "▶ Run" to start. Logs will display live output.
4. **View Results** – Output saved in a per-target directory.

---

## 📁 Output Format

- Output stored in: `results/<target>/`
- Each tool/module generates its own `.txt` file.
- Logs include the full command used and the complete stdout.

Example:
```
results/example.com/
├── 1_WHOIS.txt
├── 2_Subfinder.txt
├── 3_DNSRecon.txt
...
```

---

## 🛠 Recon Modules Used

| ID | Tool           | Purpose                                  |
|----|----------------|------------------------------------------|
| 1  | WHOIS          | Domain registration info                 |
| 2  | Subfinder      | Subdomain enumeration                    |
| 3  | DNSRecon       | DNS brute-forcing and records            |
| 4  | dig            | DNS information (ANY query)              |
| 5  | httpx          | HTTP probing and tech detection          |
| 6  | nuclei         | Template-based vulnerability scanning    |
| 7  | nmap (Full)    | Service detection + OS detection         |
| 8  | nmap (Vuln)    | Vulnerability scanning via NSE           |
| 9  | nmap (Enum)    | Enumeration for http/smtp                |
| 10 | nmap(FW Bypass)| Firewall evasion test                    |
| 11 | nmap (SSL)     | SSL cipher enumeration                   |
| 12 | feroxbuster    | Directory/file brute-forcing             |

---

## 📌 Notes

- The GUI will auto-detect if `$DISPLAY` is not set and warn the user.
- All results are saved with timestamps per module run.
- You can change the output directory using the "Change Output Dir" button.

---

## 👨‍💻 Author

**Rushi Solanki**  
Cyber Security Analyst & Consultant
📫 [solanki.rushi81@gmail.com](mailto:solanki.rushi81@gmail.com)

---

## 📄 License

This project is licensed under the **MIT License**.  
Feel free to use, modify, and share this tool with proper attribution.

---
