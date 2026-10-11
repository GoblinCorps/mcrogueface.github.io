---
layout: default
title: Animation
mcrf:
  objects: [Animation]
  diataxis: reference
  disposition: current
  verified: "0.3.0-dev"
  verified_commit: 7fff142
---

# Animation

Property interpolation over time, created with the `animate()` method.

## Overview

There is **no constructible `mcrfpy.Animation` class**. Animations are created by calling `animate()` on the object you want to animate: every drawable (`Frame`, `Caption`, `Sprite`, `Grid`, `Line`, `Circle`, `Arc`, `Viewport3D`) and `Entity` exposes it. The call creates the animation, starts it, and registers it with the engine's animation manager in one step, then returns an `Animation` handle you can use to monitor or cancel it.

The handle's type displays as `mcrfpy.Animation`, but the class is not exported from the module — the only way to obtain one is as the return value of `animate()`.

## Quick Reference

```python
import mcrfpy

scene = mcrfpy.Scene("demo")
mcrfpy.current_scene = scene

frame = mcrfpy.Frame(pos=(0, 0), size=(100, 100))
scene.children.append(frame)

# Animate a property: creates, starts, and registers the animation
frame.animate("x", 500.0, 2.0, mcrfpy.Easing.EASE_OUT_QUAD)

# With a completion callback
def on_done(target, prop, value):
    print(f"{prop} finished at {value}")

frame.animate("opacity", 0.0, 1.0, callback=on_done)

# The returned Animation handle can be inspected and controlled
anim = frame.animate("w", 300.0, 1.5)
print(anim.property, anim.duration, anim.is_complete)
anim.stop()  # cancel without applying the final value
```

## The animate() Method

```python
obj.animate(property, target, duration, easing=None, delta=False,
            loop=False, callback=None, conflict_mode='replace') -> Animation
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `property` | str | required | Name of the property to animate (see [Animatable Properties](#animatable-properties)) |
| `target` | varies | required | Target value; type depends on the property (see [Target Value Types](#target-value-types)) |
| `duration` | float | required | Animation duration in seconds |
| `easing` | Easing / str | None | `mcrfpy.Easing` enum value, legacy string name (e.g. `'easeInOut'`), or None for linear |
| `delta` | bool | False | If True, `target` is relative to the current value instead of absolute |
| `loop` | bool | False | If True, the animation repeats from the start when it reaches the end |
| `callback` | callable | None | Called once when the animation completes (never called for looping animations) |
| `conflict_mode` | str | 'replace' | `'replace'`, `'queue'`, or `'error'` — behavior when the property is already animating |

**Raises:**

- `ValueError` — the name is not an animatable attribute of this object, the easing string is unknown, `conflict_mode` is not one of the three accepted values, or a Color target is out of range.
- `TypeError` — the target is not of the property's type, or `callback` is not callable.
- `RuntimeError` — `conflict_mode='error'` and the property is already being animated, or an Entity's `x`/`y`/`pos` is animated while the entity is not on a grid.

`Entity.animate()` takes the same arguments; only its set of valid property names differs (see below).

### Callback Signature

The completion callback receives three arguments:

```python
import mcrfpy

scene = mcrfpy.Scene("demo")
mcrfpy.current_scene = scene

frame = mcrfpy.Frame(pos=(0, 0), size=(100, 100))
scene.children.append(frame)

def on_arrival(target, prop, value):
    # target: the Frame that was animated
    # prop:   "x"
    # value:  500.0
    print(f"{type(target).__name__}.{prop} reached {value}")

frame.animate("x", 500.0, 2.0, mcrfpy.Easing.EASE_OUT_CUBIC, callback=on_arrival)
```

The callback fires when the animation finishes naturally, or on the next frame after `complete()` is called on the handle. It does **not** fire when the animation is cancelled with `stop()`, and looping animations never fire it (they never complete).

### Conflict Handling

Each (object, property) pair can have only one active animation. `conflict_mode` controls what happens when you call `animate()` for a property that is already animating:

| Mode | Behavior |
|------|----------|
| `'replace'` (default) | The existing animation ends immediately (jumping to its final value) and the new one starts |
| `'queue'` | The new animation waits and starts when the current one finishes |
| `'error'` | Raises `RuntimeError` |

```python
import mcrfpy

scene = mcrfpy.Scene("demo")
mcrfpy.current_scene = scene

frame = mcrfpy.Frame(pos=(0, 0), size=(100, 100))
scene.children.append(frame)

frame.animate("x", 100.0, 1.0)

# replace (default): the running animation jumps to its final value,
# then the new animation starts
frame.animate("x", 200.0, 1.0)

# queue: run after the current animation on "x" finishes
frame.animate("x", 300.0, 1.0, conflict_mode="queue")

