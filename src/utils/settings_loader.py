import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    page_id: str
    before: str
    after: str
    base_url: str | None = None


def load_settings(path: Path) -> Settings:
    if not path.exists():
        raise FileNotFoundError(f"settings file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    missing = [key for key in ("page_id", "before", "after") if key not in data]
    if missing:
        raise ValueError(f"settings missing required keys: {', '.join(missing)}")
    return Settings(
        page_id=str(data["page_id"]).strip(),
        before=str(data["before"]),
        after=str(data["after"]),
        base_url=str(data.get("base_url")).strip() if data.get("base_url") else None,
    )
