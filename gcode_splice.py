#!/usr/bin/env python3

import argparse
import re
import pprint

parser = argparse.ArgumentParser(description='Splice two gcode files together.')
parser.add_argument('files', metavar='F', type=str, nargs='+', help='gcode files to splice')
parser.add_argument('-o', '--out', action='store', dest='out', default='out.gcode', help='output file')

args = parser.parse_args()

if len(args.files) < 2:
    print('I need more than one file to splice')
    exit(-1)

print(f'saving to output file: {args.out}')

# Gcode RE's
extruder_temp = re.compile('^M10[49]\s+[RS](\d+)')
fan_speed = re.compile('^M106\s+S(\d+)')
fan_off = re.compile('^M107')
filament_change = re.compile('^M600')
linear_advance = re.compile('^M900\s+K(\d+)')
xy_move = re.compile('^G1\s+X([0-9.]+)\s+Y([0-9.]+)')

# each file's props, indexed first by order in args.files, second by section
props = []

for i in range(len(args.files)):
    file = args.files[i]

    with open(file, 'r') as fh:
        print(f'scanning file "{file}"')
        section = 0  # sections of file separated by filament changes
        linenum = 0
        props.append([{
            'extruder_temp': 0,
            'fan_speed': 0,
            'linear_advance': 0
        }])

        for line in fh.readlines():
            linenum += 1

            if filament_change.match(line):
                # Create new section; copy last settings forward
                props[i].append(props[i][section].copy())
                # Remove the XY move
                if 'xy_move' in props[i][section+1]:
                    del props[i][section+1]['xy_move']
                section += 1
                # print(f'filament change in "{file}" at L{linenum}, section {section}')
            elif section <= i:
                if m := extruder_temp.match(line):
                    # print(f'extruder temp at L{linenum}: {m.groups()[0]}')
                    props[i][section]['extruder_temp'] = int(m.groups()[0])
                elif m := fan_speed.match(line):
                    # print(f'fan speed at L{linenum}: {m.groups()[0]}')
                    props[i][section]['fan_speed'] = int(m.groups()[0])
                elif fan_off.match(line):
                    # print(f'fan off at L{linenum} section {section}')
                    props[i][section]['fan_speed'] = 0
                elif m := linear_advance.match(line):
                    # print(f'linear advance at L{linenum}: {m.groups()[0]}')
                    props[i][section]['linear_advance'] = int(m.groups()[0])
                elif m := xy_move.match(line):
                    # capture XY position, but only the first one
                    if 'xy_move' not in props[i][section]:
                        # print(f'first XY move of section {section} at L{linenum}: {m.groups()[0]}, {m.groups()[1]}')
                        props[i][section]['xy_move'] = [float(m.groups()[0]), float(m.groups()[1])]
            elif section > i:
                break  # don't need to scan any further

print(f'pre-scan found properties:')
pprint.pp(props)

with open(args.out, 'w') as out:
    for i in range(len(args.files)):
        file = args.files[i]

        with open(file, 'r') as fh:
            section = 0  # sections of file separated by filament changes
            linenum = 0

            out.write(f'; begin {file}\n')

            for line in fh.readlines():
                linenum += 1

                if filament_change.match(line):
                    section += 1

                    if section > i:
                        file1_props = props[i][section-1]
                        file2_props = props[i+1][section-1]
                        file2_nextprops = props[i+1][section]

                        # print(f'splice in "{file}" at L{linenum}')
                        # print(f'file1_props i={i} section={section-1}:')
                        # pprint.pp(file1_props)
                        # print(f'file2_props i={i+1} section={section-1}:')
                        # pprint.pp(file2_props)

                        out.write(f'; end {file}\n')
                        out.write('; -------------------- splice begin --------------------\n')
                        # Set extruder temp halfway between file1 and file2
                        if file1_props['extruder_temp'] > 0 and file2_props['extruder_temp'] > 0:
                            out.write(f'M104 S{(file1_props["extruder_temp"] + file2_props["extruder_temp"]) // 2} ; extruder temp for filament change\n')
                        out.write('G92 E0.0\n')
                        out.write('G1 E-3.0 ; big retract\n')
                        out.write('G92 E0.0\n')
                        # This won't work: next file's gcode won't always set Z position. Would need to track X/Y/Z
                        # position during pre-scan.
                        # out.write('G91 ; relative position mode\n')
                        # out.write('G1 Z3.0 ; move nozzle up to clear part\n')
                        # out.write('G90 ; absolute position mode\n')
                        if 'xy_move' in file2_nextprops:
                            # Move to position for where we'll resume the print
                            out.write(f'G1 X{file2_nextprops["xy_move"][0]} Y{file2_nextprops["xy_move"][1]} ; move to where next section begins\n')
                        out.write('M107 ; fan off\n')
                        out.write('M600 ; filament change\n')
                        out.write(f'M104 S{file2_props["extruder_temp"]} ; extruder temp for next filament\n')
                        if file2_props["fan_speed"] > 0:
                            out.write(f'M106 S{file2_props["fan_speed"]} ; fan for next filament\n')
                        out.write(f'M900 K{file2_props["linear_advance"]} ; linear advance for next filament\n')
                        out.write('G92 E0.0\n')
                        out.write('; --------------------- splice end ---------------------\n')
                elif section == i:
                    # Copy over file from this section
                    out.write(line)
                elif section > i:
                    break
