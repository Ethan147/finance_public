""" Series of utilities for encrypting / decrypting the spreedsheet with personal expenses, for privacy """

import base64
import getpass
import os
from typing import Any

import click
import pyexcel_ods3 as ods
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from utils import file_settings, utils


def derive_key(password: str) -> bytes:
    """Derives a key from the given password."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"",  # Empty salt for simplicity (single user private key)
        iterations=100000,
        backend=default_backend(),
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key


def encrypt_file(input_file: str, output_file: str, key: bytes) -> None:
    cipher_suite = Fernet(key)
    with open(input_file, "rb") as file:
        file_data = file.read()
    encrypted_data = cipher_suite.encrypt(file_data)
    with open(output_file, "wb") as file:
        file.write(encrypted_data)


def decrypt_file(input_file: str, output_file: str, key: bytes) -> None:
    cipher_suite = Fernet(key)
    with open(input_file, "rb") as file:
        encrypted_data = file.read()
    decrypted_data = cipher_suite.decrypt(encrypted_data)
    with open(output_file, "wb") as file:
        file.write(decrypted_data)


@click.command()
def encrypt() -> None:
    """Encrypt the untracked finance.ods to the tracked finance_encrypted.ods file"""
    password = getpass.getpass(prompt="Enter password: ")
    key = derive_key(password)
    encrypt_file(
        file_settings.decrypted_file_name(), file_settings.encrypted_file_name(), key
    )
    utils.print_status(f"File encrypted successfully with password {password}.")


@click.command()
def decrypt() -> None:
    """Decrypt the tracked finance_encrypted.ods file to the untracked finance.ods file"""
    password = getpass.getpass(prompt="Enter password: ")
    key = derive_key(password)
    decrypt_file(
        file_settings.encrypted_file_name(), file_settings.decrypted_file_name(), key
    )
    utils.open(file_settings.decrypted_file_name())
    utils.print_status("File decrypted successfully.")
