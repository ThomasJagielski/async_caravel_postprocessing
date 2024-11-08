#!/bin/python3
'''
 * Copyright 2024 Thomas Jagielski
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
'''

import subprocess
import re

offset_spacing = 9.35

lef_name = 'output'
routed_def = 'routed'
magic_file_name = 'top'

subprocess.run("python3 parse_interact_output.py > fill.tcl", shell=True, text=True, capture_output=False)
subprocess.run("python3 drc_find_script.py > drc_fix.tcl", shell=True, text=True, capture_output=False)

# Generate top.mag from lef and def files
magic_sequence = '''
magic -dnull -noconsole -Tsky130A << EOF
source dali_outwell.tcl
lef read ''' + lef_name + '''
def read ''' + routed_def + '''
save ''' + magic_file_name + '''
quit -noprompt 
EOF
'''

subprocess.run(magic_sequence, shell=True, text=True, capture_output=False)

# Open the file to get the size of design
magic_sequence = '''
magic -dnull -noconsole -Tsky130A << EOF
load ''' + magic_file_name + '''
grid 0.05um
snap user
select top cell
box 
quit -noprompt 
EOF
'''

result = subprocess.run(magic_sequence, shell=True, text=True, capture_output=True)


####### GENERATE THE RING #######

coords = []
tcl = open('process_chip_magic.tcl', 'w')

width = 5
offset = 10
spacing = 3
numRings = 2

viaWidth = .15

for line in result.stdout.split('\n'):
    if line.find('microns:') > -1:
        
        coords = re.findall(r'\(.*?\)', line)

xy = []

for coord in coords: 
    new = re.sub(r'[()\s]', '', coord)
    dims = new.split(',')
    xy.append(dims)
    
# print(xy)
ll = xy[0]
ur = xy[1]

llc = [ll[0], ll[1]]
ulc = [ll[0], ur[1]]
urc = [ur[0], ur[1]]
lrc = [ur[0], ll[1]]


# mtype1 = 'm4'
# mtype2 = 'm5'
# sp = 'um '
# via = 'via4'

def makeRing(width, offset, xy, net): 
    ll = xy[0]
    ur = xy[1]

    llc = [ll[0], ll[1]]
    ulc = [ll[0], ur[1]]
    urc = [ur[0], ur[1]]
    lrc = [ur[0], ll[1]]

    sp = 'um '

    # mtype1 = 'm4'
    # mtype2 = 'm5'
    # via = 'via4'

    # mtype1 = 'm2'
    # mtype2 = 'm3'
    # via = 'via2'

    mtype1 = 'm4'
    mtype2 = 'm3'
    via = 'via3'

    #left box
    llx1 = round(float(llc[0]) - offset - width, 3) 
    lly1 = round(float(llc[1]) - offset - width, 3)
    urx1 = round(float(ulc[0]) - offset, 3)
    ury1 = round(float(ulc[1]) + offset  + width, 3)

    #top box
    llx2 = round(float(ulc[0]) - offset - width, 3)
    lly2 = round(float(ulc[1]) + offset, 3)
    urx2 = round(float(urc[0]) + offset + width, 3)
    ury2 = round(float(urc[1]) + offset + width, 3)

    #right box
    llx3 = round(float(lrc[0]) + offset, 3)
    lly3 = round(float(lrc[1]) - offset - width, 3) 
    urx3 = round(float(urc[0]) + offset + width, 3)
    ury3 = round(float(urc[1]) + offset + width, 3)

    #bottom box
    llx4 = round(float(llc[0]) - offset - width, 3)
    lly4 = round(float(llc[1]) - offset - width, 3)
    urx4 = round(float(lrc[0]) + offset + width, 3)
    ury4 = round(float(lrc[1]) - offset, 3)


    #vias
    viallx1 = round(float(llc[0]) - offset - width + viaWidth, 3) 
    vially1 = round(float(llc[1]) - offset - width + viaWidth, 3)
    viaurx1 = round(viallx1 + (width - 2*viaWidth), 3)
    viaury1 = round(vially1 + (width - 2*viaWidth), 3)

    #top box
    viallx2 = round(float(ulc[0]) - offset - width + viaWidth, 3)
    vially2 = round(float(ulc[1]) + offset + viaWidth, 3)
    viaurx2 = round(viallx2 + (width - 2*viaWidth), 3)
    viaury2 = round(vially2 + (width - 2*viaWidth), 3)

    #right box
    viallx3 = round(float(urc[0]) + offset + viaWidth, 3)
    vially3 = round(float(urc[1]) + offset + viaWidth, 3)
    viaurx3 = round(viallx3 + (width - 2*viaWidth), 3)
    viaury3 = round(vially3 + (width - 2*viaWidth), 3)

    #bottom box
    viallx4 = round(float(lrc[0]) + offset + viaWidth, 3)
    vially4 = round(float(lrc[1]) - offset - width + viaWidth, 3)
    viaurx4 = round(viallx4 + width - 2*viaWidth, 3)
    viaury4 = round(vially4 + width - 2*viaWidth, 3)

    box_cmd = '''
    box ''' + str(llx1) + sp + str(lly1) + sp + str(urx1) + sp + str(ury1) + sp + '''
    paint ''' + mtype1 + '''
    label ''' + str(net) + ''' W ''' + mtype1 + '''
    port make
    box ''' + str(llx2) + sp + str(lly2) + sp + str(urx2) + sp + str(ury2) + sp + '''
    paint ''' + mtype2 + '''
    label ''' + str(net) + ''' N ''' + mtype2 + '''
    port make
    box ''' + str(llx3) + sp + str(lly3) + sp + str(urx3) + sp + str(ury3) + sp + '''
    paint ''' + mtype1 + '''
    label ''' + str(net) + ''' E ''' + mtype1 + '''
    port make
    box ''' + str(llx4) + sp + str(lly4) + sp + str(urx4) + sp + str(ury4) + sp + '''
    paint ''' + mtype2 + '''
    label ''' + str(net) + ''' S ''' + mtype2 + '''
    port make    
    '''


    via_cmd = '''
    box ''' + str(viallx1) + sp + str(vially1) + sp + str(viaurx1) + sp + str(viaury1) + sp + '''
    paint ''' + via + '''
    box ''' + str(viallx2) + sp + str(vially2) + sp + str(viaurx2) + sp + str(viaury2) + sp + '''
    paint ''' + via + '''
    box ''' + str(viallx3) + sp + str(vially3) + sp + str(viaurx3) + sp + str(viaury3) + sp + '''
    paint ''' + via + '''
    box ''' + str(viallx4) + sp + str(vially4) + sp + str(viaurx4) + sp + str(viaury4) + sp + '''
    paint ''' + via + '''
    '''

    print(box_cmd, file = tcl)
    print(via_cmd, file = tcl)


