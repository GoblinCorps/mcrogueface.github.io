---
mcrf:
  objects: [Entity, Grid, Timer, Easing, Scene]
  diataxis: howto
  disposition: current
  verified: "0.3.0-dev"
  verified_commit: 7fff142
---

# Animated Movement

Smooth entity movement using the Animation system.

## Overview

McRogueFace has no `mcrfpy.Animation` class to construct directly. Instead every
`Drawable`/`Entity` exposes an `.animate(property, target, duration, easing=None, ...)`
method that creates and starts the animation in one call. This recipe covers using
`.animate()` for fluid movement instead of instant teleportation.

Animate an entity's **`draw_pos`**: its drawn position in fractional tile
coordinates, a Vector. One call moves both axes, so a target is just the destination
cell, `(new_x, new_y)`. The entity's `x`, `y` and `pos` are **pixels**, like every
drawable's, and animate in pixels too.

The drawn position and the logical cell (`grid_pos`) are separate: animating `draw_pos`
moves the sprite, and assigning `grid_pos` moves the entity for collision and
pathfinding. A move sets both.

> **0.3.0:** before 0.3.0, `animate("x", ...)` on an entity took **tile** units, and
> `"draw_x"`/`"draw_y"` were accepted. Now `"x"`/`"y"` are pixels, and `"draw_x"`/`"draw_y"`
> raise `ValueError` pointing at `"draw_pos"`.

## Basic Animated Move

```python
import mcrfpy

def move_with_animation(entity, new_x, new_y, duration=0.2):
    """Move entity smoothly to new position."""
    entity.grid_pos = (new_x, new_y)   # logical cell, immediately
    entity.animate("draw_pos", (new_x, new_y), duration, mcrfpy.Easing.EASE_IN_OUT)
```

## Animation with Callback

Know when movement completes for turn-based games. Completion callbacks receive
`(target, property, final_value)`:

```python
import mcrfpy

# Track animation state
is_animating = False

def move_with_callback(entity, new_x, new_y, duration=0.2, on_complete=None):
    """Move entity with completion callback."""
    global is_animating
    is_animating = True

    def animation_done(target, prop, value):
        global is_animating
        is_animating = False
        if on_complete:
            on_complete()

    entity.grid_pos = (new_x, new_y)
    entity.animate("draw_pos", (new_x, new_y), duration, mcrfpy.Easing.EASE_IN_OUT,
                   callback=animation_done)


# Usage in turn-based game
def player_move(direction):
    if is_animating:
        return  # Block input during animation

    dx, dy = direction
    new_x = player.grid_x + dx
    new_y = player.grid_y + dy

    def on_move_complete():
        end_player_turn()

    move_with_callback(player, new_x, new_y, on_complete=on_move_complete)
```

## Available Easing Functions

`easing` accepts an `mcrfpy.Easing` enum value (or its string name). Common choices:

```python
# Easing options (mcrfpy.Easing enum):
# LINEAR       - Constant speed
# EASE_IN      - Slow start, fast end
# EASE_OUT     - Fast start, slow end
# EASE_IN_OUT  - Slow start and end (smooth)
# (also: *_QUAD, *_CUBIC, *_SINE, *_ELASTIC, *_BOUNCE, *_BACK, *_EXPO variants)

# Examples of each (target is a cell, in tiles)
def demo_easings(entity, target):
    # Linear - mechanical, robotic movement
    entity.animate("draw_pos", target, 0.5, mcrfpy.Easing.LINEAR)

    # EaseIn - accelerating (good for falling)
    entity.animate("draw_pos", target, 0.5, mcrfpy.Easing.EASE_IN)

    # EaseOut - decelerating (good for stopping)
    entity.animate("draw_pos", target, 0.5, mcrfpy.Easing.EASE_OUT)

    # EaseInOut - natural movement (best for walking)
    entity.animate("draw_pos", target, 0.5, mcrfpy.Easing.EASE_IN_OUT)
```

## Camera Follow Animation

Animate the grid camera to follow the player. `Grid` also has `.animate()`, and its
`center` (a Vector; also `center_x`/`center_y`) is in pixel-space camera coordinates:

