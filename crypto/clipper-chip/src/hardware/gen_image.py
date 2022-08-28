import gdspy
from svglib.svglib import svg2rlg
from rich.progress import track

lib = gdspy.GdsLibrary(infile="cipher.gds")

layers = [
    ("diff", (65, 20)),
    ("nsdm", (93, 44)),
    ("psdm", (94, 20)),
    ("poly", (66, 20)),
    ("npc", (95, 20)),
    ("licon1", (66, 44)),
    ("li1", (67, 20)),
    ("mcon", (67, 44)),
    ("met1", (68, 20)),
    ("via", (68, 44)),
    ("met2", (69, 20)),
    ("via2", (69, 44)),
    ("met3", (70, 20)),
    ("via3", (70, 44)),
    ("met4", (71, 20)),
    ("via4", (71, 44)),
    ("met5", (72, 20)),
]

top_cell = lib.top_level()[0]
text = gdspy.Text("MAPLECTF", 2, (5.5, 8.5), layer=66, datatype=20)
top_cell.add(text)
top_cell.flatten()

bb = top_cell.get_bounding_box()

style = {(0,0): {"fill": "none"}}

for i, (name, ld) in track(enumerate(layers), total=len(layers)):
    cell = top_cell.copy(name)

    cell.remove_polygons(lambda pts, l, d: (l, d) != ld)
    cell.remove_labels(lambda _: True)
    cell.remove_paths(lambda _: True)

    cell.add(gdspy.Rectangle(bb[0], bb[1], layer=0, datatype=0))

    cell.write_svg(f"masks/{i:02}_{name}.svg", background="white", style=style)
