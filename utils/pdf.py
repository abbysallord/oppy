"""Minimal PDF writer built on the standard library alone.

Oppy deliberately ships no third-party PDF dependency (see .cursorrules), so
this module emits the PDF byte format directly. It uses the Base-14 Courier
faces, which every reader has built in, meaning no font has to be embedded —
that is what keeps this small. Output is monospaced text, not styled tables.
"""

# A4 in PostScript points.
PAGE_WIDTH = 595
PAGE_HEIGHT = 842
MARGIN = 40
FONT_SIZE = 9
LEADING = 12

# Courier advances exactly 600/1000 em per glyph, so columns are predictable.
CHAR_WIDTH = FONT_SIZE * 0.6
MAX_COLS = int((PAGE_WIDTH - 2 * MARGIN) / CHAR_WIDTH)
MAX_ROWS = int((PAGE_HEIGHT - 2 * MARGIN) / LEADING)

_START_Y = PAGE_HEIGHT - MARGIN - FONT_SIZE


def _escape(text):
    """Escape the three characters that are special inside a PDF string."""
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _encode(text):
    # The fonts are declared WinAnsiEncoding; anything outside it (box drawing,
    # emoji, CJK) has no glyph and is replaced rather than corrupting the file.
    return _escape(text).encode("cp1252", "replace")


def _content_stream(page_lines):
    parts = [b"BT", b"%d TL" % LEADING, b"%d %d Td" % (MARGIN, _START_Y)]
    current_font = None

    for text, bold in page_lines:
        font = b"/F2" if bold else b"/F1"
        if font != current_font:
            parts.append(font + b" %d Tf" % FONT_SIZE)
            current_font = font
        parts.append(b"(" + _encode(text[:MAX_COLS]) + b") Tj")
        parts.append(b"T*")

    parts.append(b"ET")
    return b"\n".join(parts)


def write_pdf(path, lines, title="Oppy Opportunities"):
    """Write ``lines`` — a sequence of ``(text, bold)`` pairs — to a PDF file."""
    pages = [lines[i:i + MAX_ROWS] for i in range(0, len(lines), MAX_ROWS)] or [[]]

    # Fixed ids: 1 catalog, 2 page tree, 3-4 fonts, 5 document info.
    page_ids = [6 + 2 * i for i in range(len(pages))]
    content_ids = [7 + 2 * i for i in range(len(pages))]

    objects = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: b"<< /Type /Pages /Kids [" +
           b" ".join(b"%d 0 R" % pid for pid in page_ids) +
           b"] /Count %d >>" % len(pages),
        3: b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier /Encoding /WinAnsiEncoding >>",
        4: b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier-Bold /Encoding /WinAnsiEncoding >>",
        5: b"<< /Title (" + _encode(title) + b") /Producer (Oppy) >>",
    }

    for index, page in enumerate(pages):
        stream = _content_stream(page)
        objects[page_ids[index]] = (
            b"<< /Type /Page /Parent 2 0 R "
            b"/MediaBox [0 0 %d %d] "
            b"/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> "
            b"/Contents %d 0 R >>" % (PAGE_WIDTH, PAGE_HEIGHT, content_ids[index])
        )
        objects[content_ids[index]] = (
            b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream"
        )

    out = bytearray(b"%PDF-1.4\n")
    offsets = {}
    for object_id in sorted(objects):
        offsets[object_id] = len(out)
        out += b"%d 0 obj\n" % object_id + objects[object_id] + b"\nendobj\n"

    # Cross-reference table: byte offset of every object, in id order.
    xref_position = len(out)
    highest_id = max(objects)
    out += b"xref\n0 %d\n" % (highest_id + 1)
    out += b"0000000000 65535 f \n"
    for object_id in range(1, highest_id + 1):
        out += b"%010d 00000 n \n" % offsets[object_id]

    out += b"trailer\n<< /Size %d /Root 1 0 R /Info 5 0 R >>\n" % (highest_id + 1)
    out += b"startxref\n%d\n%%%%EOF\n" % xref_position

    with open(path, "wb") as f:
        f.write(bytes(out))

    return len(pages)
