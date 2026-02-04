import argparse
import getpass
import json
import os
from pathlib import Path

from cryptography.fernet import Fernet

from services.confluence_client import ConfluenceClient
from utils.settings_loader import load_settings

DEFAULT_SETTINGS_PATH = Path("settings.json")
DEFAULT_CONFIG_DIR = Path.home() / ".config" / "2026-tv"
DEFAULT_CREDENTIALS_PATH = DEFAULT_CONFIG_DIR / "credentials.json"
DEFAULT_KEY_PATH = DEFAULT_CONFIG_DIR / "credentials.key"


def load_or_create_key(path: Path) -> bytes:
    if path.exists():
        return path.read_bytes()
    key = Fernet.generate_key()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(key)
    os.chmod(path, 0o600)
    return key


def encrypt_password(password: str, key: bytes) -> str:
    fernet = Fernet(key)
    token = fernet.encrypt(password.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_password(token: str, key: bytes) -> str:
    fernet = Fernet(key)
    return fernet.decrypt(token.encode("utf-8")).decode("utf-8")


def load_credentials(path: Path, key: bytes) -> dict:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if "password" in data and data["password"]:
        data["password"] = decrypt_password(data["password"], key)
    return data


def save_credentials(path: Path, username: str, password: str, key: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"username": username, "password": encrypt_password(password, key)}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.chmod(path, 0o600)


def prompt_with_default(label: str, default: str | None) -> str:
    if default:
        value = input(f"{label} [{default}]: ").strip()
        return value or default
    return input(f"{label}: ").strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Confluence page word replace tool")
    parser.add_argument(
        "--settings",
        type=Path,
        default=DEFAULT_SETTINGS_PATH,
        help="Path to settings.json",
    )
    parser.add_argument("--base-url", type=str, help="Confluence base URL")
    parser.add_argument(
        "--credentials",
        type=Path,
        default=DEFAULT_CREDENTIALS_PATH,
        help="Path to stored credentials",
    )
    args = parser.parse_args()

    settings = load_settings(args.settings)
    base_url = args.base_url or settings.base_url
    if not base_url:
        base_url = prompt_with_default("Confluence base URL", None)

    key = load_or_create_key(DEFAULT_KEY_PATH)
    stored = load_credentials(args.credentials, key)
    username = prompt_with_default("Confluence username", stored.get("username"))

    password_prompt = "Confluence password (leave blank to use stored): "
    password = getpass.getpass(password_prompt)
    if not password:
        password = stored.get("password", "")
    if not password:
        raise ValueError("Password is required.")

    save_credentials(args.credentials, username, password, key)

    client = ConfluenceClient(base_url, username, password)
    page = client.get_page(settings.page_id)
    if settings.before not in page.body_storage:
        raise ValueError("The target word was not found in the page body.")
    new_body = page.body_storage.replace(settings.before, settings.after)
    client.update_page(page, new_body)
    print("Page updated successfully.")


if __name__ == "__main__":
    main()
