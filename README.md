# 2026-tv

Confluence Data Center のページ本文に対して、指定したワードの置換を行うツールです。

## 使い方

1. `settings.json` を作成します（例: `settings.sample.json`）。
2. 実行すると、Confluence のユーザー名とパスワードを入力します。
   - 入力値は `~/.config/2026-tv/credentials.json` に保存され、次回起動時に初期値として利用されます。
   - パスワードは平文保存されるため、取り扱いに注意してください。

```bash
python src/cli.py --settings settings.json --base-url https://confluence.example.com
```

`base_url` は `settings.json` にも指定できます。
