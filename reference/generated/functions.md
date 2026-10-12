---
title: Module Functions
layout: default
mcrf:
  objects:
    - Module Functions
  diataxis: reference
  source: generated
  verified: 0.3.1
  verified_commit: ""
---

# Module Functions

Top-level functions in the `mcrfpy` module.

## `mcrfpy.advance(ms: int) -> int` {% include api_badge.html kind="added" version="0.2.8-dev" %} {% include api_badge.html kind="changed" version="0.2.8-dev" %}

{% raw %}advance(ms: int) -> int

Advance the simulation clock by exactly ms milliseconds (headless mode only), running one simulation frame per timer deadline crossed so that every repeating timer fires once per elapsed interval.

Args:
    ms: Milliseconds of simulated time to advance. Must be an int >= 0.

Returns:
    int: Milliseconds actually advanced. Returns 0 in windowed mode, and 0 for advance(0).

Raises:
    TypeError: ms is not an int (step() is the one that takes float seconds)

Raises:
    ValueError: ms is negative -- the simulation clock does not run backwards

Note:
    advance(10000) fires a 1000ms repeating timer exactly 10 times, as step(10.0) does, but runs a separate frame at each deadline, so animations and Scene.update() see the time between firings. Partial intervals are carried: advance(10500) fires it 10 times and leaves it 500ms from its next deadline.

Note:
    Each boundary is a full simulation frame, so current_frame advances once per timer deadline crossed plus once for any residual. advance(0) does nothing at all -- use step(0.0) to run a frame without moving the clock.

Note:
    Read the resulting clock with get_metrics()['simulation_time_ms'] (milliseconds). The 'runtime' key is wall clock and is unrelated to simulated time.

Raises:
    OverflowError: ms would carry the clock past its int-millisecond range

Raises:
    RuntimeError: Called from a background thread that currently holds mcrfpy.lock(), or from a thread that does not drive the clock; see step().

See also: The frame barrier: rules, budget, and failure modes (docs/frame-lock.md)
{% endraw %}

## `mcrfpy.bresenham(start, end, include_start=True, include_end=True) -> list[tuple[int, int]]`

{% raw %}bresenham(start, end, include_start=True, include_end=True) -> list[tuple[int, int]]

Compute grid cells along a line using Bresenham's algorithm.

Args:
    start: (x, y) tuple or Vector - starting point
    end: (x, y) tuple or Vector - ending point
    include_start: Include the starting point in results (default: True)
    include_end: Include the ending point in results (default: True)

Returns:
    list[tuple[int, int]]: List of (x, y) grid coordinates along the line

Note:
    Useful for line-of-sight checks, projectile paths, and drawing lines on grids. The algorithm ensures minimal grid traversal between two points.
{% endraw %}

## `mcrfpy.end_benchmark() -> str`

{% raw %}end_benchmark() -> str

Stop benchmark capture and write data to JSON file.


Returns:
    str: The filename of the written benchmark data

Raises:
    RuntimeError: If no benchmark is currently running

Note:
    Returns the auto-generated filename (e.g., 'benchmark_12345_20250528_143022.json')
{% endraw %}

## `mcrfpy.exit() -> None`

{% raw %}exit() -> None

Cleanly shut down the game engine and exit the application.


Returns:
    None

Note:
    This immediately closes the window and terminates the program.
{% endraw %}

## `mcrfpy.find(name: str, scene: str = None) -> UIDrawable | None`

{% raw %}find(name: str, scene: str = None) -> UIDrawable | None

Find the first UI element with the specified name.

Args:
    name: Exact name to search for
    scene: Scene to search in (default: current scene)

Returns:
    Frame, Caption, Sprite, Grid, or Entity if found; None otherwise

Note:
    Searches scene UI elements and entities within grids.
{% endraw %}

## `mcrfpy.find_all(pattern: str, scene: str = None) -> list`

{% raw %}find_all(pattern: str, scene: str = None) -> list

Find all UI elements matching a name pattern.

Args:
    pattern: Name pattern with optional wildcards (* matches any characters)
    scene: Scene to search in (default: current scene)

Returns:
    list: All matching UI elements and entities

