import ROOT
import os
import argparse

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gErrorIgnoreLevel = ROOT.kWarning

# Argument parser
parser = argparse.ArgumentParser()
parser.add_argument('--year', choices=['2024', '2025', '2024_25'], default='2025', help='Which year to process')
parser.add_argument('--quiet', '-q', action='store_true', help='Suppress printout messages')
args = parser.parse_args()

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

    c = ROOT.TCanvas("c", "", 1000, 700)
    c.SetRightMargin(0.2)

    pad = ROOT.TPad("pad", "", 0.0, 0.0, 0.85, 1.0)
    pad.SetBottomMargin(0.12)
    pad.Draw()
    pad.cd()
    c._pad = pad

    y_min = 1.0
    y_max = 0.0
    for b in range(1, eff.GetNbinsX() + 1):
        val = eff.GetBinContent(b)
        err = eff.GetBinError(b)
        if val > 0 and val < y_min:
            y_min = val
        if val + err > y_max:
            y_max = val + err
    eff.SetMinimum(y_min * 0.9)
    eff.SetMaximum(y_max * 1.05)
    eff.SetTitle(f"{region}: {label} Efficiency vs Run")
    eff.GetXaxis().SetTitle("Run")
    eff.GetYaxis().SetTitle("Step Efficiency")
    eff.GetXaxis().SetTitleOffset(1.2)
    eff.GetYaxis().SetTitleOffset(1.3)
    eff.Draw("P")

    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.035)
    latex.SetTextColor(ROOT.kBlack)
    latex.DrawLatex(0.15, 0.87, "{HLT_Ele32_WPTight_Gsf} (from HLT DQM T&P)")

    c.cd()
    leg = ROOT.TLegend(0.75, 0.78, 0.94, 0.89)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetTextSize(0.035)
    leg.AddEntry(eff, label, "p")
    leg.Draw()

    outdir = f"/eos/user/s/savarghe/www/EGMDQM/{args.year}/plots_step_eff_single"
    os.makedirs(outdir, exist_ok=True)
    cname = f"{outdir}/{region}_{short_label(filters[i])}.png"
    c.SaveAs(cname)
    if not args.quiet:
        print(f"Saved: {cname}")

# MAIN
infile = f"out_barrelendcaps_{args.year}.root"
f = ROOT.TFile(infile)

for region in ["EB", "EE", "EBplus", "EBminus", "EEplus", "EEminus"]:
    histos = load_histograms(f, region)
    for i in range(1, len(filters)):
        eff, label, delta = compute_single_efficiency(histos, i, region)
        draw_single(eff, label, region, i)

f.Close()
