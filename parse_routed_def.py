#!/bin/python3

import re
from collections import defaultdict

def check_vertical_stripe(line: str):
    '''
    Example Lines from Dali:
        + SHAPE STRIPE ( 5300 5400 ) ( 5300 1576800 ) NEW met4 500
        + SHAPE STRIPE ( 36000 5400 ) ( 36000 1576800 ) NEW met4 500

    Example Lines from Innovus:
        NEW met4 500 + SHAPE STRIPE ( 36000 5400 ) ( * 1576800 )
        NEW met4 500 + SHAPE STRIPE ( 66800 5400 ) ( * 1576800 )
    '''
    validation_pattern = re.compile(
        r'^(?:NEW|\+ ROUTED) met4 \d+ \+ SHAPE STRIPE \(\s*(\d+)\s+(\d+)\s*\) \(\s*(\*|\d+)\s+(\d+)\s*\)$'
    )

    # Check if the input string matches the expected format
    if validation_pattern.match(line):
        # Extract coordinates using the same pattern with groups
        extract_pattern = re.compile(r'\(\s*(\d+|\*)\s+(\d+)\s*\)')
        
        # Find all matches in the input string
        matches = extract_pattern.findall(line)
        
        # Initialize an empty list for coordinates
        coordinates = []
        
        # Variable to keep track of the previous x-coordinate
        prev_x = None
        
        # Process the matches
        for x, y in matches:
            if x == '*':
                # Use the previous x-coordinate if an asterisk is found
                x = prev_x
            else:
                # Update the previous x-coordinate
                x = int(x)
                prev_x = x
            # Append the coordinate as a tuple
            coordinates.append((x, int(y)))

        return coordinates

    else:
        return None

def check_via(line: str):
    '''
    Example Lines from Dali:
        + SHAPE STRIPE ( 5300 13200 ) v3_C NEW met4 0
        + SHAPE STRIPE ( 36000 13200 ) v3_C NEW met3 400

    Example Lines from Innovus:
        NEW met4 0 + SHAPE STRIPE ( 5300 13200 ) v3_C
        NEW met4 0 + SHAPE STRIPE ( 36000 13200 ) v3_C
    '''
    pattern = r'^NEW \w+ \d+ \+ SHAPE \w+ \(\s*(\d+)\s+(\d+)\s*\) \w+$'
    match = re.match(pattern, line.strip())
    
    if match:
        x_coordinate = int(match.group(1))
        y_coordinate = int(match.group(2))
        return (x_coordinate, y_coordinate)
    else:
        return None

def read_lines_file(filename):
    f = open(filename, "r")
    lines = f.readlines()

    return lines