Note:
    Example: find_all('enemy*') finds all elements starting with 'enemy', find_all('*_button') finds all elements ending with '_button'
{% endraw %}

## `mcrfpy.get_metrics() -> dict` {% include api_badge.html kind="changed" version="0.2.8-dev" %}

{% raw %}get_metrics() -> dict

Get current performance metrics.


Returns:
    dict: Performance data with keys: frame_time (last frame duration in MILLISECONDS), avg_frame_time (rolling mean frame time over the last 60 frames, in milliseconds), fps (frames per second, derived from avg_frame_time -- a rolling average, not an instantaneous rate), draw_calls (number of draw calls), ui_elements (total UI element count), visible_elements (visible element count), current_frame (frame counter), runtime (WALL-CLOCK seconds since engine start), simulation_time_ms (SIMULATED milliseconds, the deterministic counter advanced only by step()/advance() and the clock headless timers run on), grid_render_time (grid rendering time in ms), entity_render_time (entity rendering time in ms), fov_overlay_time (FOV overlay rendering time in ms), python_time (Python script execution time in ms), animation_time (animation processing time in ms), grid_cells_rendered (grid cell draws this frame, counted per layer), entities_rendered (number of entities drawn this frame), total_entities (total entity count across all rendered grids), audio_sources (Sound and Music objects alive), audio_playing (those the engine is keeping alive because they are playing)

Note:
    All per-frame counters and timing breakdowns describe the last COMPLETED frame. Python callbacks run before the frame is rendered, so the in-progress frame's values are not available yet; frame_time, fps, runtime, simulation_time_ms and current_frame are live.

Note:
    'runtime' and 'simulation_time_ms' are DIFFERENT clocks: runtime is wall time in seconds and advances on its own; simulation_time_ms is simulated MILLISECONDS and moves only when step()/advance() is called, which is headless-only -- in windowed mode it stays 0 and timers run on runtime instead. Rendering costs zero simulation_time_ms, so a screenshot never moves it.
{% endraw %}

## `mcrfpy.get_random_seed() -> int` {% include api_badge.html kind="added" version="0.2.8-dev" %}

{% raw %}get_random_seed() -> int

The seed the engine's internal random streams are using.


Returns:
    int: the seed set by set_random_seed(), or -- if none was ever set -- a seed generated from the system entropy source, recorded, and used from then on. This never fails to answer, so a run that was not seeded explicitly can still be replayed afterwards by passing this value to set_random_seed().

Note:
    Calling this before any randomness is consumed fixes the seed for the rest of the process -- it materialises the value rather than reporting a placeholder. Record it in a run log if reproducibility matters.
{% endraw %}

## `mcrfpy.lock() -> _LockContext` {% include api_badge.html kind="changed" version="0.2.8-dev" %}

{% raw %}lock() -> _LockContext

Get a context manager for thread-safe access to mcrfpy objects from background threads.


Returns:
    _LockContext: A context manager that blocks until safe to touch engine objects

Note:
    Any access to mcrfpy objects from a non-main thread must happen inside `with mcrfpy.lock():`; behavior outside the lock is undefined. On a worker thread the context manager blocks (GIL released) until the render loop opens a safe window between frames. On the thread that drives the clock (the main thread, unless a background thread runs frames with step()/advance()) it is a no-op.

Note:
    INSIDE THE LOCK, MUTATE ONLY. The main thread parks until every holder releases, so hold time is added to frame time roughly 1:1 -- a 10 ms hold costs the frame 10 ms, and presents as engine stutter rather than as a misbehaving handler. Do I/O, waiting, and computation OUTSIDE the block and apply the result inside it. Calling mcrfpy.step() or mcrfpy.advance() while holding the lock raises RuntimeError rather than deadlocking.

See also: The frame barrier: rules, budget, and failure modes (docs/frame-lock.md)
{% endraw %}

## `mcrfpy.log_benchmark(message: str) -> None`

{% raw %}log_benchmark(message: str) -> None

Add a log message to the current benchmark frame.

Args:
    message: Text to associate with the current frame

Returns:
    None

Raises:
    RuntimeError: If no benchmark is currently running

Note:
    Messages appear in the 'logs' array of each frame in the output JSON.
{% endraw %}

