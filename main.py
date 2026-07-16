#!/usr/bin/env python3
"""Universal File Converter — Web Server (FastAPI)"""
import os
import base64
import tempfile
import zipfile
import io
import json
import time
import urllib.request
import urllib.parse
from collections import defaultdict
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse

try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    _limiter = Limiter(key_func=get_remote_address)
    _RATE_LIMIT = True
except ImportError:
    _limiter = None
    _RATE_LIMIT = False

import converter as conv

MAX_MB = int(os.getenv("MAX_FILE_MB", "500"))
STATS_FILE = Path(__file__).parent / "stats.json"

# ── Stats ─────────────────────────────────────────────────────────────────────
def _load_stats():
    if STATS_FILE.exists():
        try:
            return json.loads(STATS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"conversions": [], "errors": []}

def _save_stats(data: dict):
    try:
        STATS_FILE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

def _log_conversion(src_fmt: str, tgt_fmt: str, size_bytes: int, ok: bool,
                    steps: list = None, error: str = None, source: str = "upload"):
    data = _load_stats()
    entry = {
        "ts": int(time.time()),
        "src": src_fmt,
        "tgt": tgt_fmt,
        "size": size_bytes,
        "ok": ok,
        "source": source,
    }
    if steps:
        entry["steps"] = steps
    if error:
        entry["error"] = error
    if ok:
        data["conversions"].append(entry)
    else:
        data["errors"].append(entry)
    _save_stats(data)

app = FastAPI(title="Universal Converter")

if _RATE_LIMIT:
    app.state.limiter = _limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "formats": len(conv.ALL_FORMATS),
        "ffmpeg": conv._FFMPEG,
        "libreoffice": bool(conv._SOFFICE),
        "blender": conv._BLENDER,
        "pandoc": conv._PANDOC,
        "pillow": conv._PIL,
        "pandas": conv._PANDAS,
        "embroidery": conv._PYEMB,
        "rembg": conv._REMBG,
    }


@app.get("/api/formats")
def get_formats(fmt: str = None):
    if fmt:
        n = conv.norm(fmt)
        targets = conv.list_targets(n)
        return {"source": n, "targets": targets, "all": conv.ALL_FORMATS}
    return {"all": sorted(conv.ALL_FORMATS)}


@app.post("/api/convert")
@(_limiter.limit("30/minute") if _RATE_LIMIT else lambda f: f)
async def api_convert(
    request: Request,
    file: UploadFile = File(...),
    target_fmt: str = Form(...),
    quality: Optional[int] = Form(None),
    resize_w: Optional[int] = Form(None),
    resize_h: Optional[int] = Form(None),
):
    data = await file.read()
    if len(data) > MAX_MB * 1024 * 1024:
        raise HTTPException(413, f"Datei zu groß (max {MAX_MB} MB)")

    filename = file.filename or "upload"
    suffix = Path(filename).suffix or ".bin"
    fd, tmp_path = tempfile.mkstemp(suffix=suffix)
    kw = {k: v for k, v in {"quality": quality, "resize_w": resize_w, "resize_h": resize_h}.items() if v is not None}
    src_ext = Path(filename).suffix.lstrip(".").lower() or "bin"
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        result = conv.convert(tmp_path, target_fmt, **kw)
        if "error" in result and "result_b64" not in result:
            _log_conversion(src_ext, target_fmt, len(data), False, error=result["error"])
            raise HTTPException(422, result["error"])
        _log_conversion(src_ext, target_fmt, result.get("size_bytes", 0), True,
                        steps=result.get("steps"), source="upload")
        return result
    finally:
        try: os.unlink(tmp_path)
        except OSError: pass


@app.post("/api/convert-url")
async def api_convert_url(
    url: str = Form(...),
    target_fmt: str = Form(...),
    quality: Optional[int] = Form(None),
    resize_w: Optional[int] = Form(None),
    resize_h: Optional[int] = Form(None),
):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(400, "Nur http/https URLs erlaubt")

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read(MAX_MB * 1024 * 1024 + 1)
    except Exception as e:
        raise HTTPException(422, f"URL konnte nicht geladen werden: {e}")

    if len(data) > MAX_MB * 1024 * 1024:
        raise HTTPException(413, f"Datei zu groß (max {MAX_MB} MB)")

    filename = Path(parsed.path).name or "download"
    suffix = Path(filename).suffix or ".bin"
    fd, tmp_path = tempfile.mkstemp(suffix=suffix)
    kw = {k: v for k, v in {"quality": quality, "resize_w": resize_w, "resize_h": resize_h}.items() if v is not None}
    src_ext = Path(filename).suffix.lstrip(".").lower() or "bin"
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        result = conv.convert(tmp_path, target_fmt, **kw)
        result["source_filename"] = filename
        if "error" in result and "result_b64" not in result:
            _log_conversion(src_ext, target_fmt, len(data), False, error=result["error"])
            raise HTTPException(422, result["error"])
        _log_conversion(src_ext, target_fmt, result.get("size_bytes", 0), True,
                        steps=result.get("steps"), source="url")
        return result
    finally:
        try: os.unlink(tmp_path)
        except OSError: pass


