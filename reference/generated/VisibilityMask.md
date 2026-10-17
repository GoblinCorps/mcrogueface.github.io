---
title: VisibilityMask
layout: default
mcrf:
  objects:
    - VisibilityMask
  diataxis: reference
  source: generated
  verified: 0.3.3
  verified_commit: ""
---

# VisibilityMask {% include api_badge.html kind="added" version="0.2.8-dev" %} {% include api_badge.html kind="changed" version="0.2.8-dev" %}

{% raw %}An immutable, storable record of which cells were visible, from where, at which frame.

Created by GridData.observe(); cannot be instantiated directly. Use this for fog-of-war persistence, replaying an AI's past perception, or any case where 'what could this observer see' needs to be a value you can store, compare, and hand to other code -- rather than something you have to recompute from compute_fov()/is_in_fov() every time you need it.

Properties:
    origin (tuple | None, read-only): Observing cell, or None if unbounded
    fov_radius (int | None, read-only): Radius used, or None if unlimited
    tick (int, read-only): Engine current_frame when this mask was taken
    cells (frozenset, read-only): The visible (x, y) cells
    grid_size (tuple, read-only): (w, h) of the source grid
    light_walls (bool | None, read-only): Whether walls were lit when
                        visible, or None if no FOV computation ran
    algorithm (int | None, read-only): FOV algorithm used (mcrfpy.FOV.*),
                        or None if no FOV computation ran

An UNBOUNDED mask (origin=None) reports origin, fov_radius, light_walls and
algorithm all as None: every in-bounds cell is visible by construction, so
none of those parameters participated. A mask never reports a setting that
had no effect on it.

Equality: a value. mask == other compares origin, fov_radius, grid_size,
cells, and light_walls/algorithm when an FOV computation ran -- but NOT
tick, so the same view seen on two frames is equal; `is` tells the two
records apart. Hashable on the same fields, so masks dedupe in a set.
To compare only what was visible, compare a.cells == b.cells.

Protocol:
    (x, y) in mask   -- O(1) membership test; raises TypeError if the
                        key is not a position (an entity, a 3-tuple, ...),
                        rather than silently answering False
    len(mask)        -- number of visible cells
    iter(mask)       -- yields (x, y) in row-major order

Example:
    snap = grid_data.observe(origin=(5, 5), fov_radius=8)
    if (5, 6) in snap['mask']:
        ...
{% endraw %}

## Properties

| Property | Description |
| --- | --- |
| `algorithm` {% include api_badge.html kind="added" version="0.2.8-dev" %} {% include api_badge.html kind="changed" version="0.2.8-dev" %} | {% raw %}FOV algorithm used to compute this mask, matching one of the mcrfpy.FOV.* values, or None on an unbounded mask (origin=None), where no algorithm ran (int \| None, read-only).{% endraw %} |
| `cells` {% include api_badge.html kind="added" version="0.2.8-dev" %} | {% raw %}The materialised set of visible cells, as (x, y) pairs (frozenset, read-only).{% endraw %} |
| `fov_radius` {% include api_badge.html kind="added" version="0.2.8-dev" %} | {% raw %}Maximum view distance used to compute this mask, or None if the mask is unbounded or has an unlimited radius (int \| None, read-only).{% endraw %} |
| `grid_size` {% include api_badge.html kind="added" version="0.2.8-dev" %} | {% raw %}Dimensions of the grid this mask was taken from, as (w, h) (tuple, read-only).{% endraw %} |
| `light_walls` {% include api_badge.html kind="added" version="0.2.8-dev" %} {% include api_badge.html kind="changed" version="0.2.8-dev" %} | {% raw %}Whether walls were lit when visible in the FOV computation that produced this mask, or None on an unbounded mask (origin=None), where no FOV computation ran and the setting had no effect (bool \| None, read-only).{% endraw %} |
| `origin` {% include api_badge.html kind="added" version="0.2.8-dev" %} | {% raw %}The observing cell as (x, y), or None for an unbounded mask (tuple \| None, read-only).{% endraw %} |
| `tick` {% include api_badge.html kind="added" version="0.2.8-dev" %} | {% raw %}Engine current_frame at the moment this mask was taken (int, read-only).{% endraw %} |
