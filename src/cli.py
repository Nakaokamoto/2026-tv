import argparse
import getpass
import json
from pathlib import Path

from services.confluence_client import ConfluenceClient
from utils.settings_loader import load_settings

DEFAULT_SETTINGS_PATH = Path("settings.json")
DEFAULT_CONFIG_DIR = Path.home() / ".config" / "2026-tv"
DEFAULT_CREDENTIALS_PATH = DEFAULT_CONFIG_DIR / "credentials.json"


def load_credentials(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_credentials(path: Path, username: str, password: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"username": username, "password": password}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


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

    stored = load_credentials(args.credentials)
    username = prompt_with_default("Confluence username", stored.get("username"))

    password_prompt = "Confluence password (leave blank to use stored): "
    password = getpass.getpass(password_prompt)
    if not password:
        password = stored.get("password", "")
    if not password:
        raise ValueError("Password is required.")

    save_credentials(args.credentials, username, password)

    client = ConfluenceClient(base_url, username, password)
    page = client.get_page(settings.page_id)
    if settings.before not in page.body_storage:
        raise ValueError("The target word was not found in the page body.")
    new_body = page.body_storage.replace(settings.before, settings.after)
    client.update_page(page, new_body)
    print("Page updated successfully.")


if __name__ == "__main__":
    main()
