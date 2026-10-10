---
layout: default
title: DijkstraMap
mcrf:
  objects: [DijkstraMap, AStarPath, Grid]
  diataxis: reference
  disposition: current
  verified: "0.3.0-dev"
  verified_commit: 336f00e
---

# DijkstraMap

Dijkstra distance map from a fixed root position.

## Overview

A `DijkstraMap` represents precomputed distances from a root position to the reachable cells of a window of a Grid (by default the whole grid, up to a radius of 511). It is created by `Grid.get_dijkstra_map()` and cannot be instantiated directly. Dijkstra maps are useful for AI pathfinding, influence maps, and flow-field navigation where multiple entities need to path toward the same goal.

## Quick Reference

```python
# Create Dijkstra map from goal position
dijkstra = grid.get_dijkstra_map((goal_x, goal_y))

# Get distance from an entity (or any (x, y) tile position) to the goal
dist = dijkstra.distance(enemy)

# Get full path from position to root (an AStarPath)
path = dijkstra.path_from(enemy)

# Get single step toward goal (for AI)
next_pos = dijkstra.step_from(enemy)
if next_pos:
    enemy.grid_pos = next_pos

# Convert to heightmap for visualization (window-sized; see "Windowed maps")
heightmap = dijkstra.to_heightmap()

# Is this answer exact, or the heuristic's estimate? (see "Windowed maps")
if not dijkstra.is_exact(enemy):
    ...
```

## Constructor

`DijkstraMap` cannot be instantiated directly. Use `Grid.get_dijkstra_map()` to create maps.

```python
# Correct way to create a Dijkstra map
dijkstra = grid.get_dijkstra_map((goal_x, goal_y))
```

Dijkstra maps are cached by the Grid. Calling `get_dijkstra_map()` with the same root position returns the cached map while the grid is unchanged; after a walkability edit it returns a rebuilt one. A map you hold is a snapshot: it keeps its distances, and stays usable after the grid is gone. The cache is capped at `grid.dijkstra_cache_budget` bytes, and keyed by root, `collide`, `diagonal_cost`, `radius` and `heuristic`.

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `root` | Vector | Goal position, read-only |
| `radius` | int | Radius of the field's window around the roots, read-only |
| `window` | tuple | `(x, y, w, h)`: the grid rectangle the field covers, read-only |
| `complete` | bool | True if the field holds the roots' whole reachable region, read-only |
| `heuristic` | Heuristic or None | The estimate used beyond the field, read-only |

## Methods

| Method | Description |
|--------|-------------|
| `distance(pos)` | Get distance from pos (Vector, Entity, or (x, y) tuple) to root, or `None` if unreachable. Beyond the field, or off the grid, the heuristic's estimate |
| `is_exact(pos)` | `True` if `distance(pos)` is exact (or certainly unreachable), `False` if it is an estimate |
| `path_from(pos)` | Get complete path from pos to root as an `AStarPath`, ordered from `pos` toward the root (`origin` is `pos`, `destination` is the root); `None` beyond the field |
| `step_from(pos)` | Get next step toward root as a Vector (always a cell adjacent to `pos`), or `None` if at root/unreachable. Beyond the field, a greedy step toward it |
| `descent_step(pos)` | Get the adjacent cell with the lowest distance (steepest single-hop descent) |
| `invert()` | Return a new `DijkstraMap` with distances inverted (a "flee" field), root unchanged |
| `to_heightmap(size=None, unreachable=-1.0)` | Convert distances to a `HeightMap` for visualization. Window-sized: cell (0, 0) is grid cell `window[:2]` |

## Windowed maps

`get_dijkstra_map(root, radius=None, heuristic=mcrfpy.Heuristic.OCTILE)` computes the field over a window: the roots' bounding box grown by `radius`, clipped to the grid (so it is off-centre near an edge). The default radius is the whole grid up to 511, a field of at most 1023 x 1023 cells at 4 bytes each; on a grid up to 1023 on a side the window is the whole grid, as it always was.

