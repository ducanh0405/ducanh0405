"""Build self-contained GitHub profile SVGs; reads only logo assets and system fonts."""

from concurrent.futures import ThreadPoolExecutor
from html import escape
from pathlib import Path
from urllib.request import Request, urlopen
import re
import sys

from PIL import ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ICONS = ASSETS / "icons"
FONT = Path("C:/Windows/Fonts/segoeui.ttf")
TEXT_FONT = ImageFont.truetype(str(FONT), 16)
TAG_FONT = ImageFont.truetype(str(FONT), 13)

# label, Simple Icons slug (or an original schematic glyph), display color
TECH = {
    "Python": ("python", "3776AB"),
    "TypeScript": ("typescript", "3178C6"),
    "JavaScript": ("javascript", "F7DF1E"),
    "scikit-learn": ("scikitlearn", "F7931E"),
    "XGBoost": ("bars", "B9A4EC"),
    "LightGBM": ("tree", "62C68D"),
    "SHAP": ("bars", "EC7CA8"),
    "SciPy": ("scipy", "8CAAE6"),
    "pandas": ("pandas", "DAD7F5"),
    "NumPy": ("numpy", "67B5DA"),
    "PostgreSQL": ("postgresql", "6C9AC3"),
    "Neo4j": ("neo4j", "65B9EF"),
    "Redis": ("redis", "FF625C"),
    "Matplotlib": ("chart", "79B6DA"),
    "Seaborn": ("chart", "8AA9CF"),
    "Plotly": ("plotly", "B7B0F8"),
    "Jupyter": ("jupyter", "F37626"),
    "React": ("react", "61DAFB"),
    "Next.js": ("nextdotjs", "E7E5EF"),
    "Tailwind CSS": ("tailwindcss", "38BDF8"),
    "FastAPI": ("fastapi", "37CDBB"),
    "Node.js": ("nodedotjs", "75BA65"),
    "Express": ("express", "D5D1DE"),
    "Git": ("git", "F05032"),
    "Docker": ("docker", "2496ED"),
    "Supabase": ("supabase", "3FCF8E"),
    "Vite": ("vite", "B794FF"),
}

CARDS = [
    ("ML & modeling", "Statistical learning & explainability", "ECA06C",
     ["scikit-learn", "XGBoost", "LightGBM", "SHAP", "SciPy"], ["Forecasting", "Model interpretation"]),
    ("Data engineering", "Dataframes, pipelines & storage", "75B9E6",
     ["pandas", "NumPy", "PostgreSQL", "Neo4j", "Redis"], ["Data processing", "Graph analytics"]),
    ("Visualization", "Exploration, charts & notebooks", "D694CD",
     ["Matplotlib", "Seaborn", "Plotly", "Jupyter"], ["Statistical plots", "Interactive charts"]),
    ("Languages", "Core programming tools", "B6A1EF",
     ["Python", "TypeScript", "JavaScript"], ["Data science", "Web development"]),
    ("Web & APIs", "Interfaces and backend services", "72C7C3",
     ["React", "Next.js", "Tailwind CSS", "FastAPI", "Node.js", "Express"], ["Frontend", "Backend APIs"]),
    ("Ship & run", "Version control & development", "88C99D",
     ["Git", "Docker", "Supabase", "Vite"], ["Containers", "Build tooling"]),
]

GLYPHS = {
    "bars": '<path d="M3 20V11h4v9zm7 0V6h4v14zm7 0V2h4v18z"/>',
    "tree": '<path d="m12 1 7 8h-4l6 7h-7v7h-4v-7H3l6-7H5z"/>',
    "chart": '<path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M3 3v18h19M6 15l4-6 5 4 6-8"/>',
}


