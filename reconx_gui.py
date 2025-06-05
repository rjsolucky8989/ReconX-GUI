#!/usr/bin/env python3
"""
RECONX GUI – Automated Red‑Team Recon Engine
Version : 1.7.1‑gui (single‑file output)
Author  : Rushi Solanki | Cyber‑Security Analyst & Consultant
Contact : solanki.rushi81@gmail.com

Change‑log
----------
1.7.0 → 1.7.1
* Added single combined report instead of one file per module.
* Logo can be loaded from an external file (`logo.png`) with SVG fallback.
* Minor UI polish + version bump in window title.
"""

from __future__ import annotations
import sys, os, subprocess, base64, textwrap
from pathlib import Path

# ───────────────────────── GUI availability check ────────────────────────────
if os.name == "posix" and not os.environ.get("DISPLAY"):
    sys.stderr.write(
        "[!] $DISPLAY is not set – GUI cannot start.\n"  # noqa: E501
        "    Run inside a desktop session or prepend:\n"
        "    xvfb-run -a python reconx_gui.py\n"
    )
    sys.exit(1)

# ────────────────────────────── Qt / deps import ─────────────────────────────
try:
    from PyQt5.QtCore import Qt, QThread, pyqtSignal
    from PyQt5.QtGui import QPixmap, QIcon, QFont
    from PyQt5.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
        QPushButton, QListWidget, QListWidgetItem, QTextEdit,
        QFileDialog, QMessageBox, QProgressBar, QSplitter, QInputDialog
    )
except ImportError:
    sys.stderr.write("[!] PyQt5 not installed – run: python -m pip install PyQt5 termcolor\n")
    sys.exit(1)

from termcolor import colored

# ─────────────────────────────── Module catalog ──────────────────────────────
MODULES = {
    1: ("WHOIS",          "whois {target}"),
    2: ("WhatWeb",        "whatweb {target}"),
    3: ("Subfinder",      "subfinder -d {target} -silent"),
    4: ("DNSRecon",       "dnsrecon -d {target} -t brt"),
    5: ("dig",            "dig ANY {target} +noall +answer @8.8.8.8"),
    6: ("Nikto",          "nikto -h https://{target}"),
    7: ("httpx",          "httpx -u https://{target} -status-code -tech-detect"),
    8: ("Nuclei",         "nuclei -u https://{target} -severity critical,high,medium"),
    9: ("Nmap Full",      "nmap -T4 -A -sV -Pn {target}"),
   10: ("Nmap Vuln",      "nmap -T4 --script vuln {target}"),
   11: ("Nmap Enum",      "nmap -T4 --script http-enum,smtp-enum-users {target}"),
   12: ("Nmap FW‑Bypass", "nmap -T4 --script firewall-bypass {target}"),
   13: ("Nmap SSL",       "nmap -T4 --script ssl-enum-ciphers {target}"),
   14: ("dirb",           "dirb https://{target}"),
   15: ("feroxbuster",    "feroxbuster -u https://{target} -C 403,404"),
}
REQUIRED_TOOLS = [cmd.split()[0] for _, cmd in MODULES.values()]

# ──────────────────────────────── Logo handling ──────────────────────────────
LOGO_FILE = "logo_reconx.png"  # drop your image next to the script or adjust the path

_FALLBACK_SVG = (
    "PHN2ZyB3aWR0aD0iNjQiIGhlaWdodD0iNjQiIHZpZXdCb3g9IjAgMCA2NCA2NCIgZmlsbD0ibm9u"
    "ZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIzMiIgY3k9"
    "IjMyIiByPSIyOCIgZmlsbD0iI0ZGRiIvPjwvc3ZnPg=="
)

def _logo_pixmap() -> QPixmap:
    """Return a QPixmap built from LOGO_FILE (preferred) or fallback SVG."""
    px = QPixmap()
    img = Path(__file__).with_name(LOGO_FILE)
    if img.is_file():
        px.load(str(img))
    else:
        px.loadFromData(base64.b64decode(_FALLBACK_SVG))
    return px

