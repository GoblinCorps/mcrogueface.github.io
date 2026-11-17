---
layout: default
title: Dijkstra Maps
parent: Cookbook
nav_order: 4
mcrf:
  objects: [Grid, DijkstraMap, Color]
  diataxis: howto
  disposition: needs-review
  verified: "0.3.0-dev"
  verified_commit: 336f00e
---

# Dijkstra Distance Maps

Use Dijkstra maps for AI movement, area effects, and tactical analysis.

---

## Overview

Dijkstra maps (also called "distance fields") provide:
- Distance from any cell to a goal
- Optimal pathfinding to goals
- AI flee/chase behavior
- Area-of-influence calculations

In mcrfpy, a Dijkstra map is a `DijkstraMap` object returned by
`grid.get_dijkstra_map(root)`. The grid caches maps by their root position — calling
`get_dijkstra_map` again with the same root returns the same object, for as long as
the grid is unchanged. After a walkability edit (or, for `collide=`, a labelled entity
moving) the next call returns a rebuilt map; there is nothing to invalidate by hand.

---

## Quick Start

<!-- snippet: 372_grid_dijkstra_3 region=quickstart -->
```python
import mcrfpy

# grid is an existing mcrfpy.Grid; player is an mcrfpy.Entity on that grid

# Get (or reuse the cached) distance map rooted at the player's position
dijkstra = grid.get_dijkstra_map(player.grid_pos)

# Get distance from any cell to the root
distance = dijkstra.distance((target_x, target_y))

# Get a single step from any cell toward the root
step = dijkstra.step_from((start_x, start_y))

# Get the full path from any cell to the root
path = dijkstra.path_from((start_x, start_y))
```
<!-- /snippet -->

---

## Basic Pathfinding

Use Dijkstra for enemy movement:

<!-- snippet: 159_grid_dijkstra_1 region=move_enemy -->
```python
def move_enemy_toward_player(grid, enemy, player):
    """Move enemy one step toward the player."""
    dijkstra = grid.get_dijkstra_map(player.grid_pos)
    step = dijkstra.step_from(enemy.grid_pos)
    if step is not None:
        enemy.grid_pos = step
```
<!-- /snippet -->

---

## AI Behaviors

### Chase Behavior

Descend the distance field toward the root:

<!-- snippet: 372_grid_dijkstra_3 region=chase -->
```python
def ai_chase(grid, entity, target_x, target_y):
    """Move entity toward target using a Dijkstra map."""
    dijkstra = grid.get_dijkstra_map((target_x, target_y))

    # descent_step returns the single best neighbor toward the root,
    # or None if entity is already at a local minimum / off-grid
    step = dijkstra.descent_step(entity.grid_pos)

    if step is not None:
        entity.grid_pos = step
```
<!-- /snippet -->

### Flee Behavior

`DijkstraMap.invert()` returns a new map with the distance field flipped, so
descending it moves *away* from the original root:

<!-- snippet: 160_grid_dijkstra_2 region=flee -->
```python
def ai_flee(grid, entity, threat_x, threat_y):
    """Move entity away from threat using an inverted Dijkstra map."""
    toward_threat = grid.get_dijkstra_map((threat_x, threat_y))
    away_from_threat = toward_threat.invert()
    step = away_from_threat.descent_step(entity.grid_pos)
    if step is not None:
        entity.grid_pos = step
```
<!-- /snippet -->

---

## Multiple Goals

