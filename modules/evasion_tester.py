"""
Evasion Testing Module — Simulates signature-based detection.

This module provides a simulated Antivirus / IDS / IPS engine using:
  • Keyword/string signatures (common malicious patterns)
  • Entropy heuristic (Shannon entropy check)
  • Length anomaly detection
  • Regex-based pattern matching

All signatures are FICTIONAL / EDUCATIONAL representations.
No real malware is included.
"""

import re
import math
from collections import Counter
from typing import Union


# ---------------------------------------------------------------------------
# Simulated Signature Database
# ---------------------------------------------------------------------------

SIGNATURE_DB = {
    # Shellcode / binary markers
    "sig_shellcode_nop_sled":     r"\\x90{4,}",
    "sig_shellcode_int3":         r"\\xcc{2,}",
    "sig_windows_exec_marker":    r"\\x41\\x41\\x41\\x41",

    # Common attack strings (educational representations)
    "sig_cmd_exec":               r"\bcmd\.exe\b",
    "sig_powershell":             r"\bpowershell\b",
    "sig_wget_curl":              r"\b(wget|curl)\b",
    "sig_reverse_shell":          r"\b(nc|netcat|ncat)\b.*\-e",
    "sig_base64_decode_call":     r"base64\s*[\.\(].*decode",
    "sig_eval_exec":              r"\beval\s*\(",
    "sig_exec_system":            r"\b(exec|system|popen)\s*\(",
    "sig_socket_connect":         r"\bsocket\s*\.\s*connect\b",
    "sig_bind_shell":             r"\bsocket\s*\.\s*bind\b",

    # Script-based attack patterns
    "sig_vba_macro":              r"Auto_?Open|Document_?Open",
    "sig_js_fromcharcode":        r"String\.fromCharCode",
    "sig_js_unescape":            r"\bunescape\s*\(",
    "sig_php_passthru":           r"\bpassthru\s*\(",
    "sig_python_subprocess":      r"subprocess\.(Popen|call|run)",

    # Network indicators
    "sig_ip_pattern":             r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
    "sig_http_download":          r"http[s]?://\S+\.(exe|bat|ps1|sh|py)",

    # Suspicious keywords
    "sig_malware_terms":          r"\b(malware|exploit|shellcode|rootkit|keylogger|ransomware|trojan|backdoor)\b",
    "sig_injection_terms":        r"\b(inject|payload|overflow|overwrite|heap|stack smash)\b",
    "sig_privilege_escalation":   r"\b(privesc|sudo|runas|getsystem|bypass uac)\b",

    # Encoding indicators
    "sig_long_base64":            r"[A-Za-z0-9+/]{50,}={0,2}",
    "sig_hex_shellcode":          r"(\\x[0-9a-fA-F]{2}){10,}",
}

SEVERITY_MAP = {
    "sig_shellcode_nop_sled":       "CRITICAL",
    "sig_shellcode_int3":           "CRITICAL",
    "sig_windows_exec_marker":      "HIGH",
    "sig_cmd_exec":                 "HIGH",
    "sig_powershell":               "MEDIUM",
    "sig_wget_curl":                "MEDIUM",
    "sig_reverse_shell":            "CRITICAL",
    "sig_base64_decode_call":       "MEDIUM",
    "sig_eval_exec":                "HIGH",
    "sig_exec_system":              "HIGH",
    "sig_socket_connect":           "MEDIUM",
    "sig_bind_shell":               "HIGH",
    "sig_vba_macro":                "HIGH",
    "sig_js_fromcharcode":          "MEDIUM",
    "sig_js_unescape":              "LOW",
    "sig_php_passthru":             "HIGH",
    "sig_python_subprocess":        "MEDIUM",
    "sig_ip_pattern":               "LOW",
    "sig_http_download":            "HIGH",
    "sig_malware_terms":            "MEDIUM",
    "sig_injection_terms":          "LOW",
    "sig_privilege_escalation":     "HIGH",
    "sig_long_base64":              "LOW",
    "sig_hex_shellcode":            "HIGH",
}


# ---------------------------------------------------------------------------
# Shannon Entropy
# ---------------------------------------------------------------------------

def shannon_entropy(data: str) -> float:
    """
    Calculate Shannon entropy of a string.
    High entropy (> 4.5) may indicate encryption/encoding.
    """
    if not data:
        return 0.0
    freq = Counter(data)
    length = len(data)
    return -sum((count / length) * math.log2(count / length) for count in freq.values())


