import subprocess, re, sys

base = "https://download.blender.org/release/"

def wget(url, output=None):
    cmd = ["wget", "-q", "--no-check-certificate", url]
    if output:
        cmd += ["-O", output]
    else:
        cmd += ["-O", "-"]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        sys.exit(f"wget failed for {url}: {r.stderr.decode()[:300]}")
    return r.stdout.decode(errors="replace") if not output else None

# 1. List available series
print("Fetching Blender release index...", flush=True)
idx = wget(base)
series_list = sorted(
    set(re.findall(r"Blender(\d+\.\d+)/", idx)),
    key=lambda v: [int(x) for x in v.split(".")],
)
if not series_list:
    sys.exit(f"No Blender series found. Response snippet: {idx[:400]}")

series = series_list[-1]
print(f"Latest series: Blender {series}", flush=True)

# 2. Find newest patch in that series
series_url = base + "Blender" + series + "/"
idx2 = wget(series_url)
escaped = series.replace(".", r"\.")
patches = re.findall(r"blender-" + escaped + r"\.(\d+)-linux-x64\.tar\.xz", idx2)
if not patches:
    sys.exit(f"No linux-x64 build for Blender {series}. Response: {idx2[:400]}")

ver = series + "." + sorted(patches, key=int)[-1]
url = series_url + "blender-" + ver + "-linux-x64.tar.xz"
print(f"Downloading Blender {ver} ...", flush=True)

# 3. Download
wget(url, output="/tmp/blender.tar.xz")
print("Download complete.", flush=True)
