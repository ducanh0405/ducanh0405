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

THEMES = {
    "dark": {
        "text": "E6EDF3", "muted": "9198A1", "border": "3D444D",
        "chip": "151B23", "tag": "212830", "accent": "58A6FF",
    },
    "light": {
        "text": "1F2328", "muted": "59636E", "border": "D1D9E0",
        "chip": "F6F8FA", "tag": "EFF2F5", "accent": "0969DA",
    },
}

# label, Simple Icons slug (or an original schematic glyph), display color
TECH = {
    "Python": ("python", "3776AB"),
    "TypeScript": ("typescript", "3178C6"),
    "JavaScript": ("javascript", "F7DF1E"),
    "SQL": ("database", "79B8FF"),
    "Java": ("openjdk", "ED8B00"),
    "scikit-learn": ("scikitlearn", "F7931E"),
    "XGBoost": ("bars", "79B8FF"),
    "LightGBM": ("tree", "62C68D"),
    "PyTorch": ("pytorch", "EE4C2C"),
    "SciPy": ("scipy", "8CAAE6"),
    "pandas": ("pandas", "E6EDF3"),
    "NumPy": ("numpy", "67B5DA"),
    "PostgreSQL": ("postgresql", "6C9AC3"),
    "Neo4j": ("neo4j", "65B9EF"),
    "MySQL": ("mysql", "79B8DB"),
    "SQLite": ("sqlite", "79C3E6"),
    "Matplotlib": ("chart", "79B6DA"),
    "Seaborn": ("chart", "8AA9CF"),
    "Plotly": ("plotly", "79B8FF"),
    "Jupyter": ("jupyter", "F37626"),
    "React": ("react", "61DAFB"),
    "Next.js": ("nextdotjs", "E6EDF3"),
    "Tailwind CSS": ("tailwindcss", "38BDF8"),
    "FastAPI": ("fastapi", "37CDBB"),
    "Node.js": ("nodedotjs", "75BA65"),
    "Express": ("express", "E6EDF3"),
    "Git": ("git", "F05032"),
    "Docker": ("docker", "2496ED"),
    "Supabase": ("supabase", "3FCF8E"),
    "Vite": ("vite", "B794FF"),
    "Vercel": ("vercel", "E6EDF3"),
    "Claude": ("claude", "D97757"),
    "Codex": ("terminal", "E6EDF3"),
    "Gemini": ("googlegemini", "8AB4F8"),
    "Harness": ("workflow", "79B8FF"),
}

LIGHT_ICON_COLORS = {
    "Python": "3776AB", "JavaScript": "9A7B00", "SQL": "0969DA",
    "Java": "B46A00", "scikit-learn": "B06000", "XGBoost": "0969DA",
    "LightGBM": "1A7F37", "PyTorch": "D43E20", "SciPy": "405F9D",
    "pandas": "150458", "NumPy": "176580", "PostgreSQL": "4169A1",
    "Neo4j": "156B9C", "MySQL": "4479A1", "SQLite": "0F6091",
    "Matplotlib": "11557C", "Seaborn": "4C72B0", "Plotly": "3F4F75",
    "Jupyter": "BD4B00", "React": "087EA4", "Next.js": "1F2328",
    "Tailwind CSS": "087EA4", "FastAPI": "008577", "Node.js": "417E38",
    "Express": "1F2328", "Docker": "0969DA", "Supabase": "18794E",
    "Vite": "7052CB", "Vercel": "1F2328", "Claude": "B14F2D",
    "Codex": "1F2328", "Gemini": "3767C5", "Harness": "0969DA",
}

CARDS = [
    ("ML & modeling", "Statistical learning & explainability",
     ["scikit-learn", "XGBoost", "LightGBM", "PyTorch", "SciPy"], ["Forecasting", "Model interpretation"]),
    ("Data engineering", "Dataframes, pipelines & storage",
     ["pandas", "NumPy", "PostgreSQL", "Neo4j", "MySQL", "SQLite"], ["Data processing", "Graph analytics"]),
    ("Visualization", "Exploration, charts & notebooks",
     ["Matplotlib", "Seaborn", "Plotly", "Jupyter"], ["Statistical plots", "Interactive charts"]),
    ("Languages", "Core programming tools",
     ["Python", "TypeScript", "JavaScript", "SQL", "Java"], ["Data science", "Web development"]),
    ("Web & APIs", "Interfaces and backend services",
     ["React", "Next.js", "Tailwind CSS", "FastAPI", "Node.js", "Express"], ["Frontend", "Backend APIs"]),
    ("Ship & run", "Version control & development",
     ["Git", "Docker", "Supabase", "Vite", "Vercel"], ["Containers", "Build tooling"]),
]

LLM_TOOLS = ["Claude", "Codex", "Gemini", "Harness"]