makeRing(width, offset, xy, net="GND")
makeRing(width, offset + spacing + width, xy, net="Vdd")


####### 
import parse_routed_def

def print_box(coordinates, units):
    llx = str(round(coordinates[0], 3))
    lly = str(round(coordinates[1], 3))
    urx = str(round(coordinates[2], 3))
    ury = str(round(coordinates[3], 3))

    print("box " + llx + units + lly + units + urx + units + ury + units, file = tcl)

def draw_vertical_top(origin, vertical_origin_offset, track_width, ring_offset, ring_width, via_width, via_offset):
    # NOTE: This assumes the lower one is the left most strip
    # TODO: Add options for layers
    origin_llx = origin[0] - vertical_origin_offset
    origin_lly = origin[1]

    # -- Metal to ring -- 
    urx = origin_llx + track_width
    ury = origin_lly + ring_offset + ring_width
    coordinates = (origin_llx, origin_lly, urx, ury)
    print_box(coordinates, units="um ")
    print("paint m4", file = tcl)

    # Use this for m4 to m3
    lly = ury - ring_width + via_offset
    urx = urx - via_offset
    ury = ury - via_offset
    llx = origin_llx + via_offset
    coordinates = (llx, lly, urx, ury)
    print_box(coordinates, units="um ")
    print("paint via3", file = tcl)

def draw_vertical_bottom(origin, vertical_origin_offset, track_width, ring_offset, ring_width, via_width, via_offset):
    # TODO: Add options for layers
    origin_llx = origin[0] - vertical_origin_offset
    origin_lly = origin[1] - ring_offset - ring_width

    # -- Metal to ring -- 
    urx = origin_llx + track_width
    ury = origin_lly + ring_offset + ring_width
    coordinates = (origin_llx, origin_lly, urx, ury)
    print_box(coordinates, units="um ")
    print("paint m4", file = tcl)

    # Use this for m4 to m3
    llx = origin_llx + via_offset
    lly = origin_lly + via_offset
    urx = urx - via_offset
    ury = origin_lly + ring_width - via_offset
    coordinates = (llx, lly, urx, ury)
    print_box(coordinates, units="um ")
    print("paint via3", file = tcl)

