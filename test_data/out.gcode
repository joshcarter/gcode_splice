; begin file1.gcode
; file 1
M104 S101 ; foo
; this should be ignored
; M104 S500
M190 S101
M106 S101
; M106 S500
M900 K1
; before spice 1, file 1
; end file1.gcode
; -------------------- splice begin --------------------
M104 S151 ; extruder temp for filament change
G92 E0.0
G1 E-3.0 ; big retract
G92 E0.0
M107 ; fan off
M600 ; filament change
M104 S201 ; extruder temp for next filament
M106 S201 ; fan for next filament
M900 K2 ; linear advance for next filament
G92 E0.0
; --------------------- splice end ---------------------
; begin file2.gcode
; after splice 1, file 2
M104 S202
M190 S202
M106 S202
; before spice 2, file 2
; end file2.gcode
; -------------------- splice begin --------------------
M104 S252 ; extruder temp for filament change
G92 E0.0
G1 E-3.0 ; big retract
G92 E0.0
M107 ; fan off
M600 ; filament change
M104 S302 ; extruder temp for next filament
M106 S302 ; fan for next filament
M900 K3 ; linear advance for next filament
G92 E0.0
; --------------------- splice end ---------------------
; begin file3.gcode
; after splice 2, file 3
M104 S303
M190 S303
M106 S303
M104 S0
M140 S0
M107
