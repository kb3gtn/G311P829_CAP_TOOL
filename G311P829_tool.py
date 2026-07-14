#!/usr/bin/env python3
"""
NASA S-311-P-829 Rev. M  —  G311P829 / Presidio SR Capacitor PIN Tool
PySide6 GUI  |  Python 3.8+ compatible  |  Windows safe stylesheet
"""

import sys
import re
import traceback
from typing import Optional, Tuple, Dict, List

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QComboBox, QLineEdit, QPushButton, QTextEdit,
    QGroupBox, QMessageBox, QRadioButton,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor, QPalette

# ---------------------------------------------------------------------------
# Colour palette  (referenced by name so the QSS builder stays readable)
# ---------------------------------------------------------------------------
DARK = {
    "bg":            "#1E1E2E",
    "bg_alt":        "#252535",
    "bg_input":      "#2A2A3E",
    "bg_group":      "#252535",
    "border":        "#44445A",
    "border_focus":  "#6E8EFF",
    "text":          "#CDD6F4",
    "text_dim":      "#888AAA",
    "accent":        "#6E8EFF",
    "success":       "#A6E3A1",
    "success_bg":    "#1E3A1E",
    "success_bdr":   "#4CAF50",
    "warn":          "#F9A825",
    "error":         "#F38BA8",
    "field_ok_bg":   "#1A2E1A",
    "field_ok_bdr":  "#4CAF50",
    "field_ok_txt":  "#A6E3A1",
    "field_er_bg":   "#2E1A1A",
    "field_er_bdr":  "#CF6679",
    "field_er_txt":  "#F38BA8",
    "field_def_bg":  "#2A2A3E",
    "field_def_bdr": "#44445A",
    "field_def_txt": "#CDD6F4",
    "tab_bg":        "#1A1A2A",
    "tab_sel":       "#2A2A3E",
    "header_bg":     "#0A0A1A",
    "btn_bg":        "#3D3D5C",
    "btn_hover":     "#5050AA",
    "btn_text":      "#FFFFFF",
    "btn_accent_bg": "#4455BB",
    "btn_accent_hv": "#6E8EFF",
    "btn_copy_bg":   "#1E4A2E",
    "btn_copy_hv":   "#2A6E40",
    "presidio_acc":  "#FFB86C",
    "presidio_bg":   "#2E2218",
    "presidio_bdr":  "#A0621E",
}

# ---------------------------------------------------------------------------
# Build stylesheet using str.format() — avoids f-string / brace conflicts
# ---------------------------------------------------------------------------
def _build_stylesheet():
    """Return the full application QSS stylesheet."""
    # Use a plain string with {0} style substitutions only where colour
    # values are needed.  All CSS braces are written as literal { } here
    # because we call .format() with keyword args that don't clash.
    c = DARK
    parts = []

    def rule(selector, body):
        parts.append(selector + " {\n" + body + "\n}")

    rule("QMainWindow, QWidget",
         "background-color: {bg}; color: {text};\n"
         "font-family: 'Segoe UI', Arial, sans-serif; font-size: 9pt;".format(**c))

    rule("QGroupBox",
         "background-color: {bg_group}; border: 1px solid {border};\n"
         "border-radius: 6px; margin-top: 10px; padding-top: 6px;\n"
         "font-weight: bold; color: {accent};".format(**c))

    rule("QGroupBox::title",
         "subcontrol-origin: margin; subcontrol-position: top left;\n"
         "padding: 0 6px; left: 10px;")

    rule("QLabel",
         "color: {text}; background: transparent;".format(**c))

    rule("QLineEdit",
         "background-color: {bg_input}; color: {text};\n"
         "border: 1px solid {border}; border-radius: 4px;\n"
         "padding: 4px 8px;\n"
         "selection-background-color: {accent};".format(**c))

    rule("QLineEdit:focus",
         "border: 1px solid {border_focus};".format(**c))

    rule("QComboBox",
         "background-color: {bg_input}; color: {text};\n"
         "border: 1px solid {border}; border-radius: 4px;\n"
         "padding: 4px 8px; min-height: 24px;".format(**c))

    rule("QComboBox:focus",
         "border: 1px solid {border_focus};".format(**c))

    rule("QComboBox::drop-down",
         "border: none; width: 20px;")

    rule("QComboBox::down-arrow",
         "width: 10px; height: 10px; image: none;\n"
         "border-left: 4px solid transparent;\n"
         "border-right: 4px solid transparent;\n"
         "border-top: 6px solid {text};".format(**c))

    rule("QComboBox QAbstractItemView",
         "background-color: {bg_alt}; color: {text};\n"
         "border: 1px solid {border};\n"
         "selection-background-color: {accent};\n"
         "selection-color: white; outline: none;".format(**c))

    rule("QPushButton",
         "background-color: {btn_bg}; color: {btn_text};\n"
         "border: 1px solid {border}; border-radius: 4px;\n"
         "padding: 6px 16px; font-weight: bold;".format(**c))

    rule("QPushButton:hover",
         "background-color: {btn_hover}; border-color: {accent};".format(**c))

    rule("QPushButton:pressed",
         "background-color: {accent};".format(**c))

    rule("QPushButton#accent",
         "background-color: {btn_accent_bg}; border-color: {accent};\n"
         "color: white;".format(**c))

    rule("QPushButton#accent:hover",
         "background-color: {btn_accent_hv};".format(**c))

    rule("QPushButton#copy",
         "background-color: {btn_copy_bg}; border-color: {success_bdr};\n"
         "color: {success};".format(**c))

    rule("QPushButton#copy:hover",
         "background-color: {btn_copy_hv};".format(**c))

    rule("QPushButton#copy:disabled",
         "background-color: {bg_alt}; border-color: {border};\n"
         "color: {text_dim};".format(**c))

    rule("QPushButton#copy_sr",
         "background-color: {presidio_bg}; border-color: {presidio_bdr};\n"
         "color: {presidio_acc};".format(**c))

    rule("QPushButton#copy_sr:hover",
         "background-color: #3E2E18;")

    rule("QPushButton#copy_sr:disabled",
         "background-color: {bg_alt}; border-color: {border};\n"
         "color: {text_dim};".format(**c))

    rule("QTextEdit",
         "background-color: {bg_input}; color: {text};\n"
         "border: 1px solid {border}; border-radius: 4px;\n"
         "padding: 4px;".format(**c))

    rule("QTabWidget::pane",
         "border: 1px solid {border}; border-radius: 4px;\n"
         "background-color: {bg};".format(**c))

    rule("QTabBar::tab",
         "background-color: {tab_bg}; color: {text_dim};\n"
         "border: 1px solid {border}; border-bottom: none;\n"
         "padding: 8px 20px; border-top-left-radius: 4px;\n"
         "border-top-right-radius: 4px; margin-right: 2px;".format(**c))

    rule("QTabBar::tab:selected",
         "background-color: {tab_sel}; color: {accent};\n"
         "border-bottom: 2px solid {accent};\n"
         "font-weight: bold;".format(**c))

    rule("QTabBar::tab:hover:!selected",
         "background-color: {bg_alt}; color: {text};".format(**c))

    rule("QRadioButton",
         "color: {text}; spacing: 6px;".format(**c))

    rule("QRadioButton::indicator",
         "width: 14px; height: 14px; border-radius: 7px;\n"
         "border: 2px solid {border};\n"
         "background: {bg_input};".format(**c))

    rule("QRadioButton::indicator:checked",
         "background: {accent}; border-color: {accent};".format(**c))

    rule("QScrollBar:vertical",
         "background: {bg_alt}; width: 10px; border-radius: 5px;".format(**c))

    rule("QScrollBar::handle:vertical",
         "background: {border}; border-radius: 5px; min-height: 20px;".format(**c))

    rule("QScrollBar::handle:vertical:hover",
         "background: {accent};".format(**c))

    rule("QScrollBar::add-line:vertical",
         "height: 0px;")

    rule("QScrollBar::sub-line:vertical",
         "height: 0px;")

    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# GSFC PIN data tables