```python
def animate_camera_follow(grid, target_x, target_y, duration=0.2):
    """Smoothly pan camera to follow entity."""
    # Grid center is in pixel coordinates (tile_size = 16)
    center_x = (target_x + 0.5) * 16
    center_y = (target_y + 0.5) * 16

    grid.animate("center", (center_x, center_y), duration, mcrfpy.Easing.LINEAR)


def move_player_with_camera(player, grid, new_x, new_y, duration=0.2):
    """Move player and camera together."""

    def on_complete(target, prop, value):
        # Ensure camera is exactly centered after animation
        grid.center = ((new_x + 0.5) * 16, (new_y + 0.5) * 16)

    # Animate player
    player.grid_pos = (new_x, new_y)
    player.animate("draw_pos", (new_x, new_y), duration, mcrfpy.Easing.EASE_IN_OUT,
                   callback=on_complete)

    # Animate camera
    animate_camera_follow(grid, new_x, new_y, duration)
```

## Path Animation

Animate movement along a path from `entity.path_to()` (returns a plain list of
`(x, y)` tuples):

```python
class PathAnimator:
    """Animate entity movement along a path."""

    def __init__(self, entity, path, step_duration=0.2, on_complete=None):
        self.entity = entity
        self.path = list(path)  # Copy the path
        self.step_duration = step_duration
        self.on_complete = on_complete
        self.current_step = 0
        self.animating = False

    def start(self):
        """Begin path animation."""
        if not self.path or self.animating:
            return

        self.animating = True
        self.current_step = 0
        self._animate_next_step()

    def _animate_next_step(self):
        """Animate to next path position."""
        if self.current_step >= len(self.path):
            # Path complete
            self.animating = False
            if self.on_complete:
                self.on_complete()
            return

        target_x, target_y = self.path[self.current_step]

        # Update the logical cell immediately; draw_pos animates separately
        self.entity.grid_pos = (target_x, target_y)

        # Create step animation
        self.entity.animate("draw_pos", (target_x, target_y), self.step_duration,
                            mcrfpy.Easing.EASE_IN_OUT)

        # Schedule next step
        self.current_step += 1
        delay_ms = int(self.step_duration * 1000) + 20  # Small buffer

        def continue_path(timer, runtime):
            if self.animating:  # Check if still active
                self._animate_next_step()

        mcrfpy.Timer(f"path_{id(self)}", continue_path, delay_ms)

    def stop(self):
        """Stop path animation."""
        self.animating = False  # Timer callbacks will check this flag


# Usage
def move_enemy_along_path(enemy, player, grid):
    path = enemy.path_to(player.grid_x, player.grid_y)

    if not path:
        return

    # Only move a few steps per turn
    path = path[:3]

    def on_path_complete():
        end_enemy_turn()

    animator = PathAnimator(enemy, path, step_duration=0.15, on_complete=on_path_complete)
    animator.start()
```

## Movement Queue

Handle rapid input by queuing moves:

```python
class MovementController:
    """Handles queued movement with animations."""

    def __init__(self, entity, grid, move_duration=0.2):
        self.entity = entity
        self.grid = grid
        self.move_duration = move_duration
        self.is_moving = False
        self.move_queue = []
        self.max_queue = 2

    def queue_move(self, dx, dy):
        """Add a move to the queue."""
        if len(self.move_queue) < self.max_queue:
            self.move_queue.append((dx, dy))

        if not self.is_moving:
            self._process_queue()

    def _process_queue(self):
        """Process the next queued move."""
        if not self.move_queue:
            self.is_moving = False
            return

        dx, dy = self.move_queue.pop(0)
        current_x = self.entity.grid_x
        current_y = self.entity.grid_y
        new_x = current_x + dx
        new_y = current_y + dy

        # Validate move
        if not self._is_valid_move(new_x, new_y):
            self._process_queue()  # Try next queued move
            return

        self.is_moving = True
        self._animate_move(new_x, new_y)

    def _is_valid_move(self, x, y):
        """Check if move is valid."""
        grid_w, grid_h = self.grid.grid_size
        if x < 0 or x >= grid_w or y < 0 or y >= grid_h:
            return False
        return self.grid.at(x, y).walkable

    def _animate_move(self, new_x, new_y):
        """Perform the animated move."""

        def on_complete(target, prop, value):
            self.entity.grid_pos = (new_x, new_y)
            self._process_queue()

        self.entity.animate("draw_pos", (new_x, new_y), self.move_duration,
                            mcrfpy.Easing.EASE_IN_OUT, callback=on_complete)

        # Also animate camera
        center_x = (new_x + 0.5) * 16
        center_y = (new_y + 0.5) * 16

        self.grid.animate("center", (center_x, center_y), self.move_duration, mcrfpy.Easing.LINEAR)


# Usage (assumes scene, player, game_grid already defined)
controller = MovementController(player, game_grid, move_duration=0.15)

def handle_input(key, action):
    if action != mcrfpy.InputState.PRESSED:
        return

    if key in (mcrfpy.Key.W, mcrfpy.Key.UP):
        controller.queue_move(0, -1)
    elif key in (mcrfpy.Key.S, mcrfpy.Key.DOWN):
        controller.queue_move(0, 1)
    elif key in (mcrfpy.Key.A, mcrfpy.Key.LEFT):
        controller.queue_move(-1, 0)
    elif key in (mcrfpy.Key.D, mcrfpy.Key.RIGHT):
        controller.queue_move(1, 0)

scene.on_key = handle_input
```

