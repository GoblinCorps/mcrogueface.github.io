---
title: GridData
layout: default
mcrf:
  objects:
    - GridData
  diataxis: reference
  source: generated
  verified: 0.3.5
  verified_commit: ""
---

# GridData {% include api_badge.html kind="added" version="0.2.8-dev" %} {% include api_badge.html kind="changed" version="0.2.8-dev" %}

{% raw %}GridData(grid_size=None, texture=None, layers=None)

A tile map: cells, entities, layers, FOV and pathfinding state.

GridData is DATA, not a widget -- it has no position, no size, no
camera, and is never drawn. Appending one to a scene raises TypeError.
To display it, point one or more Grid (GridView) cameras at it:

    data = mcrfpy.GridData(grid_size=(80, 40))
    main = mcrfpy.Grid(grid=data, pos=(0, 0), size=(800, 400))
    mini = mcrfpy.Grid(grid=data, pos=(820, 0), size=(160, 80))

Both views show the same map and the same entities, each through its
own camera. A map with no view at all is perfectly valid (an offscreen
level, still steppable and queryable).

mcrfpy.Grid(grid_size=...) is sugar for a GridView that creates its own
GridData; reach it with `grid.grid_data`.

Args:
    grid_size (tuple): Grid dimensions as (grid_w, grid_h). Default: (2, 2)
    texture (Texture): Tile atlas; its sprite size fills cell_size. Default:
        None (needs no display; the first view to draw it assigns
        mcrfpy.default_texture, with a TextureWarning).
    layers (list): ColorLayer/TileLayer objects. Omit for a default
        'tilesprite' TileLayer; pass None for no layers at all.

Attributes:
    grid_size (Vector, read-only): Dimensions in tiles
    grid_w, grid_h (int, read-only): Dimensions in tiles
    texture (Texture | None): Tile atlas. Layers and entities with no
        texture of their own draw with it.
    cell_size (Vector): Pixels per cell for every tile<->pixel conversion.
        Unset: the texture's sprite size, or 1x1 with no texture.
    cell_width, cell_height (int): Components of cell_size
    entities (EntityCollection): Entities on this map
    layers (tuple, read-only): Layers sorted by z_index
    fov (FOV): Default field-of-view algorithm
    fov_radius (int): Default field-of-view radius{% endraw %}

## Properties

| Property | Description |
| --- | --- |
| `cell_height` {% include api_badge.html kind="added" version="0.2.8-dev" %} | {% raw %}cell_size.y (int).{% endraw %} |
| `cell_size` {% include api_badge.html kind="added" version="0.2.8-dev" %} | {% raw %}Pixels per cell, used by every tile<->pixel conversion: entity x/y/pos and a view's camera (Vector). Unset, it reads the texture's sprite size, or 1x1 with no texture. Assign whole pixels to set it, or None to unset it. Changing it keeps each view's camera on the same cells.{% endraw %} |
| `cell_width` {% include api_badge.html kind="added" version="0.2.8-dev" %} | {% raw %}cell_size.x (int).{% endraw %} |
| `dijkstra_cache_budget` {% include api_badge.html kind="added" version="0.2.8-dev" %} | {% raw %}Bytes of Dijkstra distance field get_dijkstra_map() may keep cached (int, default 256 MiB; each map costs 4 bytes per cell). Least recently used maps are evicted past it; the most recent one is always kept. Lowering it evicts at once.{% endraw %} |
| `dijkstra_cache_bytes` {% include api_badge.html kind="added" version="0.2.8-dev" %} | {% raw %}Bytes of Dijkstra distance field currently cached (int, read-only). Compare with dijkstra_cache_budget.{% endraw %} |
| `entities` {% include api_badge.html kind="added" version="0.2.8-dev" %} | {% raw %}EntityCollection of entities on this map (EntityCollection, read-only). Shared by every view of this data.{% endraw %} |
| `fov` {% include api_badge.html kind="added" version="0.2.8-dev" %} | {% raw %}FOV algorithm for this map (FOV enum). Used by entity.updateVisibility() and layer methods when fov=None.{% endraw %} |
| `fov_radius` {% include api_badge.html kind="added" version="0.2.8-dev" %} | {% raw %}Default FOV radius for this map (int). Used when radius is not specified.{% endraw %} |
| `grid_h` {% include api_badge.html kind="added" version="0.2.8-dev" %} | {% raw %}Grid height in cells (int, read-only).{% endraw %} |
| `grid_size` {% include api_badge.html kind="added" version="0.2.8-dev" %} | {% raw %}Grid dimensions as (grid_w, grid_h) (Vector, read-only).{% endraw %} |
| `grid_w` {% include api_badge.html kind="added" version="0.2.8-dev" %} | {% raw %}Grid width in cells (int, read-only).{% endraw %} |
| `layers` {% include api_badge.html kind="added" version="0.2.8-dev" %} | {% raw %}Tuple of grid layers sorted by z_index (tuple, read-only). Contains ColorLayer and TileLayer objects.{% endraw %} |
| `texture` {% include api_badge.html kind="added" version="0.2.8-dev" %} {% include api_badge.html kind="changed" version="0.2.8-dev" %} | {% raw %}Tile atlas for this map (Texture \| None). Layers and entities with no texture of their own draw with it, so assigning it restyles them. Setting one fills an unset cell_size; removing it (None) leaves cell_size as it is.{% endraw %} |

