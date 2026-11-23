"""
compare_osi.py - consistency checks and diff for OsdagBridge .osi input files.

Usage:
    python compare_osi.py tc001.osi                 # checks one file
    python compare_osi.py tc001.osi tc003.osi       # checks both, then lists changed keys

Requires: pip install pyyaml   (already present in most conda envs)
"""
import sys
import yaml

def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None

def check(path, d):
    print(f"\n=== Checks for {path} ===")
    ok = True

    # 1. Segment table end must equal the span
    span = num(d.get("geometry.span"))
    for g in range(1, 5):
        seg = d.get(f"member_properties.girder_details.segment_table.G{g}")
        if not seg:
            continue
        end = num(seg[-1].get("end"))
        status = "OK" if (span is not None and end == span) else "MISMATCH"
        ok &= status == "OK"
        print(f"G{g} segment end = {end} vs span = {span}: {status}")

    # 2. Overall width = (n-1)*spacing + 2*overhang
    n = num(d.get("typical_section.no_of_girders"))
    sp = num(d.get("typical_section.girder_spacing"))
    oh = num(d.get("typical_section.deck_overhang"))
    ow = num(d.get("typical_section.overall_bridge_width"))
    if None not in (n, sp, oh, ow):
        calc = (n - 1) * sp + 2 * oh
        status = "OK" if abs(calc - ow) < 1e-6 else "MISMATCH"
        ok &= status == "OK"
        print(f"Overall width {ow} vs (n-1)*spacing + 2*overhang = {calc}: {status}")

    # 3. Seismic horizontal coefficient = Z/2 * Sa/g * (damping factor 1)
    z = num(d.get("loading.seismic_load.computed.zone_factor"))
    sa = num(d.get("loading.seismic_load.computed.spectral_coeff"))
    ah = num(d.get("loading.seismic_load.computed.horizontal_coeff"))
    if None not in (z, sa, ah):
        calc = z / 2 * sa
        status = "OK" if abs(calc - ah) < 1e-3 else "MISMATCH"
        ok &= status == "OK"
        print(f"Horizontal seismic coeff {ah} vs Z/2*Sa/g = {calc:.3f}: {status}")

    # 4. Girder mass = area * 7850 kg/m3
    area = num(d.get("member_properties.girder_details.section_properties.area"))
    mass = num(d.get("member_properties.girder_details.section_properties.mass"))
    if None not in (area, mass):
        calc = area * 7850
        status = "OK" if abs(calc - mass) < 0.5 else "MISMATCH"
        ok &= status == "OK"
        print(f"Girder mass {mass} vs area*7850 = {calc:.2f}: {status}")

    print("ALL CHECKS PASSED" if ok else "SOME CHECKS FAILED")

def diff(p1, d1, p2, d2):
    print(f"\n=== Keys that differ: {p1} vs {p2} ===")
    keys = sorted(set(d1) | set(d2))
    shown = 0
    for k in keys:
        if ".G2." in k or ".G3." in k or ".G4." in k or "E1M2" in k or "E2" in k or "E3" in k:
            continue  # skip repeated per-girder / per-member copies
        a, b = d1.get(k, "<missing>"), d2.get(k, "<missing>")
        if a != b:
            print(f"{k}: {a}  ->  {b}")
            shown += 1
    print(f"{shown} differing keys shown (repeated per-girder copies skipped)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    files = sys.argv[1:3]
    data = [load(f) for f in files]
    for f, d in zip(files, data):
        check(f, d)
    if len(files) == 2:
        diff(files[0], data[0], files[1], data[1])
