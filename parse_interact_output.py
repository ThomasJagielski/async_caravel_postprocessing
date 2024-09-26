#!/bin/python3

import re

class GAP_BOX:
    def __init__(self, llx, lly, urx, ury, nwell_y, flipped):
        self.llx = llx
        self.lly = lly
        self.urx = urx
        self.ury = ury
        self.nwell_y = nwell_y
        self.flipped = flipped # 0 is PMOS/nwell on top, 1 is PMOS/nwell on bottom

        # TODO: Potentially add a buffer between the top of the cell and the effective height allowed to avoid drc violations
        top_height = round(self.ury - self.nwell_y, 3)
        bottom_height = round(self.nwell_y - self.lly, 3)

        self.p_height = top_height if self.flipped == 0 else bottom_height
        self.n_height = bottom_height if self.flipped == 0 else top_height
        self.width = round(self.urx - self.llx, 3)

    def get_bbox(self):
        magic_box_string = "box " + str(self.llx) + 'um ' + str(self.lly) + 'um ' + str(self.urx) + 'um ' + str(self.ury) + 'um'
        return magic_box_string

def get_list_gaps(filename):
    output_list = None
    with open(filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if "#list" in line:
                output_list = '(' + line.strip().split('(', 1)[-1]
                # Remove the outer parentheses
                output_list = output_list[1:-1]

                pattern = r'\(\((.*?)\)\)'
                matches = re.findall(pattern, output_list)
                # Process each match to convert to the appropriate structure
                groups = []
                for match in matches:
                    # Split the match into elements by finding inner parentheses
                    elements = re.findall(r'\(.*?\)', '(' + match + ')')
                    groups.append(elements)

    return groups

def magic_bounding_boxes(gap_list):
    all_gaps = []

    for mini_row in gap_list:
        mini_row_info = mini_row.pop(0)
        mini_row_info = mini_row_info.replace('(', '').replace(')', '').split(' ')
        # mini_row_llx = int(mini_row_info[0])
        # mini_row_lly = int(mini_row_info[1])
        # mini_row_urx = int(mini_row_info[2])
        # mini_row_ury = int(mini_row_info[3])
        mini_row_well_bound = int(mini_row_info[4])
        mini_row_flipped = 0 if mini_row_info[5] == '#f' else 1 # 0 is PMOS/nwell on top, 1 is PMOS/nwell on bottom

        for gap in mini_row:
            gap = gap.replace('(', '').replace(')', '').split(' ')
            llx = round(int(gap[0]) / 1000, 3)
            lly = round(int(gap[1]) / 1000, 3)
            urx = round(int(gap[2]) / 1000, 3)
            ury = round(int(gap[3]) / 1000, 3)
            nwell_y = round(mini_row_well_bound / 1000, 3)
            all_gaps.append(GAP_BOX(llx=llx, lly=lly, urx=urx, ury=ury, nwell_y=nwell_y, flipped=mini_row_flipped))

    return all_gaps


def box_length_width(origin:tuple, height:int, width:int):
    llx = origin[0]
    lly = origin[1]
    urx = round(origin[0] + width, 3)
    ury = round(origin[1] + height, 3)
    box_string = 'box ' + str(llx) + 'um ' + str(lly) + 'um ' + str(urx) + 'um ' + str(ury) + 'um' 

    return box_string

def draw_fill(box):
    output_string = ''
    distance_from_center = 0.35 #  um NOTE: 0.35 is the minimum distance
    min_width = 0.65 + 0.9 # 0.65 + 0.2
    distance_from_top_bottom_edge = 0.35 # 0.4 # 0.3 # um

    effective_width = box.width - 0.9
    effective_llx = box.llx + 0.45 # 0.2 / 2 = 0.1

    # poly_overhang = 0.15 # um

    if box.width > min_width:

        # North Diffusion
        north_origin_y = round(box.nwell_y + distance_from_center, 3)
        north_height = round(box.ury - distance_from_top_bottom_edge - north_origin_y, 3)
        output_string += box_length_width(origin=(effective_llx,north_origin_y), height=north_height, width=round(effective_width, 3)) + '\n'
        output_string += "paint ndiff\n"
        
        # North Poly
        new_origin = (round(effective_llx + 0.25, 3), round(north_origin_y - 0.15, 3))
        output_string += box_length_width(origin=new_origin, height=round(north_height+0.3, 3), width=round(effective_width-0.5, 3)) + '\n'
        output_string += "paint poly\n"

        # South Diffusion
        south_origin_y = round(box.lly + distance_from_top_bottom_edge, 3)
        south_height = round(box.nwell_y - distance_from_center - south_origin_y, 3)
        output_string += box_length_width(origin=(effective_llx,south_origin_y), height=south_height, width=round(effective_width, 3)) + '\n'
        output_string += "paint ndiff\n"

        # South Poly
        new_origin = (round(effective_llx + 0.25, 3), round(south_origin_y - 0.15, 3))
        output_string += box_length_width(origin=new_origin, height=round(south_height+0.3, 3), width=round(effective_width-0.5, 3)) + '\n'
        output_string += "paint poly\n"

    return output_string


if __name__ == '__main__':
    filename = '../interact_output.log'
    gap_list = get_list_gaps(filename)
    all_gaps = magic_bounding_boxes(gap_list)

    # gap = all_gaps[2]
    # print(gap.get_bbox())
    output_string = ''
    for box in all_gaps:
        output_string += draw_fill(box)

    print(output_string)
