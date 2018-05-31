#!/bin/bash

alias python=python3
source ~/.bashrc

python creat_list.py

alias python=python2
source ~/.bashrc

python submit_data_jobs.py

rm lfn.txt input.txt days.txt
