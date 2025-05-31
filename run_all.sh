#!/bin/bash
echo "[`date`] Starting run_all.sh"
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /afs/cern.ch/work/s/savarghe/private/2024_Rate_test/CMSSW_15_0_3/src
eval `scramv1 runtime -sh`
# Go to working directory
cd DQM
echo "[`date`] Environment ready, starting Python"
# Run scripts
python3 unpack.py
python3 compute_eff.py 
python3 plot_all.py
python3 plot_each_filter.py
#Run for 2024_25
python3 copy_newfiles.py
python3 compute_eff.py --year 2024_25 --quiet
python3 plot_all.py --year 2024_25 --quiet
python3 plot_each_filter.py --year 2024_25 --quiet
#update website
python3 website/generate_html_index.py
echo "[`date`] Finished compute_eff and plots updated"
