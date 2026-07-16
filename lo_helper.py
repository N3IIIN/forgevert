#!/usr/bin/env python3
"""
LibreOffice UNO Konvertierungs-Helper.
Muss mit LibreOffices eigenem Python ausgeführt werden (hat das uno-Modul).
Aufruf: python.exe lo_helper.py <src> <dst> <host> <port>
"""
import sys, os

def convert(src_path, dst_path, host="127.0.0.1", port=2002):
    import uno
    from com.sun.star.beans import PropertyValue

    localCtx = uno.getComponentContext()
    resolver = localCtx.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", localCtx
    )
    try:
        ctx = resolver.resolve(
            f"uno:socket,host={host},port={port};urp;StarOffice.ComponentContext"
        )
    except Exception as e:
        print(f"CONNECT_FAIL:{e}", file=sys.stderr)
        sys.exit(1)

    smgr = ctx.ServiceManager
    desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)

    src_url = uno.systemPathToFileUrl(os.path.abspath(src_path))
    load_prop = PropertyValue()
    load_prop.Name = "Hidden"
    load_prop.Value = True

    try:
        doc = desktop.loadComponentFromURL(src_url, "_blank", 0, (load_prop,))
    except Exception as e:
        print(f"LOAD_FAIL:{e}", file=sys.stderr)
        sys.exit(2)

    ext = dst_path.rsplit(".", 1)[-1].lower()

    # Writer
    writer_filters = {
        "pdf": "writer_pdf_Export", "docx": "MS Word 2007 XML",
        "doc": "MS Word 97", "odt": "writer8", "rtf": "Rich Text Format",
        "html": "HTML (StarWriter)", "txt": "Text", "epub": "EPUB2",
    }
    # Impress
    impress_filters = {
        "pdf": "impress_pdf_Export", "pptx": "Impress MS PowerPoint 2007 XML",
        "ppt": "MS PowerPoint 97", "odp": "impress8",
    }
    # Calc
    calc_filters = {
        "pdf": "calc_pdf_Export", "xlsx": "Calc MS Excel 2007 XML",
        "xls": "MS Excel 97", "ods": "calc8",
        "csv": "Text - txt - csv (StarCalc)",
    }
    # Draw
    draw_filters = {
        "pdf": "draw_pdf_Export", "svg": "draw_svg_Export",
        "png": "draw_png_Export",
    }

    stype = doc.getImplementationName()
    if "Impress" in stype or "Presentation" in stype:
        filter_map = impress_filters
    elif "Calc" in stype or "Spreadsheet" in stype:
        filter_map = calc_filters
    elif "Draw" in stype:
        filter_map = draw_filters
    else:
        filter_map = writer_filters

    filter_name = filter_map.get(ext, "writer_pdf_Export")

    dst_url = uno.systemPathToFileUrl(os.path.abspath(dst_path))
    p1 = PropertyValue(); p1.Name = "FilterName"; p1.Value = filter_name
    p2 = PropertyValue(); p2.Name = "Overwrite"; p2.Value = True

    try:
        doc.storeToURL(dst_url, (p1, p2))
    except Exception as e:
        print(f"SAVE_FAIL:{e}", file=sys.stderr)
        try: doc.close(True)
        except: pass
        sys.exit(3)

    try: doc.close(True)
    except: pass
    print(f"OK:{dst_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: lo_helper.py <src> <dst> [host] [port]", file=sys.stderr)
        sys.exit(1)
    src  = sys.argv[1]
    dst  = sys.argv[2]
    host = sys.argv[3] if len(sys.argv) > 3 else "127.0.0.1"
    port = int(sys.argv[4]) if len(sys.argv) > 4 else 2002
    convert(src, dst, host, port)
