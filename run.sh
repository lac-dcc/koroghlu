#!/bin/bash

if [ $# -lt 1 ]
then
    echo Syntax: ./run.sh <ARCH> [Arch: x86, arm, cuda]
    exit 1
else
    ARCH=$1
    RESULTS=results/$ARCH.csv

    echo "Turning,time(ms),std(ms),Space search(s),tile_i,tile_j,tile_k,order" > $RESULTS
    python3 src/mm.py $ARCH >> $RESULTS
    python3 src/plot_figure.py $RESULTS $ARCH

    echo "done!"
fi