# ---------------------------------------------------------------------------
GSFC_IDENTIFIER  = "G311P829"
ULTRASONIC       = {"A": "100% Ultrasonic Examination"}

SIZE_CODES: Dict[str, str] = {
    "A": "0402", "B": "0403", "C": "0504", "D": "0603",
    "E": "0805", "F": "1206", "G": "1209", "H": "1725",
    "J": "2225", "K": "1712", "L": "0502", "M": "0306",
    "N": "0508", "P": "0612", "Q": "0912", "R": "1812",
    "S": "1210", "T": "1825", "U": "0201",
}
SIZE_CODES_INV   = {v: k for k, v in SIZE_CODES.items()}
NO_MARKING_SIZES = {"A", "B", "C", "D", "L", "M", "N", "P", "U"}

DIELECTRIC_TYPES: Dict[str, str] = {
    "N": "NPO  (0 \u00b130 ppm/\u00b0C, -55\u00b0C to +125\u00b0C)",
    "X": "X7R  (\u00b115%, -55\u00b0C to +125\u00b0C)",
}

TOLERANCE_CODES: Dict[str, str] = {
    "A": "\u00b10.05 pF  [NPO, <10 pF only]",
    "B": "\u00b10.10 pF  [NPO, <10 pF only]",
    "C": "\u00b10.25 pF  [NPO, <10 pF only]",
    "D": "\u00b10.50 pF  [NPO, <10 pF only]",
    "F": "\u00b11%       [NPO, \u226510 pF only]",
    "G": "\u00b12%       [NPO, \u226510 pF only]",
    "J": "\u00b15%       [NPO, \u226510 pF only]",
    "K": "\u00b110%      [NPO/X7R, \u226510 pF]",
    "L": "+20%/-10% [NPO/X7R, \u226510 pF]",
}

VOLTAGE_CODES: Dict[str, str] = {
    "1": "25 V", "2": "50 V", "3": "100 V",
    "4": "5 V",  "5": "10 V", "6": "16 V",
    "7": "6.3 V","8": "4 V",
}

TERMINATION_CODES: Dict[str, str] = {
    "P": "PdAg alloy (conductive epoxy only)",
    "N": "Ni-Sn/Pb Plated (soldering OK)",
    "G": "Ag-Ni-Au plated (wire bond OK)",
    "H": "Gold, Thick Film (conductive epoxy / wire bond)",
}

PACKAGING_CODES: Dict[str, str] = {
    "1": '7" Tape & Reel, Unmarked',
    "2": '7" Tape & Reel, Marked',
    "3": "Waffle Pack, Unmarked",
    "4": "Waffle Pack, Marked",
}

# ---------------------------------------------------------------------------
# Presidio SR translation maps
# ---------------------------------------------------------------------------
PRESIDIO_VOLT: Dict[str, str] = {
    "8": "A",  # 4 V
    "4": "B",  # 5 V
    "7": "C",  # 6.3 V
    "5": "E",  # 10 V
    "6": "F",  # 16 V
    "1": "G",  # 25 V
    "2": "H",  # 50 V
    "3": "J",  # 100 V
}

PRESIDIO_DIEL: Dict[str, str] = {"N": "NPO", "X": "X7R"}

PRESIDIO_TOL: Dict[str, str] = {
    k: k for k in ("A", "B", "C", "D", "F", "G", "J", "K", "L")
}

PRESIDIO_TERM: Dict[str, str] = {
    "P": "P",
    "N": "NT9",
    "G": "NG",
    "H": "H",
}

PRESIDIO_PKG: Dict[str, str] = {
    "1": "1", "2": "1",
    "3": "9", "4": "9",
}


def build_presidio_pn(size_code, diel_code, cap_code,
                      tol_code, volt_code, term_code,
                      pkg_code):
    # type: (str,str,str,str,str,str,str) -> Tuple[str, List[str]]
    notes     = []
    size_str  = SIZE_CODES.get(size_code, size_code)
    diel_str  = PRESIDIO_DIEL.get(diel_code, diel_code)
    volt_str  = PRESIDIO_VOLT.get(volt_code)
    term_str  = PRESIDIO_TERM.get(term_code)
    pkg_str   = PRESIDIO_PKG.get(pkg_code, "1")
    tol_str   = PRESIDIO_TOL.get(tol_code, tol_code)

    if volt_str is None:
        notes.append("Voltage code '{}' has no Presidio equivalent.".format(volt_code))
        volt_str = "?"
    if term_str is None:
        notes.append("Termination code '{}' has no Presidio equivalent.".format(term_code))
        term_str = "?"

    pn = "SR{}{}{}{}{}{}{}\u0023M123A".format(
        size_str, diel_str, cap_code, tol_str, volt_str, term_str, pkg_str)
    return pn, notes


# ---------------------------------------------------------------------------
# Presidio SR-M123A max capacitance table
# ---------------------------------------------------------------------------
def _uf(v):
    return v * 1_000_000.0


