"""
Unit Tests — PayloadForge Encoding & Obfuscation Framework

Run with:
  python -m pytest tests.py -v
  OR
  python tests.py
"""

import sys
import os
import unittest

# Ensure modules are importable
sys.path.insert(0, os.path.dirname(__file__))

from modules.encoder import (
    base64_encode, base64_decode,
    xor_encode, xor_decode,
    rot13_encode, rot13_decode,
    hex_encode, hex_decode,
    multi_layer_encode,
)
from modules.obfuscator import (
    random_char_insertion, random_char_remove,
    char_split_concat, char_split_join,
    reverse_transform,
    escape_sequence_obfuscation,
    case_scramble,
    null_byte_injection, null_byte_remove,
    identifier_substitution,
    apply_all_obfuscations,
)
from modules.evasion_tester import (
    run_signature_check, quick_scan, shannon_entropy, entropy_verdict
)


SAMPLE_PAYLOAD = "cmd.exe /c powershell -enc test123"
SIMPLE_TEXT    = "Hello World"


class TestBase64(unittest.TestCase):
    def test_encode_returns_dict(self):
        r = base64_encode(SIMPLE_TEXT)
        self.assertIn("encoded", r)
        self.assertEqual(r["method"], "Base64")

    def test_roundtrip(self):
        r = base64_encode(SIMPLE_TEXT)
        decoded = base64_decode(r["encoded"])
        self.assertEqual(decoded, SIMPLE_TEXT)

    def test_empty_string(self):
        r = base64_encode("")
        self.assertIsNotNone(r["encoded"])

    def test_special_chars(self):
        payload = "!@#$%^&*()_+\n\t"
        r = base64_encode(payload)
        self.assertEqual(base64_decode(r["encoded"]), payload)


class TestXOR(unittest.TestCase):
    def test_encode_returns_dict(self):
        r = xor_encode(SIMPLE_TEXT, "KEY")
        self.assertIn("encoded", r)
        self.assertEqual(r["method"], "XOR")

    def test_roundtrip(self):
        r = xor_encode(SIMPLE_TEXT, "MyKey123")
        decoded = xor_decode(r["encoded"], "MyKey123")
        self.assertEqual(decoded, SIMPLE_TEXT)

    def test_single_char_key(self):
        r = xor_encode("test", "A")
        self.assertEqual(xor_decode(r["encoded"], "A"), "test")

    def test_different_keys_differ(self):
        r1 = xor_encode(SIMPLE_TEXT, "key1")
        r2 = xor_encode(SIMPLE_TEXT, "key2")
        self.assertNotEqual(r1["encoded"], r2["encoded"])


class TestROT13(unittest.TestCase):
    def test_encode_returns_dict(self):
        r = rot13_encode(SIMPLE_TEXT)
        self.assertIn("encoded", r)

    def test_double_apply_returns_original(self):
        r1 = rot13_encode(SIMPLE_TEXT)
        r2 = rot13_decode(r1["encoded"])
        self.assertEqual(r2, SIMPLE_TEXT)

    def test_size_unchanged(self):
        r = rot13_encode(SIMPLE_TEXT)
        self.assertEqual(r["size_increase"], 0.0)


class TestHex(unittest.TestCase):
    def test_encode(self):
        r = hex_encode("ABC")
        self.assertEqual(r["encoded"], "414243")

    def test_roundtrip(self):
        r = hex_encode(SIMPLE_TEXT)
        self.assertEqual(hex_decode(r["encoded"]), SIMPLE_TEXT)


class TestMultiLayer(unittest.TestCase):
    def test_chain_two_layers(self):
        r = multi_layer_encode(SIMPLE_TEXT, ["rot13", "base64"])
        self.assertEqual(r["method"], "Multi-Layer")
        self.assertEqual(len(r["steps"]), 2)
        self.assertNotEqual(r["encoded"], SIMPLE_TEXT)

    def test_chain_three_layers(self):
        r = multi_layer_encode(SIMPLE_TEXT, ["base64", "xor", "rot13"], "K3Y")
        self.assertEqual(len(r["steps"]), 3)

    def test_unknown_layer_raises(self):
        with self.assertRaises(ValueError):
            multi_layer_encode(SIMPLE_TEXT, ["unknown_algo"])


