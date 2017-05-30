#!/bin/bash
for i in {1..700}
do
    python in_corral.py load
done

python in_corral.py run
