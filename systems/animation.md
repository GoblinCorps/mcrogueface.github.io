---
layout: default
title: Animation System
mcrf:
  objects: [Animation, Easing, Timer, Caption]
  diataxis: reference
  disposition: current
  verified: "0.3.0-dev"
  verified_commit: 7fff142
---

# Animation System

The Animation System provides smooth property transitions for UI elements and entities. Animate position, size, color, and other properties with configurable easing functions and completion callbacks.

## Overview

Animations in McRogueFace work by interpolating a property from its current value to a target value over a duration. The `.animate()` method is available on every drawable and on `Entity`.

```python
# Move a sprite from its current position to (200, 100) over 0.5 seconds
sprite.animate("pos", (200, 100), 0.5, mcrfpy.Easing.EASE_OUT_QUAD)
```

**The rule:** every name `animate()` accepts is a readable attribute, animated in that attribute's units and type, so an animation ends exactly where assigning the same value would.

## Objects

| Object | Purpose |
|--------|---------|
| [Animation](../objects/Animation) | Property interpolation with easing |

---

## The animate() Method {#animate-method}

All drawables and entities have an `.animate()` method.

### Signature

```python
element.animate(property, target, duration, easing=None, delta=False,
                loop=False, callback=None, conflict_mode='replace')
```

- `property`: name of the attribute to animate (`"x"`, `"pos"`, `"opacity"`, `"fill_color"`, ...)
- `target`: the end value, of the attribute's type: a number, a `Vector` or `(x, y)`, a `Color` or `(r, g, b[, a])`, an int (or a list of ints to step through), or a string
- `duration`: animation duration in seconds (required)
- `easing`: an `mcrfpy.Easing` value, a legacy string name, or `None` for linear
- `callback`: called when the animation completes, receiving `(target, property, final_value)`

`.animate()` returns an `Animation` handle representing the running animation. A name that isn't an animatable attribute raises `ValueError`; a target of the wrong type raises `TypeError`.

### Animatable Properties

**Every drawable:** `x`, `y`, `pos` (pixels), `rotation`, `origin`, `opacity`, `z_index`.

**By type:** `w`, `h`, `size` (Frame, Grid, Viewport3D); colors such as `fill_color` and `outline_color`, and `fill_color.r`-style channels on Frame and Caption; `font_size` and `text` (Caption); `scale` and `sprite_index` (Sprite); `center`, `zoom` and `camera_rotation` (Grid).

**Entity:** `draw_pos` (tiles: the smooth-movement property), `x`, `y`, `pos` (pixels), `opacity`, `sprite_index`, `sprite_offset`.

