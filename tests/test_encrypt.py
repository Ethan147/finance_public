import base64
import unittest

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from scripts import encrypt as en


class TestDeriveKey(unittest.TestCase):

    def test_key_derivation(self) -> None:
        password = "my_secure_password"
        expected_key = self._manual_key_derivation(password)

        derived_key = en.derive_key(password)
        self.assertEqual(derived_key, expected_key)

    def test_empty_password(self) -> None:
        password = ""
        expected_key = self._manual_key_derivation(password)

        derived_key = en.derive_key(password)
        self.assertEqual(derived_key, expected_key)

    def test_same_key_for_same_password(self) -> None:
        password = "repeatable_password"
        key1 = en.derive_key(password)
        key2 = en.derive_key(password)

        self.assertEqual(key1, key2)

    def test_different_passwords(self) -> None:
        password1 = "password_one"
        password2 = "password_two"

        key1 = en.derive_key(password1)
        key2 = en.derive_key(password2)

        self.assertNotEqual(key1, key2)

    def _manual_key_derivation(self, password: str) -> bytes:
        """Manually derive the key using the same logic as derive_key."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"",  # Same empty salt as in derive_key
            iterations=100000,
            backend=default_backend(),
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