def entropy_verdict(entropy: float) -> dict:
    """Interpret entropy value for detection purposes."""
    if entropy < 3.0:
        label = "LOW"
        color = "green"
        note = "Plain text — readable, easy to detect by keyword scan"
    elif entropy < 4.5:
        label = "MEDIUM"
        color = "yellow"
        note = "Partially obfuscated or mixed content"
    elif entropy < 6.0:
        label = "HIGH"
        color = "orange"
        note = "High randomness — likely encoded/encrypted"
    else:
        label = "VERY HIGH"
        color = "red"
        note = "Near-random — strong encryption/encoding detected"

    return {"label": label, "color": color, "value": round(entropy, 4), "note": note}


# ---------------------------------------------------------------------------
# Core Signature Scanner
# ---------------------------------------------------------------------------

def run_signature_check(payload: str) -> dict:
    """
    Scan a payload against the simulated signature database.
    Returns all matched signatures with severity and match details.
    """
    matched = []
    not_matched = []

    for sig_id, pattern in SIGNATURE_DB.items():
        try:
            match = re.search(pattern, payload, re.IGNORECASE | re.DOTALL)
            severity = SEVERITY_MAP.get(sig_id, "UNKNOWN")
            if match:
                matched.append({
                    "signature_id": sig_id,
                    "pattern": pattern,
                    "match": match.group(0)[:80],   # truncate long matches
                    "position": match.start(),
                    "severity": severity,
                })
            else:
                not_matched.append({"signature_id": sig_id, "severity": severity})
        except re.error:
            not_matched.append({"signature_id": sig_id, "severity": "ERROR"})

    entropy = shannon_entropy(payload)
    ent_verdict = entropy_verdict(entropy)

    # Heuristic: anomalously long single-token strings
    length_alert = len(payload) > 500 and " " not in payload[:100]

    detected = len(matched) > 0

    return {
        "detected": detected,
        "verdict": "DETECTED" if detected else "BYPASSED",
        "signatures_matched": matched,
        "signatures_not_matched": not_matched,
        "match_count": len(matched),
        "total_signatures": len(SIGNATURE_DB),
        "detection_rate": round(len(matched) / len(SIGNATURE_DB) * 100, 2),
        "entropy": ent_verdict,
        "length_alert": length_alert,
        "payload_length": len(payload),
    }


# ---------------------------------------------------------------------------
# Comparative Evasion Test
# ---------------------------------------------------------------------------

def run_evasion_test(original: str, transformations: list) -> dict:
    """
    Compare detection of original payload vs. a list of transformed variants.

    transformations: list of dicts with 'label' and 'payload' keys.

    Returns a comprehensive comparison report.
    """
    original_result = run_signature_check(original)

    comparison = []
    bypassed_count = 0
    detected_count = 0

    for t in transformations:
        label = t.get("label", "Unknown")
        payload = t.get("payload", "")
        result = run_signature_check(payload)

        evasion_improvement = (
            original_result["detection_rate"] - result["detection_rate"]
        )

        comparison.append({
            "label": label,
            "payload_preview": payload[:120] + ("..." if len(payload) > 120 else ""),
            "detected": result["detected"],
            "verdict": result["verdict"],
            "match_count": result["match_count"],
            "detection_rate": result["detection_rate"],
            "evasion_improvement": round(evasion_improvement, 2),
            "entropy": result["entropy"],
        })

        if result["detected"]:
            detected_count += 1
        else:
            bypassed_count += 1

    bypass_rate = round(bypassed_count / max(len(transformations), 1) * 100, 2)

    return {
        "original": {
            "payload_preview": original[:120] + ("..." if len(original) > 120 else ""),
            "detected": original_result["detected"],
            "verdict": original_result["verdict"],
            "match_count": original_result["match_count"],
            "detection_rate": original_result["detection_rate"],
            "entropy": original_result["entropy"],
        },
        "transformations": comparison,
        "summary": {
            "total_tested": len(transformations),
            "bypassed": bypassed_count,
            "detected": detected_count,
            "bypass_rate": bypass_rate,
            "most_effective": min(comparison, key=lambda x: x["detection_rate"])["label"]
            if comparison else "N/A",
        },
    }


# ---------------------------------------------------------------------------
# Quick Scan Helper
# ---------------------------------------------------------------------------

def quick_scan(payload: str) -> dict:
    """Return a concise detection summary."""
    result = run_signature_check(payload)
    return {
        "verdict": result["verdict"],
        "detected": result["detected"],
        "matches": result["match_count"],
        "detection_rate_pct": result["detection_rate"],
        "entropy": result["entropy"]["value"],
        "entropy_label": result["entropy"]["label"],
    }