## Methods

### `add_layer(layer: ColorLayer | TileLayer) -> ColorLayer | TileLayer` {% include api_badge.html kind="added" version="0.2.8-dev" %}

{% raw %}add_layer(layer: ColorLayer | TileLayer) -> ColorLayer | TileLayer

Add a layer to the grid. Layers with size (0, 0) are automatically resized to match the grid.

Args:
    layer: A ColorLayer or TileLayer object. Named layers replace any existing layer with the same name.

Returns:
    The added layer object

Raises:
    ValueError: If layer is already attached to another grid, or if layer size doesn't match grid (and isn't (0,0))

Raises:
    TypeError: If argument is not a ColorLayer or TileLayer
{% endraw %}

### `apply_ranges(source: HeightMap, ranges: list) -> GridData` {% include api_badge.html kind="added" version="0.2.8-dev" %}

{% raw %}apply_ranges(source: HeightMap, ranges: list) -> GridData

Apply multiple walkability thresholds to the grid in a single pass.

Args:
    source: HeightMap with values to check. Must match grid size.
    ranges: List of (range_tuple, properties_dict) tuples where range_tuple=(min,max) and properties_dict has 'walkable'/'transparent' keys

Returns:
    GridData: self, for method chaining
{% endraw %}

### `apply_threshold(source: HeightMap, range: tuple, walkable: bool = None, transparent: bool = None) -> GridData` {% include api_badge.html kind="added" version="0.2.8-dev" %}

{% raw %}apply_threshold(source: HeightMap, range: tuple, walkable: bool = None, transparent: bool = None) -> GridData

Apply walkable/transparent properties to cells where heightmap values fall within range.

Args:
    source: HeightMap with values to check. Must match grid size.
    range: Tuple of (min, max) - cells with values in this range are affected
    walkable: If not None, set walkable to this value for cells in range
    transparent: If not None, set transparent to this value for cells in range

Returns:
    GridData: self, for method chaining

Raises:
    ValueError: If HeightMap size doesn't match grid size
{% endraw %}

### `at(x: int, y: int) -> GridPoint` {% include api_badge.html kind="added" version="0.2.8-dev" %}

{% raw %}at(x: int, y: int) -> GridPoint

Return the GridPoint cell at grid coordinates (x, y).

Args:
    x: Column index (0-based)
    y: Row index (0-based)

Returns:
    GridPoint: the cell at the given position

Raises:
    IndexError: If x or y is out of range

Note:
    Also accepts a single positional tuple/list/Vector: at((x, y)) or at(vec), or keyword form: at(pos=(x, y)).
{% endraw %}

### `compute_fov(pos, radius: int = 0, light_walls: bool = True, algorithm: FOV | int = FOV.BASIC) -> None` {% include api_badge.html kind="added" version="0.2.8-dev" %}

{% raw %}compute_fov(pos, radius: int = 0, light_walls: bool = True, algorithm: FOV | int = FOV.BASIC) -> None

Compute field of view from a position. Updates the internal FOV state; use is_in_fov() to query visibility.

Args:
    pos: Position as (x, y) tuple, list, or Vector
    radius: Maximum view distance (0 = unlimited)
    light_walls: Whether walls are lit when visible
    algorithm: FOV algorithm to use (FOV.BASIC, FOV.DIAMOND, FOV.SHADOW, FOV.PERMISSIVE_0-8)

Returns:
    None
{% endraw %}

### `entities_in_radius(pos: tuple | Vector, radius: float) -> list` {% include api_badge.html kind="added" version="0.2.8-dev" %} {% include api_badge.html kind="changed" version="0.3.2-dev" %}

{% raw %}entities_in_radius(pos: tuple | Vector, radius: float) -> list

