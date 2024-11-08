'''
 * Copyright 2024 Xiayuan Wen
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

import re

class circuitVerilog:

  def __init__(self):
    self.ports = []

  def setName(self, module_name):
    self.name = module_name
  
  def printName(self):
    print('The name is'+self.name)

  def addPort(self, port):
    self.ports.append(port)

  def printPorts(self):
    for port in self.ports:
      print(port[0]+' '+port[1])

  def emitVerilog(self, filename):
    file = open(filename, "w")
    file.write('module '+self.name+'(\n')
    for port in self.ports[:-1]:
      if port[1] == 'INPUT':
        file.write('  input '+port[0]+',\n')
      elif port[1] == 'OUTPUT':
        file.write('  output '+port[0]+',\n')
      elif port[1] == 'INOUT':
        file.write('  inout '+port[0]+',\n')

    port = self.ports[-1]
    if port[1] == 'INPUT':
      file.write('  input '+port[0])
    elif port[1] == 'OUTPUT':
      file.write('  output '+port[0])
    elif port[1] == 'INOUT':
      file.write('  inout '+port[0])

    file.write(');\nendmodule')
    file.close()
    

def read_lines_file(filename):
  f = open(filename, "r")
  lines = f.readlines()

  return lines

def extract_info(filename, circuit):
  lines = read_lines_file(filename)
  
  flag = None
  port_name = None

  count = 0
  for line in lines:
    count = count+1
    contents = line.split()
    if contents[0] == 'MACRO':
      circuit.setName(contents[1])
      break

  for line in lines[count:]:
    if line != '\n':
      contents = contents = line.split()
      if contents[0] == 'PIN':
        flag = 'PIN'
        port_name = contents[1]

      if flag == 'PIN':
        contents = line.split()
        if len(contents) == 2:
          if (contents[0] == 'END') & (contents[1] == port_name):
            print("END "+port_name)
            flag = None
        else:
          if contents[0] == 'DIRECTION':
            port = ((port_name, contents[1]))
            circuit.addPort(port)

 
def main():
  filename = "top_fill.lef"
  circuit = circuitVerilog()
  extract_info(filename, circuit)
  filename_v = circuit.name+".v"
  circuit.emitVerilog(filename_v)

main()




    