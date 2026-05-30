"""
Obfuscator Module — String obfuscation techniques for educational research.

Techniques implemented:
  • Random character insertion (junk bytes)
  • Character splitting & concatenation notation
  • Reversal transform
  • Escape-sequence obfuscation (hex/unicode)
  • Case scrambling
  • Null-byte injection notation
  • Variable-name substitution (identifier scrambling)
"""

import random
import string


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _random_junk(length: int = 1) -> str:
    """Return a string of random printable non-alphanumeric characters."""
    chars = "!@#$%^&*()-_=+[]{}|;':,.<>?/~`\\"
    return "".join(random.choice(chars) for _ in range(length))


# ---------------------------------------------------------------------------
# Technique 1: Random Character Insertion
# ---------------------------------------------------------------------------

def random_char_insertion(payload: str, density: float = 0.2, marker: str = "@@") -> dict:
    """
    Insert junk characters at random positions, wrapped in a marker so they
    can be stripped back out (reversible).

    density: probability of inserting a junk group after each character (0–1).
    """
    result = []
    insertions = 0
    for ch in payload:
        result.append(ch)
        if random.random() < density:
            junk = _random_junk(random.randint(1, 3))
            result.append(f"{marker}{junk}{marker}")
            insertions += 1

    obfuscated = "".join(result)
    return {
        "technique": "Random Character Insertion",
        "original": payload,
        "obfuscated": obfuscated,
        "insertions": insertions,
        "marker": marker,
        "reversible": True,
        "reverse_note": f"Strip all substrings matching /{marker}.*?{marker}/ regex",
        "original_length": len(payload),
        "obfuscated_length": len(obfuscated),
    }


def random_char_remove(obfuscated: str, marker: str = "@@") -> str:
    """Reverse random_char_insertion by stripping marker-wrapped junk."""
    import re
    pattern = re.escape(marker) + r".*?" + re.escape(marker)
    return re.sub(pattern, "", obfuscated)


# ---------------------------------------------------------------------------
# Technique 2: Character Splitting & Concatenation
# ---------------------------------------------------------------------------

def char_split_concat(payload: str, chunk_size: int = 3) -> dict:
    """
    Split the payload into chunks and represent it as a string concat expression.
    Example: "hello" → '"hel" + "lo"'
    """
    chunks = [payload[i:i+chunk_size] for i in range(0, len(payload), chunk_size)]
    concat_expr = " + ".join(f'"{chunk}"' for chunk in chunks)
    return {
        "technique": "Character Split & Concatenation",
        "original": payload,
        "obfuscated": concat_expr,
        "chunks": chunks,
        "chunk_size": chunk_size,
        "reversible": True,
        "reverse_note": "Evaluate or join the string literals",
        "original_length": len(payload),
        "obfuscated_length": len(concat_expr),
    }


def char_split_join(concat_expr: str) -> str:
    """Reverse: evaluate a concat expression."""
    import re
    parts = re.findall(r'"(.*?)"', concat_expr)
    return "".join(parts)


# ---------------------------------------------------------------------------
# Technique 3: Reversal Transform
# ---------------------------------------------------------------------------

def reverse_transform(payload: str) -> dict:
    """Reverse the entire payload string. Applying twice returns the original."""
    reversed_payload = payload[::-1]
    return {
        "technique": "Reversal Transform",
        "original": payload,
        "obfuscated": reversed_payload,
        "reversible": True,
        "reverse_note": "Apply reversal again: payload[::-1]",
        "original_length": len(payload),
        "obfuscated_length": len(reversed_payload),
    }


# ---------------------------------------------------------------------------
# Technique 4: Escape-Sequence Obfuscation
# ---------------------------------------------------------------------------

def escape_sequence_obfuscation(payload: str, mode: str = "hex") -> dict:
    """
    Replace each character with its escape-sequence representation.

    mode='hex'     → \\x41 style
    mode='unicode' → \\u0041 style
    mode='octal'   → \\101 style
    """
    if mode == "hex":
        obfuscated = "".join(f"\\x{ord(c):02x}" for c in payload)
        note = "Unescape \\xNN sequences"
    elif mode == "unicode":
        obfuscated = "".join(f"\\u{ord(c):04x}" for c in payload)
        note = "Unescape \\uNNNN sequences"
    elif mode == "octal":
        obfuscated = "".join(f"\\{ord(c):03o}" for c in payload)
        note = "Unescape \\NNN octal sequences"
    else:
        raise ValueError(f"Unknown escape mode: {mode}")

    return {
        "technique": f"Escape-Sequence Obfuscation ({mode})",
        "original": payload,
        "obfuscated": obfuscated,
        "mode": mode,
        "reversible": True,
        "reverse_note": note,
        "original_length": len(payload),
        "obfuscated_length": len(obfuscated),
    }


