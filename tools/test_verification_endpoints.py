
ra = 133.786245
dec = -7.244372

endpoints = {
    "LegacySurvey": f"http://legacysurvey.org/viewer?ra={ra}&dec={dec}&zoom=13&layer=unwise-neo11",
    "PanSTARRS1": f"https://ps1images.stsci.edu/cgi-bin/ps1cutouts?pos={ra}+{dec}&filter=color&filter=g&filter=r&filter=i&filter=z&filter=y&filetypes=stack&auxiliary=data&size=240&output_size=0&verbose=0&autoscale=99.500000&catlist=",
    "Simbad": f"http://simbad.u-strasbg.fr/simbad/sim-coo?Coord={ra}%20{dec}&Radius=10&Radius.unit=arcsec&coodisp1=d2&list.pmsel=on&list.plxsel=on&list.rvsel=on&list.bibsel=off&list.notesel=off&output.format=HTML",
    "VizieR": f"http://vizier.u-strasbg.fr/viz-bin/VizieR?-c={ra}%20{dec}&-c.rs=10&-out.add=_r&-sort=_r",
    "ZooniverseTalk": "https://www.zooniverse.org/projects/marckuchner/backyard-worlds-planet-9/talk/subjects/"
}

print("Generated Verification Endpoints:")
for k, v in endpoints.items():
    print(f"[{k}] -> {v}\n")
