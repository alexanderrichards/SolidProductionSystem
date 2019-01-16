#!/bin/bash

jobnumber=$1
{% if macro == "cosmicsSim.mac" %}
inputfile="-f $2"
{% else %}
inputfile=
{% endif %}
randomseed={{ seed }}
Version={{ version }}
Macro={{ macro }}
echo -e "arguments="
echo $Version
echo $Macro
echo -e "randomseed"
echo $jobnumber
echo $inputfile
echo $randomseed
echo {{ id }}
date
pwd
sleep 2
echo -e "\n Checking the environment \n"
ghostname=`hostname --long 2>&1`
gipname=`hostname --ip-address 2>&1`
echo $ghostname "has address" $gipname
uname -a
cat /etc/redhat-release
env | sort

echo "ls -l /cvmfs/solidexperiment.egi.eu"
ls -l /cvmfs/solidexperiment.egi.eu

echo -e " \n ================================== \n"

# **** who am i ***
dirac-proxy-info

echo -e "\n"

#echo -e "File specified in InputSandbox/InputData"
#ls -l

echo -e "\nSetting up dependancies..."

echo -e "\nPath and list of production...\n"
echo $PWD
echo -e "\n"
ls -l
echo -e "\n"

source /cvmfs/sft.cern.ch/lcg/releases/gcc/6.2.0/x86_64-slc6/setup.sh
source /cvmfs/sft.cern.ch/lcg/releases/Geant4/10.03.p01-8919f/x86_64-slc6-gcc62-opt/bin/geant4.sh
source /cvmfs/sft.cern.ch/lcg/releases/clhep/2.3.4.4-adaae/x86_64-slc6-gcc62-opt/CLHEP-env.sh
source /cvmfs/sft.cern.ch/lcg/releases/ROOT/6.08.06-b32f2/x86_64-slc6-gcc62-opt/bin/thisroot.sh
#source /cvmfs/sft.cern.ch/lcg/releases/ROOT/6.02.10-617d9/x86_64-slc6-gcc49-opt/bin/thisroot.sh

export PATH=/cvmfs/sft.cern.ch/lcg/releases/CMake/3.7.0-a8e5d/x86_64-slc6-gcc62-opt/bin/:${PATH}
#export PATH=/cvmfs/sft.cern.ch/lcg/releases/clhep/2.3.4.4-adaae/x86_64-slc6-gcc62-opt/bin:${PATH}
export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/cvmfs/sft.cern.ch/lcg/releases/clhep/2.3.4.4-adaae/x86_64-slc6-gcc62-opt/lib/pkgconfig

echo $LD_LIBRARY_PATH

echo -e "\nI am hereeeeee.\n"

# temporary hack
ln -s /cvmfs/solidexperiment.egi.eu/el6/SolidSim/${Version}/solid_g4_sim/solid-build/properties .
#ln -s /cvmfs/solidexperiment.egi.eu/el6/SolidSim/${Version}/solid_g4_sim/input_macros/phase1.config .

echo -e "\n"
ls -l
echo -e "\n"

output_dir=$(dirname "{{ output_lfn }}")
{% if solidsim_inputfiletype == "atm-n" %}
    output_filename={{ output_lfn }}/neutorns_${jobnumber}_{{ id }}.root
{% elif solidsim_inputfiletype == "muons" %}
    output_filename={{ output_lfn }}/muons_${jobnumber}_{{ id }}.root
{% endif %}
/cvmfs/solidexperiment.egi.eu/el6/SolidSim/${Version}/solid_g4_sim/solid-build/SolidSim /cvmfs/solidexperiment.egi.eu/el6/SolidSim/${Version}/solid_g4_sim/input_macros/${Macro} -o ${output_filename} ${inputfile} -n {{ nevents }} -s ${randomseed} &> log.txt
#-c /cvmfs/solidexperiment.egi.eu/el6/SolidSim/${Version}/solid_g4_sim/input_macros/phase1.config

dirac-dms-add-file ${output_dir}/ntuples/${output_filename} ${output_filename} BEgrid-ULB-VUB-disk  #BEgrid-ULB-VUB-disk #UKI-LT2-IC-HEP-disk
dirac-dms-add-file ${output_dir}/logs/log_${jobnumber}_{{ id }}.txt log.txt BEgrid-ULB-VUB-disk  #BEgrid-ULB-VUB-disk #UKI-LT2-IC-HEP-disk
#dirac-dms-add-file /solidexperiment.org/MC/Phase1-validation/cosmics/Neutron-reduced/NEUTRONS-T9cut1/g4/1h1/logs/Script_${jobnumber}.log Script1_macN.sh.log UKI-LT2-IC-HEP-disk #BEgrid-ULB-VUB-disk 

rm ${inputfile} ${output_filename} log.txt
rm -r properties

echo -e "\nList of production at the end ...\n"
echo -e "\n"
ls -l
echo -e "\n"

echo -e "\nI am done here."
