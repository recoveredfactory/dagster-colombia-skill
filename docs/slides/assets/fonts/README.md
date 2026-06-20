# Fonts

The deck self-hosts David's pairing: **Migra** (high-contrast serif) for
headlines + **NeueBit** (bitmap) for body. Both are Pangram Pangram
**"Free for Personal Use"** (license docs in this folder). The `@font-face`
rules and the `--display` / `--sans` variables in `../../theme.css` wire them up.
Google Fonts (Pixelify Sans + DotGothic16, loaded in `index.html`) stay as the
fallback chain.

## What's actually installed

| File | Font | Role | Notes |
|------|------|------|-------|
| `Migra-Extralight.woff2`             | Migra Extralight (200)        | headlines | the thin/editorial cut |
| `Migra-Extrabold.woff2`              | Migra Extrabold (800)         | headlines | **default** headline weight |
| `MigraItalic-ExtralightItalic.woff2` | Migra Extralight Italic (200) | headlines | |
| `MigraItalic-ExtraboldItalic.woff2`  | Migra Extrabold Italic (800)  | headlines | |
| `PPNeueBit-Bold.otf`                  | NeueBit Bold                  | body, kickers, captions | only weight in the free pack; mapped across 100–900 |
| `PPMondwest-Regular.otf`              | MondWest Regular              | (bonus) display alternative/fallback | |

The Migra free pack ships **only Extralight + Extrabold** (each with an italic) —
there is no regular/medium/semibold. NeueBit and MondWest free packs ship a
**single weight each**.

`Departure Mono` (code) is still optional and **not** included — drop
`DepartureMono.woff2` here to enable it ([departuremono.com](https://departuremono.com/),
free/OFL). Until then code falls back to `ui-monospace`.

## Switching the headline look

One knob in `theme.css` `:root`:

```css
--display-weight: 800;   /* 800 = Extrabold (default), 200 = Extralight */
```

For italic headlines, add `font-style: italic` to the heading rule you want
(e.g. `.reveal section.quote .q`) — the italic woff2 files are already loaded.

## Licensing

"Free for Personal Use." Fine for a personal talk / teaching; **not** for
commercial use. See `Migra-Personal-license.txt` and
`EULA-PangramPangram-FreeForPersonalUse-MAY2021.pdf`. A commercial license is
available from [pangrampangram.com](https://pangrampangram.com/) if this ever
ships commercially.