def fetch_logo(slug):
    target = ICONS / f"{slug}.svg"
    if target.exists():
        return
    url = f"https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/{slug}.svg"
    request = Request(url, headers={"User-Agent": "GitHub-profile-asset-builder"})
    with urlopen(request, timeout=30) as response:
        svg = response.read().decode("utf-8")
    if "<svg" not in svg or "<path" not in svg:
        raise ValueError(f"Invalid logo: {slug}")
    target.write_text(svg, encoding="utf-8")


def icon(slug, color, x, y):
    if slug in GLYPHS:
        body = GLYPHS[slug]
    else:
        svg = (ICONS / f"{slug}.svg").read_text(encoding="utf-8")
        body = "".join(re.findall(r"<path\b[^>]*?\/>", svg))
        if not body:
            raise ValueError(f"Missing path: {slug}")
    return f'<g transform="translate({x} {y}) scale(0.75)" fill="#{color}" color="#{color}">{body}</g>'


def text(x, y, value, size=16, color="EDEAF4", weight=400):
    return (f'<text x="{x}" y="{y}" fill="#{color}" font-size="{size}" '
            f'font-weight="{weight}">{escape(value)}</text>')


def card(index, x, y):
    title, subtitle, accent, labels, tags = CARDS[index]
    elements = [
        f'<g transform="translate({x} {y})">',
        '<rect x="0.5" y="0.5" width="351" height="277" rx="6" fill="#1C1929" stroke="#3B354F"/>',
        f'<rect x="20" y="23" width="3" height="18" rx="1.5" fill="#{accent}"/>',
        text(32, 38, title, 20, weight=650),
        text(20, 65, subtitle, 14, "B3ABC6"),
    ]
    bx, by = 20, 85
    for label in labels:
        width = round(TEXT_FONT.getlength(label)) + 43
        if bx + width > 332:
            bx, by = 20, by + 43
        if by + 35 > 215:
            raise ValueError(f"Badge overflow: {title}")
        slug, color = TECH[label]
        elements.extend([
            f'<rect x="{bx + 0.5}" y="{by + 0.5}" width="{width - 1}" height="34" rx="4" fill="#110F1A" stroke="#3B354F"/>',
            icon(slug, color, bx + 9, by + 8),
            text(bx + 34, by + 23, label),
        ])
        bx += width + 7
    tx = 20
    for tag in tags:
        width = round(TAG_FONT.getlength(tag)) + 16
        if tx + width > 332:
            raise ValueError(f"Tag overflow: {title}")
        elements.extend([
            f'<rect x="{tx}" y="239" width="{width}" height="23" rx="3" fill="#242033"/>',
            text(tx + 8, 255, tag, 13, "CEC5DF"),
        ])
        tx += width + 7
    elements.append("</g>")
    return "\n".join(elements)


def render(columns, output):
    rows = (len(CARDS) + columns - 1) // columns
    width = columns * 352 + (columns - 1) * 16 + 2
    height = rows * 278 + (rows - 1) * 16 + 2
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Duc Anh — Technologies</title>',
        '<desc id="desc">Six technology cards: machine learning, data engineering, visualization, languages, web APIs, and development tools.</desc>',
        '<g font-family="Segoe UI, Arial, sans-serif">',
    ]
    for index in range(len(CARDS)):
        parts.append(card(index, 1 + (index % columns) * 368, 1 + (index // columns) * 294))
    parts.extend(["</g>", "</svg>"])
    output.write_text("\n".join(parts) + "\n", encoding="utf-8")


def main():
    ICONS.mkdir(parents=True, exist_ok=True)
    if "--fetch-icons" in sys.argv:
        slugs = sorted({slug for slug, _ in TECH.values() if slug not in GLYPHS})
        with ThreadPoolExecutor(max_workers=6) as executor:
            list(executor.map(fetch_logo, slugs))
    render(3, ASSETS / "tech-stack.svg")
    render(1, ASSETS / "tech-stack-mobile.svg")
    print("Built desktop and mobile technology cards.")


if __name__ == "__main__":
    main()