- Distances up to the radius are exact (`radius * diagonal_cost` if `diagonal_cost` is below 1). If the flood stayed inside the window, `complete` is `True`: every distance is exact and every other cell is certainly unreachable (`None`), off the grid included.
- Otherwise, beyond the radius and off the grid, `distance()` returns the heuristic's estimate (a lower bound, never below the radius) and `is_exact()` is `False`. Build the map with `heuristic=None` to make those queries raise `IndexError` instead.
- `step_from()` / `descent_step()`, and SEEK/FLEE behaviors, take a greedy step toward the field (away, on an inverted map); this needs the grid to still exist. `path_from()` returns `None` there.
- Place `to_heightmap()` on a grid-sized `HeightMap` with `full.copy_from(dijkstra.to_heightmap(), pos=dijkstra.window[:2])`.

```python
# A 129 x 129 field around the player on a 4000 x 4000 grid
dm = grid.get_dijkstra_map(player.cell_pos, radius=64)
print(dm.window)                       # (1936, 1936, 129, 129) for a player at (2000, 2000)
dm.distance((2010, 2005))              # 12.05, exact
dm.distance((2500, 2500))              # 705.0, the OCTILE estimate
dm.is_exact((2500, 2500))              # False
dm.step_from((2500, 2500))             # Vector(2499, 2499): a greedy step toward the field
```

On an 8192 x 8192 grid (the largest a grid can be), a default map builds in about 45 ms and holds 4 MB; a whole-grid map took about 6 s and 268 MB.

## Usage Patterns

### AI Movement Toward Goal

```python
# Create map toward player
player_dijkstra = grid.get_dijkstra_map(player.grid_pos)

# Move all enemies toward player
for enemy in grid.entities:
    if enemy != player:
        next_step = player_dijkstra.step_from(enemy)
        if next_step:
            enemy.grid_pos = next_step
```

### Flee Behavior

```python
# To flee, move to neighbor with highest distance
danger_map = grid.get_dijkstra_map(threat.grid_pos)

def flee_step(entity):
    best_pos = None
    best_dist = danger_map.distance(entity)

    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = entity.grid_x + dx, entity.grid_y + dy
        if 0 <= nx < grid.grid_size.x and 0 <= ny < grid.grid_size.y and grid.at(nx, ny).walkable:
            dist = danger_map.distance((nx, ny))
            if dist is not None and (best_dist is None or dist > best_dist):
                best_dist = dist
                best_pos = (nx, ny)

    if best_pos:
        entity.grid_pos = best_pos
```

### Distance-Based Decisions

```python
goal_map = grid.get_dijkstra_map(treasure.grid_pos)

for entity in grid.entities:
    dist = goal_map.distance(entity)
    if dist is None:
        print(f"{entity} cannot reach treasure")
    elif dist < 5:
        print(f"{entity} is very close!")
    elif dist < 15:
        print(f"{entity} is {dist} steps away")
```

### Visualization with HeightMap

```python
dijkstra = grid.get_dijkstra_map((goal_x, goal_y))
heightmap = dijkstra.to_heightmap()

# Apply to a color layer for visualization
color_layer = mcrfpy.ColorLayer(z_index=1, name="distance_gradient")
grid.add_layer(color_layer)
color_layer.apply_gradient(
    heightmap,
    (0, 20),                    # value range: 0 (root) to 20 tiles away
    mcrfpy.Color(0, 255, 0),    # Close = green
    mcrfpy.Color(255, 0, 0)     # Far = red
)
```

### Cache Management

```python
# Dijkstra maps are cached automatically
map1 = grid.get_dijkstra_map((10, 10))
map2 = grid.get_dijkstra_map((10, 10))  # Returns cached map

# Changing the grid: the next request is rebuilt
grid.at(5, 5).walkable = False
map3 = grid.get_dijkstra_map((10, 10))  # Recomputed against the new wall
```

## Related

<div class="related-objects">
<div class="object-links">
<a href="Grid" class="object-link">Grid</a>
<a href="Entity" class="object-link">Entity</a>
<a href="AStarPath" class="object-link">AStarPath</a>
<a href="GridPoint" class="object-link">GridPoint</a>
<a href="../systems/grid" class="object-link">Grid System</a>
</div>
</div>
