#!/bin/sh
# Lädt die neueste stabile Blender-Version für Linux x64 herunter.
# Wird beim Docker-Build ausgeführt damit immer die aktuelle Version vorhanden ist.

set -e

python3 - <<'PYEOF'
import urllib.request, re, sys

base = "https://download.blender.org/release/"

# Alle verfügbaren Major.Minor-Serien auflisten
idx = urllib.request.urlopen(base).read().decode()
series_list = sorted(set(re.findall(r'Blender(\d+\.\d+)/', idx)),
                     key=lambda v: [int(x) for x in v.split('.')])
if not series_list:
    sys.exit("Keine Blender-Releases gefunden")

series = series_list[-1]
series_url = f"{base}Blender{series}/"

# Neuesten Patch in dieser Serie finden
idx2 = urllib.request.urlopen(series_url).read().decode()
patches = re.findall(
    rf'blender-{re.escape(series)}\.(\d+)-linux-x64\.tar\.xz', idx2)
if not patches:
    sys.exit(f"Kein Linux-Build für Blender {series} gefunden")

patch = sorted(patches, key=int)[-1]
ver = f"{series}.{patch}"
url = f"{series_url}blender-{ver}-linux-x64.tar.xz"

print(f">>> Lade Blender {ver} von {url}", flush=True)
urllib.request.urlretrieve(url, "/tmp/blender.tar.xz")
print(f">>> Download fertig", flush=True)
PYEOF

tar -xf /tmp/blender.tar.xz -C /opt/
BDIR=$(ls -dt /opt/blender-*-linux-x64 | head -1)
ln -sf "$BDIR/blender" /usr/local/bin/blender
rm /tmp/blender.tar.xz
echo ">>> Blender installiert: $(blender --version 2>&1 | head -1)"