GLYPHS = {
    "bars": '<path d="M3 20V11h4v9zm7 0V6h4v14zm7 0V2h4v18z"/>',
    "tree": '<path d="m12 1 7 8h-4l6 7h-7v7h-4v-7H3l6-7H5z"/>',
    "chart": '<path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M3 3v18h19M6 15l4-6 5 4 6-8"/>',
    "database": '<g fill="none" stroke="currentColor" stroke-width="1.8"><ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 4 16 4 16 0V5M4 12c0 4 16 4 16 0"/></g>',
    "terminal": '<g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="18" rx="3"/><path d="m6 8 4 4-4 4m8 0h4"/></g>',
    "workflow": '<g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><rect x="1" y="8" width="6" height="8" rx="1"/><rect x="17" y="1" width="6" height="6" rx="1"/><rect x="17" y="17" width="6" height="6" rx="1"/><path d="M7 12h5V4h5m-5 8v8h5"/></g>',
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


def text(x, y, value, size=16, color="E6EDF3", weight=400):
    return (f'<text x="{x}" y="{y}" fill="#{color}" font-size="{size}" '
            f'font-weight="{weight}">{escape(value)}</text>')


def badge_width(label):
    return round(TEXT_FONT.getlength(label)) + 43


def badge(label, x, y, theme):
    palette = THEMES[theme]
    width = badge_width(label)
    slug, color = TECH[label]
    if theme == "light":
        color = LIGHT_ICON_COLORS.get(label, color)
    return [
        f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{width - 1}" height="34" rx="4" fill="#{palette["chip"]}" stroke="#{palette["border"]}"/>',
        icon(slug, color, x + 9, y + 8),
        text(x + 34, y + 23, label, color=palette["text"]),
    ]


def card(index, x, y, theme):
    title, subtitle, labels, tags = CARDS[index]
    palette = THEMES[theme]
    elements = [
        f'<g transform="translate({x} {y})">',
        f'<rect x="0.5" y="0.5" width="351" height="277" rx="6" fill="none" stroke="#{palette["border"]}"/>',
        f'<rect x="20" y="23" width="3" height="18" rx="1.5" fill="#{palette["accent"]}"/>',
        text(32, 38, title, 20, palette["text"], weight=650),
        text(20, 65, subtitle, 14, palette["muted"]),
    ]
    bx, by = 20, 85
    for label in labels:
        width = badge_width(label)
        if bx + width > 332:
            bx, by = 20, by + 43
        if by + 35 > 215:
            raise ValueError(f"Badge overflow: {title}")
        elements.extend(badge(label, bx, by, theme))
        bx += width + 7
    tx = 20
    for tag in tags:
        width = round(TAG_FONT.getlength(tag)) + 16
        if tx + width > 332:
            raise ValueError(f"Tag overflow: {title}")
        elements.extend([
            f'<rect x="{tx}" y="239" width="{width}" height="23" rx="3" fill="#{palette["tag"]}"/>',
            text(tx + 8, 255, tag, 13, palette["text"]),
        ])
        tx += width + 7
    elements.append("</g>")
    return "\n".join(elements)


def llm_section(width, y, theme):
    palette = THEMES[theme]
    badges = []
    bx, by = 20, 85
    for label in LLM_TOOLS:
        if bx + badge_width(label) > width - 22:
            bx, by = 20, by + 43
        badges.extend(badge(label, bx, by, theme))
        bx += badge_width(label) + 7
    height = by + 35 + 20
    elements = [
        f'<g transform="translate(1 {y})">',
        f'<rect x="0.5" y="0.5" width="{width - 3}" height="{height - 1}" rx="6" fill="none" stroke="#{palette["border"]}"/>',
        f'<rect x="20" y="23" width="3" height="18" rx="1.5" fill="#{palette["accent"]}"/>',
        text(32, 38, "LLM", 20, palette["text"], weight=650),
        text(20, 65, "AI coding tools & harness", 14, palette["muted"]),
        *badges,
        '</g>',
    ]
    return "\n".join(elements), height


def render(columns, output, theme):
    rows = (len(CARDS) + columns - 1) // columns
    width = columns * 352 + (columns - 1) * 16 + 2
    grid_height = rows * 278 + (rows - 1) * 16 + 2
    footer, footer_height = llm_section(width, grid_height + 16, theme)
    height = grid_height + 16 + footer_height + 1
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Duc Anh — Technologies</title>',
        '<desc id="desc">Six technology cards: machine learning, data engineering, visualization, languages, web APIs, and development tools. An LLM row lists Claude, Codex, Gemini, and Harness.</desc>',
        '<g font-family="Segoe UI, Arial, sans-serif">',
    ]
    for index in range(len(CARDS)):
        parts.append(card(index, 1 + (index % columns) * 368, 1 + (index // columns) * 294, theme))
    parts.append(footer)
    parts.extend(["</g>", "</svg>"])
    output.write_text("\n".join(parts) + "\n", encoding="utf-8")


def main():
    ICONS.mkdir(parents=True, exist_ok=True)
    if "--fetch-icons" in sys.argv:
        slugs = sorted({slug for slug, _ in TECH.values() if slug not in GLYPHS})
        with ThreadPoolExecutor(max_workers=6) as executor:
            list(executor.map(fetch_logo, slugs))
    for theme, suffix in [("dark", ""), ("light", "-light")]:
        render(3, ASSETS / f"tech-stack{suffix}.svg", theme)
        render(1, ASSETS / f"tech-stack-mobile{suffix}.svg", theme)
    print("Built dark/light desktop and mobile technology cards.")


if __name__ == "__main__":
    main()
