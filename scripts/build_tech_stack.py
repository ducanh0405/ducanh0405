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
TEXT_FONT = ImageFont.truetype(str(FONT), 15)
TAG_FONT = ImageFont.truetype(str(FONT), 12)
CARD_WIDTH = 352
CARD_HEIGHT = 232
GAP = 16

THEMES = {
    "dark": {
        "text": "DCE3EB", "muted": "94A0AF", "border": "293440",
        "surface": "10161E", "chip": "1B2531", "rule": "25303C",
    },
    "light": {
        "text": "242D38", "muted": "5D6B7B", "border": "D8DEE6",
        "surface": "FFFFFF", "chip": "F0F3F6", "rule": "E8ECF0",
    },
}

CATEGORY_ACCENTS = {
    "dark": ["7CC9A3", "85B8E5", "DAB77E", "A9B8CC", "7BC9C1", "D9A28D"],
    "light": ["287B53", "2B73A8", "946821", "526C89", "227D74", "A45F43"],
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
    return f'<g transform="translate({x} {y}) scale(0.667)" fill="#{color}" color="#{color}">{body}</g>'


def text(x, y, value, size=15, color="DCE3EB", weight=400):
    return (f'<text x="{x}" y="{y}" fill="#{color}" font-size="{size}" '
            f'font-weight="{weight}">{escape(value)}</text>')


def badge_width(label):
    return round(TEXT_FONT.getlength(label)) + 41


def badge(label, x, y, theme):
    palette = THEMES[theme]
    width = badge_width(label)
    slug, color = TECH[label]
    if theme == "light":
        color = LIGHT_ICON_COLORS.get(label, color)
    return [
        f'<rect x="{x}" y="{y}" width="{width}" height="30" rx="6" fill="#{palette["chip"]}"/>',
        icon(slug, color, x + 9, y + 7),
        text(x + 32, y + 20, label, color=palette["text"]),
    ]


def card(index, x, y, theme):
    title, subtitle, labels, tags = CARDS[index]
    palette = THEMES[theme]
    accent = CATEGORY_ACCENTS[theme][index]
    elements = [
        f'<g transform="translate({x} {y})">',
        f'<rect x="0.5" y="0.5" width="{CARD_WIDTH - 1}" height="{CARD_HEIGHT - 1}" rx="10" fill="#{palette["surface"]}" stroke="#{palette["border"]}"/>',
        f'<rect x="20" y="18" width="26" height="3" rx="1.5" fill="#{accent}"/>',
        text(20, 47, title, 18, palette["text"], weight=600),
        text(20, 69, subtitle, 13, palette["muted"]),
    ]
    bx, by = 20, 87
    for label in labels:
        width = badge_width(label)
        if bx + width > 332:
            bx, by = 20, by + 36
        if by + 30 > 194:
            raise ValueError(f"Badge overflow: {title}")
        elements.extend(badge(label, bx, by, theme))
        bx += width + 6
    elements.append(f'<path d="M20 202H332" stroke="#{palette["rule"]}"/>')
    tx = 20
    for tag_index, tag in enumerate(tags):
        width = round(TAG_FONT.getlength(tag))
        if tx + width > 332:
            raise ValueError(f"Tag overflow: {title}")
        elements.append(text(tx, 221, tag, 12, palette["muted"]))
        tx += width + 13
        if tag_index < len(tags) - 1:
            elements.append(f'<circle cx="{tx}" cy="217" r="1.5" fill="#{accent}"/>')
            tx += 13
    elements.append("</g>")
    return "\n".join(elements)


def llm_section(width, y, theme):
    palette = THEMES[theme]
    badges = []
    wide = width > 640
    bx, by = (325, 26) if wide else (20, 78)
    for label in LLM_TOOLS:
        if bx + badge_width(label) > width - 22:
            bx, by = 20, by + 36
        badges.extend(badge(label, bx, by, theme))
        bx += badge_width(label) + 8
    height = 82 if wide else by + 30 + 20
    elements = [
        f'<g transform="translate(1 {y})">',
        f'<rect x="0.5" y="0.5" width="{width - 3}" height="{height - 1}" rx="10" fill="#{palette["surface"]}" stroke="#{palette["border"]}"/>',
        text(20, 34, "LLM", 18, palette["text"], weight=600),
        text(20, 56, "AI coding tools & harness", 13, palette["muted"]),
        *badges,
        '</g>',
    ]
    return "\n".join(elements), height


def render(columns, output, theme):
    rows = (len(CARDS) + columns - 1) // columns
    width = columns * CARD_WIDTH + (columns - 1) * GAP + 2
    grid_height = rows * CARD_HEIGHT + (rows - 1) * GAP + 2
    footer, footer_height = llm_section(width, grid_height + GAP, theme)
    height = grid_height + GAP + footer_height + 1
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Duc Anh — Technologies</title>',
        '<desc id="desc">Six technology cards: machine learning, data engineering, visualization, languages, web APIs, and development tools. An LLM row lists Claude, Codex, Gemini, and Harness.</desc>',
        '<g font-family="Segoe UI, Arial, sans-serif">',
    ]
    for index in range(len(CARDS)):
        parts.append(card(index, 1 + (index % columns) * (CARD_WIDTH + GAP), 1 + (index // columns) * (CARD_HEIGHT + GAP), theme))
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
