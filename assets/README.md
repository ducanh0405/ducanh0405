# Technology cards

`tech-stack.svg` is the desktop layout (three columns). `tech-stack-mobile.svg`
is the narrow-screen layout (one column). The profile README selects the mobile
layout below a viewport width of 640px using `<picture>`.

Both images are self-contained SVGs with embedded vector paths. They contain no
scripts, external fonts, external images, or runtime badge-service requests.
The technology selection comes from project dependency manifests and documentation.

To update the cards, edit `TECH` / `CARDS` in `scripts/build_tech_stack.py`, then run:

```powershell
python scripts/build_tech_stack.py
```

The builder uses Python and Pillow, and measures labels with Windows' Segoe UI font.
To fetch missing brand icons, explicitly add `--fetch-icons`.

Brand icon paths in `icons/` come from [Simple Icons](https://github.com/simple-icons/simple-icons),
distributed under [CC0 1.0](https://github.com/simple-icons/simple-icons/blob/develop/LICENSE.md).
Names and logos belong to their respective owners. XGBoost, LightGBM, SHAP,
Matplotlib, and Seaborn use original schematic chart/tree glyphs rather than brand logos.
