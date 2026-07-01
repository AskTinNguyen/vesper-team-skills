# Detail Mode Calibration ASCII Previs

This file is the spatial contract for `detail_mode_calibration_test.py`.

Use it before changing the 3D generator when the building is being invented from text or when a facade element is landing on the wrong plane.

## Axis Rules

- `X`: left / right symmetry axis
- `Y-`: front / approach / gate side
- `Y+`: rear court side
- `Z+`: vertical height

Interpretation rules:

- door leaves and gate leaves must stand vertically on the facade plane
- threshold stones sit low in `Z` but stay centered on the same facade plane
- beams and lintels are horizontal in `X`
- posts and stiles are vertical in `Z`
- stairs and forecourt extend toward `Y-`
- the main hall door sits deeper inside the hall frontage than the front colonnade
- the gatehouse opening is wider than the hall door opening
- the arrival path is intentionally offset from the hall center axis
- the arrival path should feel strongly offset, with a noticeable lateral shift before reaching the hall

## Top Plan

```text
Y+

...........TT...........TT...........
....#############################....
....#.......=============.......#....
....#.......=============.......#....
....#....|..... HALL .....|.....#....
....#....|....FFFFFFFF....|.....#....
....#....|....DDDDDDDD....|.....#....
....#....|....DDDDDDDD....|.....#....
....#.........PPPPPPP............#....
....#.............................#...
....#########................#####....
........####.................####.....
...........#.........SSSSS.....#......
...........#.......SSSSSSS.....#......
...........#...................#......
...........#.............GGGGGGGGGGGG#
...........#.............GGGGGGGGGGGG#
...........###########################
....LL................TT..............
................TT...............LL...

Y-
```

Legend:

- `HALL`: main front hall core
- `FF`: front colonnade / facade band in front of the recessed door
- `DD`: main doorway within the frontispiece
- `PP`: frontispiece platform / porch band
- `SS`: ceremonial stair
- `GG`: gatehouse opening and gate leaves
- `LL`: lantern markers
- `TT`: tree markers
- `#`: wall / heavy mass
- `=`: roof mass above
- `|`: vertical post line on the facade plane

## Front Elevation

```text
                    ========= upper roof =========
              =========================================
         ======== lower roof / eave spread / beam line ========

              |   |   |   |   |   |   |   |   |   |
              |       FRONT HALL COLONNADE         |
              |                                     |
              |      [ recessed doorway zone ]     |
              |   | |   DDDDDDDDDDDD   | |        |
              |   | |   DDDDDDDDDDDD   | |        |
              |   |_|---DDDDDDDDDDDD---|_|        |
              |      [ deep timber portal ]        |

                         ______PP______
                           ____SS____
                      ________SSSSS_______

         [ wider gatehouse strongly shifted off-axis ]
                          | | GGGGGGGGGGGG | |
                          | | GGGGGGGGGGGG | |
                          |_|-GGGGGGGGGGGG-|_|
                  [ gate frame + threshold band ]
```

Front elevation intent:

- main doorway is centered and vertically dominant
- main doorway sits deeper behind the front colonnade instead of flush with it
- frontispiece is subordinate to the hall roof but stronger than the stair
- gate is a wider gatehouse threshold in front of the hall, not a flat ground marking
- stairs and gate align to the approach sequence, not the perfect hall centerline
- the stair and gatehouse should read clearly offset at first glance, not just slightly misaligned
- stairs widen toward the bottom and narrow toward the hall

## Side Elevation

```text
Y- approach side                                 Y+ rear side

        ===== lower eave =====
     ============================
          ===== upper roof =====

                | hall core |
                | hall core |
                | hall core |
         _______| recessed door |_____
             ____ front platform _____
              .... wider forecourt gap ....
                .... lateral garden shift ....
            __ strongly offset stair ___
                 ____ wider gatehouse roof ______
       |   gate frame / leaves        |
       |   gate threshold band        |
```

Side elevation intent:

- stair and gate occur before the hall facade in depth
- frontispiece sits on the hall facade plane, not on the ground plane
- the hall door sits deeper than the facade band and front colonnade
- the gate is its own vertical assembly, not a floor decal
- the forecourt gap between gatehouse and hall is intentionally larger than before

## Component Stack

```text
1. plinth
2. main hall core
3. side wings
4. lower roof
5. upper roof
6. under-eave beams and bracket rhythm
7. front colonnade
8. recessed frontispiece portal
9. front platform
10. widened forecourt gap
11. offset ceremonial stair
12. gatehouse portal
13. gatehouse roof
14. forecourt terrace and markers
15. lanterns and tree markers
```

## Translation To Generator Helpers

```text
Top plan / massing:
- plinth -> build_variant / build_modular_building plinth
- hall core -> build_variant / build_modular_building core
- wings -> side wing block placement
- roof masses -> spawn_deep_roof_tier

Facade:
- front colonnade -> spawn_front_colonnade
- front door assembly -> spawn_axial_frontispiece + spawn_timber_portal
- under-eave timber rhythm -> spawn_bracket_rhythm

Threshold:
- stair -> spawn_ceremonial_stair
- gate frame + leaves -> spawn_gate_composition + spawn_timber_portal
- forecourt -> spawn_processional_forecourt
- offset composition -> move stair and gatehouse helpers off the hall centerline while preserving a readable arrival route
```

## Alignment Checks Before 3D

If the ASCII is correct, the 3D should satisfy all of these:

- the hall doorway sits on the same plane as the front hall facade
- the hall doorway sits deeper than the front colonnade and frontispiece edge
- the gate doorway sits on the same plane as the gate frame
- door leaves are tall, narrow, and vertical
- threshold stones are short and low, never mistaken for doors
- the gatehouse opening reads wider than the hall door opening
- stair width reads wider than the doorway
- the gatehouse reads in front of the stair, not merged into it
- the approach reads strongly offset and garden-like rather than only slightly shifted

## Current Known Risks

- frontispiece can drift too deep into the hall if `center_y` is too positive
- gate portal can drift into the forecourt if `center_y` is too close to the threshold
- thin portal depth can make vertical parts read like floor strips from oblique camera angles
- roof ornament can distract from doorway legibility if it is too dense before the doorway is resolved
- a perfectly centered stair and gatehouse will erase the intended garden-like asymmetry
- the gatehouse can feel too small if its opening width does not clearly exceed the hall doorway
- if the offset is too weak, the result will still read as formal axial architecture rather than a routed garden approach

## Next Use

When editing the generator next:

1. compare the proposed helper placement against this ASCII first
2. adjust facade-plane `Y` positions before adding new ornament
3. only add detail that reinforces the plan and elevation shown here
