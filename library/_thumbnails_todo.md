# Thumbnails TODO

Follow-up checklist for the Library gallery. Copying demo screenshots into the site is a separate task (not owned by the library generator). The generator only reports which thumbnails are present.

- Demo screens total: **6**
- Thumbnails available (`<name>.png` present): **0**
- Thumbnails missing: **6**

## Demo screens missing a `<name>.png` thumbnail

- [ ] `tests/demo/screenshots/animation_demo.png` (for screen `animation_demo`)
- [ ] `tests/demo/screenshots/caption_demo.png` (for screen `caption_demo`)
- [ ] `tests/demo/screenshots/color_demo.png` (for screen `color_demo`)
- [ ] `tests/demo/screenshots/frame_demo.png` (for screen `frame_demo`)
- [ ] `tests/demo/screenshots/grid_demo.png` (for screen `grid_demo`)
- [ ] `tests/demo/screenshots/primitives_demo.png` (for screen `primitives_demo`)

## Existing screenshots with no matching screen name

These files already exist in `tests/demo/screenshots/` but do not match a screen stem, so they are not auto-detected as thumbnails. A human should decide which screen each belongs to (or rename).

- `demo_00_caption.png`
- `demo_01_frame.png`
- `demo_02_drawing_primitives.png`
- `demo_03_grid_system.png`
- `demo_04_animation_system.png`
- `demo_05_color_system.png`