See [Animation](../objects/Animation#animatable-properties) for the full per-type tables and the names removed in 0.3.0 (`draw_x`/`draw_y`, `position`, `origin_x`, ...).

---

## Easing Functions {#easing}

Easing functions control the rate of change during animation.

### Linear
```python
element.animate("x", 100, 1.0, mcrfpy.Easing.LINEAR)
```
Constant speed from start to finish.

### Ease In (Accelerating)
```python
element.animate("x", 100, 1.0, mcrfpy.Easing.EASE_IN_QUAD)    # Quadratic
element.animate("x", 100, 1.0, mcrfpy.Easing.EASE_IN_CUBIC)   # Cubic
element.animate("x", 100, 1.0, mcrfpy.Easing.EASE_IN_EXPO)    # Exponential
```
Starts slow, accelerates toward the end.

### Ease Out (Decelerating)
```python
element.animate("x", 100, 1.0, mcrfpy.Easing.EASE_OUT_QUAD)   # Quadratic
element.animate("x", 100, 1.0, mcrfpy.Easing.EASE_OUT_CUBIC)  # Cubic
element.animate("x", 100, 1.0, mcrfpy.Easing.EASE_OUT_EXPO)   # Exponential
element.animate("x", 100, 1.0, mcrfpy.Easing.EASE_OUT_BOUNCE) # Bounce effect
```
Starts fast, decelerates toward the end.

### Ease In-Out (Smooth)
```python
element.animate("x", 100, 1.0, mcrfpy.Easing.EASE_IN_OUT_QUAD)
element.animate("x", 100, 1.0, mcrfpy.Easing.EASE_IN_OUT_CUBIC)
```
Smooth acceleration and deceleration.

The `mcrfpy.Easing` enum (e.g. `mcrfpy.Easing.EASE_OUT_QUAD`) is the preferred
spelling for easing values. Legacy string names like `"easeOutQuad"` are still
accepted for backward compatibility (see `src/PyEasing.cpp`). Starting a new animation
of a property that is already animating replaces the running one, unless you pass
`conflict_mode='queue'` or `'error'`.

---

## Completion Callbacks {#callbacks}

Execute code when an animation finishes using the `callback` parameter.

### Basic Callback

```python
def on_complete(target, prop, value):
    print(f"{prop} reached {value}")

sprite.animate("x", 200, 1.0, callback=on_complete)
```

### Chained Animations

Chain animations by starting the next in a callback:

```python
def move_right(target, prop, value):
    sprite.animate("x", 200, 0.5, callback=move_down)

def move_down(target, prop, value):
    sprite.animate("y", 200, 0.5, callback=move_left)

def move_left(target, prop, value):
    sprite.animate("x", 0, 0.5, callback=move_up)

def move_up(target, prop, value):
    sprite.animate("y", 0, 0.5, callback=move_right)

sprite.animate("x", 200, 0.5, callback=move_down)  # Start infinite square movement
```

### State Changes

Use callbacks to change game state after animations:

```python
def on_death_animation_complete(target, prop, value):
    grid.entities.remove(enemy)
    check_victory_condition()

enemy.animate("opacity", 0.0, 0.3, callback=on_death_animation_complete)
```

---

## Animation Patterns {#patterns}

### Smooth Entity Movement

```python
def move_entity(entity, target_x, target_y, duration=0.2):
    # draw_pos is the drawn position in tiles; grid_pos is the logical cell
    entity.grid_pos = (target_x, target_y)
    entity.animate("draw_pos", (target_x, target_y), duration, mcrfpy.Easing.EASE_OUT_QUAD)

# Player moves one tile right, smoothly instead of snapping
move_entity(player, player.grid_x + 1, player.grid_y)
```

### Damage Flash

```python
def flash_damage(entity):
    entity.animate("opacity", 0.3, 0.05,
                    callback=lambda t, p, v: entity.animate("opacity", 1.0, 0.1))
```

### Screen Shake

```python
import random

def screen_shake(grid, intensity=5, duration=0.3):
    original_x, original_y = grid.x, grid.y
    shake_count = [0]

    def shake(timer, runtime):
        shake_count[0] += 1
        if shake_count[0] > duration * 20:
            grid.x, grid.y = original_x, original_y
            timer.stop()
            return

        grid.x = original_x + random.randint(-intensity, intensity)
        grid.y = original_y + random.randint(-intensity, intensity)

    t = mcrfpy.Timer("shake", shake, 50)
```

### Floating Text

```python
def floating_text(scene, text, x, y):
    caption = mcrfpy.Caption(pos=(x, y), text=text)
    caption.fill_color = mcrfpy.Color(255, 255, 0)
    scene.children.append(caption)

    def remove(target, prop, value):
        scene.children.remove(caption)

    caption.animate("y", y - 30, 0.5, mcrfpy.Easing.EASE_OUT_QUAD)
    caption.animate("opacity", 0.0, 0.5, callback=remove)
```

---

## Related Objects

<div class="related-objects">
<div class="object-links">
<a href="../objects/Animation" class="object-link">Animation</a>
<a href="../objects/Timer" class="object-link">Timer</a>
<a href="../objects/Entity" class="object-link">Entity</a>
<a href="../objects/Sprite" class="object-link">Sprite</a>
</div>
</div>