# error: raise RuntimeError if "x" is already animating
try:
    frame.animate("x", 400.0, 1.0, conflict_mode="error")
except RuntimeError as e:
    print(e)
```

Notes:

- When `animate()` is called from inside an animation callback, a replaced animation is cancelled in place rather than jumped to its final value.
- The per-property lock is released when the finished `Animation` object is destroyed, not at the moment it completes. If you hold a reference to a completed animation, a queued animation on the same property will not start until you drop that reference. When using `conflict_mode='queue'`, discard handles you don't need.
- Sub-properties are locked independently of their parent: `"fill_color"` and `"fill_color.a"` are separate keys and can animate simultaneously.

## The Animation Handle

`animate()` returns an `Animation` object. All of its data attributes are read-only.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `property` | str | Name of the property being animated |
| `duration` | float | Total duration in seconds |
| `elapsed` | float | Seconds since the animation started (clamped to `duration`) |
| `is_complete` | bool | True when `elapsed >= duration` or `complete()` was called |
| `is_delta` | bool | Whether the animation uses delta (relative) mode |
| `is_looping` | bool | Whether the animation repeats when it reaches the end |

### Methods

| Method | Description |
|--------|-------------|
| `complete()` | Jump to the final value immediately; the callback, if any, fires on the next frame |
| `stop()` | Cancel without applying the final value; the callback is NOT fired |
| `get_current_value()` | Current interpolated value (type matches the property) |
| `hasValidTarget()` | True if the animated object still exists; animations self-clean when their target is destroyed |
| `start(target, conflict_mode='replace')` | Attach and start on a target object (used internally by `animate()`; rarely needed) |
| `update(delta_time)` | Advance by `delta_time` seconds; returns True while running (called automatically by the engine) |

```python
import mcrfpy

scene = mcrfpy.Scene("demo")
mcrfpy.current_scene = scene

frame = mcrfpy.Frame(pos=(0, 0), size=(100, 100))
scene.children.append(frame)

anim = frame.animate("x", 500.0, 2.0)

print(anim.property)      # "x"
print(anim.duration)      # 2.0
print(anim.elapsed)       # seconds since start
print(anim.is_complete)   # False until finished (or complete() called)
print(anim.get_current_value())  # current interpolated value

