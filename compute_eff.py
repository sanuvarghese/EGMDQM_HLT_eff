#based on Laurent's code
import ROOT
import os
import re

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

def extract_run_number(filename):
    match = re.search(r'R0*([0-9]{6})', filename)
    if match:
        return int(match.group(1))
    return None

# Helper to extract counts for all regions in one go
def getfiltercountsperrun(filename, forfakes=False):
    full_path = os.path.join("inputFiles", filename)  # prepend inputFiles/ to filename
    f = ROOT.TFile(full_path, "READ")
    prefix = filename[-11:-5]
    folder = f"DQMData/Run {prefix}/HLT/Run summary/EGM/TrigObjTnP/"
    firstbin = 55 if forfakes else 25
    lastbin = 60 if forfakes else 35

    EB_counts = []
    EBplus_counts = []
    EBminus_counts = []
    EE_counts = []
    EEplus_counts = []
    EEminus_counts = []

    for i in filters:
        h = f.Get(folder + "stdTag_" + i + "_eta")
        if not h:
            EB_counts.append(0)
            EBplus_counts.append(0)
            EBminus_counts.append(0)
            EE_counts.append(0)
            EEplus_counts.append(0)
            EEminus_counts.append(0)
            continue
        val_EB = int(h.Integral(2, 3, firstbin, 60))
        val_EBplus = int(h.Integral(3, 3, firstbin, 60))
        val_EBminus = int(h.Integral(2, 2, firstbin, 60))
        val_EEplus = int(h.Integral(4, 4, firstbin, 60))
        val_EEminus = int(h.Integral(1, 1, firstbin, 60))
        val_EE = val_EEplus + val_EEminus

        EB_counts.append(val_EB)
        EBplus_counts.append(val_EBplus)
        EBminus_counts.append(val_EBminus)
        EE_counts.append(val_EE)
        EEplus_counts.append(val_EEplus)
        EEminus_counts.append(val_EEminus)

    return int(prefix), EB_counts, EBplus_counts, EBminus_counts, EE_counts, EEplus_counts, EEminus_counts

# Gather all run numbers from files
folder_path = '.'
run_numbers = []
file_info = []
for filename in os.listdir(folder_path):
    if os.path.isfile(os.path.join(folder_path, filename)) and filename.endswith('.root') and filename.startswith('DQM'):
        run = extract_run_number(filename)
        if run is not None:
            run_numbers.append(run)
            file_info.append((filename, run))

if not run_numbers:
    print("No valid ROOT files with run numbers found.")
    exit(1)

min_run = (min(run_numbers) // 1000) * 1000
max_run = ((max(run_numbers) // 1000) + 1) * 1000
nbins = max_run - min_run

# Create histograms
histos_EB = []
histos_EBplus = []
histos_EBminus = []
histos_EE = []
histos_EEplus = []
histos_EEminus = []

for i in filters:
    histos_EB.append(ROOT.TH1F('histosEB_countsvsrun_' + i, '', nbins, min_run, max_run))
    histos_EBplus.append(ROOT.TH1F('histosEBplus_countsvsrun_' + i, '', nbins, min_run, max_run))
    histos_EBminus.append(ROOT.TH1F('histosEBminus_countsvsrun_' + i, '', nbins, min_run, max_run))
    histos_EE.append(ROOT.TH1F('histosEE_countsvsrun_' + i, '', nbins, min_run, max_run))
    histos_EEplus.append(ROOT.TH1F('histosEEplus_countsvsrun_' + i, '', nbins, min_run, max_run))
    histos_EEminus.append(ROOT.TH1F('histosEEminus_countsvsrun_' + i, '', nbins, min_run, max_run))

# Loop through all files
for filename, run in file_info:
    print(f"Found file: {filename}")
    run, EB_vals, EBplus_vals, EBminus_vals, EE_vals, EEplus_vals, EEminus_vals = getfiltercountsperrun(os.path.join(folder_path, filename), forfakes=False)

    # Fill EB histograms
    for i, hist in enumerate(histos_EB):
        hist.Fill(run, EB_vals[i])
        hist.SetBinError(hist.FindBin(run), pow(EB_vals[i], 0.5))

    # Fill EB+ histograms
    for i, hist in enumerate(histos_EBplus):
        hist.Fill(run, EBplus_vals[i])
        hist.SetBinError(hist.FindBin(run), pow(EBplus_vals[i], 0.5))

    # Fill EB- histograms
    for i, hist in enumerate(histos_EBminus):
        hist.Fill(run, EBminus_vals[i])
        hist.SetBinError(hist.FindBin(run), pow(EBminus_vals[i], 0.5))

    # Fill EE histograms
    for i, hist in enumerate(histos_EE):
        hist.Fill(run, EE_vals[i])
        hist.SetBinError(hist.FindBin(run), pow(EE_vals[i], 0.5))

    # Fill EE+ histograms
    for i, hist in enumerate(histos_EEplus):
        hist.Fill(run, EEplus_vals[i])
        hist.SetBinError(hist.FindBin(run), pow(EEplus_vals[i], 0.5))

    # Fill EE- histograms
    for i, hist in enumerate(histos_EEminus):
        hist.Fill(run, EEminus_vals[i])
        hist.SetBinError(hist.FindBin(run), pow(EEminus_vals[i], 0.5))

# Write histograms
out = ROOT.TFile('out_barrelendcaps_new.root', "RECREATE")
for h in histos_EB + histos_EBplus + histos_EBminus + histos_EE + histos_EEplus + histos_EEminus:
    h.Write()
out.Close()

print(f"Histograms written to out_barrelendcaps_new.root with run range {min_run} to {max_run}")
