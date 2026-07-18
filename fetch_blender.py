import urllib.request, re, sys

base = "https://download.blender.org/release/"

idx = urllib.request.urlopen(base).read().decode()
series_list = sorted(
    set(re.findall(r"Blender(\d+\.\d+)/", idx)),
    key=lambda v: [int(x) for x in v.split(".")],
)
if not series_list:
    sys.exit("No Blender releases found on download.blender.org")

series = series_list[-1]
series_url = base + "Blender" + series + "/"
idx2 = urllib.request.urlopen(series_url).read().decode()
escaped = series.replace(".", r"\.")
patches = re.findall(r"blender-" + escaped + r"\.(\d+)-linux-x64\.tar\.xz", idx2)
if not patches:
    sys.exit(f"No Linux x64 build found for Blender {series}")

ver = series + "." + sorted(patches, key=int)[-1]
url = series_url + "blender-" + ver + "-linux-x64.tar.xz"
print(f"Downloading Blender {ver} from {url}", flush=True)
urllib.request.urlretrieve(url, "/tmp/blender.tar.xz")
print("Download complete.", flush=True)