# (GSFC size letter, GSFC voltage code) : (NPO_max_pF, X7R_max_pF)
# None = Not Available
TABLE_PRESIDIO: Dict[Tuple[str, str], Tuple] = {
    ("U", "8"): (None,          _uf(0.022)),
    ("U", "5"): (100.0,         _uf(0.010)),
    ("A", "8"): (None,          _uf(0.22)),
    ("A", "5"): (390.0,         _uf(0.10)),
    ("A", "6"): (200.0,         _uf(0.033)),
    ("A", "1"): (120.0,         4700.0),
    ("A", "2"): (100.0,         4700.0),
    ("A", "3"): (39.0,          4700.0),
    ("B", "5"): (1200.0,        _uf(0.047)),
    ("B", "6"): (560.0,         _uf(0.022)),
    ("B", "1"): (390.0,         _uf(0.015)),
    ("B", "2"): (330.0,         _uf(0.012)),
    ("B", "3"): (68.0,          2200.0),
    ("L", "7"): (None,          _uf(0.10)),
    ("C", "5"): (2700.0,        _uf(0.082)),
    ("C", "6"): (1800.0,        _uf(0.082)),
    ("C", "1"): (1500.0,        _uf(0.047)),
    ("C", "2"): (1200.0,        _uf(0.039)),
    ("C", "3"): (180.0,         6800.0),
    ("M", "4"): (None,          _uf(0.10)),
    ("M", "6"): (None,          _uf(0.10)),
    ("M", "1"): (None,          _uf(0.022)),
    ("D", "5"): (2200.0,        _uf(0.22)),
    ("D", "6"): (1000.0,        _uf(0.22)),
    ("D", "1"): (680.0,         _uf(0.18)),
    ("D", "2"): (560.0,         _uf(0.022)),
    ("D", "3"): (100.0,         _uf(0.018)),
    ("N", "7"): (None,          _uf(0.18)),
    ("N", "5"): (None,          _uf(0.12)),
    ("N", "6"): (None,          _uf(0.10)),
    ("N", "1"): (None,          _uf(0.047)),
    ("E", "5"): (4700.0,        _uf(1.0)),
    ("E", "6"): (3300.0,        _uf(0.22)),
    ("E", "1"): (2700.0,        _uf(0.10)),
    ("E", "2"): (2200.0,        _uf(0.10)),
    ("E", "3"): (560.0,         _uf(0.10)),
    ("P", "6"): (None,          _uf(0.27)),
    ("P", "1"): (None,          _uf(0.22)),
    ("F", "5"): (_uf(0.012),    _uf(1.8)),
    ("F", "6"): (8200.0,        _uf(0.39)),
    ("F", "1"): (6800.0,        _uf(0.27)),
    ("F", "2"): (5600.0,        _uf(0.22)),
    ("F", "3"): (1500.0,        _uf(0.10)),
    ("Q", "6"): (None,          _uf(0.68)),
    ("Q", "1"): (None,          _uf(0.47)),
    ("G", "5"): (_uf(0.018),    _uf(2.7)),
    ("G", "6"): (_uf(0.012),    _uf(0.68)),
    ("G", "1"): (_uf(0.010),    _uf(0.47)),
    ("G", "2"): (8200.0,        _uf(0.39)),
    ("G", "3"): (3900.0,        _uf(0.15)),
    ("S", "5"): (_uf(0.018),    _uf(2.7)),
    ("S", "6"): (_uf(0.012),    _uf(0.68)),
    ("S", "1"): (_uf(0.010),    _uf(0.47)),
    ("S", "2"): (8200.0,        _uf(0.39)),
    ("S", "3"): (3900.0,        _uf(0.15)),
    ("K", "6"): (_uf(0.027),    _uf(1.2)),
    ("K", "1"): (_uf(0.022),    _uf(1.0)),
    ("K", "2"): (_uf(0.015),    _uf(0.68)),
    ("K", "3"): (6800.0,        _uf(0.27)),
    ("R", "5"): (None,          _uf(4.7)),
    ("R", "6"): (None,          _uf(1.2)),
    ("R", "1"): (_uf(0.022),    _uf(1.0)),
    ("R", "2"): (_uf(0.015),    _uf(0.68)),
    ("R", "3"): (6800.0,        _uf(0.27)),
    ("H", "6"): (_uf(0.068),    _uf(3.3)),
    ("H", "1"): (_uf(0.056),    _uf(2.2)),
    ("H", "2"): (_uf(0.039),    _uf(2.2)),
    ("H", "3"): (_uf(0.018),    _uf(0.68)),
    ("T", "6"): (_uf(0.068),    _uf(3.3)),
    ("T", "1"): (_uf(0.056),    _uf(2.2)),
    ("T", "2"): (_uf(0.039),    _uf(1.8)),
    ("T", "3"): (_uf(0.018),    _uf(0.68)),
    ("J", "6"): (_uf(0.082),    _uf(3.9)),
    ("J", "1"): (_uf(0.068),    _uf(3.3)),
    ("J", "2"): (_uf(0.056),    _uf(2.2)),
    ("J", "3"): (_uf(0.027),    _uf(1.0)),
}


def get_max_capacitance(size_code, volt_code, diel_code):
    # type: (str, str, str) -> Optional[float]
    """Returns max pF, None (NA), or -1.0 (combo not in table)."""
    key = (size_code, volt_code)
    if key not in TABLE_PRESIDIO:
        return -1.0
    npo_max, x7r_max = TABLE_PRESIDIO[key]
    return npo_max if diel_code == "N" else x7r_max


def check_capacitance_vs_table(size_code, volt_code, diel_code, cap_pf):
    # type: (str, str, str, float) -> Tuple[bool, str]
    max_pf   = get_max_capacitance(size_code, volt_code, diel_code)
    size_str = SIZE_CODES.get(size_code, size_code)
    volt_str = VOLTAGE_CODES.get(volt_code, volt_code)
    diel_str = "NPO" if diel_code == "N" else "X7R"
    if max_pf == -1.0:
        return (False,
                "{}/{} not listed in Presidio SR table.".format(size_str, volt_str))
    if max_pf is None:
        return (False,
                "{} not available for {}/{} (Presidio SR).".format(
                    diel_str, size_str, volt_str))
    if cap_pf > max_pf:
        return (False,
                "{} exceeds Presidio SR max of {} for {}/{}/{}.".format(
                    _pf_human(cap_pf), _pf_human(max_pf),
                    diel_str, size_str, volt_str))
    return (True,
            "OK \u2014 within Presidio SR limit of {} for {}/{}/{}.".format(
                _pf_human(max_pf), diel_str, size_str, volt_str))


# ---------------------------------------------------------------------------
# Capacitance helpers
# ---------------------------------------------------------------------------
def _pf_human(pf):
    # type: (float) -> str
    if pf >= 1_000_000:
        return "{:g} \u00b5F".format(pf / 1_000_000)
    if pf >= 1_000:
        return "{:g} nF".format(pf / 1_000)
    return "{:g} pF".format(pf)


def _decode_eia(code):
    # type: (str) -> Tuple[str, Optional[float]]
    code = code.strip().upper()
    try:
        if "R" in code:
            parts = code.split("R")
            pf = float("{}.{}".format(parts[0] or "0", parts[1] or "0"))
            return (code, pf)
        if len(code) < 2:
            return (code, None)
        return (code, float(int(code[:-1]) * (10 ** int(code[-1]))))
    except Exception:
        return (code, None)


def pf_to_eia_code(value_pf):
    # type: (float) -> Tuple[str, str]
    if value_pf <= 0:
        raise ValueError("Capacitance must be > 0.")
    if value_pf < 10.0:
        formatted = "{:.2f}".format(value_pf).rstrip("0")
        if formatted.endswith("."):
            formatted += "0"
        code = formatted.replace(".", "R")
        return (code, "{:g} pF -> [{}]".format(value_pf, code))
    for exp in range(0, 13):
        mantissa = value_pf / (10 ** exp)
        if 10.0 <= mantissa < 100.0:
            sig = round(mantissa)
            if sig == 100:
                sig, exp = 10, exp + 1
            if abs(sig * (10 ** exp) - value_pf) / value_pf < 0.005:
                code = "{:02d}{}".format(sig, exp)
                return (code, "{} -> [{}]".format(_pf_human(value_pf), code))
    raise ValueError("Cannot represent {:g} pF in EIA 3-digit format.".format(value_pf))


