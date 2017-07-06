#!/bin/bash
for i in {1..10}
do
    for i in {1..125}
        do
            python in_corral.py load
        done
    python in_corral.py run
    python in_corral.py run
    python in_corral.py run
done