def draw_horizontal_left(origin, horizontal_origin_offset, horizontal_bbox_offset, track_width, ring_offset, ring_width, via_width, via_offset):
    # TODO: Add options for layers
    urx = origin[0] - horizontal_origin_offset
    ury = origin[1] + horizontal_origin_offset

    # -- Metal to ring -- 
    llx = origin[0] - ring_offset - ring_width - horizontal_origin_offset - horizontal_bbox_offset
    lly = origin[1] - horizontal_origin_offset
    coordinates = (llx, lly, urx, ury)
    print_box(coordinates, units="um ")
    print("paint m3", file = tcl)

    # # -- Draw via --
    urx = llx + ring_width - via_offset
    coordinates = (coordinates[0] + via_offset, coordinates[1] + via_offset, urx, coordinates[3] - via_offset)
    print_box(coordinates, units="um ")
    print("paint via3", file = tcl)

def draw_horizontal_right(origin, horizontal_origin_offset, horizontal_bbox_offset, track_width, ring_offset, ring_width, via_width, via_offset):
    # TODO: Add options for layers
    llx = origin[0] + horizontal_origin_offset
    lly = origin[1] - horizontal_origin_offset

    # -- Metal to ring -- 
    urx = origin[0] + ring_offset + ring_width + horizontal_bbox_offset
    ury = origin[1] + horizontal_origin_offset
    coordinates = (llx, lly, urx, ury)
    print_box(coordinates, units="um ")
    print("paint m3", file = tcl)

    # # -- Draw via --
    llx = urx - ring_width + via_offset
    coordinates = (llx, coordinates[1] + via_offset, coordinates[2] - via_offset, coordinates[3] - via_offset)
    print_box(coordinates, units="um ")
    print("paint via3", file = tcl)


# via_dimensions = 1.2um x 1.2um
via_width = 1.2 # um
# via_offset = 0.15 # um
via_offset = 0.05 # um 
horizontal_via_offset = 0.05 # um
track_width = 0.5 # um
track_spacing = 0.3 # um


ring_offset = 10 # um
ring_spacing = 3 # um
ring_width = 5 # um

ring_2_offset = ring_offset + ring_spacing + ring_width

filename = "./routed.def"

coordinates, gnd_vertical_stripes, vdd_vertical_stripes, die_area_coordinates, pins_list = parse_routed_def.main(filename)

gnd_bottom_left_coordinate = coordinates["left_gnd"][0]
gnd_bottom_right_coordinate = coordinates["right_gnd"][0]

vdd_bottom_left_coordinate = coordinates["left_vdd"][0]
vdd_bottom_right_coordinate = coordinates["right_vdd"][0]

# NOTE: Assumes that GND is on the left and VDD is on the right

# TODO: Extract this from parse routed def
die_llx = die_area_coordinates[0]
die_lly = die_area_coordinates[1]
die_urx = die_area_coordinates[2]
die_ury = die_area_coordinates[3]

# vertical_origin_offset = round((gnd_bottom_left_coordinate[0] - die_llx) / 1000, 2) - (track_width / 2) # um
horizontal_origin_offset = round((gnd_bottom_left_coordinate[0] - die_llx) / 1000, 2) - (track_width / 2) # um
vertical_origin_offset = horizontal_origin_offset

horizontal_bbox_offset_outside_left = round((gnd_bottom_left_coordinate[0] - die_llx) / 1000, 2) - (track_width / 2) # um
horizontal_bbox_offset_inside_left = round((vdd_bottom_left_coordinate[0] - die_llx) / 1000, 2) - (track_width / 2) # um

horizontal_bbox_offset_outside_right = (track_width / 2) + offset_spacing#round((die_urx - vdd_bottom_right_coordinate[0]) / 1000, 2) # um
horizontal_bbox_offset_inside_right = (track_width / 2) + track_width + track_spacing + offset_spacing#- 0.95 # um

# -- Use this for connecting to the first (inner) ring -- 
for origin in coordinates["top_gnd"]:
    # origin = coordinates["top_gnd"][0]
    origin = ((origin[0] / 1000), (origin[1] / 1000))
    draw_vertical_top(origin=origin, vertical_origin_offset=vertical_origin_offset, track_width=track_width, ring_offset=ring_offset, ring_width=ring_width, via_width=via_width, via_offset=via_offset)

