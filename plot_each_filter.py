import ROOT
import os

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gErrorIgnoreLevel = ROOT.kWarning

filters = [
    "hltEG32L1SingleEGOrEtFilter",
    "hltEle32WPTightClusterShapeFilter",
    "hltEle32WPTightHEFilter",
    "hltEle32WPTightEcalIsoFilter",
    "hltEle32WPTightHcalIsoFilter",
    "hltEle32WPTightPixelMatchFilter",
    "hltEle32WPTightPMS2Filter",
    "hltEle32WPTightGsfOneOEMinusOneOPFilter",
    "hltEle32WPTightGsfMissingHitsFilter",
    "hltEle32WPTightGsfDetaFilter",
    "hltEle32WPTightGsfDphiFilter",
    "hltEle32WPTightGsfTrackIsoFilter"
]

colors = [
    ROOT.kRed + 1, ROOT.kBlue + 1, ROOT.kGreen + 2, ROOT.kOrange + 7,
    ROOT.kViolet + 1, ROOT.kCyan + 1, ROOT.kMagenta + 2, ROOT.kAzure + 2,
    ROOT.kPink + 9, ROOT.kTeal + 2, ROOT.kSpring + 9, ROOT.kGray + 3
]

def short_label(name):
    return (name.replace("hltEG32L1SingleEGOrEtFilter", "L1")
                .replace("hltEle32WPTight", "")
                .replace("Gsf", "")
                .replace("Filter", ""))

def load_histograms(file, region):
    histos = {}
    for filt in filters:
        hname = f"histos{region}_countsvsrun_{filt}"
        h = file.Get(hname)
        if h:
            histos[filt] = h.Clone(f"{region}_{filt}")
    return histos

def compute_single_efficiency(histos, i, region_label):
    num = histos.get(filters[i])
    denom = histos.get(filters[i - 1])
    if not num or not denom:
        return None, None, None

    eff = num.Clone(f"eff_{region_label}_{i}")
    eff.Divide(denom)
    eff.SetLineWidth(3)
    eff.SetMarkerStyle(20)
    eff.SetMarkerSize(0.9)
    eff.SetMarkerColor(colors[i % len(colors)])
    eff.SetLineColor(colors[i % len(colors)])

    values = [eff.GetBinContent(b) for b in range(1, eff.GetNbinsX() + 1)]
    first = [v for v in values[:5] if v > 0]
    last = [v for v in values[-5:] if v > 0]
    delta = 0
    if first and last:
        delta = (sum(last) / len(last)) - (sum(first) / len(first))

    label = short_label(filters[i])
    if delta > 0.01:
        label += " (up)"
    elif delta < -0.01:
        label += " (down)"
    return eff, label, delta

def draw_single(eff, label, region, i):
    if not eff:
        return

    c = ROOT.TCanvas("c", "", 900, 700)
    y_min = 1.0
    for b in range(1, eff.GetNbinsX() + 1):
        val = eff.GetBinContent(b)
        if val > 0 and val < y_min:
            y_min = val

    eff.SetMinimum(y_min*0.)
    eff.SetMaximum(1.0)
    eff.SetTitle(f"{region}: {label} Efficiency vs Run")
    eff.GetXaxis().SetTitle("Run")
    eff.GetYaxis().SetTitle("Step Efficiency")
    eff.GetXaxis().SetTitleOffset(1.2)
    eff.GetYaxis().SetTitleOffset(1.3)
    eff.Draw("P")

    leg = ROOT.TLegend(0.55, 0.82, 0.79, 0.89)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetTextSize(0.03)
    leg.AddEntry(eff, label, "p")
    leg.Draw()

    outdir = "plots_step_eff_single"
    os.makedirs(outdir, exist_ok=True)
    cname = f"{outdir}/{region}_{short_label(filters[i])}.png"
    c.SaveAs(cname)
    print(f"Saved: {cname}")

# MAIN
f = ROOT.TFile("out_barrelendcaps_new.root")

for region in ["EB", "EE", "EBplus", "EBminus", "EEplus", "EEminus"]:
    histos = load_histograms(f, region)
    for i in range(1, len(filters)):
        eff, label, delta = compute_single_efficiency(histos, i, region)
        draw_single(eff, label, region, i)

f.Close()