## `mcrfpy.set_dev_console(enabled: bool) -> None`

{% raw %}set_dev_console(enabled: bool) -> None

Enable or disable the developer console overlay.

Args:
    enabled: True to enable the console (default), False to disable

Returns:
    None

Note:
    When disabled, the grave/tilde key will not open the console. Use this to ship games without debug features.
{% endraw %}

## `mcrfpy.set_random_seed(seed: int) -> None` {% include api_badge.html kind="added" version="0.2.8-dev" %}

{% raw %}set_random_seed(seed: int) -> None

Seed the engine's internal random streams and reset them to their start. Call this before anything consumes randomness to make a run reproducible.

Args:
    seed: Unsigned 32-bit integer, 0 to 4294967295 inclusive

Returns:
    None

Raises:
    TypeError: seed is not an integer

Raises:
    ValueError: seed is negative or larger than 4294967295

Note:
    Covers the randomness the engine generates on its own behalf: entity behaviour selection (Behavior.NOISE4 / NOISE8) and Sound.play_varied(). Objects that take their own seed -- NoiseSource, BSP.split_recursive, SoundBuffer.sfxr -- are unaffected; seed those individually.

Note:
    Each subsystem gets an independent stream derived from this one seed, so playing sounds does not shift entity behaviour. Reordering or removing a stream would change every sequence at a given seed.
{% endraw %}

## `mcrfpy.set_scale(multiplier: float) -> None`

{% raw %}set_scale(multiplier: float) -> None

Deprecated: use Window.resolution instead. Scale the game window size.

Args:
    multiplier: Scale factor (e.g., 2.0 for double size)

Returns:
    None

Note:
    The internal resolution remains 1024x768, but the window is scaled. This is deprecated - use Window.resolution instead.
{% endraw %}

## `mcrfpy.start_benchmark() -> None`

{% raw %}start_benchmark() -> None

Start capturing benchmark data to a file.


Returns:
    None

Raises:
    RuntimeError: If a benchmark is already running

Note:
    Benchmark filename is auto-generated from PID and timestamp. Use end_benchmark() to stop and get filename.
{% endraw %}

## `mcrfpy.step(dt: float = None) -> float` {% include api_badge.html kind="changed" version="0.2.8-dev" %}

{% raw %}step(dt: float = None) -> float

Run one full simulation frame (headless mode only). Advances the scene update, timers, Python Scene.update() callbacks, animations, and scene transitions (including their completion), records frame-time metrics, and increments the frame counter -- everything a windowed frame does except render and input.

Args:
    dt: Time to advance in seconds, finite and >= 0. If None, advances to the next scheduled event (timer/animation).

Returns:
    float: Actual time advanced in seconds. Returns 0.0 in windowed mode.

Note:
    Rendering is deliberately excluded: it is orthogonal to the clock and costs zero simulation time, so a screenshot draws arbitrary state without time passing. In windowed mode this is a no-op returning 0.0. Timers run on simulation time -- explicit, deterministic time is the point of driving a headless test with step().

Note:
    A headless --exec script must end by calling sys.exit(), because step() is the only headless clock: without it the engine cannot advance itself. --run-forever keeps a headless process alive, but its loop does not move the simulation clock, so timers and animations advance only through step()/advance() (#448).

Note:
    A wide step catches timers up: step(10.0) fires a 1000ms repeating timer ten times within the one frame, each call receiving its own deadline as runtime, and the timer keeps its phase. Animations receive the whole dt. advance() differs only in running a separate frame per deadline.

Raises:
    ValueError: dt is negative, NaN or infinite

Raises:
    OverflowError: dt would carry the clock past its int-millisecond range

Raises:
    RuntimeError: Called from a background thread that currently holds mcrfpy.lock(). Advancing a frame from inside the lock re-enters the frame the lock synchronises with, which cannot complete until the caller releases. Inside the lock, mutate only. (lock() is a no-op on the thread that drives the clock, so this cannot fire from script init or a timer callback.)

Raises:
    RuntimeError: Called from a thread that does not drive the simulation clock. The first thread to run a frame owns the clock until it exits (#411).

See also: The frame barrier: rules, budget, and failure modes (docs/frame-lock.md)
{% endraw %}
