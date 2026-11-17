---
title: EngineConfig
layout: default
mcrf:
  objects:
    - EngineConfig
  diataxis: reference
  source: generated
  verified: 0.3.5
  verified_commit: ""
---

# EngineConfig {% include api_badge.html kind="added" version="0.3.4-dev" %}

{% raw %}EngineConfig()

The engine's run configuration, available as mcrfpy.config.

Under --exec, sys.argv is the script's, so engine flags are visible only here.
Every property is read-only except exit_on_exception. Reading raises
RuntimeError when no engine is running.

Properties:
    headless (bool, read-only): True when running without a window (--headless).
    audio_enabled (bool, read-only): False after --audio-off (or --headless).
    exec_scripts (tuple[str], read-only): The --exec scripts, in order.
    script_path (str | None, read-only): The script named on the command line, or None.
    script_args (tuple[str], read-only): Arguments after the script (or after --).
    run_forever (bool, read-only): True with --run-forever.
    interactive (bool, read-only): True with -i.
    screenshot_path (str | None, read-only): The --screenshot path, or None.
    exit_on_exception (bool): Whether the first uncaught exception in a Python callback
        ends the process. False with --continue-after-exceptions. Assign a bool.

Example:
    if mcrfpy.config.exit_on_exception:
        raise RuntimeError('run me with --continue-after-exceptions')
{% endraw %}

## Properties

| Property | Description |
| --- | --- |
| `audio_enabled` {% include api_badge.html kind="added" version="0.3.4-dev" %} | {% raw %}False after --audio-off, or --headless without --audio-on (bool, read-only).{% endraw %} |
| `exec_scripts` {% include api_badge.html kind="added" version="0.3.4-dev" %} | {% raw %}The --exec scripts in command-line order (tuple[str], read-only).{% endraw %} |
| `exit_on_exception` {% include api_badge.html kind="added" version="0.3.4-dev" %} | {% raw %}Whether an uncaught exception in a Python callback ends the process (bool). False with --continue-after-exceptions. Assign a bool; anything else raises TypeError.{% endraw %} |
| `headless` {% include api_badge.html kind="added" version="0.3.4-dev" %} | {% raw %}True when running without a window, --headless (bool, read-only).{% endraw %} |
| `interactive` {% include api_badge.html kind="added" version="0.3.4-dev" %} | {% raw %}True with -i (bool, read-only).{% endraw %} |
| `run_forever` {% include api_badge.html kind="added" version="0.3.4-dev" %} | {% raw %}True with --run-forever (bool, read-only).{% endraw %} |
| `screenshot_path` {% include api_badge.html kind="added" version="0.3.4-dev" %} | {% raw %}The --screenshot path, or None (str \| None, read-only).{% endraw %} |
| `script_args` {% include api_badge.html kind="added" version="0.3.4-dev" %} | {% raw %}Arguments after the script, or after -- (tuple[str], read-only).{% endraw %} |
| `script_path` {% include api_badge.html kind="added" version="0.3.4-dev" %} | {% raw %}The script named on the command line, or None (str \| None, read-only).{% endraw %} |
| `virtual_env` {% include api_badge.html kind="added" version="0.3.4-dev" %} {% include api_badge.html kind="changed" version="0.3.5-dev" %} | {% raw %}The virtual environment this interpreter runs in (sys.prefix when it differs from sys.base_prefix), or None (str \| None, read-only). Found from the launch path, never from the VIRTUAL_ENV variable. See docs/sys-path-order.md.{% endraw %} |
