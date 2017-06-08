#!/bin/bash
for i in {1..8}
do
    for i in {1..100}
        do
            python in_corral.py load
        done
    python in_corral.py run
    python in_corral.py run
    python in_corral.py run
done

