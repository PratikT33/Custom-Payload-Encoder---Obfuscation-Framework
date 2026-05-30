"""
PayloadForge — CLI interface for the Payload Encoder & Obfuscation Framework.

Usage examples:
  python cli.py encode --payload "cmd.exe /c whoami" --method base64
  python cli.py encode --payload "cmd.exe /c whoami" --method xor --key MyKey
  python cli.py encode --payload "test" --method multi --layers base64 xor rot13
  python cli.py obfuscate --payload "eval(exec(cmd))" --technique escape_hex
  python cli.py obfuscate --payload "eval(exec(cmd))" --all
  python cli.py scan --payload "powershell -enc <b64>"
  python cli.py decode --encoded "dGVzdA==" --method base64
"""

import argparse
import json
import sys

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
from modules.evasion_tester import run_signature_check, quick_scan

# ANSI colors
GRN  = "\033[92m"
RED  = "\033[91m"
CYN  = "\033[96m"
YLW  = "\033[93m"
MAG  = "\033[95m"
RST  = "\033[0m"
BLD  = "\033[1m"

BANNER = f"""
{GRN}{BLD}
  ██████╗  █████╗ ██╗   ██╗██╗      ██████╗  █████╗ ██████╗ ███████╗
  ██╔══██╗██╔══██╗╚██╗ ██╔╝██║     ██╔═══██╗██╔══██╗██╔══██╗██╔════╝
  ██████╔╝███████║ ╚████╔╝ ██║     ██║   ██║███████║██║  ██║█████╗
  ██╔═══╝ ██╔══██║  ╚██╔╝  ██║     ██║   ██║██╔══██║██║  ██║██╔══╝
  ██║     ██║  ██║   ██║   ███████╗╚██████╔╝██║  ██║██████╔╝███████╗
  ╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚══════╝
{RST}
{CYN}  Custom Payload Encoder & Obfuscation Framework{RST}
{YLW}  [ EDUCATIONAL USE ONLY — CONTROLLED LAB ENVIRONMENT ]{RST}
"""


def print_json(data):
    print(json.dumps(data, indent=2, default=str))


def cmd_encode(args):
    print(BANNER)
    payload = args.payload
    method = args.method.lower()
    key = args.key or "K3Y"

    print(f"{CYN}[*] Encoding Method: {BLD}{method.upper()}{RST}")
    print(f"{CYN}[*] Payload: {RST}{repr(payload)}\n")

    if method == "base64":
        result = base64_encode(payload)
    elif method == "xor":
        result = xor_encode(payload, key)
    elif method == "rot13":
        result = rot13_encode(payload)
    elif method == "hex":
        result = hex_encode(payload)
    elif method == "multi":
        layers = args.layers or ["base64"]
        result = multi_layer_encode(payload, layers, key)
        print(f"{CYN}[*] Layer chain: {' → '.join(layers)}{RST}\n")
    else:
        print(f"{RED}[!] Unknown method: {method}{RST}")
        sys.exit(1)

    print(f"{GRN}[+] Encoded Output:{RST}")
    print(result["encoded"])
    print()
    print(f"{CYN}[i] Original length : {result['original_length']} B{RST}")
    print(f"{CYN}[i] Encoded length  : {result['encoded_length']} B{RST}")
    print(f"{CYN}[i] Size change     : {'+' if result['size_increase'] > 0 else ''}{result['size_increase']}%{RST}")


def cmd_decode(args):
    method = args.method.lower()
    encoded = args.encoded
    key = args.key or "K3Y"

    if method == "base64":
        decoded = base64_decode(encoded)
    elif method == "xor":
        decoded = xor_decode(encoded, key)
    elif method == "rot13":
        decoded = rot13_decode(encoded)
    elif method == "hex":
        decoded = hex_decode(encoded)
    else:
        print(f"{RED}[!] Unknown method: {method}{RST}")
        sys.exit(1)

    print(f"{GRN}[+] Decoded:{RST} {decoded}")