Query entities whose logical cell (grid_pos) is within radius, using the spatial hash (O(k) where k = nearby entities). Measured from the cell, not from draw_pos: an entity mid-animation is found at its cell.

Args:
    pos: Center cell as (x, y) tuple, Vector, or other 2-element sequence (cell units; may be fractional)
    radius: Search radius in cells

Returns:
    List of Entity objects within the radius
{% endraw %}

### `find_path(start, end, diagonal_cost: float = 1.41, collide: str = None, heuristic = None, weight: float = 1.0) -> AStarPath | None` {% include api_badge.html kind="added" version="0.2.8-dev" %}

{% raw %}find_path(start, end, diagonal_cost: float = 1.41, collide: str = None, heuristic = None, weight: float = 1.0) -> AStarPath | None

Compute A* path between two points. The returned AStarPath can be iterated or walked step-by-step.

Args:
    start: Starting position as Vector, Entity, or (x, y) tuple
    end: Target position as Vector, Entity, or (x, y) tuple
    diagonal_cost: Cost of diagonal movement (default: 1.41)
    collide: Label string. Entities with this label block pathfinding.
    heuristic: Heuristic enum member, string name, or int (EUCLIDEAN=0, MANHATTAN=1, CHEBYSHEV=2). None uses default (Euclidean).
    weight: Heuristic weight multiplier. Values > 1.0 trade optimality for speed (weighted A*).

Returns:
    AStarPath object if path exists, None otherwise
{% endraw %}

### `get_dijkstra_map(root=None, diagonal_cost: float = 1.41, collide: str = None, roots=None, radius: int = None, heuristic: Heuristic = Heuristic.OCTILE) -> DijkstraMap` {% include api_badge.html kind="added" version="0.2.8-dev" %} {% include api_badge.html kind="changed" version="0.2.8-dev" %}

{% raw %}get_dijkstra_map(root=None, diagonal_cost: float = 1.41, collide: str = None, roots=None, radius: int = None, heuristic: Heuristic = Heuristic.OCTILE) -> DijkstraMap

Get or create a cached Dijkstra distance map for a root position. A cached map is returned only while it is still current: changing walkability, or moving an entity that carries the collide label, makes the next request rebuild it. The cache bounds its own memory.

Args:
    root: Root position as Vector, Entity, or (x, y) tuple. Use 'root' for single-source maps (cached by position).
    diagonal_cost: Cost of diagonal movement (default: 1.41)
    collide: Label string. Entities with this label block pathfinding.
    roots: Sequence of root positions or a DiscreteMap mask for multi-source Dijkstra. Pass 'roots' instead of 'root' for multi-source maps (not cached).
    radius: The field covers the roots' bounding box grown by radius, clipped to the grid; distances up to radius are exact. Default (None): the whole grid, up to 511 -- a field of at most 1023 x 1023 cells, 4 bytes each.
    heuristic: Estimate for positions beyond the exact field, including off the grid (default Heuristic.OCTILE, which uses diagonal_cost). None: such queries raise IndexError.

Returns:
    DijkstraMap object for querying distances and paths

Note:
    The returned map is a snapshot: it does not change when the grid does. Call get_dijkstra_map() again (cheap while nothing changed) to follow edits.
{% endraw %}

### `is_in_fov(x: int, y: int) -> bool` {% include api_badge.html kind="added" version="0.2.8-dev" %}

{% raw %}is_in_fov(x: int, y: int) -> bool

Check if a cell is in the field of view. Must call compute_fov() first to calculate visibility.

Args:
    x: Column index (0-based)
    y: Row index (0-based)

Returns:
    True if the cell is visible, False otherwise

Note:
    Also accepts a single positional tuple/list/Vector: is_in_fov((x, y)) or is_in_fov(vec), or keyword form: is_in_fov(pos=(x, y)).
{% endraw %}

### `layer(name: str) -> ColorLayer | TileLayer | None` {% include api_badge.html kind="added" version="0.2.8-dev" %}

{% raw %}layer(name: str) -> ColorLayer | TileLayer | None

Get a layer by its name.

Args:
    name: The name of the layer to find

Returns:
    The layer with the specified name, or None if not found
{% endraw %}

### `observe(origin=None, fov_radius: int = None, light_walls: bool = True, algorithm: FOV | int = FOV.BASIC) -> dict` {% include api_badge.html kind="added" version="0.2.8-dev" %} {% include api_badge.html kind="changed" version="0.2.8-dev" %}

{% raw %}observe(origin=None, fov_radius: int = None, light_walls: bool = True, algorithm: FOV | int = FOV.BASIC) -> dict

