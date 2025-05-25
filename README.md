# EGMDQM_HLT_eff
Filter-wise HLT efficiencies for EGM paths using HLT DQM files


```
git clone https://github.com/sanuvarghese/EGMDQM_HLT_eff.git

cd EGMDQM_HLT_eff

```

Then download the online HLT DQM (HLTpb) root files of the selected runs from 
https://cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OnlineData/original/

to this directory,

then run
```
python3 compute_eff.py

python3 plot_all.py

python3 plot_each_filter.py
```
