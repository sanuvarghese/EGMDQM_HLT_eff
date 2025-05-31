import ROOT
import os
import argparse

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gErrorIgnoreLevel = ROOT.kWarning

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
    name = name.replace("hltEG32L1SingleEGOrEtFilter", "L1")
    name = name.replace("hltEle32WPTight", "")
    name = name.replace("Gsf", "")
    name = name.replace("Filter", "")
    return name

def load_histograms(file, region):
    histos = {}
    for filt in filters:
        hname = f"histos{region}_countsvsrun_{filt}"
        h = file.Get(hname)
        if h:
            histos[filt] = h.Clone(f"{region}_{filt}")
            h.SetDirectory(0)
    return histos

def compute_efficiencies(histos, region_label):
    effs = []
    for i in range(1, len(filters)):
        num = histos.get(filters[i])
        denom = histos.get(filters[i - 1])
        if not num or not denom:
            continue
        eff = num.Clone(f"eff_{region_label}_{i}")
        eff.SetDirectory(0)
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

        effs.append((label, eff))

    # Total efficiency
    num = histos.get(filters[-1])
    denom = histos.get(filters[0])
    if num and denom:
        total_eff = num.Clone(f"eff_{region_label}_total")
        total_eff.SetDirectory(0)
        total_eff.Divide(denom)
        total_eff.SetLineWidth(4)
        total_eff.SetLineColor(ROOT.kBlack)
        total_eff.SetMarkerColor(ROOT.kBlack)
        total_eff.SetMarkerStyle(20)
        total_eff.SetTitle("Total")
        effs.append(("Total", total_eff))

    return effs

def draw_overlay(effs, title, outname, outdir):
    c = ROOT.TCanvas("c", "", 1000, 700)
    c.SetRightMargin(0.2)

    pad = ROOT.TPad("pad", "", 0.0, 0.0, 0.85, 1.0)
    pad.SetBottomMargin(0.12)
    pad.Draw()
    pad.cd()
    c._pad = pad

    # Compute global y_min and y_max from all histograms
    y_min = 1.0
    y_max = 0.0
    for _, h in effs:
        for b in range(1, h.GetNbinsX() + 1):
            val = h.GetBinContent(b)
            err = h.GetBinError(b)
            if val > 0 and val < y_min:
                y_min = val
            if val + err > y_max:
                y_max = val + err

    for i, (label, h) in enumerate(effs):
        h.SetMinimum(y_min * 0.95)
        h.SetMaximum(y_max * 1.05)
        h.SetTitle(title)
        h.GetXaxis().SetTitle("Run")
        h.GetYaxis().SetTitle("Filter Efficiency")
        h.GetXaxis().SetTitleOffset(1.2)
        h.GetYaxis().SetTitleOffset(1.3)
        h.GetXaxis().SetLabelSize(0.04)
        h.GetYaxis().SetLabelSize(0.04)
        h.Draw("E SAME" if i else "E")

    # Annotation
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.035)
    latex.SetTextColor(ROOT.kBlack)
    latex.DrawLatex(0.15, 0.87, "{HLT_Ele32_WPTight_Gsf} (from HLT DQM T&P)")

    # Legend
    c.cd()
    legend = ROOT.TLegend(0.76, 0.25, 0.99, 0.95)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.SetTextSize(0.03)
    for label, h in effs:
        legend.AddEntry(h, label, "l")
    legend.Draw()

    os.makedirs(outdir, exist_ok=True)
    full_out = os.path.join(outdir, outname)
    c.SaveAs(full_out)
    if not args.quiet:
        print(f"Saved: {full_out}")

# --- Main ---
if __name__ == "__main__":
    year = args.year
    infile = f"out_barrelendcaps_{year}.root"
    outdir = f"/eos/user/s/savarghe/www/EGMDQM/{year}/plots_filter_eff"

    f = ROOT.TFile(infile)
    for region in ["EB", "EE", "EBplus", "EBminus", "EEplus", "EEminus"]:
        hists = load_histograms(f, region)
        effs = compute_efficiencies(hists, region)
        draw_overlay(
            effs,
            f"{region}: Filter Efficiency vs Run",
            f"step_efficiency_{region}.png",
            outdir
        )
    f.Close()