@app.get("/api/stats")
def get_stats():
    """Betreiber-Statistik: Konvertierungen, Formate, Fehler."""
    data = _load_stats()
    convs = data.get("conversions", [])
    errs  = data.get("errors", [])

    pair_counts: dict = defaultdict(int)
    src_counts:  dict = defaultdict(int)
    tgt_counts:  dict = defaultdict(int)
    bytes_total  = 0
    by_month:    dict = defaultdict(lambda: {"ok": 0, "err": 0})

    for c in convs:
        pair_counts[f"{c['src']}->{c['tgt']}"] += 1
        src_counts[c["src"]] += 1
        tgt_counts[c["tgt"]] += 1
        bytes_total += c.get("size", 0)
        month = time.strftime("%Y-%m", time.localtime(c["ts"]))
        by_month[month]["ok"] += 1

    for e in errs:
        month = time.strftime("%Y-%m", time.localtime(e["ts"]))
        by_month[month]["err"] += 1

    # All months sorted chronologically, no cutoff
    by_month_list = sorted(
        [{"month": m, "ok": v["ok"], "err": v["err"]} for m, v in by_month.items()],
        key=lambda x: x["month"]
    )

    top_pairs = sorted(pair_counts.items(), key=lambda x: -x[1])[:20]
    top_src   = sorted(src_counts.items(),  key=lambda x: -x[1])[:10]
    top_tgt   = sorted(tgt_counts.items(),  key=lambda x: -x[1])[:10]

    # Recent: last 50, merged and sorted by timestamp
    all_recent = sorted(
        convs[-500:] + [{"ok": False, **e} for e in errs[-100:]],
        key=lambda x: x["ts"]
    )[-50:]

    return {
        "total_ok":    len(convs),
        "total_err":   len(errs),
        "bytes_total": bytes_total,
        "top_pairs":   top_pairs,
        "top_src":     top_src,
        "top_tgt":     top_tgt,
        "by_month":    by_month_list,
        "recent":      all_recent,
    }


@app.get("/api/stats/month")
def get_stats_month(m: str):
    """Detail-Statistik für einen Monat: tagesweise Breakdown nach Format-Paaren."""
    import calendar
    data   = _load_stats()
    convs  = [c for c in data.get("conversions", []) if time.strftime("%Y-%m", time.localtime(c["ts"])) == m]
    errs   = [e for e in data.get("errors",  [])    if time.strftime("%Y-%m", time.localtime(e["ts"])) == m]

    pair_counts: dict = defaultdict(int)
    src_counts:  dict = defaultdict(int)
    tgt_counts:  dict = defaultdict(int)
    bytes_total  = 0
    day_ok:      dict = defaultdict(int)
    day_err:     dict = defaultdict(int)
    day_pairs:   dict = defaultdict(lambda: defaultdict(int))

    for c in convs:
        pair = f"{c['src']}->{c['tgt']}"
        pair_counts[pair] += 1
        src_counts[c["src"]] += 1
        tgt_counts[c["tgt"]] += 1
        bytes_total += c.get("size", 0)
        d = int(time.strftime("%d", time.localtime(c["ts"])))
        day_ok[d]  += 1
        day_pairs[d][pair] += 1

    for e in errs:
        d = int(time.strftime("%d", time.localtime(e["ts"])))
        day_err[d] += 1

    try:
        year, mon = int(m[:4]), int(m[5:])
        days_in_month = calendar.monthrange(year, mon)[1]
    except Exception:
        days_in_month = 31

    by_day = [
        {"day": d, "ok": day_ok.get(d, 0), "err": day_err.get(d, 0),
         "pairs": dict(day_pairs.get(d, {}))}
        for d in range(1, days_in_month + 1)
    ]

    return {
        "month":       m,
        "total_ok":    len(convs),
        "total_err":   len(errs),
        "bytes_total": bytes_total,
        "pairs":       sorted(pair_counts.items(), key=lambda x: -x[1])[:30],
        "top_src":     sorted(src_counts.items(),  key=lambda x: -x[1])[:10],
        "top_tgt":     sorted(tgt_counts.items(),  key=lambda x: -x[1])[:10],
        "by_day":      by_day,
    }


