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

print ('''
grid 0.05um
snap user

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
