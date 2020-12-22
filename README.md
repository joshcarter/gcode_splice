# Gcode Splicer

This is a tool for splicing gcode files together, specifically to
support cases where filament changes switch materials. For example, in
PrusaSlicer you can insert M600 filament change commands, but it
assumes that the material at each change is identical.

## Use

To use the splicer, generate gcode files for each material. For
example, if the finished print will be a stack of TPU, PETG, then TPU
again, generate gcode files for TPU and PETG. Each gcode file should
include M600 commands at the appropriate places. These must be at
identical Z locations for each material! In the example case with two
filament changes, each gcode file should have two M600 commands in
them.

Then run:

    gcode_splice.py -o "My part TPU-PETG-TPU.gcode" "My Part TPU.gcode" "My Part PETG.gcode" "My Part TPU.gcode"

The splicer will take the first part (up to the first M600 command)
from the TPU gcode, then the next part from the PETG gcode, and so
forth. At each filament change, the extruder temp, fan speed, and so
forth will be adjusted appropriately. I recommend you review the code
at the splice points to ensure it's doing what you want! The splicer
is easy to change if you want different behavior.
