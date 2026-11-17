---
mcrf:
  objects: [Frame, Grid, Timer]
  diataxis: howto
  disposition: current
  verified: "0.2.8-dev"
  verified_commit: 3a85dd8
---

# Screen Shake Effect

Create a brief screen shake on impact for powerful hits, explosions, or dramatic moments.

## Quick Example

<!-- snippet: 147_effects_screen_shake_1 -->
```python
import mcrfpy

scene = mcrfpy.Scene("demo")
mcrfpy.current_scene = scene

def screen_shake(frame, intensity=5, duration=0.2):
    """
    Shake a frame/container by animating its position.

    Args:
        frame: The UI Frame to shake (often a container for all game elements)
        intensity: Maximum pixel offset
        duration: Total shake duration in seconds
    """
    original_x = frame.x
    original_y = frame.y

    # Quick shake to offset position
    frame.animate("x", float(original_x + intensity), duration / 4, mcrfpy.Easing.EASE_OUT)

    # Schedule return to center
    def return_to_center(timer, runtime):
        frame.animate("x", float(original_x), duration / 2, mcrfpy.Easing.EASE_IN_OUT)

    mcrfpy.Timer("shake_return", return_to_center, int(duration * 250), once=True)

# Usage - wrap your game content in a Frame
game_container = mcrfpy.Frame(pos=(0, 0), size=(1024, 768))
scene.children.append(game_container)
# ... add game elements to game_container.children ...
screen_shake(game_container, intensity=8, duration=0.3)
```
<!-- /snippet -->

## Multi-Directional Shake

A more realistic shake that moves in multiple directions:

<!-- snippet: 148_effects_screen_shake_2 -->
```python
import mcrfpy
import random

scene = mcrfpy.Scene("demo")
mcrfpy.current_scene = scene

game_container = mcrfpy.Frame(pos=(0, 0), size=(1024, 768))
scene.children.append(game_container)

def screen_shake_multi(frame, intensity=5, duration=0.3, shakes=4):
    """
    Shake frame in multiple random directions.

    Args:
        frame: The UI Frame to shake
        intensity: Maximum pixel offset
        duration: Total shake duration
        shakes: Number of shake movements
    """
    original_x = frame.x
    original_y = frame.y
    shake_interval = duration / shakes

    for i in range(shakes):
        # Decreasing intensity over time
        current_intensity = intensity * (1 - i / shakes)

        # Random offset direction
        offset_x = random.uniform(-current_intensity, current_intensity)
        offset_y = random.uniform(-current_intensity, current_intensity)

        def do_shake(timer, runtime, ox=offset_x, oy=offset_y, si=shake_interval):
            frame.animate("x", float(original_x + ox), si * 0.8, mcrfpy.Easing.EASE_OUT)
            frame.animate("y", float(original_y + oy), si * 0.8, mcrfpy.Easing.EASE_OUT)

        mcrfpy.Timer(f"shake_{i}", do_shake, max(1, int(i * shake_interval * 1000)), once=True)

    # Return to original position
    def reset(timer, runtime):
        frame.animate("x", float(original_x), shake_interval, mcrfpy.Easing.EASE_OUT)
        frame.animate("y", float(original_y), shake_interval, mcrfpy.Easing.EASE_OUT)

    mcrfpy.Timer("shake_reset", reset, int(duration * 1000), once=True)

# Usage
screen_shake_multi(game_container, intensity=10, duration=0.4, shakes=6)
```
<!-- /snippet -->

## Grid Camera Shake

Shake by animating the grid's center point instead of frame position:

