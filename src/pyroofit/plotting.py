# -*- coding: utf-8 -*-
""" Plot function for the PDF class

Tools to make nice plots from RooFit pdfs.
The function fast_plot is used by the PDF class
to make default plots.

Todo:
    * Plotter class containing the RooFit frame
    * Equal length ticks
    * Provide matplolib functionality


"""
from __future__ import print_function
from .utilities import  ClassLoggingMixin
import ROOT


class Plotter(ClassLoggingMixin):
    """ Experimental Plotter class

    This function serves the purpose to create a RooFit frame without the need to interface
    RooFit.

    Todo:
        * Adding plot pdf functionality

    """
    def __init__(self, pdf):
        super(Plotter, self).__init__()
        self.pdf = pdf
        self.frame = None
        self.create_frame()

    def create_frame(self, title='', nbins=10):
        # if nbins is None:
        #     try:
        #         nbins = get_optimal_bin_size(pdf.last_data.num)
        self.frame = self.pdf.get_observable().frame(ROOT.RooFit.Title(title), ROOT.RooFit.Bins(nbins))


def get_optimal_bin_size(n):
    """Helper function to calculate optimal binning

    This function calculates the optimal amount of bins for the number of events n.

    Args:
        n (int): number of events to be binned

    Returns:
        (int): Optimal number of bins

    """
    return int(2 * n**(1/3.0))


def set_root_style(font_scale=1.0, label_scale=1.0):
    """  Setting a general style that one can look at plots without getting eye-cancer.

    Args:
        font_scale (float): Scale of the fonts
        label_scale (float): Scale of the labels

    Todo:
        * Absolute font size

    """
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetLabelSize(0.04*label_scale, "xy")
    ROOT.gStyle.SetLabelOffset(0.006, "y")
    ROOT.gStyle.SetTitleSize(0.06*font_scale, "xy")
    ROOT.gStyle.SetTitleOffset(0.9, "x")
    ROOT.gStyle.SetTitleOffset(1.15, "y")
    ROOT.gStyle.SetNdivisions(505, "x")

    ROOT.gStyle.SetPadLeftMargin(0.14)
    ROOT.gStyle.SetPadRightMargin(0.05)
    ROOT.gStyle.SetPadBottomMargin(0.12)
    ROOT.gStyle.SetPadTopMargin(0.05)

    ROOT.gStyle.SetFillColor(0)
    ROOT.gStyle.SetMarkerSize(0.8)
    ROOT.gStyle.SetLineColor(ROOT.kBlack)
    ROOT.gStyle.SetLineWidth(1)

    ROOT.gStyle.SetLegendBorderSize(0)


DEFAULT_PALETTE = [1, ROOT.kRed - 7, ROOT.kAzure + 5, ROOT.kMagenta+1, ROOT.kGreen-2, ROOT.kYellow]
DEFAULT_STYLES = [1001, 3004,  3005, 3009, 3006]
""" Default color pallette and draw style for ROOT.

"""


