# PayloadForge — Custom Payload Encoder & Obfuscation Framework

> **⚠ Educational & Research Use Only**
> This framework is designed strictly for controlled lab environments, red/blue team research, cybersecurity education, and malware analysis training. Unauthorized use against systems you do not own is illegal.

---

## 📌 Project Overview

PayloadForge is a practical payload encoding and obfuscation framework built to study how offensive payloads are transformed to evade static detection systems (AV, EDR, IPS, firewalls).

Security tools rely on signature-based detection, making unmodified payloads easy to identify. This framework demonstrates those evasion techniques in a controlled, ethical environment.

---

## 🎯 Features

### 🔐 Encoding Module
| Method | Description |
|--------|-------------|
| Base64 | RFC 4648 standard encoding with decode support |
| XOR    | Multi-byte key XOR encryption (hex + B64 output) |
| ROT13  | Caesar substitution cipher (symmetric) |
| Hex    | Raw hexadecimal representation |
| Multi-Layer | Chain multiple encodings (e.g. ROT13 → Base64 → XOR) |

### 🌀 Obfuscation Module
| Technique | Description |
|-----------|-------------|
| Random Character Insertion | Inject junk chars at random positions (reversible via marker) |
| Character Split & Concat | Split into string literal chunks (`"hel" + "lo"`) |
| Reversal Transform | Reverse the entire payload string |
| Escape Sequence (Hex) | `\x41\x42\x43` hex escape representation |
| Escape Sequence (Unicode) | `\u0041\u0042` Unicode escape representation |
| Escape Sequence (Octal) | `\101\102` Octal escape representation |
| Case Scrambling | Random case alternation for case-insensitive evasion |
| Null-Byte Injection | Insert `%00` or custom delimiter between chars |
| Identifier Substitution | Replace known keywords with random-looking variable names |

### 🎯 Evasion Testing Module
- **24 simulated signatures** covering shellcode, script attacks, network indicators
- **Shannon entropy** analysis (detects encoding/encryption by randomness score)
- **Comparative analysis** — run all transformations, measure bypass rates
- **Severity classification**: CRITICAL / HIGH / MEDIUM / LOW

### 📊 Reporting Engine
- JSON reports saved to `/reports/` directory
- Defensive recommendations auto-generated from results
- Report viewer in UI + JSON download

---

## 🗂 Project Structure

```
payload-encoder/
├── app.py                   # Flask web server & REST API
├── requirements.txt         # Python dependencies
├── modules/
│   ├── __init__.py
│   ├── encoder.py           # Base64, XOR, ROT13, Hex encoding
│   ├── obfuscator.py        # 9 string obfuscation techniques
│   ├── evasion_tester.py    # Signature scanner & comparison engine
│   └── reporter.py          # Report generation & storage
├── static/
│   ├── index.html           # Single-page web application
│   ├── style.css            # Dark cyberpunk UI design
│   └── app.js               # Frontend JavaScript logic
└── reports/                 # Auto-created — generated JSON reports
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+
- pip

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Server
```bash
python app.py
```

### 4. Open the Web UI
Navigate to: [http://localhost:5000](http://localhost:5000)

---

## 🌐 API Reference

All endpoints accept and return JSON.

### Encoding
```
POST /api/encode            → Encode with single method
POST /api/encode/multi      → Multi-layer encoding
POST /api/decode            → Decode payload
```

### Obfuscation
```
POST /api/obfuscate         → Apply single technique
POST /api/obfuscate/all     → Apply all techniques
```

### Evasion Testing
```
POST /api/scan              → Quick signature scan
POST /api/evasion-test      → Full comparative evasion test
```

### Pipeline & Reports
```
POST /api/full-pipeline     → Run complete workflow
GET  /api/reports           → List all reports
GET  /api/reports/<id>      → Fetch specific report
```

### Example Request
```bash
curl -X POST http://localhost:5000/api/encode \
  -H "Content-Type: application/json" \
  -d '{"payload": "cmd.exe /c whoami", "method": "base64"}'
```

---

## 🔬 Workflow

```
START
  ↓
Load Payload
  ↓
Select Encoding Method (Base64 / XOR / ROT13 / Hex / Multi-Layer)
  ↓
Apply String Obfuscation Technique(s)
  ↓
Run Evasion Test (signature scan + entropy analysis)
  ↓
Compare Original vs Obfuscated Detection Rates
  ↓
Generate Report
  ↓
END
```

---

## 🛡 Defensive Insights

This framework helps defenders understand:

- **Why signature-only detection fails** against encoded/obfuscated payloads
- **How entropy analysis** can catch encoded content even without signatures
- **What obfuscation patterns** look like (case scrambling, escape sequences, etc.)
- **Why layered security** (behavioral analysis + sandboxing + YARA rules) is necessary

---

## 🧰 Technologies Used

| Component | Technology |
|-----------|-----------|
| Backend   | Python 3.x + Flask |
| API       | Flask-CORS REST API |
| Frontend  | Vanilla HTML/CSS/JavaScript |
| Fonts     | JetBrains Mono + Inter (Google Fonts) |
| Encoding  | Python `base64`, `codecs` stdlib |
| Reports   | JSON file storage |

---

## 📸 Modules Summary

### `modules/encoder.py`
Handles Base64, XOR (multi-byte key), ROT13, and Hex encoding with encode/decode support and multi-layer chaining.

### `modules/obfuscator.py`
Implements 9 reversible and non-reversible string obfuscation techniques with metadata for each transformation.

### `modules/evasion_tester.py`
Simulates a 24-signature detection engine with Shannon entropy heuristics and comparative bypass rate calculation.

### `modules/reporter.py`
Generates structured JSON reports with defensive recommendations saved to the `reports/` directory.

---

## ⚖ Legal & Ethical Notice

This tool is intended exclusively for:
- ✅ Authorized penetration testing
- ✅ Red team / blue team exercises
- ✅ Academic cybersecurity research
- ✅ Malware analysis education
- ✅ Defensive tool improvement

**It must NOT be used for:**
- ❌ Unauthorized system access
- ❌ Malware development or distribution
- ❌ Any illegal activities

The authors accept no liability for misuse of this tool.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
