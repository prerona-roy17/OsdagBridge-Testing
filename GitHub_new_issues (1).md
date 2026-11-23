# New issues (post these two at https://github.com/Nidhikhare12/OsdagBridge/issues/new)

---

## Issue A title
[Bug] Log Window prints raw HTML subscript tags (e.g. σ<sub>c</sub>) instead of rendering them

### Description
Design-check messages in the Log Window contain HTML subscripts such as `<sub>c</sub>`, but the Log Window shows the tags as literal text. The design itself runs fine (no crash, results correct); only the log text is affected. It happens on every design run, with default inputs.

### Steps to reproduce
1. Run `python -m osdagbridge.desktop`, Highway Bridge, span 30, carriageway 7.5, Jalpaiguri (all defaults).
2. Click **Design** and wait for it to finish.
3. Read the Log Window.

### Observed
Lines such as:
```
Concrete σ<sub>c</sub>      : 1.88 MPa ≤ 19.2 MPa → PASS
Steel σ<sub>s</sub>         : 358.89 MPa ≤ 400.0 MPa → PASS
M<sub>SLS</sub>,freq (sagging) : 23.849 kNm/m  (γ<sub>DL</sub>...
```
**Expected:** rendered subscripts (σc, σs, M_SLS, γ_DL).

### Root cause
File: `src/osdagbridge/desktop/ui/docks/log_dock.py`, method `append_log`:
```python
escaped_message = (
    message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
)
formatted_message = f'<span style="color: {color}; white-space: pre;">{escaped_message}</span>'
self.log_display.append(formatted_message)
```
All `<` and `>` are escaped, including the intentional `<sub>` / `</sub>` tags emitted by the design/check modules, so the QTextEdit displays them as text.

### Suggested fix
Escape everything, then restore only a small whitelist of formatting tags:
```python
import re

def _escape_keep_basic_tags(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return re.sub(r"&lt;(/?)(sub|sup|b|i)&gt;", r"<\1\2>", text)

# in append_log
escaped_message = _escape_keep_basic_tags(message)
```
Arbitrary tags and user text stay escaped. Alternative: have the check modules emit Unicode subscripts (σ꜀) and keep the current escaping.

### Evidence
Attach the Log Window screenshot (Screenshot 18) and your tc001.osi.

Environment: branch dev, Windows, conda env osdagbridge-env.

---

## Issue B title
[Bug] 3D CAD view has no separate End Diaphragm component; end diaphragms cannot be toggled or isolated

### Description
After a design run, the 3D view lists Bridge, Girder, Deck, Cross Bracing and Crash Barrier as selectable components. End Diaphragm has no entry, although end diaphragms have their own input section (End Diaphragm Details, grade, member IDs E1M1/E1M2) and their own material input. Users cannot show, hide or isolate them, and the report image captures (`capture_for_report`) also have no end-diaphragm group.

### Steps to reproduce
1. Default inputs (span 30, carriageway 7.5). Click **Design**.
2. Look at the checkbox row above the 3D view.

### Observed
Checkboxes: Bridge, Girder, Deck, Cross Bracing, Crash Barrier. **Expected:** an End Diaphragm entry (or a clear statement that end diaphragms are grouped under Cross Bracing).

### Root cause (code)
File: `src/osdagbridge/desktop/ui/cad_3d.py`, `CAD3DWindow.capture_for_report` (about line 621):
```python
ALL         = ['Girder', 'Deck', 'Cross Bracing', 'Crash Barrier', 'Median', 'Railing']
GIRDER_ONLY = ['Girder']
GIRDER_DECK = ['Girder', 'Deck']
```
The component lists (and the `"Cross Bracing": ["Cross Bracing", ...]` name mappings) contain no End Diaphragm. The search for `end_diaphragm_type="Cross Bracing"` suggests end diaphragms are generated with the Cross Bracing component name, so they cannot be addressed separately.

### Suggested fix
1. Give end diaphragm shapes their own component name (e.g. "End Diaphragm") in the CAD generator (`core/bridge_types/plate_girder/cad_generator.py`).
2. Add "End Diaphragm" to the checkbox list, the name-mapping dict and the `ALL` list in `cad_3d.py`.
3. If grouping with Cross Bracing is intended, rename the checkbox to "Cross Bracing / End Diaphragm".

### Evidence
Attach the 3D view screenshot (Screenshot 17) and optionally the `cad_3d.py` screenshot.

Environment: branch dev, Windows, conda env osdagbridge-env.