# ────────────────────────────── Worker thread (Runner) ───────────────────────
class Runner(QThread):
    log      = pyqtSignal(str)
    progress = pyqtSignal(int)
    done_one = pyqtSignal(str, str)
    done_all = pyqtSignal(Path)

    def __init__(self, target: str, ids: list[int], outdir: Path):
        super().__init__()
        self.target = target
        self.ids = ids
        self.outdir = outdir

    def run(self):
        # Single combined output file for this run
        combined_path = self.outdir / f"{self.target.replace(':', '_')}_recon.txt"
        total = len(self.ids)
        with combined_path.open("w", encoding="utf-8", errors="ignore") as combo:
            combo.write(f"RECONX Combined Report – {self.target}\n")
            combo.write("=" * 80 + "\n\n")
            for idx, mid in enumerate(self.ids, 1):
                if mid not in MODULES:
                    msg = colored(f"[!] Skipping invalid module ID: {mid}", "red")
                    self.log.emit(msg)
                    combo.write(msg + "\n")
                    continue
                name, raw = MODULES[mid]
                cmd = raw.format(target=self.target)
                # ── Header per module ──
                header = f"[+] MODULE {mid} – {name}\nCOMMAND: {cmd}\n" + ("-" * 80) + "\n"
                self.log.emit("\n" + colored(header, "cyan"))
                combo.write(header)
                # ── Run the process ──
                proc = subprocess.Popen(cmd, shell=True, text=True,
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                for line in proc.stdout:
                    self.log.emit(line.rstrip())
                    combo.write(line)
                proc.wait()
                combo.write("\n" + ("=" * 80) + "\n\n")
                self.done_one.emit(name, str(combined_path))
                self.progress.emit(int(idx / total * 100))
        self.done_all.emit(combined_path)

# ──────────────────────────────── Main window UI ─────────────────────────────
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RECONX – v1.7.1")
        self.setWindowIcon(QIcon(_logo_pixmap()))
        self.resize(1100, 700)
        self.output_root = Path.cwd() / "results"
        self.output_root.mkdir(exist_ok=True)
        self._build_ui()
        self._apply_theme()
        self.target = None

    # ────────── UI construction ──────────
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)

        # Header (logo + title + output-dir button)
        hdr = QHBoxLayout()
        lbl_logo = QLabel()
        lbl_logo.setPixmap(_logo_pixmap().scaledToHeight(48, Qt.SmoothTransformation))
        lbl_title = QLabel("<b style='font-size:28px;'>RECONX</b><br/><small>Automated Red‑Team Recon Engine</small>")
        lbl_title.setTextFormat(Qt.RichText)
        hdr.addWidget(lbl_logo)
        hdr.addWidget(lbl_title, 1)
        hdr.addStretch()
        btn_out = QPushButton("Change Output Dir …")
        btn_out.clicked.connect(self.choose_outdir)
        hdr.addWidget(btn_out)
        layout.addLayout(hdr)

        # Splitter (module list | log panel)
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        layout.addWidget(splitter, 1)

        # Left: module checklist
        self.list = QListWidget()
        self.list.setSelectionMode(QListWidget.MultiSelection)
        for mid, (name, _) in MODULES.items():
            item = QListWidgetItem(f"[{mid}] {name}")
            item.setCheckState(Qt.Checked)
            self.list.addItem(item)
        self.list.setMinimumWidth(260)
        splitter.addWidget(self.list)

        # Right: target + log + progress
        right = QWidget()
        rlayout = QVBoxLayout(right)
        splitter.addWidget(right)

        # Target row
        trow = QHBoxLayout()
        self.lbl_target = QLabel("<i>Target not set</i>")
        self.lbl_target.setTextInteractionFlags(Qt.TextSelectableByMouse)
        btn_set = QPushButton("Set Target …")
        btn_set.clicked.connect(self.set_target)
        self.btn_run = QPushButton("▶ Run")
        self.btn_run.clicked.connect(self.on_run)
        trow.addWidget(self.lbl_target, 1)
        trow.addWidget(btn_set)
        trow.addWidget(self.btn_run)
        rlayout.addLayout(trow)

        # Log panel
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setLineWrapMode(QTextEdit.NoWrap)
        self.log.document().setDefaultFont(QFont("Consolas", 10))
        rlayout.addWidget(self.log, 1)

        # Progress bar
        self.pb = QProgressBar()
        self.pb.setValue(0)
        rlayout.addWidget(self.pb)

    # ────────── Helpers ──────────
    def set_target(self):
        target, ok = QInputDialog.getText(self, "Set Target", "Enter domain or IP:")
        if ok and target:
            self.target = target.strip()
            self.lbl_target.setText(f"<b>Target:</b> {self.target}")

    def choose_outdir(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory", str(self.output_root))
        if path:
            self.output_root = Path(path)

    def on_run(self):
        if not self.target:
            QMessageBox.warning(self, "Target Required", "Please set a target before running.")
            return
        mids = [i for i in range(self.list.count()) if self.list.item(i).checkState() == Qt.Checked]
        if not mids:
            QMessageBox.warning(self, "Select Modules", "Please select at least one module.")
            return
        outdir = self.output_root / self.target.replace(":", "_")
        outdir.mkdir(parents=True, exist_ok=True)
        self.log.clear(); self.pb.setValue(0)
        self.runner = Runner(self.target, [i+1 for i in mids], outdir)
        self.runner.log.connect(self.log.append)
        self.runner.progress.connect(self.pb.setValue)
        self.runner.done_all.connect(lambda p: QMessageBox.information(self, "Finished", f"All modules completed.Report: {p}"))
        self.runner.start()

    # ────────── Theme ──────────
    def _apply_theme(self):
        self.setStyleSheet(textwrap.dedent("""
            * { background:#1e1e1e; color:#dcdcdc; font-family:Arial,Helvetica,sans-serif; }
            QPushButton { background:#333; border:1px solid #444; padding:6px 12px; }
            QPushButton:hover { background:#444; }
            QPushButton:disabled { background:#555; color:#888; }
            QTextEdit, QListWidget { background:#121212; }
            QProgressBar { background:#121212; border:1px solid #444; text-align:center; }
        """))

# ────────────────────────────── Application entry ────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())