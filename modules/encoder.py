"""
Encoder Module — Base64, XOR, ROT13 and multi-layer encoding.

This module is intended strictly for educational/research purposes
in controlled lab environments.
"""

import base64
import codecs
import binascii
from typing import Union


# ---------------------------------------------------------------------------
# Base64
# ---------------------------------------------------------------------------

def base64_encode(payload: str) -> dict:
    """Encode a payload string using standard Base64."""
    encoded_bytes = base64.b64encode(payload.encode("utf-8"))
    encoded_str = encoded_bytes.decode("utf-8")
    return {
        "method": "Base64",
        "original": payload,
        "encoded": encoded_str,
        "original_length": len(payload),
        "encoded_length": len(encoded_str),
        "size_increase": round((len(encoded_str) / max(len(payload), 1) - 1) * 100, 2),
        "reversible": True,
        "decode_cmd": "base64.b64decode(encoded).decode('utf-8')",
    }


def base64_decode(encoded: str) -> str:
    """Decode a Base64-encoded string back to plain text."""
    try:
        padding = 4 - len(encoded) % 4
        if padding != 4:
            encoded += "=" * padding
        return base64.b64decode(encoded.encode("utf-8")).decode("utf-8")
    except Exception as exc:
        raise ValueError(f"Base64 decode error: {exc}")


# ---------------------------------------------------------------------------
# XOR
# ---------------------------------------------------------------------------

def xor_encode(payload: str, key: str) -> dict:
    """
    XOR-encode a payload with a user-supplied key (multi-byte key cycling).
    Output is returned as a hex string for safe transport.
    """
    if not key:
        key = "A"
    payload_bytes = payload.encode("utf-8")
    key_bytes = (key * ((len(payload_bytes) // len(key)) + 1)).encode("utf-8")

    xored = bytes(b ^ k for b, k in zip(payload_bytes, key_bytes))
    hex_output = xored.hex()
    b64_output = base64.b64encode(xored).decode("utf-8")  # safe transport layer

    return {
        "method": "XOR",
        "original": payload,
        "key": key,
        "encoded_hex": hex_output,
        "encoded_b64": b64_output,
        "encoded": b64_output,          # primary encoded form
        "original_length": len(payload),
        "encoded_length": len(hex_output),
        "size_increase": round((len(hex_output) / max(len(payload), 1) - 1) * 100, 2),
        "reversible": True,
        "decode_cmd": "bytes([b ^ k for b, k in zip(bytes.fromhex(hex_str), cycle(key.encode()))]).decode()",
    }


def xor_decode(encoded_b64: str, key: str) -> str:
    """Decode a Base64-wrapped XOR-encoded string."""
    if not key:
        key = "A"
    raw = base64.b64decode(encoded_b64.encode("utf-8"))
    key_bytes = (key * ((len(raw) // len(key)) + 1)).encode("utf-8")
    decoded = bytes(b ^ k for b, k in zip(raw, key_bytes))
    return decoded.decode("utf-8")


# ---------------------------------------------------------------------------
# ROT13
# ---------------------------------------------------------------------------

def rot13_encode(payload: str) -> dict:
    """Apply ROT13 substitution cipher. Applying twice returns the original."""
    encoded = codecs.encode(payload, "rot_13")
    return {
        "method": "ROT13",
        "original": payload,
        "encoded": encoded,
        "original_length": len(payload),
        "encoded_length": len(encoded),
        "size_increase": 0.0,
        "reversible": True,
        "decode_cmd": "codecs.encode(encoded, 'rot_13')  # applying ROT13 twice reverses it",
    }


def rot13_decode(encoded: str) -> str:
    """Decode a ROT13-encoded string (same operation as encoding)."""
    return codecs.encode(encoded, "rot_13")


# ---------------------------------------------------------------------------
# Multi-layer encoding
# ---------------------------------------------------------------------------

_ENCODER_MAP = {
    "base64": base64_encode,
    "xor":    xor_encode,
    "rot13":  rot13_encode,
}

def multi_layer_encode(payload: str, layers: list, xor_key: str = "K3Y") -> dict:
    """
    Apply multiple encoding layers in sequence.
    `layers` is an ordered list of method names, e.g. ["rot13", "base64", "xor"].
    """
    current = payload
    steps = []

    for layer in layers:
        layer_lower = layer.lower()
        if layer_lower == "base64":
            result = base64_encode(current)
        elif layer_lower == "xor":
            result = xor_encode(current, xor_key)
        elif layer_lower == "rot13":
            result = rot13_encode(current)
        else:
            raise ValueError(f"Unknown encoding method: {layer}")

        steps.append({
            "layer": layer_lower,
            "input": current,
            "output": result["encoded"],
        })
        current = result["encoded"]

    return {
        "method": "Multi-Layer",
        "layers": layers,
        "original": payload,
        "encoded": current,
        "steps": steps,
        "original_length": len(payload),
        "encoded_length": len(current),
        "size_increase": round((len(current) / max(len(payload), 1) - 1) * 100, 2),
        "reversible": True,
    }


# ---------------------------------------------------------------------------
# Hex encoding (bonus)
# ---------------------------------------------------------------------------

def hex_encode(payload: str) -> dict:
    """Encode payload as hex string."""
    encoded = payload.encode("utf-8").hex()
    return {
        "method": "Hex",
        "original": payload,
        "encoded": encoded,
        "original_length": len(payload),
        "encoded_length": len(encoded),
        "size_increase": round((len(encoded) / max(len(payload), 1) - 1) * 100, 2),
        "reversible": True,
        "decode_cmd": "bytes.fromhex(encoded).decode('utf-8')",
    }


def hex_decode(encoded: str) -> str:
    return bytes.fromhex(encoded).decode("utf-8")