def parse_value_string(text):
    # type: (str) -> Tuple[float, str]
    text = text.strip()
    if re.match(r"^[0-9R]+$", text.upper()) and "R" in text.upper():
        _, pf = _decode_eia(text.upper())
        if pf is not None:
            return (pf, "EIA code")
        raise ValueError("Cannot parse R-notation: '{}'".format(text))
    m = re.match(r"^([0-9]*\.?[0-9]+)\s*(pf|nf|uf|µf)?$", text, re.IGNORECASE)
    if not m:
        if re.match(r"^\d{2,4}$", text):
            _, pf = _decode_eia(text)
            if pf is not None:
                return (pf, "EIA code")
        raise ValueError(
            "Cannot parse '{}'.\nExamples: 100, 100pF, 0.1uF, 4.7nF, 1R0, R75".format(text))
    num  = float(m.group(1))
    unit = (m.group(2) or "pf").lower().replace("\u00b5", "u")
    if unit in ("pf", ""):
        return (num, "pF")
    if unit == "nf":
        return (num * 1_000.0, "nF")
    if unit == "uf":
        return (num * 1_000_000.0, "\u00b5F")
    raise ValueError("Unknown unit: '{}'".format(unit))


def parse_capacitance_code(code):
    # type: (str) -> Tuple[str, Optional[float]]
    code, pf = _decode_eia(code.strip().upper())
    if pf is not None:
        return (_pf_human(pf), pf)
    return ("Invalid capacitance code", None)


def validate_tolerance(tol_code, dielectric, cap_pf):
    # type: (str, str, float) -> Tuple[bool, str]
    npo_sub10 = {"A", "B", "C", "D"}
    npo_ge10  = {"F", "G", "J", "K", "L"}
    x7r_ge10  = {"K", "L"}
    if dielectric == "N":
        valid = npo_sub10 if cap_pf < 10.0 else npo_ge10
        note  = ("NPO <10pF: A,B,C,D only" if cap_pf < 10.0
                 else "NPO >=10pF: F,G,J,K,L only")
    else:
        valid = x7r_ge10
        note  = "X7R: K or L only"
    if tol_code in valid:
        return (True, "OK")
    return (False, "Tolerance '{}' invalid. {}".format(tol_code, note))