<!-- snippet: 149_effects_screen_shake_3 -->
```python
import mcrfpy
import random

scene = mcrfpy.Scene("demo")
mcrfpy.current_scene = scene

grid = mcrfpy.Grid(
    grid_size=(16, 12),
    texture=mcrfpy.default_texture,
    pos=(0, 0),
    size=(1024, 768),
    zoom=4.0
)
scene.children.append(grid)

def camera_shake(grid, intensity=8, duration=0.3, shakes=4):
    """
    Shake the camera by animating grid.center.

    Args:
        grid: The Grid object
        intensity: Shake intensity in pixels
        duration: Total duration
        shakes: Number of shake movements
    """
    original_center_x = grid.center[0]
    original_center_y = grid.center[1]
    shake_interval = duration / shakes

    for i in range(shakes):
        decay = 1 - (i / shakes)  # Decreasing intensity
        offset_x = random.uniform(-intensity, intensity) * decay
        offset_y = random.uniform(-intensity, intensity) * decay

        def do_shake(timer, runtime, ox=offset_x, oy=offset_y, si=shake_interval,
                     cx=original_center_x, cy=original_center_y):
            grid.animate("center_x", cx + ox, si * 0.8, mcrfpy.Easing.EASE_OUT)
            grid.animate("center_y", cy + oy, si * 0.8, mcrfpy.Easing.EASE_OUT)

        mcrfpy.Timer(f"cam_shake_{i}", do_shake, max(1, int(i * shake_interval * 1000)), once=True)

    # Return to original
    def reset(timer, runtime):
        grid.animate("center_x", float(original_center_x), shake_interval, mcrfpy.Easing.EASE_OUT)
        grid.animate("center_y", float(original_center_y), shake_interval, mcrfpy.Easing.EASE_OUT)

    mcrfpy.Timer("cam_reset", reset, int(duration * 1000), once=True)

# Usage
camera_shake(grid, intensity=12, duration=0.25)
```
<!-- /snippet -->

## ScreenShake Manager

A complete shake system with presets and state management:

<!-- snippet: 283_effects_screen_shake_manager region=manager -->
```python
import mcrfpy
import random

class ScreenShakeManager:
    """Manages screen shake effects with presets and queuing."""

    def __init__(self, target, mode="frame"):
        """
        Args:
            target: Frame or Grid to shake
            mode: "frame" for Frame.x/y, "camera" for Grid.center
        """
        self.target = target
        self.mode = mode
        self.is_shaking = False
        self.shake_id = 0

        # Store original position
        if mode == "frame":
            self.original_x = target.x
            self.original_y = target.y
        else:
            self.original_x = target.center[0]
            self.original_y = target.center[1]

    def _get_position(self):
        if self.mode == "frame":
            return self.target.x, self.target.y
        else:
            return self.target.center

    def _animate_position(self, x, y, duration, easing=None):
        easing = easing or mcrfpy.Easing.EASE_OUT
        if self.mode == "frame":
            self.target.animate("x", float(x), duration, easing)
            self.target.animate("y", float(y), duration, easing)
        else:
            self.target.animate("center_x", float(x), duration, easing)
            self.target.animate("center_y", float(y), duration, easing)

    def shake(self, intensity=5, duration=0.3, shakes=4, decay=True):
        """
        Perform a screen shake.

        Args:
            intensity: Maximum pixel offset
            duration: Total duration in seconds
            shakes: Number of shake movements
            decay: If True, intensity decreases over time
        """
        if self.is_shaking:
            return  # Don't interrupt ongoing shake

        self.is_shaking = True
        self.shake_id += 1
        current_id = self.shake_id
        shake_interval = duration / shakes

        for i in range(shakes):
            # Calculate intensity with optional decay
            if decay:
                current_intensity = intensity * (1 - i / shakes)
            else:
                current_intensity = intensity

            offset_x = random.uniform(-current_intensity, current_intensity)
            offset_y = random.uniform(-current_intensity, current_intensity)

            def do_shake(timer, runtime, ox=offset_x, oy=offset_y, si=shake_interval,
                        sid=current_id):
                if self.shake_id != sid:
                    return  # Cancelled
                self._animate_position(
                    self.original_x + ox,
                    self.original_y + oy,
                    si * 0.8
                )

            mcrfpy.Timer(f"shake_{current_id}_{i}", do_shake,
                        max(1, int(i * shake_interval * 1000)), once=True)

        # Reset to original
        def reset(timer, runtime, sid=current_id):
            if self.shake_id != sid:
                return
            self._animate_position(self.original_x, self.original_y, shake_interval)
            self.is_shaking = False

        mcrfpy.Timer(f"shake_reset_{current_id}", reset,
                    int(duration * 1000), once=True)

    def update_origin(self):
        """Update stored origin (call after camera moves)."""
        if self.mode == "frame":
            self.original_x = self.target.x
            self.original_y = self.target.y
        else:
            self.original_x = self.target.center[0]
            self.original_y = self.target.center[1]

    # Preset effects
    def light_hit(self):
        """Small shake for minor impacts."""
        self.shake(intensity=3, duration=0.15, shakes=2)

    def heavy_hit(self):
        """Medium shake for significant damage."""
        self.shake(intensity=8, duration=0.25, shakes=4)

    def explosion(self):
        """Large shake for explosions."""
        self.shake(intensity=15, duration=0.4, shakes=6)

    def earthquake(self):
        """Long, rumbling shake."""
        self.shake(intensity=6, duration=1.0, shakes=12, decay=False)

    def death(self):
        """Dramatic shake for player/boss death."""
        self.shake(intensity=20, duration=0.5, shakes=8)


# Setup
shaker = ScreenShakeManager(grid, mode="camera")

# After player moves, update origin so shakes return to correct position
grid.center = (grid.center[0] + 32, grid.center[1])  # e.g. the camera follows the player
shaker.update_origin()

# Usage: a shake started while another is running is ignored (is_shaking), so each
# preset is started after the previous one has finished
shaker.light_hit()   # Small impact
mcrfpy.Timer("hit_heavy", lambda t, rt: shaker.heavy_hit(), 300, once=True)       # Bigger impact
mcrfpy.Timer("hit_boom", lambda t, rt: shaker.explosion(), 650, once=True)        # Boom!
mcrfpy.Timer("hit_quake", lambda t, rt: shaker.earthquake(), 1150, once=True)     # Environmental effect
mcrfpy.Timer("hit_death", lambda t, rt: shaker.death(), 2300, once=True)          # Dramatic moment
```
<!-- /snippet -->