class TestObfuscatorRandomChar(unittest.TestCase):
    def test_produces_longer_string(self):
        r = random_char_insertion(SIMPLE_TEXT, density=1.0)
        self.assertGreater(r["obfuscated_length"], r["original_length"])

    def test_reversible(self):
        r = random_char_insertion(SIMPLE_TEXT, density=0.5, marker="@@")
        recovered = random_char_remove(r["obfuscated"], marker="@@")
        self.assertEqual(recovered, SIMPLE_TEXT)


class TestObfuscatorCharSplit(unittest.TestCase):
    def test_split_produces_concat_expr(self):
        r = char_split_concat("hello", chunk_size=3)
        self.assertIn("+", r["obfuscated"])

    def test_reversible(self):
        r = char_split_concat("hello world", chunk_size=4)
        recovered = char_split_join(r["obfuscated"])
        self.assertEqual(recovered, "hello world")


class TestObfuscatorReversal(unittest.TestCase):
    def test_reversal(self):
        r = reverse_transform("ABCDE")
        self.assertEqual(r["obfuscated"], "EDCBA")

    def test_double_reversal(self):
        r1 = reverse_transform(SIMPLE_TEXT)
        r2 = reverse_transform(r1["obfuscated"])
        self.assertEqual(r2["obfuscated"], SIMPLE_TEXT)


class TestObfuscatorEscape(unittest.TestCase):
    def test_hex_escape(self):
        r = escape_sequence_obfuscation("A", mode="hex")
        self.assertEqual(r["obfuscated"], "\\x41")

    def test_unicode_escape(self):
        r = escape_sequence_obfuscation("A", mode="unicode")
        self.assertEqual(r["obfuscated"], "\\u0041")

    def test_unknown_mode_raises(self):
        with self.assertRaises(ValueError):
            escape_sequence_obfuscation("test", mode="bad_mode")


class TestObfuscatorNullByte(unittest.TestCase):
    def test_inserts_delimiter(self):
        r = null_byte_injection("ABC", delimiter="%00")
        self.assertEqual(r["obfuscated"], "A%00B%00C")

    def test_reversible(self):
        r = null_byte_injection(SIMPLE_TEXT)
        recovered = null_byte_remove(r["obfuscated"])
        self.assertEqual(recovered, SIMPLE_TEXT)


class TestObfuscatorCaseScramble(unittest.TestCase):
    def test_preserves_length(self):
        r = case_scramble(SIMPLE_TEXT)
        self.assertEqual(len(r["obfuscated"]), len(SIMPLE_TEXT))

    def test_lowered_matches_original(self):
        r = case_scramble(SIMPLE_TEXT)
        self.assertEqual(r["obfuscated"].lower(), SIMPLE_TEXT.lower())


class TestObfuscatorIdentifierSub(unittest.TestCase):
    def test_replaces_keyword(self):
        r = identifier_substitution("eval(cmd)")
        # "eval" and "cmd" should be replaced
        self.assertNotIn("eval", r["obfuscated"].lower())

    def test_no_op_on_clean_string(self):
        r = identifier_substitution("hello world foo bar")
        self.assertEqual(r["obfuscated"], "hello world foo bar")


class TestApplyAll(unittest.TestCase):
    def test_returns_list(self):
        results = apply_all_obfuscations(SIMPLE_TEXT)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

    def test_each_has_technique_field(self):
        results = apply_all_obfuscations(SIMPLE_TEXT)
        for r in results:
            self.assertIn("technique", r)


class TestEvasionTester(unittest.TestCase):
    def test_scan_detects_powershell(self):
        result = run_signature_check("powershell -enc ABC123")
        self.assertTrue(result["detected"])

    def test_scan_clean_payload(self):
        result = run_signature_check("hello beautiful world")
        # Should not match most signatures
        self.assertIsInstance(result["match_count"], int)

    def test_entropy_low(self):
        e = shannon_entropy("aaaa")
        self.assertLess(e, 1.0)

    def test_entropy_high(self):
        import random, string
        rand_str = "".join(random.choices(string.printable, k=500))
        e = shannon_entropy(rand_str)
        self.assertGreater(e, 4.0)

    def test_quick_scan_returns_verdict(self):
        result = quick_scan("normal text with no threats")
        self.assertIn("verdict", result)
        self.assertIn("detected", result)

    def test_verdict_structure(self):
        result = run_signature_check(SAMPLE_PAYLOAD)
        self.assertIn("verdict", result)
        self.assertIn("detection_rate", result)
        self.assertIn("entropy", result)
        self.assertIn("signatures_matched", result)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  PayloadForge — Unit Tests")
    print("=" * 60 + "\n")
    unittest.main(verbosity=2)
