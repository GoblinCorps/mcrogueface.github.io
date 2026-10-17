---
title: DijkstraMap
layout: default
mcrf:
  objects:
    - DijkstraMap
  diataxis: reference
  source: generated
  verified: 0.3.3
  verified_commit: ""
---

# DijkstraMap {% include api_badge.html kind="changed" version="0.2.8-dev" %}

{% raw %}A Dijkstra distance map from a fixed root position.

Created by Grid.get_dijkstra_map(). Cannot be instantiated directly.

A DijkstraMap is a snapshot of the grid when it was computed: later
walkability edits do not change it, and it stays usable after the grid
is gone. Grid caches single-root maps, returning the same map while
the grid is unchanged and a rebuilt one after it changes.

Windowed (#445): the field covers `window`, the roots' bounding box grown
by `radius` (default: the whole grid, up to 511) and clipped to the grid.
Distances up to the radius are exact. Beyond that, and off the grid,
distance() returns the map's heuristic estimate; is_exact(pos) tells
which. A `complete` field (always, when the window is the whole grid)
is exact everywhere.

Properties:
    root (Vector): Root position (read-only)
    radius (int), window (x, y, w, h), complete (bool),
    heuristic (Heuristic | None): the field's extent and estimate

Methods:
    distance(pos) -> float | None: Get distance to root
    is_exact(pos) -> bool: Is distance(pos) exact
    path_from(pos) -> AStarPath | None: Get full path to root
    step_from(pos) -> Vector | None: Get single step toward root

Example:
    dijkstra = grid.get_dijkstra_map(player.pos)
    for enemy in enemies:
        dist = dijkstra.distance(enemy.pos)
        if dist and dist < 10:
            step = dijkstra.step_from(enemy.pos)
            if step:
                enemy.pos = step{% endraw %}

## Properties

| Property | Description |
| --- | --- |
| `complete` {% include api_badge.html kind="added" version="0.2.8-dev" %} | {% raw %}True if the field holds the roots' whole reachable region (bool, read-only): every distance is then exact and every other cell is unreachable. Always True when the window is the whole grid.{% endraw %} |
| `heuristic` {% include api_badge.html kind="added" version="0.2.8-dev" %} | {% raw %}The estimate used beyond the exact field (Heuristic \| None, read-only). None: such queries raise IndexError.{% endraw %} |
| `radius` {% include api_badge.html kind="added" version="0.2.8-dev" %} | {% raw %}Radius of the field's window around the roots (int, read-only). Distances up to radius are exact (radius * diagonal_cost, if that is below 1).{% endraw %} |
| `root` | {% raw %}Root position that distances are measured from (Vector, read-only).{% endraw %} |
| `window` {% include api_badge.html kind="added" version="0.2.8-dev" %} | {% raw %}The grid rectangle the field covers, as (x, y, w, h) (tuple, read-only): the roots' bounding box grown by radius, clipped to the grid.{% endraw %} |

## Methods

### `descent_step(pos: Vector | tuple) -> Vector | None` {% include api_badge.html kind="changed" version="0.2.8-dev" %}

{% raw %}descent_step(pos: Vector | tuple) -> Vector | None

Get the adjacent cell with the lowest distance (steepest descent). Unlike step_from, this always returns the best neighbor in a single hop without following a precomputed path.

Args:
    pos: Current position as Vector, Entity, or (x, y) tuple

Returns:
    Next position as Vector, or None if pos is a local minimum

Raises:
    IndexError: pos is beyond the exact field and the map was built with heuristic=None
{% endraw %}

### `distance(pos: Vector | tuple) -> float | None` {% include api_badge.html kind="changed" version="0.2.8-dev" %}

{% raw %}distance(pos: Vector | tuple) -> float | None

Get distance from position to the nearest root. Any position is answered, on or off the grid: exact within the map's field, otherwise the map's heuristic estimate (a lower bound). is_exact(pos) tells which.

Args:
    pos: Position as Vector, Entity, or (x, y) tuple

Returns:
    Float distance or estimate, or None if the position is certainly unreachable

Raises:
    IndexError: pos is beyond the exact field and the map was built with heuristic=None
{% endraw %}

### `invert() -> DijkstraMap`

{% raw %}invert() -> DijkstraMap

Return a new DijkstraMap whose distance field is inverted (safety field). Cells near a root become high values; descend to flee from original roots. The original DijkstraMap is unchanged.


Returns:
    New DijkstraMap with inverted distances
{% endraw %}

### `is_exact(pos: Vector | tuple) -> bool` {% include api_badge.html kind="added" version="0.2.8-dev" %}

{% raw %}is_exact(pos: Vector | tuple) -> bool

Whether distance(pos) is certain: an exact distance, or certainly unreachable. False where it is the heuristic's estimate.

Args:
    pos: Position as Vector, Entity, or (x, y) tuple (any position, on or off the grid)

Returns:
    True if the answer for pos is exact
{% endraw %}

### `path_from(pos: Vector | tuple) -> AStarPath` {% include api_badge.html kind="changed" version="0.2.8-dev" %}

{% raw %}path_from(pos: Vector | tuple) -> AStarPath

Get full path from position to root, along the exact field.

Args:
    pos: Starting position as Vector, Entity, or (x, y) tuple

Returns:
    AStarPath from pos toward root (empty at a root or if unreachable), or None if pos is beyond the exact field

Raises:
    IndexError: pos is beyond the exact field and the map was built with heuristic=None
{% endraw %}

### `step_from(pos: Vector | tuple) -> Vector | None` {% include api_badge.html kind="changed" version="0.2.8-dev" %}

{% raw %}step_from(pos: Vector | tuple) -> Vector | None

Get single step from position toward root. Beyond the exact field this is a greedy step to the walkable neighbour with the lowest estimate (it needs the grid to still exist).

Args:
    pos: Current position as Vector, Entity, or (x, y) tuple

Returns:
    Next position as Vector, or None if at root, unreachable, or no neighbour is closer

Raises:
    IndexError: pos is beyond the exact field and the map was built with heuristic=None
{% endraw %}

### `to_heightmap(size=None, unreachable=-1.0) -> HeightMap` {% include api_badge.html kind="changed" version="0.2.8-dev" %}

{% raw %}to_heightmap(size=None, unreachable=-1.0) -> HeightMap

Convert the exact distance field to a HeightMap covering the map's window: cell (0, 0) is grid cell window[:2]. Each cell's height is its distance from the root; place it on a grid-sized HeightMap with copy_from(pos=window[:2]).

Args:
    size: Optional (width, height) tuple. Defaults to the window's size
    unreachable: Value for cells not in the exact field: unreachable, or past the radius (default -1.0)

Returns:
    HeightMap with distance values as heights
{% endraw %}
