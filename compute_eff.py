import ROOT
import os
import re
import argparse

filters = [
    'hltEG32L1SingleEGOrEtFilter',
    'hltEle32WPTightClusterShapeFilter',
    'hltEle32WPTightHEFilter',
    'hltEle32WPTightEcalIsoFilter',
    'hltEle32WPTightHcalIsoFilter',
    'hltEle32WPTightPixelMatchFilter',
    'hltEle32WPTightPMS2Filter',
    'hltEle32WPTightGsfOneOEMinusOneOPFilter',
    'hltEle32WPTightGsfMissingHitsFilter',
    'hltEle32WPTightGsfDetaFilter',
    'hltEle32WPTightGsfDphiFilter',
    'hltEle32WPTightGsfTrackIsoFilter'
]

parser = argparse.ArgumentParser()
parser.add_argument('--year', choices=['2024', '2025', '2024_25'], default='2025', help='Which year to run over')
parser.add_argument('--quiet', '-q', action='store_true', help='Suppress printout messages')
args = parser.parse_args()

base_dir = '/eos/cms/store/group/tsg/STEAM/savarghe/HLTpbFiles'
folder_path = os.path.join(base_dir, args.year)

def extract_run_number(filename):
    match = re.search(r'R0*([0-9]{6})', filename)
    return int(match.group(1)) if match else None

def get_counts(filename, forfakes=False):
    f = ROOT.TFile.Open(filename)
    prefix = filename[-11:-5]
    folder = f"DQMData/Run {prefix}/HLT/Run summary/EGM/TrigObjTnP/"
    firstbin = 55 if forfakes else 25

    EB, EBplus, EBminus = [], [], []
    EE, EEplus, EEminus = [], [], []

    for filt in filters:
        h = f.Get(folder + "stdTag_" + filt + "_eta")
        if not h:
            EB.append(0); EBplus.append(0); EBminus.append(0)
            EE.append(0); EEplus.append(0); EEminus.append(0)
            continue
        val_EB = int(h.Integral(2, 3, firstbin, 60))
        val_EBplus = int(h.Integral(3, 3, firstbin, 60))
        val_EBminus = int(h.Integral(2, 2, firstbin, 60))
        val_EEplus = int(h.Integral(4, 4, firstbin, 60))
        val_EEminus = int(h.Integral(1, 1, firstbin, 60))
        val_EE = val_EEplus + val_EEminus

        EB.append(val_EB)
        EBplus.append(val_EBplus)
        EBminus.append(val_EBminus)
        EE.append(val_EE)
        EEplus.append(val_EEplus)
        EEminus.append(val_EEminus)

    return EB, EBplus, EBminus, EE, EEplus, EEminus

# Step 1: Read and store data for valid runs
valid_runs = []
all_counts = []

for fname in sorted(os.listdir(folder_path)):
    if not (fname.endswith(".root") and fname.startswith("DQM")):
        continue
    full_path = os.path.join(folder_path, fname)
    if not args.quiet:
        print(f"Found file: {fname}")
    run = extract_run_number(fname)
    if run is None:
        if not args.quiet:
            print(f"Skipping {fname} (no run number found)")
        continue
    try:
        EB, EBplus, EBminus, EE, EEplus, EEminus = get_counts(full_path)
        if EB[0] > 20000:
            valid_runs.append(run)
            all_counts.append((run, EB, EBplus, EBminus, EE, EEplus, EEminus))
        else:
            if not args.quiet:
                print(f"Skipping run {run} (first filter EB count = {EB[0]})")
    except Exception as e:
        if not args.quiet:
            print(f"Skipping {fname} due to error: {e}")
        continue

if not valid_runs:
    print(f"No valid runs found passing EB > 30000 in {folder_path}")
    exit(1)

min_run = (min(valid_runs) // 1000) * 1000
max_run = ((max(valid_runs) // 1000) + 1) * 1000
nbins = max_run - min_run

# Step 2: Initialize histograms
histos = {region: [] for region in ["EB", "EBplus", "EBminus", "EE", "EEplus", "EEminus"]}
for region in histos:
    for filt in filters:
        histos[region].append(ROOT.TH1F(f"histos{region}_countsvsrun_{filt}", '', nbins, min_run, max_run))

# Step 3: Fill histograms
for run, EB, EBplus, EBminus, EE, EEplus, EEminus in all_counts:
    for i, h in enumerate(histos["EB"]):        h.Fill(run, EB[i]);        h.SetBinError(h.FindBin(run), EB[i]**0.5)
    for i, h in enumerate(histos["EBplus"]):    h.Fill(run, EBplus[i]);    h.SetBinError(h.FindBin(run), EBplus[i]**0.5)
    for i, h in enumerate(histos["EBminus"]):   h.Fill(run, EBminus[i]);   h.SetBinError(h.FindBin(run), EBminus[i]**0.5)
    for i, h in enumerate(histos["EE"]):        h.Fill(run, EE[i]);        h.SetBinError(h.FindBin(run), EE[i]**0.5)
    for i, h in enumerate(histos["EEplus"]):    h.Fill(run, EEplus[i]);    h.SetBinError(h.FindBin(run), EEplus[i]**0.5)
    for i, h in enumerate(histos["EEminus"]):   h.Fill(run, EEminus[i]);   h.SetBinError(h.FindBin(run), EEminus[i]**0.5)

# Step 4: Write output
outname = f"out_barrelendcaps_{args.year}.root"
out = ROOT.TFile(outname, "RECREATE")
for hlist in histos.values():
    for h in hlist:
        h.Write()
out.Close()

print(f"Done. Histograms saved to {outname} with run range {min_run}-{max_run} ({len(valid_runs)} valid runs)")
