# Floor Plan Reading

Use this when the user provides a floor plan, layout sketch, plan view, courtyard diagram, or architectural sheet.

## Convert Plan to Generator Spec

Extract these in order:

- axis system: central axis, bilateral symmetry, or offset compound spine
- bay rhythm: repeated room width or column spacing
- major solids: halls, towers, gate blocks, shrine cores, side wings
- major voids: courtyards, entry courts, circulation gaps
- entry sequence: outer gate, stairs, bridge, forecourt, main hall
- perimeter logic: walls, edge buildings, moat edge, terrace edge
- elevation hints: stairs, raised plinths, bridges, tiered plateaus

## Plan-to-Blockout Mapping

| Plan Signal | Generator Knob |
|---|---|
| repeated bay width | column spacing / module width |
| central court void | courtyard footprint |
| mirrored side wings | wing count and symmetry mode |
| long axial hall | hall footprint and stair orientation |
| nested walls | perimeter wall ring count |
| offset annex | optional side module toggle |

## Worked Example

If a plan shows:

- one main hall on the centerline
- two mirrored side halls
- a rectangular forecourt
- a rear shrine on a raised plinth

translate it into:

- a central hall generator
- two side-wing modules
- `COURTYARD_ENABLED = True`
- a second elevated landmark module behind the forecourt

Then save the result as a compound-friendly generator instead of four unrelated scripts.
