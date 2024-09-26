print ('''
proc fix {{ message "Hit Y to fix ==> "}} {
  puts -nonewline $message
  flush stdout
  gets stdin ans
  if {$ans == Y} {
    source fix_m3_spacing_drc.tcl
  } elseif {$ans == N} {
    puts "No!"
  } else {
    puts "Something else..."
  }
}
''')

for i in range(290):
  print (f"drc find")
  print ("box")
  print ("findbox zoom")
  print ("zoom 10")
  print ("fix")
