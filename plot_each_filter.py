import ROOT
import os
import argparse

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gErrorIgnoreLevel = ROOT.kWarning
ROOT.gErrorIgnoreLevel = ROOT.kError
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
    ROOT.kViolet + 1, ROOT.kOrange + 3, ROOT.kMagenta + 2, ROOT.kAzure + 2,
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

    g = ROOT.TGraphAsymmErrors()
    g.BayesDivide(num, denom)
    # Shift X points back by 0.5 to align with integer run numbers
    for j in range(g.GetN()):
        x = g.GetX()[j]
        y = g.GetY()[j]
        ex_low = g.GetErrorXlow(j)
        ex_high = g.GetErrorXhigh(j)
        ey_low = g.GetErrorYlow(j)
        ey_high = g.GetErrorYhigh(j)
        g.SetPoint(j, x - 0.5, y)
        g.SetPointEXlow(j, ex_low)
        g.SetPointEXhigh(j, ex_high)
        g.SetPointEYlow(j, ey_low)
        g.SetPointEYhigh(j, ey_high)

    g.SetName(f"g_{region_label}_{i}")
    g.SetLineWidth(3)
    g.SetMarkerStyle(20)
    g.SetMarkerSize(1.1)
    g.SetMarkerColor(colors[i % len(colors)])
    g.SetLineColor(colors[i % len(colors)])

    # Trend
    yvals = [g.GetY()[j] for j in range(g.GetN()) if g.GetY()[j] > 0]
    first = yvals[:5]
    last = yvals[-5:]
    delta = (sum(last) / len(last)) - (sum(first) / len(first)) if first and last else 0

    label = short_label(filters[i])
    # if delta > 0.01:
    #     label += " (up)"
    # elif delta < -0.01:
    #     label += " (down)"

    return g, label, delta

def draw_single(graph, label, region, i):
    if not graph:
        return

    c = ROOT.TCanvas("c", "", 1000, 700)
    c.SetRightMargin(0.1)

    pad = ROOT.TPad("pad", "", 0.0, 0.0, 1.0, 1.0)
    pad.SetBottomMargin(0.12)
    pad.Draw()
    pad.cd()

    # Y-axis range
    y_min = 1.0
    y_max = 0.0
    for b in range(graph.GetN()):
        y = graph.GetY()[b]
        yerr = graph.GetErrorYhigh(b)
        if y > 0 and y < y_min:
            y_min = y
        if y + yerr > y_max:
            y_max = y + yerr

    graph.SetMinimum(y_min * 0.95)
    graph.SetMaximum(y_max * 1.02)
    graph.SetTitle(f"{region}: {label} Filter Efficiency vs Run") 
    graph.GetXaxis().SetTitle("Run")
    graph.GetYaxis().SetTitle("Step Efficiency")
    graph.GetXaxis().SetTitleOffset(1.2)
    graph.GetYaxis().SetTitleOffset(1.3)

    graph.Draw("AP")
    # Get latest run
    latest_run = int(max([graph.GetX()[j] for j in range(graph.GetN())]))
    

    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.035)
    latex.SetTextColor(ROOT.kBlack)
    latex.DrawLatex(0.15, 0.87, "{HLT_Ele32_WPTight_Gsf} (from HLT DQM T&P)")
    latex.DrawLatex(0.10, 0.03, f"#it{{Updated till Run {latest_run}}}")
    c.cd()
    leg = ROOT.TLegend(0.15, 0.18, 0.34, 0.29)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetTextSize(0.035)
    leg.AddEntry(graph, label, "p")
    leg.Draw()

    outdir = f"/eos/user/s/savarghe/www/EGMDQM/{args.year}/plots_step_eff_single"
    os.makedirs(outdir, exist_ok=True)
    cname = f"{outdir}/{region}_{short_label(filters[i])}.png"
    c.SaveAs(cname)
    c.SaveAs(cname.replace(".png", ".pdf"))  # Save PDF
    # Also save the graph to a ROOT file
    rootname = f"{outdir}/{region}_{short_label(filters[i])}.root"
    fout = ROOT.TFile.Open(rootname, "RECREATE")
    graph.Write()
    fout.Close()
    if not args.quiet:
        print(f"Saved: {cname}")

if __name__ == "__main__":
    year = args.year
    infile = f"out_barrelendcaps_{year}.root"
    f = ROOT.TFile.Open(infile)

    for region in ["EB", "EE", "EBplus", "EBminus", "EEplus", "EEminus"]:
        histos = load_histograms(f, region)
        for i in range(1, len(filters)):
            graph, label, delta = compute_single_efficiency(histos, i, region)
            draw_single(graph, label, region, i)

    f.Close()
