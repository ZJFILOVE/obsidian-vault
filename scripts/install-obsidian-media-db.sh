#!/usr/bin/env bash
set -euo pipefail

VERSION="0.9.1"
PLUGIN_ID="obsidian-media-db-plugin"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLUGIN_DIR="$ROOT/.obsidian/plugins/$PLUGIN_ID"
BASE_URL="https://github.com/mProjectsCode/obsidian-media-db-plugin/releases/download/$VERSION"

mkdir -p "$PLUGIN_DIR"

for file in main.js manifest.json styles.css; do
  echo "Downloading $file ..."
  curl -fL "$BASE_URL/$file" -o "$PLUGIN_DIR/$file"
done

python - "$ROOT/.obsidian/community-plugins.json" "$PLUGIN_ID" <<'PY'
import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
plugin_id = sys.argv[2]
plugins = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
if plugin_id not in plugins:
    plugins.append(plugin_id)
path.write_text(json.dumps(plugins, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

echo
printf 'Media DB %s installed and enabled. Restart Obsidian.\n' "$VERSION"
printf 'Configured folders are already stored in %s/data.json\n' "$PLUGIN_DIR"
printf 'For TMDB movie/series search, add your API Read Access Token in Obsidian -> Settings -> Media DB.\n'