# ---------------------------------------------------------------------------
# Encoder Tab
# ---------------------------------------------------------------------------
class EncoderTab(QWidget):
    def __init__(self):
        super(EncoderTab, self).__init__()
        self._cap_pf         = None   # type: Optional[float]
        self._cap_code       = ""
        self._current_gsfc   = ""
        self._current_sr     = ""
        self._build_ui()

    # ------------------------------------------------------------------ UI --
    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setSpacing(10)
        main.setContentsMargins(12, 12, 12, 12)

        sub = QLabel("Build a valid G311P829 GSFC PIN from the selections below.")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet("color: {}; font-style: italic;".format(DARK["text_dim"]))
        main.addWidget(sub)

        # --- field group ---
        fg   = QGroupBox("Part Number Fields")
        grid = QGridLayout(fg)
        grid.setColumnStretch(1, 2)
        grid.setColumnStretch(3, 2)
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(8)
        grid.setContentsMargins(12, 16, 12, 12)
        r = 0

        # GSFC ID
        grid.addWidget(self._fl("GSFC Identifier:"), r, 0, Qt.AlignRight)
        id_lbl = QLabel(
            "<b style='color:{};'>{}</b>"
            "<span style='color:{};'>  (fixed)</span>".format(
                DARK["accent"], GSFC_IDENTIFIER, DARK["text_dim"]))
        grid.addWidget(id_lbl, r, 1)
        r += 1

        # Ultrasonic
        grid.addWidget(self._fl("Ultrasonic Exam:"), r, 0, Qt.AlignRight)
        self.cb_ultra = QComboBox()
        for k, v in ULTRASONIC.items():
            self.cb_ultra.addItem("{}  \u2014  {}".format(k, v), k)
        grid.addWidget(self.cb_ultra, r, 1)
        r += 1

        # Size / Dielectric
        grid.addWidget(self._fl("Size Code:"), r, 0, Qt.AlignRight)
        self.cb_size = QComboBox()
        for k, v in SIZE_CODES.items():
            self.cb_size.addItem("{}  \u2014  {}".format(k, v), k)
        grid.addWidget(self.cb_size, r, 1)

        grid.addWidget(self._fl("Dielectric Type:"), r, 2, Qt.AlignRight)
        self.cb_diel = QComboBox()
        for k, v in DIELECTRIC_TYPES.items():
            self.cb_diel.addItem("{}  \u2014  {}".format(k, v), k)
        grid.addWidget(self.cb_diel, r, 3)
        r += 1

        # Capacitance block
        grid.addWidget(self._fl("Capacitance:"), r, 0,
                       Qt.AlignRight | Qt.AlignTop)
        cap_block = QWidget()
        cap_v     = QVBoxLayout(cap_block)
        cap_v.setContentsMargins(0, 0, 0, 0)
        cap_v.setSpacing(4)

        rr = QHBoxLayout()
        self.rb_value = QRadioButton("Enter value  (pF / nF / \u00b5F)")
        self.rb_code  = QRadioButton("Enter EIA code directly")
        self.rb_value.setChecked(True)
        rr.addWidget(self.rb_value)
        rr.addWidget(self.rb_code)
        rr.addStretch()
        cap_v.addLayout(rr)

        ir = QHBoxLayout()
        self.le_cap = QLineEdit()
        self.le_cap.setMaximumWidth(220)
        self.le_cap.setMinimumHeight(28)
        ir.addWidget(self.le_cap)
        self.lbl_cap_result = QLabel("")
        self.lbl_cap_result.setStyleSheet(
            "color: {}; font-style: italic;".format(DARK["accent"]))
        ir.addWidget(self.lbl_cap_result)
        ir.addStretch()
        cap_v.addLayout(ir)

        self.lbl_cap_hint = QLabel("")
        self.lbl_cap_hint.setStyleSheet(
            "color: {}; font-size: 8pt;".format(DARK["text_dim"]))
        cap_v.addWidget(self.lbl_cap_hint)

        self.lbl_cap_limit = QLabel("")
        self.lbl_cap_limit.setStyleSheet(
            "color: {}; font-size: 8pt; font-style: italic;".format(DARK["text_dim"]))
        cap_v.addWidget(self.lbl_cap_limit)

        grid.addWidget(cap_block, r, 1, 1, 3)
        r += 1

        # Tolerance / Voltage
        grid.addWidget(self._fl("Tolerance:"), r, 0, Qt.AlignRight)
        self.cb_tol = QComboBox()
        grid.addWidget(self.cb_tol, r, 1)

        grid.addWidget(self._fl("Voltage (Vdc):"), r, 2, Qt.AlignRight)
        self.cb_volt = QComboBox()
        for k, v in VOLTAGE_CODES.items():
            self.cb_volt.addItem("{}  \u2014  {}".format(k, v), k)
        grid.addWidget(self.cb_volt, r, 3)
        r += 1

        # Termination / Packaging
        grid.addWidget(self._fl("Termination:"), r, 0, Qt.AlignRight)
        self.cb_term = QComboBox()
        for k, v in TERMINATION_CODES.items():
            self.cb_term.addItem("{}  \u2014  {}".format(k, v), k)
        grid.addWidget(self.cb_term, r, 1)

        grid.addWidget(self._fl("Packaging / Marking:"), r, 2, Qt.AlignRight)
        self.cb_pkg = QComboBox()
        for k, v in PACKAGING_CODES.items():
            self.cb_pkg.addItem("{}  \u2014  {}".format(k, v), k)
        grid.addWidget(self.cb_pkg, r, 3)

        main.addWidget(fg)

        # --- result group ---
        rg = QGroupBox("Generated Part Numbers")
        rl = QVBoxLayout(rg)
        rl.setContentsMargins(12, 16, 12, 12)
        rl.setSpacing(10)

        # Generate button
        gen_row = QHBoxLayout()
        self.btn_encode = QPushButton("\u2699  Generate Part Numbers")
        self.btn_encode.setObjectName("accent")
        self.btn_encode.setMinimumHeight(38)
        gen_row.addStretch()
        gen_row.addWidget(self.btn_encode)
        gen_row.addStretch()
        rl.addLayout(gen_row)

        # GSFC PIN row
        gsfc_row = QHBoxLayout()
        lbl_g = QLabel("GSFC PIN:")
        lbl_g.setFixedWidth(100)
        lbl_g.setStyleSheet(
            "color: {}; font-weight: bold;".format(DARK["text_dim"]))
        gsfc_row.addWidget(lbl_g)
        self.lbl_pin = QLabel("\u2014")
        self.lbl_pin.setFont(QFont("Courier New", 13, QFont.Bold))
        self.lbl_pin.setStyleSheet(
            "color: {acc}; background: {bg};"
            "border: 2px solid {acc}; padding: 5px 14px;"
            "border-radius: 4px;".format(
                acc=DARK["accent"], bg=DARK["bg_input"]))
        self.lbl_pin.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.lbl_pin.setMinimumWidth(280)
        gsfc_row.addWidget(self.lbl_pin)
        gsfc_row.addStretch()
        self.btn_copy_gsfc = QPushButton("\u29c9  Copy")
        self.btn_copy_gsfc.setObjectName("copy")
        self.btn_copy_gsfc.setMinimumHeight(34)
        self.btn_copy_gsfc.setMinimumWidth(90)
        self.btn_copy_gsfc.setEnabled(False)
        self.btn_copy_gsfc.setToolTip("Copy GSFC PIN to clipboard")
        gsfc_row.addWidget(self.btn_copy_gsfc)
        rl.addLayout(gsfc_row)

        # Presidio SR PIN row
        sr_row = QHBoxLayout()
        lbl_s = QLabel("Presidio SR:")
        lbl_s.setFixedWidth(100)
        lbl_s.setStyleSheet(
            "color: {}; font-weight: bold;".format(DARK["presidio_acc"]))
        sr_row.addWidget(lbl_s)
        self.lbl_sr_pin = QLabel("\u2014")
        self.lbl_sr_pin.setFont(QFont("Courier New", 13, QFont.Bold))
        self.lbl_sr_pin.setStyleSheet(
            "color: {acc}; background: {bg};"
            "border: 2px solid {bdr}; padding: 5px 14px;"
            "border-radius: 4px;".format(
                acc=DARK["presidio_acc"],
                bg=DARK["presidio_bg"],
                bdr=DARK["presidio_bdr"]))
        self.lbl_sr_pin.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.lbl_sr_pin.setMinimumWidth(280)
        sr_row.addWidget(self.lbl_sr_pin)
        sr_row.addStretch()
        self.btn_copy_sr = QPushButton("\u29c9  Copy")
        self.btn_copy_sr.setObjectName("copy_sr")
        self.btn_copy_sr.setMinimumHeight(34)
        self.btn_copy_sr.setMinimumWidth(90)
        self.btn_copy_sr.setEnabled(False)
        self.btn_copy_sr.setToolTip("Copy Presidio SR part number to clipboard")
        sr_row.addWidget(self.btn_copy_sr)
        rl.addLayout(sr_row)

        self.lbl_sr_note = QLabel("")
        self.lbl_sr_note.setStyleSheet(
            "color: {}; font-size: 8pt; font-style: italic;".format(
                DARK["text_dim"]))
        self.lbl_sr_note.setWordWrap(True)
        rl.addWidget(self.lbl_sr_note)

        self.lbl_warnings = QLabel("")
        self.lbl_warnings.setWordWrap(True)
        self.lbl_warnings.setStyleSheet(
            "color: {}; font-style: italic; padding: 2px;".format(DARK["warn"]))
        rl.addWidget(self.lbl_warnings)

        main.addWidget(rg)
        main.addStretch()

        # --- connections ---
        self.le_cap.textChanged.connect(self._on_cap_changed)
        self.rb_value.toggled.connect(self._on_mode_changed)
        self.rb_code.toggled.connect(self._on_mode_changed)
        self.btn_encode.clicked.connect(self._encode)
        self.btn_copy_gsfc.clicked.connect(
            lambda: self._copy(
                self._current_gsfc, self.btn_copy_gsfc,
                DARK["success"], DARK["success_bg"], DARK["success_bdr"]))
        self.btn_copy_sr.clicked.connect(
            lambda: self._copy(
                self._current_sr, self.btn_copy_sr,
                DARK["presidio_acc"], DARK["presidio_bg"], DARK["presidio_bdr"]))
        self.cb_diel.currentIndexChanged.connect(self._update_tol)
        self.cb_diel.currentIndexChanged.connect(self._update_limit)
        self.cb_size.currentIndexChanged.connect(self._check_marking)
        self.cb_size.currentIndexChanged.connect(self._update_limit)
        self.cb_volt.currentIndexChanged.connect(self._update_limit)
        self.cb_pkg.currentIndexChanged.connect(self._check_marking)

        self._update_tol()
        self._on_mode_changed()
        self._update_limit()

    # ---------------------------------------------------------------- helpers
    def _fl(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(
            "color: {}; font-weight: bold;".format(DARK["text_dim"]))
        return lbl

    def _update_limit(self):
        sc = self.cb_size.currentData()
        vc = self.cb_volt.currentData()
        dc = self.cb_diel.currentData()
        if not (sc and vc and dc):
            return
        mx       = get_max_capacitance(sc, vc, dc)
        diel_str = "NPO" if dc == "N" else "X7R"
        size_str = SIZE_CODES.get(sc, sc)
        volt_str = VOLTAGE_CODES.get(vc, vc)
        if mx == -1.0:
            self.lbl_cap_limit.setText(
                "Presidio SR: {}/{} not listed.".format(size_str, volt_str))
            self.lbl_cap_limit.setStyleSheet(
                "color: {}; font-size: 8pt; font-style: italic;".format(
                    DARK["error"]))
        elif mx is None:
            self.lbl_cap_limit.setText(
                "Presidio SR: {} not available for {}/{}.".format(
                    diel_str, size_str, volt_str))
            self.lbl_cap_limit.setStyleSheet(
                "color: {}; font-size: 8pt; font-style: italic;".format(
                    DARK["error"]))
        else:
            self.lbl_cap_limit.setText(
                "Presidio SR limit: {}/{}/{}  \u2192  max = {}".format(
                    diel_str, size_str, volt_str, _pf_human(mx)))
            self.lbl_cap_limit.setStyleSheet(
                "color: {}; font-size: 8pt; font-style: italic;".format(
                    DARK["text_dim"]))
        self._on_cap_changed(self.le_cap.text())

    # ----------------------------------------------------------------- slots
    def _on_mode_changed(self):
        if self.rb_value.isChecked():
            self.le_cap.setPlaceholderText(
                "e.g.  100pF   0.1uF   4.7nF   100")
            self.lbl_cap_hint.setText(
                "Units: pF (default), nF, uF \u2014 e.g. 100, 100pF, 0.1uF, 4.7nF")
        else:
            self.le_cap.setPlaceholderText("e.g.  101   1R0   R75   0R5")
            self.lbl_cap_hint.setText(
                "EIA 3-digit (101=100pF) or R-notation (1R0=1pF, R75=0.75pF)")
        self._on_cap_changed(self.le_cap.text())

    def _on_cap_changed(self, text):
        self._cap_pf   = None
        self._cap_code = ""
        text = text.strip()
        if not text:
            self.lbl_cap_result.setText("")
            return
        try:
            if self.rb_value.isChecked():
                pf, _   = parse_value_string(text)
                code, _ = pf_to_eia_code(pf)
            else:
                desc, pf = parse_capacitance_code(text.upper())
                if pf is None:
                    raise ValueError(desc)
                code = text.upper()
            self._cap_pf   = pf
            self._cap_code = code
            ok, msg = check_capacitance_vs_table(
                self.cb_size.currentData(),
                self.cb_volt.currentData(),
                self.cb_diel.currentData(), pf)
            base = "\u2192  {}  |  EIA Code: <b>{}</b>".format(
                _pf_human(pf), code)
            if ok:
                self.lbl_cap_result.setText(base)
                self.lbl_cap_result.setStyleSheet(
                    "color: {}; font-style: italic;".format(DARK["success"]))
            else:
                self.lbl_cap_result.setText(base + "  \u26a0  " + msg)
                self.lbl_cap_result.setStyleSheet(
                    "color: {}; font-style: italic;".format(DARK["error"]))
        except ValueError as e:
            self.lbl_cap_result.setText("\u26a0  {}".format(e))
            self.lbl_cap_result.setStyleSheet(
                "color: {}; font-style: italic;".format(DARK["error"]))

    def _update_tol(self):
        diel = self.cb_diel.currentData()
        self.cb_tol.clear()
        if diel == "N":
            for k, v in TOLERANCE_CODES.items():
                self.cb_tol.addItem("{}  \u2014  {}".format(k, v), k)
        else:
            for k in ("K", "L"):
                self.cb_tol.addItem(
                    "{}  \u2014  {}".format(k, TOLERANCE_CODES[k]), k)

    def _check_marking(self):
        if (self.cb_size.currentData() in NO_MARKING_SIZES
                and self.cb_pkg.currentData() in ("2", "4")):
            self.lbl_warnings.setStyleSheet(
                "color: {}; font-style: italic; padding: 2px;".format(
                    DARK["warn"]))
            self.lbl_warnings.setText(
                "\u26a0  Marking options 2/4 not available for sizes smaller "
                "than 0805/0612 (A,B,C,D,L,M,N,P,U) \u2014 para. 1.2.4.")
        else:
            self.lbl_warnings.setText("")

    def _encode(self):
        warnings  = []
        ultra     = self.cb_ultra.currentData()
        size_code = self.cb_size.currentData()
        diel_code = self.cb_diel.currentData()
        tol_code  = self.cb_tol.currentData()
        volt_code = self.cb_volt.currentData()
        term_code = self.cb_term.currentData()
        pkg_code  = self.cb_pkg.currentData()

        if self._cap_pf is None or not self._cap_code:
            QMessageBox.warning(self, "Capacitance Required",
                                "Please enter a valid capacitance value.")
            return

        ok, msg = check_capacitance_vs_table(
            size_code, volt_code, diel_code, self._cap_pf)
        if not ok:
            warnings.append("Presidio SR Table: " + msg)

        ok2, msg2 = validate_tolerance(tol_code, diel_code, self._cap_pf)
        if not ok2:
            warnings.append("Tolerance: " + msg2)

        if size_code in NO_MARKING_SIZES and pkg_code in ("2", "4"):
            warnings.append(
                "Marking options 2/4 not allowed for this package size.")

        gsfc_pin = "{}{}{}{}{}{}{}{}{}".format(
            GSFC_IDENTIFIER, ultra, size_code, diel_code,
            self._cap_code, tol_code, volt_code, term_code, pkg_code)

        sr_pin, sr_notes = build_presidio_pn(
            size_code, diel_code, self._cap_code,
            tol_code, volt_code, term_code, pkg_code)

        self._current_gsfc = gsfc_pin
        self._current_sr   = sr_pin
        self.lbl_pin.setText(gsfc_pin)
        self.lbl_sr_pin.setText(sr_pin)
        self.btn_copy_gsfc.setEnabled(True)
        self.btn_copy_sr.setEnabled(True)

        # Build SR annotation
        vp = PRESIDIO_VOLT.get(volt_code, "?")
        tp = PRESIDIO_TERM.get(term_code, "?")
        pp = PRESIDIO_PKG.get(pkg_code, "?")
        dp = PRESIDIO_DIEL.get(diel_code, "?")
        ss = SIZE_CODES.get(size_code, size_code)
        note = ("SR+{ss}+{dp}+{cap}+{tol}+{vp}({vd})+{tp}+{pp}+#M123A".format(
            ss=ss, dp=dp, cap=self._cap_code, tol=tol_code,
            vp=vp, vd=VOLTAGE_CODES.get(volt_code, ""), tp=tp, pp=pp))
        if sr_notes:
            note += "  |  " + "  |  ".join(sr_notes)
        self.lbl_sr_note.setText(note)

        if warnings:
            self.lbl_warnings.setStyleSheet(
                "color: {}; font-style: italic; padding: 2px;".format(
                    DARK["warn"]))
            self.lbl_warnings.setText(
                "\u26a0  " + "   |   ".join(warnings))
        else:
            self.lbl_warnings.setStyleSheet(
                "color: {}; font-style: italic; padding: 2px;".format(
                    DARK["success"]))
            self.lbl_warnings.setText(
                "\u2714  Part numbers generated successfully.")

    def _copy(self, text, btn, fg, bg, bdr):
        if not text:
            return
        QApplication.clipboard().setText(text)
        orig = btn.text()
        btn.setText("\u2714  Copied!")
        btn.setStyleSheet(
            "background-color: {bg}; border-color: {bdr};"
            "color: {fg}; border-radius: 4px;"
            "padding: 6px 16px; font-weight: bold;".format(
                bg=bg, bdr=bdr, fg=fg))
        QTimer.singleShot(1500,
                          lambda: (btn.setText(orig), btn.setStyleSheet("")))


# ---------------------------------------------------------------------------
# Decoder Tab
# ---------------------------------------------------------------------------
class DecoderTab(QWidget):
    def __init__(self):
        super(DecoderTab, self).__init__()
        self._build_ui()

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setSpacing(10)
        main.setContentsMargins(12, 12, 12, 12)

        sub = QLabel(
            "Enter a complete G311P829 GSFC PIN to decode its parameters.")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(
            "color: {}; font-style: italic;".format(DARK["text_dim"]))
        main.addWidget(sub)

        # Input
        ig = QGroupBox("Input Part Number")
        il = QHBoxLayout(ig)
        il.setContentsMargins(12, 16, 12, 12)
        self.le_pin = QLineEdit()
        self.le_pin.setPlaceholderText("e.g.  G311P829ADN101K1P1")
        self.le_pin.setFont(QFont("Courier New", 12))
        self.le_pin.setMinimumHeight(36)
        il.addWidget(self.le_pin)
        self.btn_decode = QPushButton("\U0001f50d  Decode")
        self.btn_decode.setObjectName("accent")
        self.btn_decode.setMinimumHeight(36)
        self.btn_decode.setMinimumWidth(110)
        il.addWidget(self.btn_decode)
        self.btn_clear = QPushButton("\u2715  Clear")
        self.btn_clear.setMinimumHeight(36)
        self.btn_clear.setMinimumWidth(80)
        il.addWidget(self.btn_clear)
        main.addWidget(ig)

        # Results grid
        rg    = QGroupBox("Decoded Parameters")
        rgrid = QGridLayout(rg)
        rgrid.setColumnStretch(1, 2)
        rgrid.setColumnStretch(3, 2)
        rgrid.setHorizontalSpacing(16)
        rgrid.setVerticalSpacing(6)
        rgrid.setContentsMargins(12, 16, 12, 12)
        self.result_labels = {}  # type: Dict[str, QLabel]

        std_fields = [
            "GSFC Identifier",    "Ultrasonic Examination",
            "Size Code",          "Dielectric Type",
            "Capacitance",        "Tolerance",
            "Voltage Rating",     "Termination",
            "Packaging / Marking","Presidio SR Table",
        ]
        for i, name in enumerate(std_fields):
            grid_row  = i // 2
            col_label = (i % 2) * 2
            col_value = col_label + 1
            lbl = QLabel("{}:".format(name))
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            lbl.setStyleSheet(
                "color: {}; font-weight: bold;".format(DARK["text_dim"]))
            rgrid.addWidget(lbl, grid_row, col_label)
            val = QLabel("\u2014")
            val.setWordWrap(True)
            val.setMinimumHeight(26)
            self._style(val, "default")
            rgrid.addWidget(val, grid_row, col_value)
            self.result_labels[name] = val

        # Presidio SR PIN — full width row
        last_row = len(std_fields) // 2 + 1
        sr_lbl = QLabel("Presidio SR PIN:")
        sr_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        sr_lbl.setStyleSheet(
            "color: {}; font-weight: bold;".format(DARK["presidio_acc"]))
        rgrid.addWidget(sr_lbl, last_row, 0)
        sr_val = QLabel("\u2014")
        sr_val.setFont(QFont("Courier New", 11, QFont.Bold))
        sr_val.setWordWrap(True)
        sr_val.setMinimumHeight(28)
        self._style(sr_val, "default")
        rgrid.addWidget(sr_val, last_row, 1, 1, 3)
        self.result_labels["Presidio SR PIN"] = sr_val

        main.addWidget(rg)

        # Notes
        ng = QGroupBox("Validation Notes")
        nl = QVBoxLayout(ng)
        nl.setContentsMargins(8, 12, 8, 8)
        self.te_notes = QTextEdit()
        self.te_notes.setReadOnly(True)
        self.te_notes.setMaximumHeight(90)
        self.te_notes.setFont(QFont("Courier New", 9))
        nl.addWidget(self.te_notes)
        main.addWidget(ng)
        main.addStretch()

        self.btn_decode.clicked.connect(self._decode)
        self.btn_clear.clicked.connect(self._clear)
        self.le_pin.returnPressed.connect(self._decode)

    # -------------------------------------------------------------- helpers
    def _style(self, lbl, state):
        styles = {
            "default":  (DARK["field_def_bg"], DARK["field_def_bdr"],
                         DARK["field_def_txt"]),
            "ok":       (DARK["field_ok_bg"],  DARK["field_ok_bdr"],
                         DARK["field_ok_txt"]),
            "error":    (DARK["field_er_bg"],  DARK["field_er_bdr"],
                         DARK["field_er_txt"]),
            "presidio": (DARK["presidio_bg"],  DARK["presidio_bdr"],
                         DARK["presidio_acc"]),
        }
        bg, bdr, txt = styles.get(state, styles["default"])
        lbl.setStyleSheet(
            "background: {bg}; border: 1px solid {bdr}; color: {txt};"
            "padding: 3px 6px; border-radius: 3px;".format(
                bg=bg, bdr=bdr, txt=txt))

    def _set(self, name, text, ok=True):
        lbl = self.result_labels[name]
        lbl.setText(text)
        self._style(lbl, "ok" if ok else "error")

    def _short_err(self, field):
        self._set(field, "\u26a0  Part number too short", ok=False)
        self.te_notes.setHtml(
            "<span style='color:{};'>"
            "\u2718  Ended unexpectedly at: <b>{}</b></span>".format(
                DARK["error"], field))

    # --------------------------------------------------------------- clear
    def _clear(self):
        self.le_pin.clear()
        for lbl in self.result_labels.values():
            lbl.setText("\u2014")
            self._style(lbl, "default")
        self.te_notes.clear()

    # -------------------------------------------------------------- decode
    def _decode(self):
        raw = (self.le_pin.text().strip().upper()
               .replace(" ", "").replace("-", ""))
        self._clear()
        self.le_pin.setText(raw)
        warnings = []

        if not raw.startswith(GSFC_IDENTIFIER):
            self.te_notes.setHtml(
                "<span style='color:{};'>"
                "\u2718  Must begin with <b>{}</b>.</span>".format(
                    DARK["error"], GSFC_IDENTIFIER))
            return
        rem = raw[len(GSFC_IDENTIFIER):]
        self._set("GSFC Identifier", GSFC_IDENTIFIER)

        # Ultrasonic
        if not rem:
            return self._short_err("Ultrasonic Examination")
        u = rem[0]; rem = rem[1:]
        if u in ULTRASONIC:
            self._set("Ultrasonic Examination",
                      "[{}]  {}".format(u, ULTRASONIC[u]))
        else:
            self._set("Ultrasonic Examination",
                      "[{}]  \u26a0 Unknown".format(u), ok=False)
            warnings.append("Unknown ultrasonic code: '{}'".format(u))

        # Size
        if not rem:
            return self._short_err("Size Code")
        size = rem[0]; rem = rem[1:]
        if size in SIZE_CODES:
            self._set("Size Code",
                      "[{}]  {}".format(size, SIZE_CODES[size]))
        else:
            self._set("Size Code",
                      "[{}]  \u26a0 Unknown".format(size), ok=False)
            warnings.append("Unknown size code: '{}'".format(size))

        # Dielectric
        if not rem:
            return self._short_err("Dielectric Type")
        diel = rem[0]; rem = rem[1:]
        if diel in DIELECTRIC_TYPES:
            self._set("Dielectric Type",
                      "[{}]  {}".format(diel, DIELECTRIC_TYPES[diel]))
        else:
            self._set("Dielectric Type",
                      "[{}]  \u26a0 Unknown".format(diel), ok=False)
            warnings.append("Unknown dielectric code: '{}'".format(diel))

        # Capacitance — last 4 chars are Tol+Volt+Term+Pkg
        if len(rem) < 6:
            return self._short_err("Capacitance")
        sfx       = rem[-4:]
        cap_field = rem[:-4]
        tol_code  = sfx[0]
        volt_code = sfx[1]
        term_code = sfx[2]
        pkg_code  = sfx[3]

        cap_desc, cap_pf = parse_capacitance_code(cap_field)
        if cap_pf is not None:
            extra = ("  ({:,.0f} pF)".format(cap_pf) if cap_pf >= 1000 else "")
            self._set("Capacitance",
                      "[{}]  {}{}".format(cap_field, cap_desc, extra))
        else:
            self._set("Capacitance",
                      "[{}]  \u26a0 {}".format(cap_field, cap_desc), ok=False)
            warnings.append("Cannot parse capacitance: '{}'".format(cap_field))

        # Tolerance
        if tol_code in TOLERANCE_CODES:
            tpf = cap_pf if cap_pf is not None else 100.0
            tok, tmsg = validate_tolerance(tol_code, diel, tpf)
            self._set("Tolerance",
                      "[{}]  {}".format(tol_code, TOLERANCE_CODES[tol_code]),
                      ok=tok)
            if not tok:
                warnings.append("Tolerance: " + tmsg)
        else:
            self._set("Tolerance",
                      "[{}]  \u26a0 Unknown".format(tol_code), ok=False)
            warnings.append("Unknown tolerance: '{}'".format(tol_code))

        # Voltage
        if volt_code in VOLTAGE_CODES:
            self._set("Voltage Rating",
                      "[{}]  {}".format(volt_code, VOLTAGE_CODES[volt_code]))
        else:
            self._set("Voltage Rating",
                      "[{}]  \u26a0 Unknown".format(volt_code), ok=False)
            warnings.append("Unknown voltage: '{}'".format(volt_code))

        # Termination
        if term_code in TERMINATION_CODES:
            self._set("Termination",
                      "[{}]  {}".format(term_code, TERMINATION_CODES[term_code]))
        else:
            self._set("Termination",
                      "[{}]  \u26a0 Unknown".format(term_code), ok=False)
            warnings.append("Unknown termination: '{}'".format(term_code))

        # Packaging
        if pkg_code in PACKAGING_CODES:
            mok = not (size in NO_MARKING_SIZES and pkg_code in ("2", "4"))
            self._set("Packaging / Marking",
                      "[{}]  {}".format(pkg_code, PACKAGING_CODES[pkg_code]),
                      ok=mok)
            if not mok:
                warnings.append(
                    "Marking '{}' not permitted for size '{}' \u2014 "
                    "para. 1.2.4.".format(pkg_code, size))
        else:
            self._set("Packaging / Marking",
                      "[{}]  \u26a0 Unknown".format(pkg_code), ok=False)
            warnings.append("Unknown packaging: '{}'".format(pkg_code))

        # Presidio SR table
        if (cap_pf is not None
                and volt_code in VOLTAGE_CODES
                and diel in DIELECTRIC_TYPES):
            tok, tmsg = check_capacitance_vs_table(
                size, volt_code, diel, cap_pf)
            self._set("Presidio SR Table", tmsg, ok=tok)
            if not tok:
                warnings.append("Presidio SR Table: " + tmsg)
        else:
            self._set("Presidio SR Table",
                      "Cannot validate \u2014 earlier field errors", ok=False)

        # Presidio SR PIN
        if (cap_pf is not None
                and volt_code in VOLTAGE_CODES
                and diel in DIELECTRIC_TYPES
                and term_code in TERMINATION_CODES):
            sr_pin, sr_notes = build_presidio_pn(
                size, diel, cap_field,
                tol_code, volt_code, term_code, pkg_code)
            sr_lbl = self.result_labels["Presidio SR PIN"]
            sr_lbl.setText(sr_pin)
            self._style(sr_lbl, "presidio")
            if sr_notes:
                warnings += ["SR PIN: " + n for n in sr_notes]
        else:
            self._set("Presidio SR PIN",
                      "Cannot generate \u2014 earlier field errors", ok=False)

        # Summary
        if warnings:
            html = ("<span style='color:{};'>"
                    "<b>Warnings / Errors:</b></span><br>".format(DARK["warn"]))
            for w in warnings:
                html += ("<span style='color:{};'>"
                         "\u26a0  {}</span><br>".format(DARK["error"], w))
            self.te_notes.setHtml(html)
        else:
            self.te_notes.setHtml(
                "<span style='color:{};'>"
                "<b>\u2714  Decoded successfully \u2014 no errors.</b>"
                "</span>".format(DARK["success"]))


# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle(
            "NASA S-311-P-829 Rev. M  \u2014  "
            "G311P829 / Presidio SR Capacitor PIN Tool")
        self.setMinimumSize(960, 720)

        central = QWidget()
        self.setCentralWidget(central)
        lay = QVBoxLayout(central)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(6)

        hdr = QLabel(
            "NASA GSFC  \u00b7  S-311-P-829 Rev. M  \u00b7  "
            "Multilayer Chip Capacitor  \u00b7  PIN Encoder / Decoder")
        hdr.setAlignment(Qt.AlignCenter)
        hdr.setFont(QFont("Segoe UI", 10, QFont.Bold))
        hdr.setStyleSheet(
            "background-color: {hbg}; color: {acc};"
            "padding: 8px; border-radius: 4px;"
            "border: 1px solid {acc};".format(
                hbg=DARK["header_bg"], acc=DARK["accent"]))
        lay.addWidget(hdr)

        tabs = QTabWidget()
        tabs.setFont(QFont("Segoe UI", 10))
        tabs.addTab(EncoderTab(), "  \u2699  Encoder  ")
        tabs.addTab(DecoderTab(), "  \U0001f50d  Decoder  ")
        lay.addWidget(tabs)

        ftr = QLabel(
            "Ref: NASA S-311-P-829 Rev. M (08/04/2025)  \u00b7  "
            "Presidio SR-M123A Datasheet  \u00b7  "
            "Goddard Space Flight Center, Code 562  \u00b7  "
            "For informational use \u2014 verify against current specifications.")
        ftr.setAlignment(Qt.AlignCenter)
        ftr.setStyleSheet(
            "color: {}; font-size: 8pt; padding: 2px;".format(DARK["text_dim"]))
        lay.addWidget(ftr)

