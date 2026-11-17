---
title: TextureWarning
layout: default
mcrf:
  objects:
    - TextureWarning
  diataxis: reference
  source: generated
  verified: 0.3.5
  verified_commit: ""
---

# TextureWarning {% include api_badge.html kind="added" version="0.2.8-dev" %} {% include api_badge.html kind="changed" version="0.3.5-dev" %}

{% raw %}Warns about the texture a grid draws with: drawn with no texture, so mcrfpy.default_texture was assigned; or a TileLayer was written a tile index above its texture's highest sprite index (it will not be rendered). Silence with warnings.simplefilter('ignore', mcrfpy.TextureWarning).{% endraw %}

## Properties

| Property | Description |
| --- | --- |
| `args` {% include api_badge.html kind="added" version="0.2.8-dev" %} |  |

## Methods

### `add_note($self, note, /)` {% include api_badge.html kind="added" version="0.2.8-dev" %}

{% raw %}Add a note to the exception{% endraw %}

### `with_traceback($self, tb, /)` {% include api_badge.html kind="added" version="0.2.8-dev" %}

{% raw %}Set self.__traceback__ to tb and return self.{% endraw %}
