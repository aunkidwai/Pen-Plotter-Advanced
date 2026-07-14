"""Generate a printable PDF font sheet template for handwriting capture.

Print the PDF, write each character in its cell with a pen, then scan
the completed sheet so the plotter software can digitise your handwriting.
"""

import string
from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas


UPPERCASE = list(string.ascii_uppercase)
LOWERCASE = list(string.ascii_lowercase)
DIGITS = list(string.digits)
PUNCTUATION = list(".,;:!?'\"()-&@#$%*/+=<>[]{}\\|~^_`")

SECTIONS = [
    ("Uppercase", UPPERCASE),
    ("Lowercase", LOWERCASE),
    ("Numbers", DIGITS),
    ("Punctuation", PUNCTUATION),
]

PAGE_WIDTH, PAGE_HEIGHT = LETTER
MARGIN = 0.6 * inch
CELL_SIZE = 0.55 * inch
LABEL_FONT_SIZE = 9
HEADER_FONT_SIZE = 12
SECTION_FONT_SIZE = 14
COLS = int((PAGE_WIDTH - 2 * MARGIN) // CELL_SIZE)


def _draw_header(c: Canvas, y: float) -> float:
    c.setFont("Helvetica-Bold", HEADER_FONT_SIZE + 4)
    c.drawCentredString(PAGE_WIDTH / 2, y, "Font Sheet Template")
    y -= 18
    c.setFont("Helvetica", 9)
    c.drawCentredString(
        PAGE_WIDTH / 2, y,
        "Write each character clearly inside its cell, then scan this sheet.",
    )
    return y - 28


def _draw_section(
    c: Canvas,
    title: str,
    chars: list[str],
    x0: float,
    y: float,
) -> float:
    """Draw a labelled grid of cells. Returns the new y position."""
    c.setFont("Helvetica-Bold", SECTION_FONT_SIZE)
    c.drawString(x0, y, title)
    y -= 6

    for i, ch in enumerate(chars):
        col = i % COLS
        row = i // COLS
        cx = x0 + col * CELL_SIZE
        cy = y - row * CELL_SIZE - CELL_SIZE

        # cell box
        c.setStrokeColorRGB(0.65, 0.65, 0.65)
        c.setLineWidth(0.5)
        c.rect(cx, cy, CELL_SIZE, CELL_SIZE)

        # baseline guide
        baseline_y = cy + CELL_SIZE * 0.25
        c.setStrokeColorRGB(0.82, 0.82, 0.82)
        c.setLineWidth(0.3)
        c.setDash(3, 3)
        c.line(cx + 2, baseline_y, cx + CELL_SIZE - 2, baseline_y)
        c.setDash()

        # reference label
        c.setFillColorRGB(0.55, 0.55, 0.55)
        c.setFont("Helvetica", LABEL_FONT_SIZE)
        c.drawString(cx + 2, cy + CELL_SIZE - LABEL_FONT_SIZE, ch)
        c.setFillColorRGB(0, 0, 0)

    total_rows = (len(chars) + COLS - 1) // COLS
    return y - total_rows * CELL_SIZE - 16


def generate_font_sheet(output_path: str | Path = "font_sheet.pdf") -> Path:
    """Create a font-sheet PDF at *output_path* and return the resolved path."""
    output_path = Path(output_path)
    c = Canvas(str(output_path), pagesize=LETTER)

    y = PAGE_HEIGHT - MARGIN
    y = _draw_header(c, y)

    for title, chars in SECTIONS:
        rows_needed = (len(chars) + COLS - 1) // COLS
        space_needed = rows_needed * CELL_SIZE + SECTION_FONT_SIZE + 24

        if y - space_needed < MARGIN:
            c.showPage()
            y = PAGE_HEIGHT - MARGIN

        y = _draw_section(c, title, chars, MARGIN, y)

    c.save()
    return output_path.resolve()


if __name__ == "__main__":
    path = generate_font_sheet()
    print(f"Font sheet saved to {path}")
