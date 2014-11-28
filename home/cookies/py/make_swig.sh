#!/bin/bash

other_objects='-Lstd'
mod_name='ivector'
python_libs='/usr/include/python3.4'

echo "Cleaning up"
rm -rf *${mod_name}*.so
rm -rf *${mod_name}*.o
rm -rf *${mod_name}*.pyd
rm -rf *${mod_name}*.py
rm -rf *${mod_name}_wrap.cpp

echo "SWIG compiling ivector"
swig -python -c++ -o ${mod_name}_wrap.cpp ${mod_name}.i
gcc -fpic -std=c++11 -c ${mod_name}.cpp
gcc -fpic -std=c++11 -I${python_libs} -c ${mod_name}_wrap.cpp
g++ -shared -Wl,-soname,_${mod_name}.so ${mod_name}_wrap.o ${mod_name}.o -o _${mod_name}.so

echo "Running test"
python test_swig_${mod_name}.py