Take an immutable snapshot of this map as seen through a field of view: which cells are visible, which of those are walkable or transparent, and which entities stand on a visible cell. Use this for fog-of-war persistence, AI perception queries, or replaying what an observer could see at a point in time -- the returned dict holds no live references and is unaffected by later grid or entity changes.

Args:
    origin: Observing position as (x, y) tuple, list, or Vector. None (the default) means an unbounded mask: every in-bounds cell is visible and no FOV state is touched at all.
    fov_radius: Maximum view distance from origin. None (the default) means an unlimited radius -- occlusion from walls still applies if origin is given. Must be > 0 when given: 0 is a ValueError, not 'unlimited', because a caller-computed radius of 0 means 'see nothing', not 'see everything'.
    light_walls: Whether walls are themselves visible when lit, passed through to the FOV computation exactly as compute_fov() would use it. Ignored when origin is None.
    algorithm: FOV algorithm to use (FOV.BASIC, FOV.DIAMOND, FOV.SHADOW, FOV.PERMISSIVE_0-8, FOV.RESTRICTIVE, FOV.SYMMETRIC_SHADOWCAST). Ignored when origin is None.

Returns:
    dict with keys: 'tick' (int, engine current_frame read once at the projection instant), 'mask' (VisibilityMask, the cells this projection could see), 'walkable' (frozenset of (x,y) tuples, the subset of mask.cells that are walkable), 'transparent' (frozenset of (x,y) tuples, the subset of mask.cells that are transparent), and 'entities' (tuple of dict, one per entity standing on a masked cell -- each with keys 'name' (str), 'cell_pos' ((x,y) tuple), 'labels' (frozenset of str), and 'turn_order' (int)).

Raises:
    ValueError: fov_radius is given without an origin, origin is out of bounds for this grid, or fov_radius <= 0

Raises:
    TypeError: origin is not a valid position, or fov_radius/algorithm is the wrong type

Raises:
    RuntimeError: The engine is not initialized, so there is no current_frame tick to record

Note:
    An entity's 'cell_pos' is a plain (x, y) int tuple, NOT the live entity.cell_pos Vector -- the snapshot is inert: hashable, serialisable, and unaffected by later entity movement.

Note:
    'labels' is a frozenset, so membership is a real predicate: label in snap['entities'][i]['labels'].

Note:
    'entities' is a tuple, not a dict keyed by name: entity names are not unique and may be empty, so keying by name here would silently discard entities. The caller chooses the collision policy.

Note:
    Terrain is given as two cell sets rather than a per-cell record: (x, y) in snap['walkable']. A cell absent from 'walkable' is either not walkable OR not observed -- check snap['mask'] to tell those apart. That distinction is deliberate: it is the entire point of a masked projection.

Note:
    Grid layers are NOT projected. They are appearance, not world state.

Note:
    The tick is read once, at the projection instant, and is the same value carried by mask.tick. Calling observe() inside mcrfpy.lock() is what makes that instant a frame barrier.

Note:
    observe() is side-effect-free with or without an origin (#402): it computes its FOV in a scratch buffer private to the call and never writes the shared per-grid FOV state that compute_fov()/is_in_fov() use. A background observer projecting from an NPC's position therefore cannot disturb a field of view the player or the renderer just computed, and two observers on one grid do not interfere.

Note:
    observe() never advances a frame and never releases the GIL: the snapshot is atomic with respect to other Python threads. It does NOT take the lock for you -- wrap the call in mcrfpy.lock() yourself when you need it to be atomic with respect to the frame.
{% endraw %}

### `remove_layer(name_or_layer: str | ColorLayer | TileLayer) -> None` {% include api_badge.html kind="added" version="0.2.8-dev" %}

{% raw %}remove_layer(name_or_layer: str | ColorLayer | TileLayer) -> None

Remove a layer from the grid by name or by object reference.

Args:
    name_or_layer: Either a layer name (str) or the layer object itself

Raises:
    KeyError: If name is provided but no layer with that name exists

Raises:
    TypeError: If argument is not a string, ColorLayer, or TileLayer
{% endraw %}

### `step(n: int = 1, turn_order: int = None) -> None` {% include api_badge.html kind="added" version="0.2.8-dev" %}

{% raw %}step(n: int = 1, turn_order: int = None) -> None

Execute n rounds of turn-based entity behavior. Each round: entities grouped by turn_order (ascending), behaviors executed, triggers fired (TARGET, DONE, BLOCKED), movement animated.

Args:
    n: Number of rounds to execute (default: 1)
    turn_order: If provided, only process entities with this turn_order value
{% endraw %}