def fast_plot(model, data, observable, filename, components=None, nbins=None, extra_info=None, lw=2, size=1280,
              average=True, pi_label=False, font_scale=1.0, label_scale=1.0, color_cycle=DEFAULT_PALETTE,
              fill_cycle=DEFAULT_STYLES, line_shade=0, legend=False, extra_text=None,
              ):
    """ Generic plot function

    Args:
        model (RooAbsPDF):
            Fit model to be drawn
        data (RooDataSet):
            Dataset to be plotted
        observable (RooAbsVar):
            Observable to be drawn
        filename (str):
            Name of the output file. Suffix determines file type
        components (list of tuples):
            Normalisation and ROOT.RooAbsPDF to be drawn searately
        nbins (int):
            Number of bins
        extra_info (list or TPaveText):
        lw (int):
            Width of the line of the total fit model
        size (int):
            Plot size in pixels
        average (bool):
            Average bin content for calculating the pull distribution, if false, take central value
        pi_label (bool):
            Calculate the bin count in radians
        font_scale (float):
            Set relative font scale
        label_scale (float):
            Set relative lable scale
        color_cycle (list of ROOT.TColor):
            Overwrite for the default color cycle
        fill_cycle (list of ROOT.TAttrFill):
            Overwrite for the default fill cycle
        line_shade (int):
            Integer to add to the color cycle for the fill color
        legend (list):
            Vector with four coordinates for the TLegend position
        extra_text (list of ROOT.TPaveText or ROOT.TPaveText):
            Extra text to be drawn on the plor

    Todo:
        * Change or remove extra_info
    """
    
    set_root_style(font_scale, label_scale)

    numbins = get_optimal_bin_size(data.numEntries()) if nbins is None else nbins
    if isinstance(data, ROOT.RooDataHist):
        numbins = observable.getBins()

    frame = observable.frame(ROOT.RooFit.Title("Fit Result"), ROOT.RooFit.Bins(numbins))
    
    if isinstance(legend, list):
        assert len(legend) == 4, "Please provide four coordinates for the legend"
        leg = ROOT.TLegend(*legend)
    else:
        leg = ROOT.TLegend(0.7, 0.78, 0.93, 0.92)

    data.plotOn(frame, ROOT.RooFit.Name("Data"), ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))
    leg.AddEntry(frame.findObject("Data"), "Data", "LEP")

    model.plotOn(frame, ROOT.RooFit.Name("Model"), ROOT.RooFit.LineColor(color_cycle[0]))
    leg.AddEntry(frame.findObject("Model"), "Fit", "L")
    
    if components is not None:
        n_col = 1
        for c, ni in components:
            c.plotOn(frame,
                     ROOT.RooFit.LineColor(color_cycle[n_col]+line_shade),
                     ROOT.RooFit.Normalization(ni, 2),
                     ROOT.RooFit.FillColor(color_cycle[n_col]),
                     ROOT.RooFit.FillStyle(fill_cycle[n_col]),
                     ROOT.RooFit.Name(c.GetName()),
                     ROOT.RooFit.DrawOption("F"))
            leg.AddEntry(frame.findObject(c.GetName()), c.getTitle().Data())
            c.plotOn(frame,
                     ROOT.RooFit.LineColor(color_cycle[n_col]+line_shade),
                     ROOT.RooFit.Normalization(ni, 2),
                     ROOT.RooFit.FillColor(color_cycle[n_col]),
                     ROOT.RooFit.LineWidth(lw), )  # ROOT.RooFit.DrawOption("F")) #4050

            n_col += 1

    model.plotOn(frame, ROOT.RooFit.Name("Model"), ROOT.RooFit.LineColor(color_cycle[0]))
    data.plotOn(frame, ROOT.RooFit.Name("Data"), ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))
    
    # Create Canvas
    canvas = ROOT.TCanvas("plot", "plot", size, size)
    canvas.Divide(1, 2)
    canvas.GetPad(1).SetPad(0.0, 0.25, 1, 1)
    canvas.GetPad(1).SetBottomMargin(0.05)
    canvas.GetPad(1).SetRightMargin(0.05)
    canvas.GetPad(1).SetTicks(1, 1)
    canvas.GetPad(2).SetPad(0.0, 0.0, 1, 0.25)
    canvas.GetPad(2).SetBottomMargin(0.32)
    canvas.GetPad(2).SetRightMargin(0.05)
    canvas.GetPad(2).SetTicks(1, 1)

    # Pi label because of...
    if pi_label:
        pifactor = 1 if observable.getMax() > 1.9 else 2
        ylabel = "Events / ( %.2f #pi rad )" % (1.0 / float(pifactor * numbins))
        frame.SetYTitle(ylabel)

    # Draw All The Stuff
    canvas.cd(1)
    frame.Draw()
    if legend is not False:
        leg.Draw("same")
    
    # Draw Pull
    canvas.cd(2)
    pulls = frame.pullHist("Data", "Model", average)
    plot_pulls = observable.frame(ROOT.RooFit.Name("Pull_distribution"),
                                  ROOT.RooFit.Title("Pull distribution"),
                                  ROOT.RooFit.Range("full_range"))

    hist_pulls = ROOT.TH1F("hist_pulls", "hist pulls", numbins,
                           observable.getMin("full_range"), observable.getMax("full_range"))
    pull_values = pulls.GetY()
    xerr = (observable.getMax("full_range") - observable.getMin("full_range")) / (2. * numbins)  # numbins
    for i in range(numbins):
        hist_pulls.SetBinContent(i + 1, pull_values[i])
        pulls.SetPointEXlow(i, xerr)
        pulls.SetPointEXhigh(i, xerr)

        pulls.SetPointEYlow(i, 0)
        pulls.SetPointEYhigh(i, 0)

    plot_pulls.addPlotable(pulls, "PE1")
    # Messy
    plot_pulls.GetYaxis().SetTitle("Pull")
    plot_pulls.GetYaxis().CenterTitle()
    plot_pulls.GetXaxis().SetTitleSize(0.18)
    plot_pulls.GetYaxis().SetTitleSize(0.18)
    plot_pulls.GetYaxis().SetTitleOffset(0.39)
    plot_pulls.GetXaxis().SetTitleOffset(0.74)
    # plot_pulls.GetXaxis().SetTitleOffset(0.2)
    plot_pulls.GetXaxis().SetLabelSize(0.12 * label_scale)
    plot_pulls.GetYaxis().SetLabelSize(0.12 * label_scale)
    # plot_pulls.GetYaxis().SetLabelOffset(0.0)
    plot_pulls.GetYaxis().SetLabelOffset(0.006)
    # plot_pulls.GetXaxis().SetLabelOffset(0.06)
    plot_pulls.GetXaxis().SetTickLength(plot_pulls.GetXaxis().GetTickLength() * 3.0)
    plot_pulls.GetYaxis().SetNdivisions(505)
    # set reasonable limits for the pull plots
    if hist_pulls.GetMaximum() > 3.5 or hist_pulls.GetMinimum() < -3.5:
        plot_pulls.SetMinimum(-5.5)
        plot_pulls.SetMaximum(5.5)
    else:
        plot_pulls.SetMinimum(-3.5)
        plot_pulls.SetMaximum(3.5)
    plot_pulls.SetMarkerStyle(6)
    plot_pulls.SetMarkerColor(0)  # This has to be the worst soloution
    plot_pulls.Draw("")
    hist_pulls.SetFillColor(33)
    hist_pulls.SetLineColor(33)
    hist_pulls.Draw("HISTsame")
    plot_pulls.Draw("Xsame")

    if extra_text is not None:
        canvas.cd(1)
        if isinstance(extra_text, ROOT.TPaveText):
            extra_info.Draw("Same")
        if isinstance(extra_text, list):
            for txt in extra_text:
                assert isinstance(txt, ROOT.TPaveText), "Please provide extra_txt with a list or ROOT.TPaveText"
                txt.Draw("Same")

    if extra_info is not None:
        canvas.cd(1)
        if isinstance(extra_info, ROOT.TPaveText):
            extra_info.Draw("Same")
        else:
            assert isinstance(extra_info, list), "Please provide extra_info with a list or ROOT.TPaveText"
            box = ROOT.TPaveText(0.2, 0.75, 0.4, 0.9, "NDC")
            box.SetFillColor(10)
            box.SetBorderSize(0)
            box.SetTextAlign(12)
            box.SetTextSize(0.04)
            box.SetFillStyle(1001)
            box.SetFillColor(10)
            for info in extra_info:
                try:
                    if not isinstance(info, list):
                        if isinstance(info, ROOT.TPaveText):
                            info.Draw('same')
                        else:
                            info = [info]
                    if len(info) == 1:
                        box.AddText(info[0])
                    elif len(info) == 3:
                        box.AddText(info[0] + ' = %.2f #pm %.2f' % (info[1], info[2]))
                    else:
                        print("Could not add to legend ", info)
                except IndexError:
                    print("Something went wrong in plotting")

            box.Draw("same")

    canvas.SaveAs(filename)
