# EGMDQM_HLT_eff
Filter-wise HLT efficiencies for EGM paths using HLT DQM files

First login to a cms environment (this is not strictly needed but better to ensure consistancy).



```
cmsrel CMSSW_15_0_3
cd CMSSW_15_0_3/src
cmsenv
git cms-init
scram build -j 4

git clone https://github.com/sanuvarghese/EGMDQM_HLT_eff.git

cd EGMDQM_HLT_eff

```

The output plots can be found in https://savarghe.web.cern.ch/EGMDQM/

## Running the full workflow

You can simply run 
```
./run_all.sh
```

this runs the following scripts

```
python3 unpack.py 
python3 compute_eff.py
python3 plot_all.py
python3 plot_each_filter.py
python3 website/website/generate_html_index.py 
```
`unpack.py ` unpacks the zip files from ```/eos/cms/store/group/comm_dqm/DQMGUI_Backup/data/offline/OnlineData/original/``` selecting only the HLTpb files of  greater than a run number and a minimum size (10 MB). It also skips the existing files(that are already unpacked) in the target directory.

`compute_eff.py` saves the filter wise counts of each Single Ele filter in the desired mass window for EE and EB (plus/minus). This is a modified version of Laurent's original script

`plot_all.py` calculates the filter wise efficiency and plots them overlaying them in a single plot.

`plot_each_filter.py` does the same but creates individual filter png files.

`generate_html_index.py ` regenerates the hltml index files so that the website shows the correct modified file size and time for the images.

## Setting up Cron Jobs.

Cron jobs are set up using [acron service](https://acrondocs.web.cern.ch/)

in lxplus use the command ```man acrontab``` and follow the instructions there. 

 
