"""Programmatic generator for the Smart Markdown-to-Print Desktop Publisher multi-resolution icon."""

from pathlib import Path
from PIL import Image, ImageDraw


def draw_icon_frame(size: int) -> Image.Image:
    """Render a single crisp Slate-Teal & Crisp White fountain-pen / Markdown typeset badge icon frame."""
    scale = 4
    canvas_size = size * scale
    img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Colors
    slate_dark = (15, 23, 42, 255)      # #0F172A
    teal_primary = (13, 148, 136, 255)  # #0D9488
    teal_bright = (20, 184, 166, 255)   # #14B8A6
    crisp_white = (248, 250, 252, 255)  # #F8FAFC
    page_shadow = (30, 41, 59, 255)     # #1E293B
    gold_nib = (245, 158, 11, 255)      # #F59E0B

    pad = int(canvas_size * 0.06)
    radius = int(canvas_size * 0.22)

    # Outer rounded badge background (Dark Slate with Teal border)
    draw.rounded_rectangle(
        [pad, pad, canvas_size - pad, canvas_size - pad],
        radius=radius,
        fill=slate_dark,
        outline=teal_primary,
        width=max(2, int(canvas_size * 0.045)),
    )

    # Inner subtle top-left accent glow bar
    accent_margin = int(canvas_size * 0.16)
    draw.rounded_rectangle(
        [
            accent_margin,
            accent_margin,
            canvas_size - accent_margin,
            canvas_size - accent_margin,
        ],
        radius=int(radius * 0.65),
        fill=page_shadow,
    )

    # Crisp white typeset page sheet inside badge
    page_l = int(canvas_size * 0.22)
    page_t = int(canvas_size * 0.17)
    page_r = int(canvas_size * 0.72)
    page_b = int(canvas_size * 0.83)
    draw.rounded_rectangle(
        [page_l, page_t, page_r, page_b],
        radius=max(2, int(canvas_size * 0.05)),
        fill=crisp_white,
    )

    # Teal header bar on the page
    header_h = max(4, int((page_b - page_t) * 0.16))
    draw.rounded_rectangle(
        [page_l, page_t, page_r, page_t + header_h],
        radius=max(2, int(canvas_size * 0.04)),
        fill=teal_primary,
    )

    # Typeset ruled lines on the page (representing Markdown / print lines)
    line_left = page_l + int((page_r - page_l) * 0.15)
    line_right_full = page_r - int((page_r - page_l) * 0.15)
    line_right_short = page_l + int((page_r - page_l) * 0.62)
    line_h = max(2, int(canvas_size * 0.038))

    for idx, y_frac in enumerate([0.42, 0.54, 0.66]):
        y_pos = int(canvas_size * y_frac)
        right_edge = line_right_short if idx == 2 else line_right_full
        draw.rounded_rectangle(
            [line_left, y_pos, right_edge, y_pos + line_h],
            radius=max(1, line_h // 2),
            fill=slate_dark if idx == 0 else (100, 116, 139, 255),
        )

    # Fountain pen nib badge overlapping bottom-right
    nib_cx = int(canvas_size * 0.70)
    nib_cy = int(canvas_size * 0.66)
    nib_r = int(canvas_size * 0.20)

    draw.ellipse(
        [nib_cx - nib_r, nib_cy - nib_r, nib_cx + nib_r, nib_cy + nib_r],
        fill=teal_bright,
        outline=slate_dark,
        width=max(2, int(canvas_size * 0.03)),
    )

    # Pen nib diamond polygon pointing down-left
    tip_x = nib_cx - int(nib_r * 0.55)
    tip_y = nib_cy + int(nib_r * 0.55)
    top_x = nib_cx + int(nib_r * 0.50)
    top_y = nib_cy - int(nib_r * 0.50)
    shoulder_1 = (nib_cx - int(nib_r * 0.35), nib_cy - int(nib_r * 0.10))
    shoulder_2 = (nib_cx + int(nib_r * 0.10), nib_cy + int(nib_r * 0.35))

    draw.polygon(
        [(tip_x, tip_y), shoulder_1, (top_x, top_y), shoulder_2],
        fill=crisp_white,
        outline=slate_dark,
    )

    # Fountain pen breather hole & slit
    hole_r = max(2, int(nib_r * 0.16))
    draw.ellipse(
        [nib_cx - hole_r, nib_cy - hole_r, nib_cx + hole_r, nib_cy + hole_r],
        fill=gold_nib,
    )
    draw.line(
        [(tip_x, tip_y), (nib_cx, nib_cy)],
        fill=slate_dark,
        width=max(2, int(canvas_size * 0.025)),
    )

    return img.resize((size, size), Image.Resampling.LANCZOS)


def generate_app_icon(output_path: Path | None = None) -> Path:
    """Generate the multi-resolution Windows .ico file at assets/app_icon.ico."""
    project_root = Path(__file__).resolve().parent.parent
    target_path = output_path or (project_root / "assets" / "app_icon.ico")
    target_path.parent.mkdir(parents=True, exist_ok=True)

    resolutions = [16, 32, 48, 256]
    frames = [draw_icon_frame(sz) for sz in resolutions]

    # Save 256x256 base with all sizes embedded
    frames[-1].save(
        target_path,
        format="ICO",
        sizes=[(sz, sz) for sz in resolutions],
        append_images=frames[:-1],
    )
    return target_path


if __name__ == "__main__":
    saved = generate_app_icon()
    print(f"Generated multi-resolution icon at: {saved} ({saved.stat().st_size} bytes)")
