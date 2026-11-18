---
title: Window
layout: default
mcrf:
  objects:
    - Window
  diataxis: reference
  source: generated
  verified: 0.3.6
  verified_commit: ""
---

# Window

{% raw %}Window singleton for accessing and modifying the game window properties{% endraw %}

## Properties

| Property | Description |
| --- | --- |
| `console_key` {% include api_badge.html kind="added" version="0.3.4-dev" %} {% include api_badge.html kind="changed" version="0.3.4-dev" %} | {% raw %}Key that toggles the developer console (Key, or None for no hotkey). Default Key.GRAVE. Takes effect immediately; while it is a dev hotkey neither its key events nor the text it types reach on_key/on_text. Windowed desktop builds only: headless and web builds have no console, and the key always reaches the game there. mcrfpy.set_dev_console(False) disables the console and releases the key.{% endraw %} |
| `explorer_key` {% include api_badge.html kind="added" version="0.3.4-dev" %} {% include api_badge.html kind="changed" version="0.3.4-dev" %} | {% raw %}Key that toggles the scene explorer (Key, or None for no hotkey). Default Key.F4. Same rules as console_key; the tools cannot share a key.{% endraw %} |
| `framerate_limit` | {% raw %}Frame rate limit in FPS (int, 0 for unlimited). Caps maximum frame rate.{% endraw %} |
| `fullscreen` | {% raw %}Window fullscreen state (bool). Setting this recreates the window.{% endraw %} |
| `game_resolution` | {% raw %}Fixed game resolution as (width, height) tuple. Enables resolution-independent rendering with scaling.{% endraw %} |
| `profiler_key` {% include api_badge.html kind="added" version="0.3.4-dev" %} | {% raw %}Key that toggles the profiler overlay (Key, or None for no hotkey). Default Key.F3. Same rules as console_key; the tools cannot share a key. Works wherever there is a window, desktop and web; headless has no overlay, so the key always reaches the game there.{% endraw %} |
| `resolution` | {% raw %}Window resolution as (width, height) tuple. Setting this recreates the window.{% endraw %} |
| `scaling_mode` | {% raw %}Viewport scaling mode (str): 'center' (no scaling), 'stretch' (fill window), or 'fit' (maintain aspect ratio).{% endraw %} |
| `title` | {% raw %}Window title string (str). Displayed in the window title bar.{% endraw %} |
| `visible` | {% raw %}Window visibility state (bool). Hidden windows still process events.{% endraw %} |
| `vsync` | {% raw %}Vertical sync enabled state (bool). Prevents screen tearing but may limit framerate.{% endraw %} |

## Methods

### `center() -> None`

{% raw %}center() -> None

Center the window on the screen.


Returns:
    None

Note:
    Only works in windowed mode. Has no effect when fullscreen or in headless mode.
{% endraw %}

### `get() -> Window`

*classmethod*

{% raw %}get() -> Window

Get the Window singleton instance.


Returns:
    Window: The global window object

Note:
    This is a class method. Call as Window.get(). There is only one window instance per application.
{% endraw %}

### `screenshot(filename: str = None) -> bytes | None` {% include api_badge.html kind="changed" version="0.3.6-dev" %}

{% raw %}screenshot(filename: str = None) -> bytes | None

Take a screenshot of the current window contents.

Args:
    filename: Optional path to save screenshot. If omitted, returns raw RGBA bytes.

Returns:
    bytes | None: Raw RGBA pixel data if no filename given, otherwise None after saving

Note:
    Taken at the actual window resolution. Captures the last complete frame, never a mid-frame render: a second call after changing objects, with no frame in between, returns the same image, and in a Timer callback you get the previous frame. If no frame has been rendered yet in this process, the first call renders one, so a script that builds a scene and shoots at once gets the scene. Headless step() and advance() do not draw: a headless screenshot after a step draws the scene as it is at the time of the shot, and further calls with no step in between return that image again. Raises RuntimeError if called while a frame is being rendered (e.g. from a warnings hook): there is no complete frame yet.
{% endraw %}
