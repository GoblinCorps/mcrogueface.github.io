---
title: Keyboard
layout: default
mcrf:
  objects:
    - Keyboard
  diataxis: reference
  source: generated
  verified: 0.3.6
  verified_commit: ""
---

# Keyboard {% include api_badge.html kind="changed" version="0.3.4-dev" %}

{% raw %}Keyboard modifier state singleton: the modifiers (shift, ctrl, alt, system) carried by the key event being handled; they persist until the next key event.{% endraw %}

## Properties

| Property | Description |
| --- | --- |
| `alt` {% include api_badge.html kind="changed" version="0.3.4-dev" %} | {% raw %}True if Alt was held for the key event being handled (read-only). See shift.{% endraw %} |
| `ctrl` {% include api_badge.html kind="changed" version="0.3.4-dev" %} | {% raw %}True if Control was held for the key event being handled (read-only). See shift.{% endraw %} |
| `shift` {% include api_badge.html kind="changed" version="0.3.4-dev" %} | {% raw %}True if Shift was held for the key event being handled (read-only). Read from the event stream, so it is correct inside on_key, for synthesized events and in headless runs.{% endraw %} |
| `system` {% include api_badge.html kind="changed" version="0.3.4-dev" %} | {% raw %}True if the System key (Win/Cmd) was held for the key event being handled (read-only). See shift.{% endraw %} |
