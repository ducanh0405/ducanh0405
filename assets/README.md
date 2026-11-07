# Technology cards

`tech-stack.svg` is the dark desktop layout (three columns), and
`tech-stack-mobile.svg` is the dark mobile layout (one column). The matching
light layouts are `tech-stack-light.svg` and `tech-stack-mobile-light.svg`.
All layouts end with a full-width LLM row: Claude, Codex, Gemini, and Harness.

The profile README uses `<picture>` to select the color scheme and switches to
the mobile layout below a viewport width of 640px. Card backgrounds are transparent
so the page shows through; borders, text, and badges use neutral GitHub colors,
based on [Primer's color system](https://primer.style/product/primitives/color/).

Both images are self-contained SVGs with embedded vector paths. They contain no
scripts, external fonts, external images, or runtime badge-service requests.
The technology selection comes from project documentation and explicit profile updates.

To update the cards, edit `TECH` / `CARDS` in `scripts/build_tech_stack.py`, then run:

```powershell
python scripts/build_tech_stack.py
```

The builder uses Python and Pillow, and measures labels with Windows' Segoe UI font.
To fetch missing brand icons, explicitly add `--fetch-icons`.

Brand icon paths in `icons/` come from [Simple Icons](https://github.com/simple-icons/simple-icons),
distributed under [CC0 1.0](https://github.com/simple-icons/simple-icons/blob/develop/LICENSE.md).
Names and logos belong to their respective owners. Java uses the OpenJDK icon.
XGBoost, LightGBM, Matplotlib, Seaborn, SQL, Codex, and Harness use original
schematic chart, tree, database, terminal, or workflow glyphs rather than brand logos.
