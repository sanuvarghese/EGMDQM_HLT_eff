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
        total_eff.SetMarkerStyle(22)
        total_eff.SetTitle("Total")
        effs.append(("Total", total_eff))

    return effs

def draw_overlay(effs, title, outname):
    c = ROOT.TCanvas("c", "", 1000, 700)
    c.SetRightMargin(0.2)

    pad = ROOT.TPad("pad", "", 0.0, 0.0, 0.85, 1.0)
    pad.SetBottomMargin(0.12)
    pad.Draw()
    pad.cd()
    c._pad = pad

    y_min = 1.0
    for _, h in effs:
        for b in range(1, h.GetNbinsX() + 1):
            val = h.GetBinContent(b)
            if val > 0 and val < y_min:
                y_min = val

    for i, (label, h) in enumerate(effs):
        h.SetMinimum(y_min * 0.9)
        h.SetMaximum(1.04)
        h.SetTitle(title)
        h.GetXaxis().SetTitle("Run")
        h.GetYaxis().SetTitle("Filter Efficiency")
        h.GetXaxis().SetTitleOffset(1.2)
        h.GetYaxis().SetTitleOffset(1.3)
        h.GetXaxis().SetLabelSize(0.04)
        h.GetYaxis().SetLabelSize(0.04)
        h.Draw("E SAME" if i else "E")

    # Annotations
    region = outname.split("_")[-1].replace(".png", "")
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.035)
    latex.SetTextColor(ROOT.kViolet + 1)
    latex.DrawLatex(0.15, 0.87, "{HLT_Ele32_WPTight_Gsf} (from HLT DQM T&P)")

    # region_latex = {
    #     "EB": "|#eta^{HLT}(e)| < 1.5,  p_{T}^{HLT}(e) > 32 GeV",
    #     "EE": "|#eta^{HLT}(e)| > 1.5,  p_{T}^{HLT}(e) > 32 GeV",
    #     "EBplus": "#eta^{HLT}(e) > 0,  |#eta| < 1.5,  p_{T}^{HLT}(e) > 32 GeV",
    #     "EBminus": "#eta^{HLT}(e) < 0,  |#eta| < 1.5,  p_{T}^{HLT}(e) > 32 GeV",
    #     "EEplus": "#eta^{HLT}(e) > 1.5,  p_{T}^{HLT}(e) > 32 GeV",
    #     "EEminus": "#eta^{HLT}(e) < -1.5,  p_{T}^{HLT}(e) > 32 GeV"
    # }
    #latex.DrawLatex(0.15, 0.86, region_latex.get(region, ""))

    # Legend
    c.cd()
    legend = ROOT.TLegend(0.76, 0.25, 0.99, 0.95)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.SetTextSize(0.03)
    for label, h in effs:
        legend.AddEntry(h, label, "l")
    legend.Draw()

    outdir = "/eos/user/s/savarghe/www/EGMDQM/2025/plots_filter_eff"
    os.makedirs(outdir, exist_ok=True)
    c.SaveAs(f"{outdir}/{outname}")
    print(f"Saved: {outdir}/{outname}")

# --- Main ---
f = ROOT.TFile("out_barrelendcaps_new.root")
for region in ["EB", "EE", "EBplus", "EBminus", "EEplus", "EEminus"]:
    hists = load_histograms(f, region)
    effs = compute_efficiencies(hists, region)
    draw_overlay(
        effs,
        f"{region}: Filter Efficiency vs Run",
        f"step_efficiency_{region}.png"
    )
f.Close()