def cmd_obfuscate(args):
    print(BANNER)
    payload = args.payload

    if args.all:
        print(f"{CYN}[*] Applying ALL obfuscation techniques...{RST}\n")
        results = apply_all_obfuscations(payload)
        for r in results:
            print(f"{MAG}[{r['technique']}]{RST}")
            print(f"  {r.get('obfuscated','ERROR')[:120]}...")
            print()
        return

    technique = args.technique or "escape_hex"
    tech_map = {
        "random_char": lambda p: random_char_insertion(p),
        "char_split":  lambda p: char_split_concat(p),
        "reverse":     lambda p: reverse_transform(p),
        "escape_hex":  lambda p: escape_sequence_obfuscation(p, "hex"),
        "escape_unicode": lambda p: escape_sequence_obfuscation(p, "unicode"),
        "case_scramble": lambda p: case_scramble(p),
        "null_byte":   lambda p: null_byte_injection(p),
        "identifier_sub": lambda p: identifier_substitution(p),
    }

    if technique not in tech_map:
        print(f"{RED}[!] Unknown technique. Choose from: {', '.join(tech_map)}{RST}")
        sys.exit(1)

    result = tech_map[technique](payload)
    print(f"{CYN}[*] Technique: {BLD}{result['technique']}{RST}")
    print(f"\n{GRN}[+] Obfuscated Output:{RST}")
    print(result["obfuscated"])
    if result.get("reverse_note"):
        print(f"\n{YLW}[i] Reversal: {result['reverse_note']}{RST}")


def cmd_scan(args):
    print(BANNER)
    payload = args.payload
    result = run_signature_check(payload)

    verdict_color = RED if result["detected"] else GRN
    verdict_icon = "🚨 DETECTED" if result["detected"] else "✅ BYPASSED"

    print(f"\n{verdict_color}{BLD}  {verdict_icon}{RST}")
    print(f"  {CYN}Detection Rate: {result['detection_rate']}%{RST}")
    print(f"  {CYN}Signatures Hit: {result['match_count']} / {result['total_signatures']}{RST}")
    print(f"  {CYN}Entropy:        {result['entropy']['value']} ({result['entropy']['label']}){RST}")
    print(f"  {CYN}Note:           {result['entropy']['note']}{RST}")

    if result["signatures_matched"]:
        print(f"\n{RED}[!] Matched Signatures:{RST}")
        for s in result["signatures_matched"]:
            print(f"    [{s['severity']:8}] {s['signature_id']}")
            print(f"             Match: {repr(s['match'][:60])}")


def main():
    parser = argparse.ArgumentParser(
        prog="payloadforge",
        description="PayloadForge — Payload Encoder & Obfuscation Framework CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # encode
    p_enc = sub.add_parser("encode", help="Encode a payload")
    p_enc.add_argument("--payload", required=True, help="Payload string to encode")
    p_enc.add_argument("--method", default="base64",
                       choices=["base64","xor","rot13","hex","multi"],
                       help="Encoding method")
    p_enc.add_argument("--key", default="K3Y", help="XOR key (for XOR method)")
    p_enc.add_argument("--layers", nargs="+", default=["base64"],
                       help="Layers for multi method (e.g. rot13 base64 xor)")

    # decode
    p_dec = sub.add_parser("decode", help="Decode an encoded payload")
    p_dec.add_argument("--encoded", required=True, help="Encoded string to decode")
    p_dec.add_argument("--method", default="base64",
                       choices=["base64","xor","rot13","hex"])
    p_dec.add_argument("--key", default="K3Y", help="XOR key")

    # obfuscate
    p_obf = sub.add_parser("obfuscate", help="Apply obfuscation techniques")
    p_obf.add_argument("--payload", required=True)
    p_obf.add_argument("--technique", default="escape_hex",
                       choices=["random_char","char_split","reverse","escape_hex",
                                "escape_unicode","case_scramble","null_byte","identifier_sub"])
    p_obf.add_argument("--all", action="store_true", help="Apply ALL techniques")

    # scan
    p_scan = sub.add_parser("scan", help="Run signature scan on a payload")
    p_scan.add_argument("--payload", required=True)

    args = parser.parse_args()

    if args.command == "encode":   cmd_encode(args)
    elif args.command == "decode": cmd_decode(args)
    elif args.command == "obfuscate": cmd_obfuscate(args)
    elif args.command == "scan":   cmd_scan(args)


if __name__ == "__main__":
    main()
