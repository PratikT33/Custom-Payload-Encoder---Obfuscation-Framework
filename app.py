"""
Flask Application — Custom Payload Encoder & Obfuscation Framework API + Web Server.

For educational and research use only in controlled lab environments.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import traceback

from modules.encoder import (
    base64_encode, base64_decode,
    xor_encode, xor_decode,
    rot13_encode, rot13_decode,
    hex_encode, hex_decode,
    multi_layer_encode,
)
from modules.obfuscator import (
    random_char_insertion, char_split_concat,
    reverse_transform, escape_sequence_obfuscation,
    case_scramble, null_byte_injection,
    identifier_substitution, apply_all_obfuscations,
)
from modules.evasion_tester import (
    run_signature_check, run_evasion_test, quick_scan,
    shannon_entropy, entropy_verdict,
)
from modules.reporter import generate_report, list_reports, load_report

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")
CORS(app)


# ---------------------------------------------------------------------------
# Static UI
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


# ---------------------------------------------------------------------------
# Encoding endpoints
# ---------------------------------------------------------------------------

@app.route("/api/encode", methods=["POST"])
def api_encode():
    """Apply a single encoding method to a payload."""
    data = request.get_json(force=True)
    payload = data.get("payload", "")
    method = data.get("method", "base64").lower()
    xor_key = data.get("xor_key", "K3Y")

    if not payload:
        return jsonify({"error": "Payload is required"}), 400

    try:
        if method == "base64":
            result = base64_encode(payload)
        elif method == "xor":
            result = xor_encode(payload, xor_key)
        elif method == "rot13":
            result = rot13_encode(payload)
        elif method == "hex":
            result = hex_encode(payload)
        else:
            return jsonify({"error": f"Unknown method: {method}"}), 400

        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


@app.route("/api/encode/multi", methods=["POST"])
def api_multi_encode():
    """Apply multiple encoding layers."""
    data = request.get_json(force=True)
    payload = data.get("payload", "")
    layers = data.get("layers", ["base64"])
    xor_key = data.get("xor_key", "K3Y")

    if not payload:
        return jsonify({"error": "Payload is required"}), 400

    try:
        result = multi_layer_encode(payload, layers, xor_key)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/decode", methods=["POST"])
def api_decode():
    """Decode an encoded payload."""
    data = request.get_json(force=True)
    encoded = data.get("encoded", "")
    method = data.get("method", "base64").lower()
    xor_key = data.get("xor_key", "K3Y")

    if not encoded:
        return jsonify({"error": "Encoded payload is required"}), 400

    try:
        if method == "base64":
            decoded = base64_decode(encoded)
        elif method == "xor":
            decoded = xor_decode(encoded, xor_key)
        elif method == "rot13":
            decoded = rot13_decode(encoded)
        elif method == "hex":
            decoded = hex_decode(encoded)
        else:
            return jsonify({"error": f"Unknown method: {method}"}), 400

        return jsonify({"success": True, "decoded": decoded, "method": method})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# Obfuscation endpoints
# ---------------------------------------------------------------------------

@app.route("/api/obfuscate", methods=["POST"])
def api_obfuscate():
    """Apply a single obfuscation technique."""
    data = request.get_json(force=True)
    payload = data.get("payload", "")
    technique = data.get("technique", "random_char").lower()
    options = data.get("options", {})

    if not payload:
        return jsonify({"error": "Payload is required"}), 400

    try:
        if technique == "random_char":
            result = random_char_insertion(payload, density=options.get("density", 0.25))
        elif technique == "char_split":
            result = char_split_concat(payload, chunk_size=options.get("chunk_size", 4))
        elif technique == "reverse":
            result = reverse_transform(payload)
        elif technique == "escape_hex":
            result = escape_sequence_obfuscation(payload, mode="hex")
        elif technique == "escape_unicode":
            result = escape_sequence_obfuscation(payload, mode="unicode")
        elif technique == "escape_octal":
            result = escape_sequence_obfuscation(payload, mode="octal")
        elif technique == "case_scramble":
            result = case_scramble(payload)
        elif technique == "null_byte":
            result = null_byte_injection(payload, delimiter=options.get("delimiter", "%00"))
        elif technique == "identifier_sub":
            result = identifier_substitution(payload)
        else:
            return jsonify({"error": f"Unknown technique: {technique}"}), 400

        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/obfuscate/all", methods=["POST"])
def api_obfuscate_all():
    """Apply all obfuscation techniques to a payload."""
    data = request.get_json(force=True)
    payload = data.get("payload", "")

    if not payload:
        return jsonify({"error": "Payload is required"}), 400

    try:
        results = apply_all_obfuscations(payload)
        return jsonify({"success": True, "results": results, "count": len(results)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# Evasion Testing endpoints
# ---------------------------------------------------------------------------

@app.route("/api/scan", methods=["POST"])
def api_scan():
    """Run signature scan on a single payload."""
    data = request.get_json(force=True)
    payload = data.get("payload", "")

    if not payload:
        return jsonify({"error": "Payload is required"}), 400

    try:
        result = run_signature_check(payload)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/evasion-test", methods=["POST"])
def api_evasion_test():
    """
    Run full evasion comparison test.
    Automatically encodes + obfuscates the payload and compares detection rates.
    """
    data = request.get_json(force=True)
    payload = data.get("payload", "")
    xor_key = data.get("xor_key", "K3Y")

    if not payload:
        return jsonify({"error": "Payload is required"}), 400

    try:
        # Build transformations
        transformations = []

        # Encodings
        b64 = base64_encode(payload)
        transformations.append({"label": "Base64 Encoded", "payload": b64["encoded"]})

        xor_r = xor_encode(payload, xor_key)
        transformations.append({"label": f"XOR Encoded (key={xor_key})", "payload": xor_r["encoded"]})

        rot = rot13_encode(payload)
        transformations.append({"label": "ROT13 Encoded", "payload": rot["encoded"]})

        hx = hex_encode(payload)
        transformations.append({"label": "Hex Encoded", "payload": hx["encoded"]})

        multi = multi_layer_encode(payload, ["rot13", "base64"], xor_key)
        transformations.append({"label": "ROT13 → Base64 (Multi-layer)", "payload": multi["encoded"]})

        multi2 = multi_layer_encode(payload, ["base64", "xor"], xor_key)
        transformations.append({"label": "Base64 → XOR (Multi-layer)", "payload": multi2["encoded"]})

        # Obfuscations
        rev = reverse_transform(payload)
        transformations.append({"label": "Reversal Transform", "payload": rev["obfuscated"]})

        esc = escape_sequence_obfuscation(payload, mode="hex")
        transformations.append({"label": "Hex Escape Obfuscation", "payload": esc["obfuscated"]})

        cs = case_scramble(payload)
        transformations.append({"label": "Case Scramble", "payload": cs["obfuscated"]})

        null = null_byte_injection(payload)
        transformations.append({"label": "Null-Byte Injection", "payload": null["obfuscated"]})

        idn = identifier_substitution(payload)
        transformations.append({"label": "Identifier Substitution", "payload": idn["obfuscated"]})

        # Run comparison
        evasion_result = run_evasion_test(payload, transformations)

        return jsonify({"success": True, "evasion": evasion_result})
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


# ---------------------------------------------------------------------------
# Full Pipeline endpoint
# ---------------------------------------------------------------------------

@app.route("/api/full-pipeline", methods=["POST"])
def api_full_pipeline():
    """
    Run the complete framework pipeline:
      1. Original payload scan
      2. Apply all encodings
      3. Apply all obfuscations
      4. Evasion comparison
      5. Generate report
    """
    data = request.get_json(force=True)
    payload = data.get("payload", "")
    xor_key = data.get("xor_key", "K3Y")
    layers = data.get("layers", ["base64", "xor"])

    if not payload:
        return jsonify({"error": "Payload is required"}), 400

    try:
        session = {}

        # 1. Scan original
        session["original_scan"] = run_signature_check(payload)

        # 2. Encodings
        session["encodings"] = [
            base64_encode(payload),
            xor_encode(payload, xor_key),
            rot13_encode(payload),
            hex_encode(payload),
            multi_layer_encode(payload, layers, xor_key),
        ]

        # 3. Obfuscations
        session["obfuscations"] = apply_all_obfuscations(payload)

        # 4. Evasion test
        transformations = (
            [{"label": e["method"], "payload": e["encoded"]} for e in session["encodings"]]
            + [{"label": o["technique"], "payload": o.get("obfuscated", "")}
               for o in session["obfuscations"] if "obfuscated" in o]
        )
        session["evasion"] = run_evasion_test(payload, transformations)

        # 5. Report
        meta = generate_report(session)
        session["report_meta"] = meta

        return jsonify({"success": True, "session": session, "report": meta})
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


# ---------------------------------------------------------------------------
# Report endpoints
# ---------------------------------------------------------------------------

@app.route("/api/reports", methods=["GET"])
def api_list_reports():
    return jsonify({"success": True, "reports": list_reports()})


@app.route("/api/reports/<report_id>", methods=["GET"])
def api_get_report(report_id):
    try:
        report = load_report(report_id)
        return jsonify({"success": True, "report": report})
    except FileNotFoundError:
        return jsonify({"error": f"Report not found: {report_id}"}), 404


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Custom Payload Encoder & Obfuscation Framework")
    print("  Educational Use Only — Controlled Lab Environment")
    print("=" * 60)
    print("  Starting server at: http://localhost:5000")
    print("=" * 60 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
