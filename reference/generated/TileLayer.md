---
title: TileLayer
layout: default
mcrf:
  objects:
    - TileLayer
  diataxis: reference
  source: generated
  verified: 0.3.5
  verified_commit: ""
---

# TileLayer {% include api_badge.html kind="changed" version="0.3.5-dev" %}

{% raw %}TileLayer(name=None, z_index=-1, texture=None, grid_size=None, grid=None)

A grid layer that stores sprite indices per cell for tile-based rendering.

TileLayers can be created standalone and attached to a Grid via add_layer()
or passed to the Grid constructor's layers parameter. Layers with size (0, 0)
automatically resize to match the Grid when attached.

Args:
    name (str): Layer name for Grid.layer(name) lookup. Default: None
    z_index (int): Render order relative to entities. Negative values render
        below entities (as backgrounds), positive values render above entities
        (as overlays). Default: -1 (background)
    texture (Texture): Sprite atlas containing tile images. Default: None,
        drawing with the grid's texture (looked up when drawn, so changing
        the grid's texture restyles this layer).
    grid_size (tuple): Dimensions as (width, height). If None or (0, 0), the
        layer will auto-resize when attached to a Grid. Default: None
    grid (Grid): If given, the layer is attached to it as if by grid.add_layer(layer)
        at construction (a mcrfpy.Grid, else TypeError). Default: None

Attributes:
    z_index (int): Layer z-order relative to entities (read/write)
    name (str): Layer name for lookup (read-only)
    visible (bool): Whether layer is rendered (read/write)
    texture (Texture | None): Its own atlas; None draws with the grid's
    grid_size (tuple): Layer dimensions as (width, height) (read-only)
    grid (Grid): Parent Grid or None. Setting manages layer association.

Methods:
    at(pos) -> int: Get the tile index at cell position pos (a tuple/Vector, or at(x, y))
    set(pos, index): Set the tile index at cell position pos
    fill(index): Fill the entire layer with a single tile index
    layer[x, y] -> int: Get the tile index at cell (x, y); layer[x, y] = index sets it
        (key must be a 2-tuple of ints)
    fill_rect((x, y), (w, h), index): Fill the rectangle at (x, y) of size (w, h) with a
        tile index. pos and size must be real tuples (a Vector or list raises TypeError)
    edit(): Context manager yielding a writable (height, width) int32 view of the tile indices
    apply_threshold(source, range, tile) -> TileLayer: Set a tile where the HeightMap
        value is within (min, max)
    apply_ranges(source, ranges) -> TileLayer: Apply several ((min, max), tile_index)
        specs from a HeightMap in one pass

Tile Index Values:
    -1: No tile (transparent/empty cell)
    0+: Index into the texture's sprite atlas (row-major order)

Example:
    terrain = mcrfpy.TileLayer(z_index=-2, name='terrain', texture=mcrfpy.default_texture)
    grid = mcrfpy.Grid(grid_size=(20, 15), layers=[terrain])
    terrain.fill(0)  # Fill with tile index 0
    grid.layer('terrain').set((5, 5), 42)  # Place tile 42 at (5, 5)
    terrain.fill_rect((2, 2), (4, 3), 7)  # 4x3 block of tile 7 from (2, 2){% endraw %}

## Properties

| Property | Description |
| --- | --- |
| `grid` | {% raw %}Parent Grid or None (Grid \| None). Setting manages layer association and handles lazy allocation.{% endraw %} |
| `grid_size` | {% raw %}Layer dimensions as (width, height) tuple (tuple, read-only).{% endraw %} |
| `name` | {% raw %}Layer name (str, read-only). Used for Grid.layer(name) lookup.{% endraw %} |
| `texture` {% include api_badge.html kind="changed" version="0.2.8-dev" %} | {% raw %}This layer's own tile atlas (Texture \| None). None: it draws with its grid's texture, looked up each time it's drawn. Assign None to inherit again.{% endraw %} |
| `visible` | {% raw %}Whether the layer is rendered (bool).{% endraw %} |
| `z_index` | {% raw %}Layer z-order (int). Negative values render below entities.{% endraw %} |

