#!/bin/bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /afs/cern.ch/work/s/savarghe/private/2024_Rate_test/CMSSW_15_0_3/src
eval `scramv1 runtime -sh`

# Go to working directory
cd DQM

# Run scripts
python3 unpack.py
python3 compute_eff.py
python3 plot_all.py
python3 plot_each_filter.py