def extract_coordinates_from_file(filename):
    end_net_string = ";"
    lines = read_lines_file(filename)
    flag = None
    net_name = None

    vdd_vertical_stripes = []
    gnd_vertical_stripes = []
    gnd_vias = []
    vdd_vias = []
    pins_list = {}

    for line in lines:
        line = line.strip()
        
        if "DIEAREA" in line:
            pattern = r'DIEAREA\s*\(\s*(\d+)\s+(\d+)\s*\)\s*\(\s*(\d+)\s+(\d+)\s*\)'
            match = re.search(pattern, line)
            die_area_coordinates = tuple(map(int, match.groups()))

        # Check for beginning of Vdd
        if line == '- Vdd  ( * Vdd )': # '- Vdd ( * Vdd )' # Commented out version is the output from Dali
            assert flag == None
            flag = 'Vdd'
            # print(line)

        # Check for beginning of GND
        if line == '- GND  ( * GND )': # '- GND ( * GND )': # Commented out verison is the output from Dali
            assert flag == None
            flag = 'GND'
            # print(line)

        # Check for pins
        if line.startswith('PINS'): # '- GND ( * GND )': # Commented out verison is the output from Dali
            assert flag == None
            flag = 'PINS'
            # print(line)


        if flag == 'Vdd' or flag == 'GND':
            # Case where net is now done
            if ";" in line:
                flag = None
            
            # Case where line is still associated with net
            else:
                # Check for vertical stripes
                coordinates = check_vertical_stripe(line)
                if coordinates != None:
                    if flag == 'GND':
                        gnd_vertical_stripes.append(coordinates)
                    if flag == 'Vdd':
                        vdd_vertical_stripes.append(coordinates)

                # Check for horizontal vias
                coordinates = check_via(line)
                if coordinates != None:
                    if flag == 'GND':
                        gnd_vias.append(coordinates)
                    if flag == 'Vdd':
                        vdd_vias.append(coordinates)

        if flag == 'PINS':
            # Case where net is now done
            if line == "END PINS":
                flag = None
            else:
                if line.startswith('-'):
                    net_name = None
                if "NET" in line:
                    pattern = r'\+ NET\s+(\w+)'
                    # Apply the regex to extract the net name
                    match = re.search(pattern, line)
                    # If a match is found, print the net name
                    if match:
                        net_name = match.group(1)
                elif (net_name is not None) and "PLACED" in line:
                    pattern = r'\+ PLACED\s*\(\s*(\d+)\s+(\d+)\s*\)'
                    match = re.search(pattern, line)
                    if match:
                        coordinates = tuple(map(int, match.groups()))
                        assert(net_name != None)
                        pins_list[net_name] = coordinates

    return gnd_vertical_stripes, vdd_vertical_stripes, gnd_vias, vdd_vias, die_area_coordinates, pins_list

def sort_vias(via_list):
    output_dict = defaultdict(list)
    for via in via_list:
        output_dict[via[0]].append(via[1])

    return(output_dict)

def get_min_max_key(input_list):
    return min(input_list), max(input_list)

def check_vertical_stripe_assumption(output_coordinates):
    '''
    Function to check the assertion that the left strip is ground for each set
    '''
    gnd_coordinates = output_coordinates["top_gnd"]
    vdd_coordinates = output_coordinates["top_vdd"]

    assert(len(gnd_coordinates) == len(vdd_coordinates))

    for i in range(len(gnd_coordinates)):
        assert(gnd_coordinates[i][0] < vdd_coordinates[i][0])
        assert(vdd_coordinates[i][0] - 800 == gnd_coordinates[i][0])


def main(filename):
    gnd_vertical_stripes, vdd_vertical_stripes, gnd_vias, vdd_vias, die_area_coordinates, pins_list = extract_coordinates_from_file(filename)
    gnd_vias = sort_vias(gnd_vias)
    vdd_vias = sort_vias(vdd_vias)

    min_gnd, max_gnd = get_min_max_key(gnd_vias.keys())
    min_vdd, max_vdd = get_min_max_key(vdd_vias.keys())

    output_coordinates = {}

    output_coordinates["bottom_gnd"] = [x[0] for x in gnd_vertical_stripes]
    output_coordinates["bottom_vdd"] = [x[0] for x in vdd_vertical_stripes]

    output_coordinates["top_gnd"] = [x[1] for x in gnd_vertical_stripes]
    output_coordinates["top_vdd"] = [x[1] for x in vdd_vertical_stripes]

    output_coordinates["left_gnd"] = [(min_gnd, x) for x in gnd_vias[min_gnd]]
    output_coordinates["left_vdd"] = [(min_vdd, x) for x in vdd_vias[min_vdd]]
    
    output_coordinates["right_gnd"] = [(max_gnd, x) for x in gnd_vias[max_gnd]]
    output_coordinates["right_vdd"] = [(max_vdd, x) for x in vdd_vias[max_vdd]]

    check_vertical_stripe_assumption(output_coordinates)

    return output_coordinates, gnd_vertical_stripes, vdd_vertical_stripes, die_area_coordinates, pins_list

if __name__ == '__main__':
    filename = "./routed.def"

    output_coordinates = main(filename)

