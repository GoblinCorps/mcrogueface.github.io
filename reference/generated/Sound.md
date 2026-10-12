---
title: Sound
layout: default
mcrf:
  objects:
    - Sound
  diataxis: reference
  source: generated
  verified: 0.3.1
  verified_commit: ""
---

# Sound

{% raw %}Sound(source)

Sound effect object for short audio clips.

Args:
    source: Filename string or SoundBuffer object.

Properties:
    volume (float): Volume 0-100.
    loop (bool): Whether to loop.
    playing (bool, read-only): True if playing.
    duration (float, read-only): Duration in seconds.
    source (str, read-only): Source filename.
    pitch (float): Playback pitch (1.0 = normal).
    buffer (SoundBuffer, read-only): The SoundBuffer, if created from one.
{% endraw %}

## Properties

| Property | Description |
| --- | --- |
| `buffer` | {% raw %}The SoundBuffer if created from one, else None (read-only).{% endraw %} |
| `duration` | {% raw %}Total duration of the sound in seconds (read-only).{% endraw %} |
| `loop` | {% raw %}Whether the sound loops when it reaches the end.{% endraw %} |
| `pitch` | {% raw %}Playback pitch multiplier (1.0 = normal, >1 = higher, <1 = lower).{% endraw %} |
| `playing` | {% raw %}True if the sound is currently playing (read-only).{% endraw %} |
| `source` | {% raw %}Filename path used to load this sound (read-only).{% endraw %} |
| `volume` | {% raw %}Volume level from 0 (silent) to 100 (full volume).{% endraw %} |

## Methods

### `pause() -> None`

{% raw %}pause() -> None

Pause the sound. Use play() to resume from the paused position.

{% endraw %}

### `play() -> None` {% include api_badge.html kind="changed" version="0.2.8-dev" %}

{% raw %}play() -> None

Start or resume playing the sound.


Note:
    The engine keeps a playing sound alive, so Sound(...).play() plays to the end without holding a reference. Does nothing when audio is off (--audio-off, or --headless without --audio-on).
{% endraw %}

### `play_varied(pitch_range: float = 0.1, volume_range: float = 3.0) -> tuple[float, float]` {% include api_badge.html kind="changed" version="0.2.8-dev" %}

{% raw %}play_varied(pitch_range: float = 0.1, volume_range: float = 3.0) -> tuple[float, float]

Play an extra voice with randomized pitch and volume for natural variation. Voices overlap, so rapid calls (footsteps, hits) layer instead of restarting.

Args:
    pitch_range: Random pitch offset range (default 0.1)
    volume_range: Random volume offset range (default 3.0)

Returns:
    tuple[float, float]: the (pitch, volume) drawn for this voice. The sound's own pitch/volume properties are not changed, and .playing reports only play(), so this return value is the only record of the draw.

Note:
    The randomness comes from the engine's AUDIO random stream. Set mcrfpy.set_random_seed() to make the variation reproducible; read mcrfpy.get_random_seed() to learn the seed a run used. The AUDIO stream is independent of the entity-behaviour stream, so playing sounds never changes how entities move.
{% endraw %}

### `stop() -> None` {% include api_badge.html kind="changed" version="0.2.8-dev" %}

{% raw %}stop() -> None

Stop playing and reset to the beginning. Also stops play_varied() voices.

{% endraw %}