anim.complete()   # jump to x=500 immediately; a callback would fire on the next frame
print(frame.x)    # 500.0
```

## Animatable Properties

**The rule (0.3.0):** every name `animate()` accepts is a readable attribute of the object, animated in that attribute's units and type, so animating ends exactly where assigning the same value would. `frame.animate("w", 300.0, 0.5)` finishes with `frame.w == 300.0`, just as `frame.w = 300.0` does. A name that isn't an animatable attribute raises `ValueError`; for names that `animate()` used to accept, the message names the replacement ([see below](#names-removed-in-030)).

### Every drawable

All drawables (Frame, Caption, Sprite, Grid, Line, Circle, Arc, Viewport3D) share these:

| Property | Value type | Description |
|----------|------------|-------------|
| `x`, `y` | float | Position in pixels |
| `pos` | Vector | Position in pixels |
| `rotation` | float | Rotation in degrees (not Viewport3D) |
| `origin` | Vector | Transform origin / rotation pivot (not Viewport3D) |
| `opacity` | float | 0.0 (transparent) to 1.0 (opaque) |
| `z_index` | int | Render order |

For Circle and Arc, the position is the **center**. For Line it is the **midpoint**: assigning or animating a Line's `pos`, `x` or `y` moves both endpoints.

### Frame

| Property | Value type | Description |
|----------|------------|-------------|
| `w`, `h` | float | Size |
| `size` | Vector | Size as a pair |
| `fill_color`, `outline_color` | Color | Colors (all channels interpolate) |
| `fill_color.r/.g/.b/.a`, `outline_color.r/.g/.b/.a` | float | Individual color channels |
| `outline` | float | Outline thickness |

Resizing a frame that clips or caches its children (`clip_children`, `cache_subtree`) resizes its texture too, whether you assign or animate the size.

### Caption

| Property | Value type | Description |
|----------|------------|-------------|
| `font_size` | float | Font size in points |
| `outline` | float | Text outline thickness |
| `fill_color`, `outline_color` | Color | Text colors, plus their `.r/.g/.b/.a` channels |
| `text` | str | Typewriter-style text transition (see [Typewriter Text](#typewriter-text)) |

A Caption's `w`, `h` and `size` are its read-only text bounds, so they are not animatable. Animate `font_size` to scale text.

### Sprite

| Property | Value type | Description |
|----------|------------|-------------|
| `sprite_index` | int or list[int] | Texture frame; a list plays a frame sequence |
| `scale` | float | Uniform scale factor |
| `scale_x`, `scale_y` | float | Per-axis scale |

### Grid

| Property | Value type | Description |
|----------|------------|-------------|
| `w`, `h` | float | Viewport size |
| `size` | Vector | Viewport size as a pair |
| `fill_color` | Color | Background color |
| `center` | Vector | Camera center in **pixels** |
| `center_x`, `center_y` | float | Camera center components (pixels) |
| `zoom` | float | Camera zoom level |
| `camera_rotation` | float | Camera rotation in degrees |

### Line, Circle, Arc

Each also has the shared properties above (`x`, `y`, `pos`, `rotation`, `origin`, `opacity`, `z_index`). Whole colors animate; per-channel sub-properties (e.g. `color.r`) are not available on these types.

| Type | Properties |
|------|------------|
| `Line` | `start`, `end` (Vector), `thickness`, `color` |
| `Circle` | `center` (Vector), `radius`, `outline`, `fill_color`, `outline_color` |
| `Arc` | `center` (Vector), `radius`, `start_angle`, `end_angle`, `thickness`, `color` |

### Viewport3D

`w`, `h` (float), `size` (Vector), `fov`, `fog_near`, `fog_far` (float), `bg_color`, `fog_color` (Color), plus the shared `x`, `y`, `pos`, `opacity` and `z_index`.

### Entity

| Property | Value type | Description |
|----------|------------|-------------|
| `draw_pos` | Vector | Drawn position in **tile** coordinates: the smooth-movement property |
| `x`, `y` | float | Position in **pixels** (`draw_pos` times the grid's cell size) |
| `pos` | Vector | Position in **pixels** |
| `opacity` | float | 0.0 to 1.0 |
| `sprite_index` | int or list[int] | Texture frame or frame sequence |
| `sprite_offset` | Vector | Pixel offset of the sprite within its cell (also `sprite_offset_x`, `sprite_offset_y`) |

`x`, `y` and `pos` exist only while the entity is on a grid, so animating them on an entity with no grid raises `RuntimeError` at `animate()` time; `draw_pos` works either way. Animation moves only the drawn position: the logical cell (`grid_pos` / `cell_pos`) is unchanged.

Shader uniforms (`"shader.<name>"`) on a drawable or entity with a shader are also animatable floats.

### Not animatable

These attributes are writable but deliberately not animatable:
- **Entity logical state:** `grid_pos`, `grid_x`, `grid_y` and the `cell_*` aliases, `tile_size`/`tile_width`/`tile_height`, `turn_order`, `sight_radius`, `default_behavior` and `move_speed`.
- **Layout margins:** `margin`, `horiz_margin`, `vert_margin`.
- **Viewport3D:** `cell_size`.

`Entity3D` still uses its own animate names (`world_x`, `rot_y`, ...); see issue #449.

### Names removed in 0.3.0

Each of these raises `ValueError` naming its replacement:

| Old name | Use instead |
|----------|-------------|
| Entity `draw_x`, `draw_y` | `draw_pos` (tiles), or `x`/`y` (pixels) |
| Entity `x`, `y` *in tile units* | `draw_pos`. `x`/`y` still exist, but they are now pixels, as when you read them |
| Entity `sprite_scale` | none: it never had an effect, because the grid's zoom sets the sprite scale |
| `position` | `pos` |
| `origin_x`, `origin_y` | `origin` |
| Line `start_x`, `start_y`, `end_x`, `end_y` | `start`, `end` |
| Caption `size` | `font_size` |

## Target Value Types

A target is converted the way assigning that attribute converts it:

| Property type | Accepted targets |
|---------------|------------------|
| float | an int or a float |
| int | an int; or a list of ints to step through (sprite frames; combine with `loop=True`) |
| Vector | a `Vector`, an `(x, y)` tuple, or a list |
| Color | a `Color`, or an `(r, g, b)` / `(r, g, b, a)` tuple, checked as strictly as `Color()`: components must be ints in 0-255 |
| str | a `str` (Caption `text`) |

A target of the wrong type raises `TypeError` naming the property. The completion callback's `value` is a float or int, an `(x, y)` tuple for a Vector, or an `(r, g, b, a)` tuple for a Color.

## Easing

Pass a `mcrfpy.Easing` enum value (preferred) or a legacy string name (`'linear'`, `'easeIn'`, `'easeOut'`, `'easeInOut'`, `'easeInQuad'`, `'easeOutBounce'`, ...). `None` means linear. Unknown string names raise `ValueError`. See [Easing](Easing) for the full list of enum values and guidance on choosing one.

## Examples

### Chained Animations

Each callback starts the next leg of the sequence:

```python
import mcrfpy

