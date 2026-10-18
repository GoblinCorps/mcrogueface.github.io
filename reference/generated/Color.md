---
title: Color
layout: default
mcrf:
  objects:
    - Color
  diataxis: reference
  source: generated
  verified: 0.3.4
  verified_commit: ""
---

# Color {% include api_badge.html kind="changed" version="0.3.4-dev" %}

{% raw %}Color(r: int, g: int, b: int, a: int = 255)
Color(rgba: tuple[int, int, int] | tuple[int, int, int, int])
Color(color: str, a: int = 255)

RGBA color representation.

Args:
    r: Red component (0-255)
    g: Green component (0-255)
    b: Blue component (0-255)
    a: Alpha component (0-255, default 255 = opaque)
    color: A color name ('red', 'Dark Green', 'dust') or hex
        ('#f00', '#f008', '#ff0000', '#ff000080'). Names ignore case and
        everything but letters and digits. A name in several sources takes
        the first of css, xkcd, crayola, jenny. Color.names() lists them.
        Unknown names raise ValueError naming close matches.

    Every Color property accepts the same values: frame.fill_color = 'red'.

Note:
    Color is a VALUE TYPE (frozen 1.0 contract): properties that return a
    Color (e.g. frame.fill_color) return a fresh COPY, so mutating a component
    of the returned object is a silent no-op on the original. The two supported
    idioms are read-modify-writeback and whole-value assignment:

        # This does NOT work:
        frame.fill_color.r = 255  # Modifies a temporary copy

        # Read-modify-writeback:
        c = frame.fill_color
        c.r = 255
        frame.fill_color = c

        # Whole-value assignment:
        frame.fill_color = mcrfpy.Color(255, 0, 0)

    See also: API stability policy (docs/api-stability.md)
{% endraw %}

## Properties

| Property | Description |
| --- | --- |
| `a` {% include api_badge.html kind="changed" version="0.2.8-dev" %} | {% raw %}Alpha component, an int in 0-255 (0=transparent, 255=opaque); out of range raises ValueError.{% endraw %} |
| `b` {% include api_badge.html kind="changed" version="0.2.8-dev" %} | {% raw %}Blue component, an int in 0-255; out of range raises ValueError.{% endraw %} |
| `g` {% include api_badge.html kind="changed" version="0.2.8-dev" %} | {% raw %}Green component, an int in 0-255; out of range raises ValueError.{% endraw %} |
| `r` {% include api_badge.html kind="changed" version="0.2.8-dev" %} | {% raw %}Red component, an int in 0-255; out of range raises ValueError.{% endraw %} |

## Methods

### `from_hex(hex_string: str) -> Color` {% include api_badge.html kind="changed" version="0.3.4-dev" %}

*classmethod*

{% raw %}from_hex(hex_string: str) -> Color

Create a Color from a hexadecimal string, '#' optional. Color('#FF0000') also works, and takes the short forms '#F00' / '#F008' too.

Args:
    hex_string: Hex color string (e.g., '#FF0000', 'FF0000', '#AABBCCDD' for RGBA)

Returns:
    Color: New Color object with values from hex string

Raises:
    ValueError: If the string is not 6 or 8 hex digits (RGB or RGBA)

Note:
    This is a class method. Call as Color.from_hex('#FF0000')
{% endraw %}

### `lerp(other: Color, t: float) -> Color`

{% raw %}lerp(other: Color, t: float) -> Color

Linearly interpolate between this color and another.

Args:
    other: The target Color to interpolate towards
    t: Interpolation factor (0.0 = this color, 1.0 = other color). Automatically clamped to [0.0, 1.0]

Returns:
    Color: New Color representing the interpolated value

Note:
    All components (r, g, b, a) are interpolated independently
{% endraw %}

### `names() -> list[str]` {% include api_badge.html kind="added" version="0.3.4-dev" %}

*classmethod*

{% raw %}names() -> list[str]

List every color name Color(name) accepts, each once, in normalized form (lowercase letters and digits), sorted.


Returns:
    list[str]: names, e.g. 'darkgreen'

Note:
    Lookup ignores case and every character but letters and digits: 'Dark Green', 'dark_green' and 'darkgreen' are one name. A name in several sources takes the first of css, xkcd, crayola, jenny.
{% endraw %}

### `to_hex() -> str`

{% raw %}to_hex() -> str

Convert this Color to a hexadecimal string.


Returns:
    str: Hex string in format '#RRGGBB' or '#RRGGBBAA' (if alpha < 255)

Note:
    Alpha component is only included if not fully opaque (< 255)
{% endraw %}