Pass several roots at once with the `roots` keyword — multi-source maps are
combined by the engine (each cell's distance is to its *nearest* root) and are
not cached, since the source set can change every call:

<!-- snippet: 372_grid_dijkstra_3 region=multi -->
```python
def get_distance_to_nearest(grid, positions, cell):
    """Distance from cell to the nearest of several source positions."""
    dijkstra = grid.get_dijkstra_map(roots=positions)
    return dijkstra.distance(cell)


# Usage: flee from the nearest of several threats
def ai_flee_group(grid, entity, threats):
    threat_positions = [t.grid_pos for t in threats]
    toward_threats = grid.get_dijkstra_map(roots=threat_positions)
    away_from_threats = toward_threats.invert()

    step = away_from_threats.descent_step(entity.grid_pos)
    if step is not None:
        entity.grid_pos = step
```
<!-- /snippet -->

For AI that weighs several competing goals (chase the player, avoid allies,
seek healing), compute one map per goal and combine their `distance()` values
yourself:

<!-- snippet: 372_grid_dijkstra_3 region=manager -->
```python
class DijkstraManager:
    """Cache several named Dijkstra maps for weighted AI decisions."""

    def __init__(self, grid):
        self.grid = grid
        self.maps = {}  # name -> DijkstraMap

    def set_goal(self, name, root_or_roots):
        """Compute (or fetch the cached) map for a named goal."""
        if isinstance(root_or_roots, list):
            self.maps[name] = self.grid.get_dijkstra_map(roots=root_or_roots)
        else:
            self.maps[name] = self.grid.get_dijkstra_map(root_or_roots)

    def get_distance(self, name, pos):
        """Get distance to a named goal, or None if not reachable/not set."""
        dmap = self.maps.get(name)
        if dmap is None:
            return None
        return dmap.distance(pos)

    def get_combined_value(self, pos, weights):
        """Get a weighted combination of multiple named maps."""
        value = 0.0
        for name, weight in weights.items():
            dist = self.get_distance(name, pos)
            if dist is not None:
                value += dist * weight
        return value


def ai_decision(grid, manager, enemy):
    """Make an AI decision based on multiple weighted factors."""
    # hp/max_hp are attributes YOU add on your Entity subclass;
    # mcrfpy.Entity has no built-in health property.
    if enemy.hp < enemy.max_hp * 0.3:
        # Low health - prioritize potions, avoid player
        weights = {
            'potions': -1.0,  # Move toward potions
            'player': 0.5,    # Move away from player
        }
    else:
        # Healthy - chase player
        weights = {
            'player': -1.0,   # Move toward player
        }

    ex, ey = enemy.grid_pos
    best_move = None
    best_value = float('inf')

    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        nx, ny = ex + dx, ey + dy

        if grid.at(nx, ny).walkable:
            value = manager.get_combined_value((nx, ny), weights)
            if value < best_value:
                best_value = value
                best_move = (nx, ny)

    if best_move:
        enemy.grid_pos = best_move
```
<!-- /snippet -->

---

## Movement Range Calculation

Use `DijkstraMap.distance()` for tactical movement:

<!-- snippet: 372_grid_dijkstra_3 region=range -->
```python
def get_reachable_cells(grid, start_x, start_y, max_cost):
    """Get all cells reachable within a movement budget."""
    dijkstra = grid.get_dijkstra_map((start_x, start_y))

    reachable = []
    for x in range(grid.grid_w):
        for y in range(grid.grid_h):
            dist = dijkstra.distance((x, y))
            if dist is not None and dist <= max_cost:
                reachable.append((x, y, dist))

    return reachable


def show_movement_range(grid, highlight_layer, entity, movement_points):
    """Highlight reachable cells with distance coloring."""
    ex, ey = entity.grid_pos
    reachable = get_reachable_cells(grid, ex, ey, movement_points)

    for x, y, dist in reachable:
        # Color intensity based on remaining movement
        remaining = movement_points - dist
        intensity = int(200 * remaining / movement_points)
        color = mcrfpy.Color(50, 50 + intensity, 255, 100)
        highlight_layer.set((x, y), color)
```
<!-- /snippet -->

`distance()` returns `None` for unreachable cells, so treat `None` the way the
old code treated `float('inf')`.

---

## Influence Mapping

Visualize tactical influence by summing several Dijkstra maps' inverse-distance
contributions:

<!-- snippet: 372_grid_dijkstra_3 region=influence -->
```python
def compute_influence_map(grid, player_team, enemy_team):
    """Show which team controls which areas."""
    influence = {}

    # Player team influence
    for ally in player_team:
        dijkstra = grid.get_dijkstra_map(ally.grid_pos)
        for x in range(grid.grid_w):
            for y in range(grid.grid_h):
                dist = dijkstra.distance((x, y))
                if dist is not None:
                    influence[(x, y)] = influence.get((x, y), 0.0) + 1.0 / (1.0 + dist)

    # Subtract enemy team influence
    for enemy in enemy_team:
        dijkstra = grid.get_dijkstra_map(enemy.grid_pos)
        for x in range(grid.grid_w):
            for y in range(grid.grid_h):
                dist = dijkstra.distance((x, y))
                if dist is not None:
                    influence[(x, y)] = influence.get((x, y), 0.0) - 1.0 / (1.0 + dist)

    return influence


def show_influence_map(influence_layer, influence):
    """Visualize influence values on a ColorLayer."""
    for (x, y), val in influence.items():
        if val > 0:
            # Player controlled - blue
            alpha = min(150, int(abs(val) * 50))
            influence_layer.set((x, y), mcrfpy.Color(50, 50, 200, alpha))
        elif val < 0:
            # Enemy controlled - red
            alpha = min(150, int(abs(val) * 50))
            influence_layer.set((x, y), mcrfpy.Color(200, 50, 50, alpha))
```
<!-- /snippet -->

---

## Movement Cost Parameters

`get_dijkstra_map` (and `find_path`) take a `diagonal_cost` argument (default
`1.41`) for the relative cost of diagonal moves, and a `collide` label string
so entities carrying that label block the path:

<!-- snippet: 372_grid_dijkstra_3 region=cost -->
```python
# Cheaper diagonal movement, and block on any entity labeled "blocker"
dijkstra = grid.get_dijkstra_map(player.grid_pos, diagonal_cost=1.0, collide="blocker")
```
<!-- /snippet -->

There is currently no per-cell weighted movement cost in the 2D grid API —
`GridPoint.walkable` is a binary flag. To model "slow" terrain (mud, water),
either keep it walkable and accept uniform cost, or make especially costly
terrain unwalkable and route around it. (Per-material path costs do exist for
the 3D voxel grid via `VoxelGrid.add_material(path_cost=...)`, but that is a
separate system from the 2D `Grid`/`GridData` used here.)

---

## Visibility-Aware Pathfinding

Only path through cells an entity has actually discovered. Per-entity
discovery state lives in `entity.perspective_map`, a `DiscreteMap` where
`0` = unknown, `1` = discovered, `2` = currently visible:

<!-- snippet: 372_grid_dijkstra_3 region=visibility -->
```python
def compute_safe_dijkstra(grid, player, goal_pos):
    """Compute a distance map that avoids cells the player hasn't discovered."""
    original_walkable = {}

    for x in range(grid.grid_w):
        for y in range(grid.grid_h):
            if player.perspective_map[x, y] == 0:  # unknown
                point = grid.at(x, y)
                original_walkable[(x, y)] = point.walkable
                point.walkable = False

    dijkstra = grid.get_dijkstra_map(goal_pos)  # built against the masked terrain

    for (x, y), walkable in original_walkable.items():
        grid.at(x, y).walkable = walkable
    # The map we hold is a snapshot, so it keeps the explored-only distances;
    # the next get_dijkstra_map() call sees the real walkability again.

    return dijkstra
```
<!-- /snippet -->

`entity.perspective_map` is only kept current by calling
`entity.updateVisibility()` after the entity moves or the map changes.

---

## Performance Tips

The grid already caches single-source maps by root position, so calling
`get_dijkstra_map(same_root)` repeatedly is cheap — the expensive part is the
first call for a root, and the first call after the map changes. So ask for the map
every turn rather than holding on to one: a held `DijkstraMap` is a snapshot and
won't see later edits.

On a big grid, pass `radius=` to bound the field to what your AI needs (default: the
whole grid, up to 511). Entities outside the field still get a greedy step from
`step_from()`, and `dijkstra.is_exact(pos)` tells you whether `distance(pos)` is exact
or the heuristic's estimate:

<!-- snippet: 372_grid_dijkstra_3 region=radius -->
```python
dijkstra = grid.get_dijkstra_map(player.grid_pos, radius=64)
for enemy in enemies:
    if not dijkstra.is_exact(enemy.grid_pos):
        continue  # far away: let it idle, or take the greedy step_from()
    step = dijkstra.step_from(enemy.grid_pos)
```
<!-- /snippet -->

The cache bounds its own memory: maps are capped at `grid.dijkstra_cache_budget`
bytes (default 256 MiB; each map costs 4 bytes per cell), least recently used
first, and `grid.dijkstra_cache_bytes` reports current use. On a very large grid
raise the budget if several roots should stay cached.

Multi-source maps (`roots=[...]`) are **not** cached, since the source set can
be different on every call — if you query the same multi-source map
repeatedly in a frame, compute it once and reuse the `DijkstraMap` object
rather than calling `get_dijkstra_map(roots=...)` again.

---

## Tips

1. **Caching**: single-root maps are cached automatically and are always
   current; request the map again after changing walkability.
2. **Multiple sources**: pass `roots=[...]` for one map whose distance is to
   the nearest of several sources, instead of computing and merging maps by hand.
3. **`step_from` vs `descent_step`**: `step_from` follows a precomputed path
   toward the root; `descent_step` looks only at immediate neighbors each call.
4. **Blocked paths**: `distance()` and `step_from()` return `None` for
   unreachable cells — check for `None`, not `float('inf')`. `path_from()`
   returns an `AStarPath` that is empty (0 steps remaining) when there is no
   route, and otherwise walks from the start cell toward the root.
5. **Direction**: distances decrease toward the root; descend the field to
   approach it, use `invert()` to flee it.

---

## Related Recipes

- [Fog of War](grid_fog_of_war.md) - Combine with visibility
- [Dungeon Generator](grid_dungeon_generator.md) - Generate maps to pathfind
- [Cell Highlighting](grid_cell_highlighting.md) - Visualize distances
