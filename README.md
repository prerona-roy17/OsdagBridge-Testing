# OsdagBridge Testing and Issue Reporting

Testing of the OsdagBridge short-span steel girder (plate girder) bridge module, branch `dev`, Windows, conda env `osdagbridge-env`.

## Contents
| File | Purpose |
|---|---|
| `OsdagBridge_Testing_Report.pdf` | Full testing report |
| `OsdagBridge_test_log.xlsx` / `.csv` | Test log: cases, UI vs input-file comparison, bug list |
| `osi_files/tc001.osi, tc002.osi, tc003.osi` | Saved inputs for the three consecutive runs |
| `compare_osi.py` | Script that checks an .osi file for consistency and diffs two files |
| `GitHub_issue_drafts.md`, `GitHub_new_issues.md` | Issue texts prepared for GitHub |
| `screenshots/` | Evidence screenshots |

## Test runs
| Run | Inputs | Time |
|---|---|---|
| TC-01 | Span 30, carriageway 7.5, skew 0, E 350A, M40 (defaults) | 77.61 s |
| TC-02 | Same, custom E 410A and M45 | 101.33 s |
| TC-03 | Span 40, carriageway 10, skew 10, E 410A, M45 | 165.49 s |

## GitHub issues
New issues raised:
- https://github.com/Nidhikhare12/OsdagBridge/issues/226 - Log Window shows raw HTML subscript tags
- https://github.com/Nidhikhare12/OsdagBridge/issues/228 - 3D view has no separate End Diaphragm component

Additional findings commented on existing issues:
- https://github.com/Nidhikhare12/OsdagBridge/issues/168 - stale girder segment end (G1 also affected)
- https://github.com/Nidhikhare12/OsdagBridge/issues/183 - wearing course density validation (accepts only 0 to 10; stored 24.0 vs UI 25)

## Using the script
    pip install pyyaml
    python compare_osi.py osi_files/tc003.osi
    python compare_osi.py osi_files/tc001.osi osi_files/tc003.osi

Video demonstration: (add link)