def apply_dark_theme(app):
    app.setStyle("Fusion")
    p = QPalette()
    c = DARK
    p.setColor(QPalette.Window,          QColor(c["bg"]))
    p.setColor(QPalette.WindowText,      QColor(c["text"]))
    p.setColor(QPalette.Base,            QColor(c["bg_input"]))
    p.setColor(QPalette.AlternateBase,   QColor(c["bg_alt"]))
    p.setColor(QPalette.ToolTipBase,     QColor(c["bg_alt"]))
    p.setColor(QPalette.ToolTipText,     QColor(c["text"]))
    p.setColor(QPalette.Text,            QColor(c["text"]))
    p.setColor(QPalette.Button,          QColor(c["btn_bg"]))
    p.setColor(QPalette.ButtonText,      QColor(c["btn_text"]))
    p.setColor(QPalette.BrightText,      QColor("#FFFFFF"))
    p.setColor(QPalette.Link,            QColor(c["accent"]))
    p.setColor(QPalette.Highlight,       QColor(c["accent"]))
    p.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
    p.setColor(QPalette.Disabled, QPalette.Text,       QColor("#555570"))
    p.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#555570"))
    p.setColor(QPalette.Disabled, QPalette.WindowText, QColor("#555570"))
    app.setPalette(p)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    try:
        app = QApplication(sys.argv)
        apply_dark_theme(app)
        stylesheet = _build_stylesheet()
        app.setStyleSheet(stylesheet)
        win = MainWindow()
        win.show()
        sys.exit(app.exec())
    except Exception:
        traceback.print_exc()
        input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()