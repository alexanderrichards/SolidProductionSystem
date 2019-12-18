#!/bin/bash

jobnumber=$1
inputfile=$2
Version={{ saffron2_version }}
Patch=patch4
echo -e "arguments="
echo $jobnumber
echo $inputfile
echo {{ day }}
echo $Version
echo $Patch

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

source /cvmfs/solidexperiment.egi.eu/el6/saffron2/${Version}/saffron2/T2_mMachine_setup.sh 

echo -e "\nI am hereeeeee.\n"

echo -e "\n"
ls -l
echo -e "\n"

file=${inputfile}
read num1 num2 num3 num4 num5 num6 <<<${file//[^0-9]/ }
runNUMBER=$num1
runTime=$num4
echo -e "runNumber and runTime is"
echo $runNUMBER $runTime


if [[ ${inputfile} = *?.bz2 ]]
then
  bzip2 -d ${inputfile}
  inputfile=${inputfile%.bz2}    
fi


/cvmfs/solidexperiment.egi.eu/el6/saffron2/${Version}/saffron2/saffron {{macro}} --RunNumber=$runNUMBER --AppendInputFiles=${inputfile} &> log.txt
#/cvmfs/solidexperiment.egi.eu/el6/saffron2/v1.2/saffron2/saffron onlineMonitoringBR2.txt --RunNumber=1002808 --AppendInputFiles=rundetector_1002808_06Dec17_1908.sbf

dirac-dms-add-file {{ analysis_output_lfndir }}/histos/S2-histos_cycleMode_${jobnumber}_${runNUMBER}_$runTime.root S2-histos_cycleMode.root UKI-LT2-IC-HEP-disk
dirac-dms-add-file {{ analysis_output_lfndir }}/ntuples/S2-tuple_${jobnumber}_${runNUMBER}_$runTime.root S2-tuple.root UKI-LT2-IC-HEP-disk
dirac-dms-add-file {{ analysis_output_lfndir }}/logs/log_${jobnumber}_${runNUMBER}_$runTime.txt log.txt UKI-LT2-IC-HEP-disk

#dirac-dms-add-file /solidexperiment.org/Data/phase1_BR2/test/test_grid/S2-histos_cycleMode_${jobnumber}_$runNUMBER.root S2-histos_cycleMode.root UKI-LT2-IC-HEP-disk
#dirac-dms-add-file /solidexperiment.org/Data/phase1_BR2/test/test_grid/S2_${jobnumber}_$runNUMBER.root S2-tuple.root UKI-LT2-IC-HEP-disk

echo -e "\n"
ls -l
echo -e "\n"

rm ${inputfile}
rm mysql-connector-c++-1.1.8-linux-glibc2.5-x86-64bit.tar.gz
rm S2-histos_cycleMode.root S2-tuple.root log.txt

echo -e "\nList of production at the end ...\n"
echo -e "\n"
ls -l
echo -e "\n"

echo -e "\nI am done here."
