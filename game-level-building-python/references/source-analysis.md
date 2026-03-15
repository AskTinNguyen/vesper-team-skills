# Source Analysis

Use this when the user provides drawings, concept art, orthographic sketches, screenshots, or mixed references.

## Extract Before Coding

Always convert the reference into a short spec first:

- archetype: pagoda, hall, gate, tower, shrine, wall run, bridge house, courtyard edge, or hybrid
- dominant footprint: square, rectangle, T-plan, U-plan, courtyard ring, axial compound, or stacked tower
- vertical stack: plinth, body tiers, roof tiers, tower caps, spire
- roof family: flat, gabled, hipped, layered pagoda, gate roof, bridge roof
- entry axis: frontal, side approach, bridge approach, axial climb
- symmetry: perfect, mostly axial, offset, asymmetrical
- repeated motifs: columns, bays, roof rhythm, corner towers, wall segments, veranda strips
- gameplay reads: choke point, arena edge, sniper perch, traversal stair, shrine platform, skyline landmark

## Concept Art Decomposition

Reduce the image into blockout modules:

1. Mark the hero silhouette.
2. Count large tiers before counting small details.
3. Identify the primary circulation path to the front door or platform.
4. Separate reusable modules from one-off hero pieces.
5. Decide which details become geometry now and which become future mesh swaps.

## Reference-to-Config Example

If the art shows:

- five stacked roofs
- a square plinth
- a strong frontal stair
- four corner towers

then start with:

- `TIER_COUNT = 5`
- square footprint values
- `STAIR_STYLE = "frontal"`
- `CORNER_TOWERS = True`

Then add only the next-most-important secondary masses.