scene = mcrfpy.Scene("demo")
mcrfpy.current_scene = scene

frame = mcrfpy.Frame(pos=(0, 0), size=(50, 50))
scene.children.append(frame)

def step2(target, prop, value):
    target.animate("y", 100.0, 0.3, callback=step3)

def step3(target, prop, value):
    target.animate("x", 0.0, 0.3, callback=step4)

def step4(target, prop, value):
    target.animate("y", 0.0, 0.3)

# Trace a rectangle: each callback starts the next leg
frame.animate("x", 100.0, 0.3, callback=step2)
```

### Looping Sprite Frames

A list target with `loop=True` cycles through frames indefinitely:

```python
import mcrfpy

scene = mcrfpy.Scene("demo")
mcrfpy.current_scene = scene

texture = mcrfpy.Texture("assets/kenney_tinydungeon.png", 16, 16)
sprite = mcrfpy.Sprite(texture=texture, sprite_index=84, pos=(100, 100))
scene.children.append(sprite)

# Cycle through frames 84-87 forever (0.6 seconds per cycle)
walk = sprite.animate("sprite_index", [84, 85, 86, 87], 0.6, loop=True)

# Later, to stop the loop:
walk.stop()
```

### Camera Pan and Zoom

```python
import mcrfpy

scene = mcrfpy.Scene("demo")
mcrfpy.current_scene = scene

texture = mcrfpy.Texture("assets/kenney_tinydungeon.png", 16, 16)
grid = mcrfpy.Grid(grid_size=(30, 20), pos=(0, 0), size=(480, 320), texture=texture)
scene.children.append(grid)

# grid.center is in PIXELS. To pan to tile (14, 8) with 16x16 tiles,
# target the middle of that tile:
tile_x, tile_y = 14, 8
target = (tile_x * 16 + 8, tile_y * 16 + 8)

grid.animate("center", target, 0.4, mcrfpy.Easing.EASE_OUT_CUBIC)
grid.animate("zoom", 2.0, 0.4, mcrfpy.Easing.EASE_IN_OUT)
```

For an instant (non-animated) camera move in tile coordinates, use `grid.center_camera((tx, ty))` instead.

### Smooth Entity Movement

```python
import mcrfpy

scene = mcrfpy.Scene("demo")
mcrfpy.current_scene = scene

texture = mcrfpy.Texture("assets/kenney_tinydungeon.png", 16, 16)
grid = mcrfpy.Grid(grid_size=(10, 10), pos=(0, 0), size=(160, 160), texture=texture)
scene.children.append(grid)

player = mcrfpy.Entity(grid_pos=(1, 1), texture=texture, sprite_index=84)
grid.entities.append(player)

# Slide the drawn position across the grid in tile coordinates.
# cell_pos (the logical cell) is NOT changed by this animation.
player.animate("draw_pos", (5, 1), 0.5, mcrfpy.Easing.EASE_OUT_QUAD)
```

Note: entities moved by the turn manager (`grid.step()` with behaviors) animate their draw position automatically over `entity.move_speed` seconds; animating `draw_pos` yourself is for movement outside the turn system.

### Colors and Delta Mode

```python
import mcrfpy

scene = mcrfpy.Scene("demo")
mcrfpy.current_scene = scene

frame = mcrfpy.Frame(pos=(100, 100), size=(200, 80))
scene.children.append(frame)

# Animate a whole color (interpolates R, G, B, and A together)
frame.animate("fill_color", (255, 0, 0, 255), 1.0)

# Animate a single channel
frame.animate("fill_color.a", 0.0, 0.5)

# Delta mode: move 50 pixels down from wherever the frame is now
frame.animate("y", 50.0, 0.5, delta=True)
```

### Typewriter Text

Animating `text` transitions between strings: the first half of the duration deletes the current text character by character, the second half types out the target. With `delta=True`, the target is appended character by character instead.

```python
import mcrfpy

scene = mcrfpy.Scene("demo")
mcrfpy.current_scene = scene

caption = mcrfpy.Caption(text="", pos=(20, 20))
scene.children.append(caption)

# Typewriter effect: reveals the target string over 2 seconds
caption.animate("text", "You awaken in a dark cell.", 2.0)
```

## Related

<div class="related-objects">
<div class="object-links">
<a href="Easing" class="object-link">Easing</a>
<a href="Timer" class="object-link">Timer</a>
<a href="Drawable" class="object-link">Drawable</a>
<a href="Frame" class="object-link">Frame</a>
<a href="Sprite" class="object-link">Sprite</a>
<a href="Caption" class="object-link">Caption</a>
<a href="Grid" class="object-link">Grid</a>
<a href="Entity" class="object-link">Entity</a>
</div>
</div>