for origin in coordinates["bottom_gnd"]:
    # origin = coordinates["bottom_gnd"][0]
    origin = ((origin[0] / 1000), (origin[1] / 1000))
    draw_vertical_bottom(origin=origin, vertical_origin_offset=vertical_origin_offset, track_width=track_width, ring_offset=ring_offset, ring_width=ring_width, via_width=via_width, via_offset=via_offset)

for origin in coordinates["left_gnd"]:
    # origin = coordinates["left_gnd"][0]
    origin = ((origin[0] / 1000), (origin[1] / 1000))
    draw_horizontal_left(origin=origin, horizontal_origin_offset=horizontal_origin_offset, horizontal_bbox_offset=horizontal_bbox_offset_outside_left, track_width=track_width, ring_offset=ring_offset, ring_width=ring_width, via_width=via_width, via_offset=horizontal_via_offset)

for origin in coordinates["right_gnd"]:
    # origin = coordinates["right_gnd"][0]
    origin = ((origin[0] / 1000), (origin[1] / 1000))
    draw_horizontal_right(origin=origin, horizontal_origin_offset=horizontal_origin_offset, horizontal_bbox_offset=horizontal_bbox_offset_inside_right, track_width=track_width, ring_offset=ring_offset, ring_width=ring_width, via_width=via_width, via_offset=horizontal_via_offset)


# -- Use this for connecting to the second (outer) ring --
for origin in coordinates["top_vdd"]:
    # origin = coordinates["top_vdd"][0]
    origin = ((origin[0] / 1000), (origin[1] / 1000))
    draw_vertical_top(origin=origin, vertical_origin_offset=vertical_origin_offset, track_width=track_width, ring_offset=ring_2_offset, ring_width=ring_width, via_width=via_width, via_offset=via_offset)

for origin in coordinates["bottom_vdd"]:
    # origin = coordinates["bottom_vdd"][0]
    origin = ((origin[0] / 1000), (origin[1] / 1000))
    draw_vertical_bottom(origin=origin, vertical_origin_offset=vertical_origin_offset, track_width=track_width, ring_offset=ring_2_offset, ring_width=ring_width, via_width=via_width, via_offset=via_offset)

for origin in coordinates["left_vdd"]:
    # origin = coordinates["left_vdd"][0]
    origin = ((origin[0] / 1000), (origin[1] / 1000))
    draw_horizontal_left(origin=origin, horizontal_origin_offset=horizontal_origin_offset, track_width=track_width, horizontal_bbox_offset=horizontal_bbox_offset_inside_left, ring_offset=ring_2_offset, ring_width=ring_width, via_width=via_width, via_offset=horizontal_via_offset)

for origin in coordinates["right_vdd"]:
    # origin = coordinates["right_vdd"][0]
    origin = ((origin[0] / 1000), (origin[1] / 1000))
    draw_horizontal_right(origin=origin, horizontal_origin_offset=horizontal_origin_offset, track_width=track_width, horizontal_bbox_offset=horizontal_bbox_offset_outside_right, ring_offset=ring_2_offset, ring_width=ring_width, via_width=via_width, via_offset=horizontal_via_offset)

########### Extend Pins #######
die_llx = die_area_coordinates[0]
die_lly = die_area_coordinates[1]
die_urx = die_area_coordinates[2]
die_ury = die_area_coordinates[3]

# top_pins = []
# bottom_pins = []
# left_pins = []
# right_pins = []

pin_layer = 'li'
pin_growth_micron = "20um"

for item in pins_list:
    item_port = item.replace(".", r"\.").replace("[", r"\[").replace("]", r"\]")
    if pins_list[item][1] == die_lly:
        # bottom_pins.append(item)
        print("goto " + item_port, file = tcl)
        print("box", file = tcl)
        print("box grow s " + pin_growth_micron, file = tcl)
        print("paint " + pin_layer, file = tcl)

    if pins_list[item][1] == die_ury:
        # top_pins.append(item)
        print("goto " + item_port, file = tcl)
        print("box", file = tcl)
        print("box grow n " + pin_growth_micron, file = tcl)
        print("paint " + pin_layer, file = tcl)

    if pins_list[item][0] == die_llx:
        # left_pins.append(item)
        print("goto " + item_port, file = tcl)
        print("box", file = tcl)
        print("box grow w " + pin_growth_micron, file = tcl)
        print("paint " + pin_layer, file = tcl)
    
    if pins_list[item][0] == die_urx:
        # right_pins.append(item)
        print("goto " + item_port, file = tcl)
        print("box", file = tcl)
        print("box grow e " + pin_growth_micron, file = tcl)
        print("paint " + pin_layer, file = tcl)