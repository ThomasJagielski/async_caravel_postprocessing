#!/bin/bash

magic -dnull -noconsole << EOF 
load top.mag
grid 0.05um
snap user
source ./fill.tcl
save top_fill.mag
quit -noprompt
EOF
