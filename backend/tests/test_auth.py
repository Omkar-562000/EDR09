from __future__ import annotations

import unittest

from backend.edr.auth import hash_password, verify_password


class PasswordVerificationTests(unittest.TestCase):
    def test_verify_password_accepts_valid_hash(self) -> None:
        password_hash = hash_password("password123")

        self.assertTrue(verify_password("password123", password_hash))

    def test_verify_password_rejects_wrong_password(self) -> None:
        password_hash = hash_password("password123")

        self.assertFalse(verify_password("wrong-password", password_hash))

    def test_verify_password_rejects_malformed_hash_without_crashing(self) -> None:
        malformed_hashes = [
            "",
            "plain-text-password",
            ":missing-salt",
            "missing-digest:",
            "not-base64:not-base64",
        ]

        for password_hash in malformed_hashes:
            with self.subTest(password_hash=password_hash):
                self.assertFalse(verify_password("password123", password_hash))


if __name__ == "__main__":
    unittest.main()
