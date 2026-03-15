# ASCII Previsualization

Use ASCII as an intermediate spatial contract when a building is being designed from text, when the camera view is ambiguous, or when facade parts keep landing on the wrong plane.

ASCII is especially useful for:

- axial compounds
- gates and threshold compositions
- doorway placement
- stair and forecourt alignment
- checking facade depth versus plan depth
- confirming which elements are vertical, horizontal, foreground, or background

## Recommended Views

Create at least two of these before generating 3D:

- top plan
- front elevation
- side elevation
- component stack list

## Minimum ASCII Contract

The ASCII draft should make these clear:

- center axis
- footprint edges
- entry sequence
- doorway width and position
- gate position and opening
- primary roof masses
- secondary wings or walls
- major vertical supports

## Suggested Symbols

- `#`: solid wall or major mass
- `=`: roof or beam band
- `|`: post, pillar, stile, or vertical support
- `-`: lintel, beam, threshold edge, or rail
- `+`: join point or column grid
- `.`: open court / circulation
- `D`: door leaf / doorway
- `G`: gate opening
- `S`: stair / steps
- `T`: tree / planting marker
- `L`: lantern / marker

## Example Pattern

Top plan:

```text
........TT........
..##############..
..#....====....#..
..#....DDDD....#..
..#....DDDD....#..
..#............#..
..###..SSSS..###..
....#..GGGG..#....
....##########....
```

Front elevation:

```text
.......======.......
....==============..
....|.|.|DD|.|.|....
....|_|_|DD|_|_|....
......___SS___......
```

Component stack:

```text
1. plinth
2. stair
3. frontispiece posts
4. door frame + leaves
5. main hall core
6. lower roof
7. upper roof
8. gate threshold
```

## Use In This Skill

When the building is still unstable, do not jump straight from prose to 3D.

Instead:

1. convert the brief into ASCII plan/elevation
2. verify the doorway, gate, and axis in ASCII
3. translate the ASCII into modular Unreal Python masses
4. only then add detail modes

## Design Note

ASCII is not for beauty. It is for alignment, hierarchy, and plane correctness.

If the ASCII is unclear, the 3D script will usually drift too.