## Directional Shake

Shake in a specific direction for directional impacts:

<!-- snippet: 283_effects_screen_shake_manager region=directional -->
```python
import mcrfpy
import math

def directional_shake(shaker, direction_x, direction_y, intensity=10, duration=0.2):
    """
    Shake in a specific direction (e.g., direction of impact).

    Args:
        shaker: ScreenShakeManager instance
        direction_x, direction_y: Direction vector (will be normalized)
        intensity: Shake strength
        duration: Shake duration
    """
    # Normalize direction
    length = math.sqrt(direction_x * direction_x + direction_y * direction_y)
    if length == 0:
        return

    dir_x = direction_x / length
    dir_y = direction_y / length

    # Shake in the direction, then opposite, then back
    shaker._animate_position(
        shaker.original_x + dir_x * intensity,
        shaker.original_y + dir_y * intensity,
        duration / 3
    )

    def reverse(timer, runtime):
        shaker._animate_position(
            shaker.original_x - dir_x * intensity * 0.5,
            shaker.original_y - dir_y * intensity * 0.5,
            duration / 3
        )

    def reset(timer, runtime):
        shaker._animate_position(
            shaker.original_x,
            shaker.original_y,
            duration / 3
        )
        shaker.is_shaking = False

    mcrfpy.Timer("dir_shake_rev", reverse, int(duration * 333), once=True)
    mcrfpy.Timer("dir_shake_reset", reset, int(duration * 666), once=True)

# Usage: shake away from impact direction
hit_from_x, hit_from_y = -1, 0  # Hit from the left
directional_shake(shaker, hit_from_x, hit_from_y, intensity=12)
```
<!-- /snippet -->

## Key Concepts

1. **Animation properties**: `x`, `y` for Frame position; `center_x`, `center_y` for Grid camera
2. **Decay**: Decreasing intensity makes shake feel more natural
3. **Multiple shakes**: Several small movements feel better than one large one
4. **Origin tracking**: Store and restore original position
5. **State management**: Prevent overlapping shakes with `is_shaking` flag

## Tips

- Use lighter shakes more frequently; save big shakes for impactful moments
- Match shake intensity to game feel (roguelikes often use subtle shakes)
- Combine with other effects (flash, sound) for maximum impact
- Update origin position after camera movement
- Consider player accessibility: some players are sensitive to screen shake (add option to disable)