## Bounce Effect

Add a bounce when hitting walls:

```python
def move_or_bump(entity, new_x, new_y, grid, duration=0.2):
    """Move to position, or bump animation if blocked."""

    if grid.at(new_x, new_y).walkable:
        # Normal move
        entity.grid_pos = (new_x, new_y)
        entity.animate("draw_pos", (new_x, new_y), duration, mcrfpy.Easing.EASE_IN_OUT)
    else:
        # Bump animation - move partway then back
        current_x = entity.draw_pos.x
        current_y = entity.draw_pos.y

        # Calculate bump position (1/4 of the way)
        bump_x = current_x + (new_x - current_x) * 0.25
        bump_y = current_y + (new_y - current_y) * 0.25

        def bump_back(target, prop, value):
            # Return to original position
            target.animate("draw_pos", (current_x, current_y), duration * 0.5,
                           mcrfpy.Easing.EASE_OUT)

        # Bump forward
        entity.animate("draw_pos", (bump_x, bump_y), duration * 0.5, mcrfpy.Easing.EASE_OUT,
                       callback=bump_back)
```

## Attack Lunge

Quick lunge toward target then return:

```python
def attack_lunge(attacker, target, duration=0.15):
    """Lunge toward target for attack animation."""
    start_x = attacker.draw_pos.x
    start_y = attacker.draw_pos.y

    # Calculate lunge position (halfway to target)
    lunge_x = start_x + (target.draw_pos.x - start_x) * 0.5
    lunge_y = start_y + (target.draw_pos.y - start_y) * 0.5

    def return_to_start(anim_target, prop, value):
        # Return to starting position
        anim_target.animate("draw_pos", (start_x, start_y), duration, mcrfpy.Easing.EASE_OUT)

    # Lunge forward
    attacker.animate("draw_pos", (lunge_x, lunge_y), duration, mcrfpy.Easing.EASE_IN,
                     callback=return_to_start)
```

## Tips

1. **Duration Tuning**: 0.15-0.25 seconds feels responsive. Slower for larger movements.

2. **One Animation per Move**: `draw_pos` animates both axes together, so one call (and
   one callback) covers a move in any direction, diagonals included.

3. **Input Blocking**: Always check `is_animating` before accepting new input in turn-based games.

4. **Camera Smoothness**: Use `mcrfpy.Easing.LINEAR` for camera, `EASE_IN_OUT` for entities - prevents jarring camera.

5. **Animation References**: `.animate()` returns an `Animation` object; keep a reference if you need to inspect or cancel it:
   ```python
   current_anim = entity.animate("draw_pos", (5, 3), 0.5, mcrfpy.Easing.LINEAR)
   current_anim.is_complete   # False while running
   current_anim.stop()        # cancel where it is (no final value, no callback)
   ```
   Starting a new animation of the same property replaces the running one by default
   (`conflict_mode='replace'`; `'queue'` waits for it, `'error'` raises).

## See Also

- [Turn System](combat_turn_system.md) - Coordinating animations with turns
- [Enemy AI](combat_enemy_ai.md) - Animating AI movement
- [Melee Combat](combat_melee.md) - Attack animations
