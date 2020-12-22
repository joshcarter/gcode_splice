; file 1
M104 S101 ; foo
; this should be ignored
; M104 S500
M190 S101
M106 S101
; M106 S500
M900 K1
; before spice 1, file 1
M600
M104 S102
M190 S102
M106 S102
; after splice 1, file 1
; before spice 2, file 1
M600
; after splice 2, file 1
M104 S0
M140 S0
M107