# ── Stickerei-Endpunkte ───────────────────────────────────────────────────────

@app.post("/api/embroidery/info")
async def embroidery_info(file: UploadFile = File(...)):
    """Metadaten einer Stickdatei: Stichzahl, Farben, Größe."""
    data = await file.read()
    if len(data) > MAX_MB * 1024 * 1024:
        raise HTTPException(413, "Datei zu groß")
    suffix = Path(file.filename or "upload").suffix or ".pes"
    fd, tmp_path = tempfile.mkstemp(suffix=suffix)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        return conv.get_embroidery_info(tmp_path)
    finally:
        try: os.unlink(tmp_path)
        except OSError: pass


@app.post("/api/embroidery/preview")
async def embroidery_preview(file: UploadFile = File(...)):
    """SVG-Vorschau einer Stickdatei (Fadenpfade farbig gerendert)."""
    data = await file.read()
    suffix = Path(file.filename or "upload").suffix or ".pes"
    fd, tmp_path = tempfile.mkstemp(suffix=suffix)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        svg = conv.get_embroidery_preview_svg(tmp_path)
        if svg is None:
            raise HTTPException(422, "Vorschau konnte nicht generiert werden")
        return {"svg": svg}
    finally:
        try: os.unlink(tmp_path)
        except OSError: pass


@app.post("/api/batch")
async def api_batch(
    files: List[UploadFile] = File(...),
    target_fmt: str = Form(...),
):
    """Mehrere Dateien auf einmal konvertieren → ZIP-Download"""
    if len(files) > 50:
        raise HTTPException(400, "Maximal 50 Dateien pro Batch")

    zip_buf = io.BytesIO()
    log = []
    count_ok = 0

    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in files:
            data = await file.read()
            if len(data) > MAX_MB * 1024 * 1024:
                log.append({"file": file.filename, "ok": False, "msg": f"Zu groß (>{MAX_MB} MB)"})
                continue

            filename = file.filename or "upload"
            suffix = Path(filename).suffix or ".bin"
            src_ext = suffix.lstrip(".").lower() or "bin"
            fd, tmp_path = tempfile.mkstemp(suffix=suffix)
            try:
                with os.fdopen(fd, "wb") as f:
                    f.write(data)
                result = conv.convert(tmp_path, target_fmt)
                if "result_b64" in result:
                    ext = result.get("result_ext", target_fmt)
                    stem = Path(filename).stem
                    out_name = f"{stem}.{ext}"
                    zf.writestr(out_name, base64.b64decode(result["result_b64"]))
                    log.append({"file": filename, "ok": True, "out": out_name})
                    _log_conversion(src_ext, target_fmt, result.get("size_bytes", 0), True,
                                    steps=result.get("steps"), source="batch")
                    count_ok += 1
                else:
                    msg = result.get("error", "Unbekannter Fehler")
                    log.append({"file": filename, "ok": False, "msg": msg})
                    _log_conversion(src_ext, target_fmt, 0, False, error=msg, source="batch")
            except Exception as e:
                log.append({"file": filename, "ok": False, "msg": str(e)})
                _log_conversion(src_ext, target_fmt, 0, False, error=str(e), source="batch")
            finally:
                try: os.unlink(tmp_path)
                except OSError: pass

    zip_buf.seek(0)
    return {
        "result_b64": base64.b64encode(zip_buf.read()).decode(),
        "result_ext": "zip",
        "count_ok": count_ok,
        "count_err": len(files) - count_ok,
        "log": log,
    }


@app.get("/api/machines")
def get_machines():
    """Maschinendatenbank: Marke → Modelle + kompatible Formate."""
    return conv.MACHINE_DB


# ── Statisches Frontend ───────────────────────────────────────────────────────
_static = Path(__file__).parent / "static"
if _static.exists():
    app.mount("/", StaticFiles(directory=str(_static), html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, loop="asyncio")