def escape_sequence_decode(obfuscated: str, mode: str = "hex") -> str:
    """Reverse escape-sequence obfuscation."""
    if mode == "hex":
        return bytes.fromhex(obfuscated.replace("\\x", "")).decode("utf-8")
    elif mode == "unicode":
        return obfuscated.encode("utf-8").decode("unicode_escape")
    elif mode == "octal":
        import re
        parts = re.findall(r'\\([0-7]{3})', obfuscated)
        return "".join(chr(int(p, 8)) for p in parts)
    else:
        raise ValueError(f"Unknown escape mode: {mode}")


# ---------------------------------------------------------------------------
# Technique 5: Case Scrambling
# ---------------------------------------------------------------------------

def case_scramble(payload: str) -> dict:
    """
    Randomly alternate character case. Useful for case-insensitive signature
    evasion on text-based patterns.
    """
    obfuscated = "".join(
        c.upper() if random.random() > 0.5 else c.lower() for c in payload
    )
    return {
        "technique": "Case Scrambling",
        "original": payload,
        "obfuscated": obfuscated,
        "reversible": False,
        "reverse_note": "Apply .lower() or .upper() to normalize",
        "original_length": len(payload),
        "obfuscated_length": len(obfuscated),
    }


# ---------------------------------------------------------------------------
# Technique 6: Null-Byte / Delimiter Injection
# ---------------------------------------------------------------------------

def null_byte_injection(payload: str, delimiter: str = "%00") -> dict:
    """
    Insert a null-byte representation between each character.
    Simulates URL/HTTP null-byte injection patterns.
    """
    obfuscated = delimiter.join(payload)
    return {
        "technique": "Null-Byte / Delimiter Injection",
        "original": payload,
        "obfuscated": obfuscated,
        "delimiter": delimiter,
        "reversible": True,
        "reverse_note": f"Split on '{delimiter}' and rejoin",
        "original_length": len(payload),
        "obfuscated_length": len(obfuscated),
    }


def null_byte_remove(obfuscated: str, delimiter: str = "%00") -> str:
    return obfuscated.replace(delimiter, "")


# ---------------------------------------------------------------------------
# Technique 7: Identifier / Variable Substitution
# ---------------------------------------------------------------------------

_VAR_CHARS = string.ascii_lowercase + string.digits

def _random_var(length: int = 8) -> str:
    """Generate a random-looking variable name."""
    return "_" + "".join(random.choice(_VAR_CHARS) for _ in range(length))


def identifier_substitution(payload: str) -> dict:
    """
    Replace common identifiable keywords with random-looking variable names.
    Returns a mapping for reversibility.
    """
    keywords = [
        "cmd", "exec", "shell", "system", "eval", "script",
        "payload", "malware", "hack", "exploit", "inject",
        "download", "upload", "connect", "socket", "bind",
    ]
    mapping = {}
    obfuscated = payload
    for kw in keywords:
        if kw.lower() in payload.lower():
            var = _random_var()
            mapping[var] = kw
            import re
            obfuscated = re.sub(re.escape(kw), var, obfuscated, flags=re.IGNORECASE)

    return {
        "technique": "Identifier Substitution",
        "original": payload,
        "obfuscated": obfuscated,
        "mapping": mapping,
        "reversible": True,
        "reverse_note": "Apply reverse mapping dictionary to restore original identifiers",
        "original_length": len(payload),
        "obfuscated_length": len(obfuscated),
    }


# ---------------------------------------------------------------------------
# Apply All Techniques (batch mode)
# ---------------------------------------------------------------------------

def apply_all_obfuscations(payload: str, xor_key: str = "K") -> list:
    """
    Apply every obfuscation technique and return a list of results.
    Useful for comparative analysis.
    """
    results = []
    try:
        results.append(random_char_insertion(payload, density=0.25))
    except Exception as e:
        results.append({"technique": "Random Char Insertion", "error": str(e)})

    try:
        results.append(char_split_concat(payload, chunk_size=4))
    except Exception as e:
        results.append({"technique": "Char Split Concat", "error": str(e)})

    try:
        results.append(reverse_transform(payload))
    except Exception as e:
        results.append({"technique": "Reversal Transform", "error": str(e)})

    try:
        results.append(escape_sequence_obfuscation(payload, mode="hex"))
    except Exception as e:
        results.append({"technique": "Escape Sequence (hex)", "error": str(e)})

    try:
        results.append(escape_sequence_obfuscation(payload, mode="unicode"))
    except Exception as e:
        results.append({"technique": "Escape Sequence (unicode)", "error": str(e)})

    try:
        results.append(case_scramble(payload))
    except Exception as e:
        results.append({"technique": "Case Scramble", "error": str(e)})

    try:
        results.append(null_byte_injection(payload))
    except Exception as e:
        results.append({"technique": "Null-Byte Injection", "error": str(e)})

    try:
        results.append(identifier_substitution(payload))
    except Exception as e:
        results.append({"technique": "Identifier Substitution", "error": str(e)})

    return results
