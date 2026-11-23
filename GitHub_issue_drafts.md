# GitHub issue drafts

Before posting: search https://github.com/Nidhikhare12/OsdagBridge/issues for "segment", "stale", "wearing course", "density". If a match exists, post the body below as a comment on it instead.

---

## Issue 1: Girder segment table keeps the old span after the span is changed

**Description**
After a design run with span 30, changing the span to 40 (design unlocked) and running again leaves every girder's segment table ending at 30.0 m. Span, carriageway, skew and materials all updated correctly; only the segment table is stale.

**Steps to reproduce**
1. Basic Inputs: span 30, carriageway 7.5, skew 0. Design, then Save Input (tc001).
2. Unlock the design. Change materials to E 410A / M45 and run again (tc002).
3. Unlock. Set span 40, carriageway 10, skew 10. Design, then Save Input (tc003).
4. Open tc003.osi.

**Observed (tc003.osi)**
```
geometry.span: '40'
member_properties.girder_details.segment_table.G1:
- end: 30.0
  id: G1M1
  start: 0.0
(G2, G3, G4 identical)
```
**Expected:** `end: 40.0`.

**Environment:** branch dev, Windows, conda env osdagbridge-env. Attach tc001.osi, tc002.osi, tc003.osi and screenshots.

**Root cause (suspected)**
File: `src/osdagbridge/desktop/ui/dialogs/additional_input/additional_inputs.py`, method `_on_girder_segments_load` (about lines 1262-1283):
```python
segments = self.working_input_dict.get(seg_key)
total_span = float(self.working_input_dict.get(KEY_SPAN))
if not segments:
    segments = [{"id": f"{girder_id}M1", "start": 0.0, "end": total_span}]
    self.working_input_dict[seg_key] = segments
target_widget.set_total_span(total_span)
target_widget.refresh(segments)
```
A segment with the current span is created only when no segments exist. Stored segments from an earlier run are reused unchanged, so `end` keeps the old span.

**Suggested fix**
```python
segments = self.working_input_dict.get(seg_key)
total_span = float(self.working_input_dict.get(KEY_SPAN))
if not segments:
    segments = [{"id": f"{girder_id}M1", "start": 0.0, "end": total_span}]
else:
    segments = [s for s in segments if float(s["start"]) < total_span]
    segments[-1]["end"] = total_span
self.working_input_dict[seg_key] = segments
```
`set_total_span` (defined in `_segment_table_widget.py`) is called only from this method, so no other code updates the segment end. Note: the setter body has not been reviewed.

---

## Issue 2: Custom wearing course density accepts only 0 to 10 and rejects realistic values

**Description**
With Wearing Course material set to Custom, the density field accepts 0, 5 and 10 and rejects 11, 15, 20, 22, 24, 25, 26 and 30 as "out of range". The Concrete default is 25 and its field is not editable. Density 0 is accepted although it is not physical.

**Additional mismatch:** the UI shows density 25 for Concrete, but the saved input file (tc001.osi, tc002.osi, tc003.osi) stores `typical_section.wearing_course.density: 24.0`.

**Steps to reproduce**
1. Additional Inputs, Wearing Course, material Custom.
2. Enter 25 (rejected), 10 (accepted), 0 (accepted).
3. Save Input and open the .osi file; search `wearing_course.density`.

**Expected:** a range suited to kN/m3 densities (e.g. about 15 to 30), no zero, and the saved value equal to the displayed value.

**Root cause:** not yet located. Search the repo for `wearing_course` and `density`; the validator range (probably `setRange` or `QDoubleValidator` with an upper limit of 10, possibly a thickness or unit-mixed range) needs changing, and the default (24 vs 25) needs to be consistent in one place.

---

## Issue 3 (only if reproducible): Deck thickness entered in the UI is saved as 250
Entered 260 in Additional Inputs; UI and 3D view showed 260, but tc002.osi has `typical_section.deck_thickness: 250.0` (tc003.osi also 250.0). Once the field reverted to 250 during editing; not reproduced in two later attempts. Verify with a fresh Save Input before posting.

---

## Optional comments or small issues
- Log Window shows raw HTML tags (`<sub>`) instead of subscripts.
- No Input/Output Dictionary viewer in the GUI; Database > Save Output shows no feedback.
- 3D view component checkboxes have no End Diaphragm entry.
- `overall_bridge_width: 10.899999999999999` (rounding).
- `modulus_of_elasticity_zy/zz` hold section moduli.
- Debug `print(f"@@: ...")` statements in additional_inputs.py and defaults.py.
