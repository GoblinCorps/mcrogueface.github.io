---
title: Color
layout: default
mcrf:
  objects:
    - Color
  diataxis: reference
  source: generated
  verified: 0.3.3
  verified_commit: ""
---

# Color

{% raw %}Color(r: int = 0, g: int = 0, b: int = 0, a: int = 255)

RGBA color representation.

Args:
    r: Red component (0-255)
    g: Green component (0-255)
    b: Blue component (0-255)
    a: Alpha component (0-255, default 255 = opaque)

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

### `from_hex(hex_string: str) -> Color`

*classmethod*

{% raw %}from_hex(hex_string: str) -> Color

Create a Color from a hexadecimal string.

Args:
    hex_string: Hex color string (e.g., '#FF0000', 'FF0000', '#AABBCCDD' for RGBA)

Returns:
    Color: New Color object with values from hex string

Raises:
    ValueError: If hex string is not 6 or 8 characters (RGB or RGBA)

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

### `to_hex() -> str`

{% raw %}to_hex() -> str

Convert this Color to a hexadecimal string.


Returns:
    str: Hex string in format '#RRGGBB' or '#RRGGBBAA' (if alpha < 255)

Note:
    Alpha component is only included if not fully opaque (< 255)
{% endraw %}
