---
title: Keyboard
layout: default
mcrf:
  objects:
    - Keyboard
  diataxis: reference
  source: generated
  verified: 0.3.1
  verified_commit: ""
---

# Keyboard

{% raw %}Keyboard state singleton for checking modifier keys{% endraw %}

## Properties

| Property | Description |
| --- | --- |
| `alt` | {% raw %}True if either Alt key is currently pressed (read-only).{% endraw %} |
| `ctrl` | {% raw %}True if either Control key is currently pressed (read-only).{% endraw %} |
| `shift` | {% raw %}True if either Shift key is currently pressed (read-only).{% endraw %} |
| `system` | {% raw %}True if either System key (Win/Cmd) is currently pressed (read-only).{% endraw %} |