## Methods

### `apply_ranges(source: HeightMap, ranges: list) -> TileLayer` {% include api_badge.html kind="changed" version="0.3.5-dev" %}

{% raw %}apply_ranges(source: HeightMap, ranges: list) -> TileLayer

Apply multiple tile assignments from a HeightMap in a single pass. Later ranges override earlier ones if overlapping.

Args:
    source: Source heightmap (must match layer dimensions)
    ranges: List of ((min, max), tile_index) tuples

Returns:
    self for method chaining

Note:
    Any int is stored. An index outside 0 to sprite_count-1 is not rendered (like -1); one above the highest sprite index of a known texture also warns (TextureWarning).

Note:
    Cells not matching any range are left unchanged.
{% endraw %}

### `apply_threshold(source: HeightMap, range: tuple, tile: int) -> TileLayer` {% include api_badge.html kind="changed" version="0.3.5-dev" %}

{% raw %}apply_threshold(source: HeightMap, range: tuple, tile: int) -> TileLayer

Set a tile index for cells where the HeightMap value falls within a range.

Args:
    source: Source heightmap (must match layer dimensions)
    range: Value range as (min, max) inclusive
    tile: Tile index to set for cells in range

Returns:
    self for method chaining

Note:
    Any int is stored. An index outside 0 to sprite_count-1 is not rendered (like -1); one above the highest sprite index of a known texture also warns (TextureWarning).
{% endraw %}

### `at(pos: tuple | Vector) or (x: int, y: int) -> int`

{% raw %}at(pos: tuple | Vector) or (x: int, y: int) -> int

Get the tile index at a cell position. Returns -1 if no tile is set.

Args:
    pos: Position as (x, y) tuple, list, or Vector; or pass x and y separately

Returns:
    Tile index at the specified cell, or -1 if empty

Raises:
    IndexError: If coordinates are out of bounds
{% endraw %}

### `edit() -> context manager`

{% raw %}edit() -> context manager

Context manager yielding a zero-copy, writable view of the layer's tile indices with shape (height, width), dtype int32 (-1 = no tile). Writes to the view alias the layer's storage (no copy). On exit the whole layer is invalidated and re-rendered.


Note:
    Use as `with layer.edit() as view:` -- e.g. np.asarray(view)[...] = ....

See also: Bulk-edit convention (#328) (docs/api-stability.md)
{% endraw %}

### `fill(index: int) -> None` {% include api_badge.html kind="changed" version="0.3.5-dev" %}

{% raw %}fill(index: int) -> None

Fill the entire layer with the specified tile index.

Args:
    index: Tile index to fill with (-1 for no tile)

Note:
    Any int is stored. An index outside 0 to sprite_count-1 is not rendered (like -1); one above the highest sprite index of a known texture also warns (TextureWarning).
{% endraw %}

### `fill_rect(pos: tuple, size: tuple, index: int) -> None` {% include api_badge.html kind="changed" version="0.3.5-dev" %}

{% raw %}fill_rect(pos: tuple, size: tuple, index: int) -> None

Fill a rectangular region with a tile index.

Args:
    pos: Top-left corner as (x, y)
    size: Dimensions as (width, height)
    index: Tile index to fill with (-1 for no tile)

Note:
    Any int is stored. An index outside 0 to sprite_count-1 is not rendered (like -1); one above the highest sprite index of a known texture also warns (TextureWarning).
{% endraw %}

### `set(pos, index: int) -> None` {% include api_badge.html kind="changed" version="0.3.5-dev" %}

{% raw %}set(pos, index: int) -> None

Set the tile index at a cell position. Use -1 to clear the tile.

Args:
    pos: Position as (x, y) tuple, list, or Vector
    index: Tile index (-1 for no tile)

Raises:
    IndexError: If coordinates are out of bounds

Note:
    Any int is stored. An index outside 0 to sprite_count-1 is not rendered (like -1); one above the highest sprite index of a known texture also warns (TextureWarning).
{% endraw %}
