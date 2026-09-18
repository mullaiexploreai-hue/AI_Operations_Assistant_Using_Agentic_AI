"""Generate a dependency-free PDF from the technical documentation."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCUMENTATION_DIR = ROOT / "documentation"
SOURCE = DOCUMENTATION_DIR / "documentation.md"
TARGET = DOCUMENTATION_DIR / "documentation.pdf"


def escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def documentation_lines() -> list[str]:
    lines: list[str] = []
    for raw_line in SOURCE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("```"):
            continue
        if line.startswith("#"):
            line = line.lstrip("# ").upper()
        if not line:
            lines.append("")
            continue
        while len(line) > 96:
            split_at = line.rfind(" ", 0, 96)
            split_at = split_at if split_at > 0 else 96
            lines.append(line[:split_at])
            line = line[split_at:].lstrip()
        lines.append(line)
    return lines


def build_pdf() -> None:
    lines = documentation_lines()
    page_lines = 46
    pages = [lines[index:index + page_lines] for index in range(0, len(lines), page_lines)]
    objects: list[bytes] = []

    def add_object(content: bytes) -> int:
        objects.append(content)
        return len(objects)

    catalog_id = add_object(b"")
    pages_id = add_object(b"")
    font_id = add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    page_ids: list[int] = []

    for page in pages:
        commands = ["BT", "/F1 10 Tf", "50 750 Td", "14 TL"]
        for line in page:
            commands.append(f"({escape_pdf_text(line)}) Tj")
            commands.append("T*")
        commands.append("ET")
        stream = "\n".join(commands).encode("latin-1", errors="replace")
        stream_id = add_object(
            b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream"
        )
        page_ids.append(
            add_object(
                b"<< /Type /Page /Parent "
                + str(pages_id).encode()
                + b" 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 "
                + str(font_id).encode()
                + b" 0 R >> >> /Contents "
                + str(stream_id).encode()
                + b" 0 R >>"
            )
        )

    kids = b"[" + b" ".join(f"{page_id} 0 R".encode() for page_id in page_ids) + b"]"
    objects[pages_id - 1] = b"<< /Type /Pages /Kids " + kids + b" /Count " + str(len(page_ids)).encode() + b" >>"
    objects[catalog_id - 1] = b"<< /Type /Catalog /Pages " + str(pages_id).encode() + b" 0 R >>"

    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for object_id, content in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{object_id} 0 obj\n".encode())
        output.extend(content)
        output.extend(b"\nendobj\n")
    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode())
    output.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode()
    )
    TARGET.write_bytes(output)
    print(f"Generated {TARGET} ({len(pages)} pages)")


if __name__ == "__main__":
    build_pdf()