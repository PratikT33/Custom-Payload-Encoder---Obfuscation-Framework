"""
Reporter Module — Generate comprehensive analysis reports.
"""

import json
import os
import uuid
from datetime import datetime


REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


def generate_report(session_data: dict) -> dict:
    """
    Generate a full JSON report from a session pipeline result.
    Saves to the reports/ directory and returns report metadata.
    """
    report_id = str(uuid.uuid4())[:8]
    timestamp = datetime.utcnow().isoformat() + "Z"

    report = {
        "report_id": report_id,
        "generated_at": timestamp,
        "framework": "Custom Payload Encoder & Obfuscation Framework",
        "version": "1.0.0",
        "disclaimer": (
            "This report is generated for EDUCATIONAL and RESEARCH purposes only "
            "in a controlled lab environment. Unauthorized use of payload encoding "
            "techniques against systems you do not own is illegal."
        ),
        "session": session_data,
        "analysis_summary": _build_summary(session_data),
    }

    filename = f"report_{report_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(REPORTS_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    return {
        "report_id": report_id,
        "filename": filename,
        "filepath": filepath,
        "generated_at": timestamp,
        "size_bytes": os.path.getsize(filepath),
    }


def _build_summary(session_data: dict) -> dict:
    """Extract key insights from session data for the report summary."""
    summary = {}

    # Encoding results
    if "encodings" in session_data:
        encodings = session_data["encodings"]
        summary["encoding_methods_applied"] = [e.get("method", "?") for e in encodings]
        summary["total_encodings"] = len(encodings)

    # Obfuscation results
    if "obfuscations" in session_data:
        obs = session_data["obfuscations"]
        summary["obfuscation_techniques_applied"] = [o.get("technique", "?") for o in obs]
        summary["total_obfuscations"] = len(obs)

    # Evasion results
    if "evasion" in session_data:
        ev = session_data["evasion"]
        orig = ev.get("original", {})
        summ = ev.get("summary", {})

        summary["original_detection_rate"] = orig.get("detection_rate", "N/A")
        summary["original_verdict"] = orig.get("verdict", "N/A")
        summary["bypass_rate"] = summ.get("bypass_rate", "N/A")
        summary["most_effective_technique"] = summ.get("most_effective", "N/A")
        summary["transformations_tested"] = summ.get("total_tested", 0)
        summary["transformations_bypassed"] = summ.get("bypassed", 0)
        summary["transformations_detected"] = summ.get("detected", 0)

    # Recommendations
    summary["recommendations"] = _generate_recommendations(session_data)

    return summary


def _generate_recommendations(session_data: dict) -> list:
    """Generate defensive recommendations based on test results."""
    recs = []

    evasion = session_data.get("evasion", {})
    orig = evasion.get("original", {})
    summ = evasion.get("summary", {})

    bypass_rate = summ.get("bypass_rate", 0)

    if bypass_rate > 75:
        recs.append({
            "priority": "CRITICAL",
            "recommendation": "Current signature-based detection is highly ineffective. "
                              "Implement behavioral/heuristic analysis immediately.",
        })
    elif bypass_rate > 50:
        recs.append({
            "priority": "HIGH",
            "recommendation": "Signature database requires urgent expansion to cover encoding patterns.",
        })
    elif bypass_rate > 25:
        recs.append({
            "priority": "MEDIUM",
            "recommendation": "Detection coverage is partial. Add entropy-based detection rules.",
        })
    else:
        recs.append({
            "priority": "LOW",
            "recommendation": "Detection rate is acceptable. Continue monitoring and updating signatures.",
        })

    recs.extend([
        {
            "priority": "HIGH",
            "recommendation": "Deploy entropy-based analysis to catch encoded/encrypted payloads regardless of content.",
        },
        {
            "priority": "MEDIUM",
            "recommendation": "Implement YARA rules targeting obfuscation patterns (e.g., hex escape sequences).",
        },
        {
            "priority": "MEDIUM",
            "recommendation": "Use sandboxed dynamic analysis for payloads that evade static detection.",
        },
        {
            "priority": "LOW",
            "recommendation": "Maintain and update signature database with new evasion patterns regularly.",
        },
    ])

    return recs


def list_reports() -> list:
    """List all saved reports in the reports directory."""
    reports = []
    for fname in sorted(os.listdir(REPORTS_DIR), reverse=True):
        if fname.endswith(".json"):
            fpath = os.path.join(REPORTS_DIR, fname)
            reports.append({
                "filename": fname,
                "filepath": fpath,
                "size_bytes": os.path.getsize(fpath),
                "modified": datetime.fromtimestamp(
                    os.path.getmtime(fpath)
                ).isoformat(),
            })
    return reports


def load_report(report_id: str) -> dict:
    """Load a report by its ID prefix."""
    for fname in os.listdir(REPORTS_DIR):
        if fname.startswith(f"report_{report_id}") and fname.endswith(".json"):
            fpath = os.path.join(REPORTS_DIR, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                return json.load(f)
    raise FileNotFoundError(f"No report found with ID: {report_id}")
