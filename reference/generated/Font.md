---
title: Font
layout: default
mcrf:
  objects:
    - Font
  diataxis: reference
  source: generated
  verified: 0.3.5
  verified_commit: ""
---

# Font {% include api_badge.html kind="changed" version="0.3.3-dev" %}

{% raw %}Font(filename: str)

A font resource for rendering text in Caption elements.

Args:
    filename: Path to a TrueType (.ttf) or OpenType (.otf) font file.

Properties:
    family (str, read-only): Font family name from metadata.
    source (str, read-only): File path used to load this font.

Methods:
    metrics(size): (ascent, descent, line_height) in px at that size.
{% endraw %}

## Properties

| Property | Description |
| --- | --- |
| `family` | {% raw %}Font family name (str, read-only). Retrieved from font metadata.{% endraw %} |
| `source` | {% raw %}Source filename path (str, read-only). The path used to load this font.{% endraw %} |

## Methods

### `metrics(size: int) -> tuple[float, float, float]` {% include api_badge.html kind="added" version="0.3.3-dev" %}

{% raw %}metrics(size: int) -> tuple[float, float, float]

Vertical metrics of this font at a pixel size, as a Caption of that font_size lays it out: (ascent, descent, line_height).

Args:
    size: Pixel size (a Caption's font_size), 1 to 2048

Returns:
    (ascent, descent, line_height) in px: ascent above the baseline, descent below it (positive), and the baseline-to-baseline distance between lines of multi-line text

Raises:
    ValueError: size is out of range, or the font has no metrics at it

Raises:
    RuntimeError: in an MCRF_HEADLESS build, which has no font rasterizer
{% endraw %}
