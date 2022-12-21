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

DEFAULT_PALETTE = [1, ROOT.kRed - 7, ROOT.kAzure + 5, ROOT.kGreen-2,  ROOT.kMagenta+1, ROOT.kYellow]
DEFAULT_STYLES = [0, 1001, 3004,  3005, 3009, 3006]
""" Default color pallette and draw style for ROOT.

"""


class Plotter(ClassLoggingMixin):
    """ Experimental Plotter class

    This function serves the purpose to create a RooFit frame without the need to interface
    RooFit.

    Todo:
        * Adding plot pdf functionality

    """
    def __init__(self, pdf, observable=None, nbins=20):
        super(Plotter, self).__init__()
        self.pdf = pdf
        self.observable = observable if observable is not None else pdf.get_observable()
        self.frame = None
        self.create_frame()
        self.nbins = nbins

    def create_frame(self, title="Fit"):
        self.frame = self.pdf.get_observable().frame(ROOT.RooFit.Title(title), ROOT.RooFit.Bins(self.nbins))


def get_optimal_bin_size(n, round=True):
    """Helper function to calculate optimal binning

    This function calculates the optimal amount of bins for the number of events n.

    Args:
        n (int): number of events to be binned
        round (bool or int): Round to
    Returns:
        (int): Optimal number of bins

    """

    def roundtobase(n, base=5):
        diff = n % base
        if diff <= base / 2.:
            return n - diff
        else:
            return n - diff + base

    n_opt = int(2 * n**(1/3.0))

    if round:
        base = 5
        if isinstance(round, int):
            base = round
        n_opt = roundtobase(n_opt, base)
    
    if n_opt == 0: 
        n_opt = 1

    return n_opt


def round_to_1(x):
    from math import log10, floor
    return round(x, -int(floor(log10(abs(x)))))


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

    ROOT.gStyle.SetFillColor(10)
    ROOT.gStyle.SetMarkerSize(0.8)
    ROOT.gStyle.SetLineColor(ROOT.kBlack)
    ROOT.gStyle.SetLineWidth(1)

    ROOT.gStyle.SetLegendBorderSize(0)


def fast_plot(model, data, observable, filename, components=None, nbins=None, extra_info=None,  size=1280,
              average=True, pi_label=False, font_scale=1.0, label_scale=1.0,
              legend=False, extra_text=None, round_bins=5, tick_len=30, model_range="Full",
              color_cycle=DEFAULT_PALETTE, fill_cycle=DEFAULT_STYLES, lw=2, line_shade=0, legend_data_name="Data", legend_fit_name="Fit",
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
            Extra text to be drawn on the plot
        round_bins (int) :
            magic to for automatically choosing the bin numbers
        tick_len (int) :
            Sets the length of the bins, EQUALLY (yes root. this is possible.), choose between 0-100
        legend_data_name (str):
            Name of the data part in the fit plot
        legend_fit_name (str):
            name of the total fit in the plot

    Todo:
        * Change or remove extra_info
    """
    
    set_root_style(font_scale, label_scale)

    nbins = get_optimal_bin_size(data.numEntries(), round_bins) if nbins is None else nbins
    if isinstance(data, ROOT.RooDataHist):
        nbins = observable.getBins()

    frame = observable.frame(ROOT.RooFit.Title("Fit Result"), ROOT.RooFit.Bins(nbins))
    if isinstance(legend, list):
        assert len(legend) == 4, "Please provide four coordinates for the legend"
        leg = ROOT.TLegend(*legend)
    elif legend == "top left":
        leg = ROOT.TLegend(0.16, 0.78, 0.39, 0.92)
    else:
        leg = ROOT.TLegend(0.7, 0.78, 0.93, 0.92)

    data.plotOn(frame, ROOT.RooFit.Name("Data"), ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))
    leg.AddEntry(frame.findObject("Data"), legend_data_name, "LEP")

    model.plotOn(frame, ROOT.RooFit.Name("Model"), ROOT.RooFit.LineColor(color_cycle[0]), ROOT.RooFit.Range(model_range))
    leg.AddEntry(frame.findObject("Model"), legend_fit_name, "L")

    if components is not None:
        n_col = 1
        for c, ni in components:
            c.plotOn(frame,
                     ROOT.RooFit.LineColor(color_cycle[n_col] + line_shade),
                     ROOT.RooFit.Normalization(ni, 2),
                     ROOT.RooFit.FillColor(color_cycle[n_col]),
                     ROOT.RooFit.FillStyle(fill_cycle[n_col]),
                     ROOT.RooFit.Name(c.GetName()),
                     ROOT.RooFit.DrawOption("F"),
                     ROOT.RooFit.VLines(), # if your pdf happens to not end on a point=0 you have to add this - obviously
                     ROOT.RooFit.Range(model_range),
                     )
            leg.AddEntry(frame.findObject(c.GetName()), c.getTitle().Data())
            c.plotOn(frame,
                     ROOT.RooFit.LineColor(color_cycle[n_col] + line_shade),
                     ROOT.RooFit.Normalization(ni, 2),
                     ROOT.RooFit.FillColor(color_cycle[n_col]),
                     ROOT.RooFit.LineWidth(lw),
                     ROOT.RooFit.Range(model_range),
                     )  # ROOT.RooFit.DrawOption("F")) #4050

            n_col += 1

    model.plotOn(frame, ROOT.RooFit.Name("Model"), ROOT.RooFit.LineColor(color_cycle[0]))
    data.plotOn(frame, ROOT.RooFit.Name("Data"), ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))

    # Create Canvas
    canvas = ROOT.TCanvas("plot", "plot", size, size)
    canvas.Divide(1, 2)
    canvas.GetPad(1).SetPad(0.0, 0.25, 1, 1)
    canvas.GetPad(1).SetBottomMargin(0.02)
    canvas.GetPad(1).SetRightMargin(0.05)
    canvas.GetPad(1).SetTicks(1, 1)
    canvas.GetPad(2).SetPad(0.0, 0.0, 1, 0.25)
    canvas.GetPad(2).SetBottomMargin(0.36)
    canvas.GetPad(2).SetTopMargin(0.0)
    canvas.GetPad(2).SetRightMargin(0.05)
    canvas.GetPad(2).SetTicks(1, 1)

    # Pi label because of...
    if pi_label:
        pifactor = 1 if observable.getMax() > 1.9 else 2
        ylabel = "Events / ( %.2f #pi rad )" % (1.0 / float(pifactor * nbins))
        frame.SetYTitle(ylabel)
    else:
        obs_range = round_to_1(observable.getMax() - observable.getMin())  # stupid overflow artefacts
        div = round(nbins/obs_range)
        # print(div,obs_range,numbins)
        unit = observable.getUnit()
        if unit is not None or unit is not "":
            ylabel = "Events / ( %s / %d )" % (observable.getUnit(), div)
            # frame.SetYTitle(ylabel)

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

    hist_pulls = ROOT.TH1F("hist_pulls", "hist pulls", pulls.GetN(),
                           # pulls.GetXaxis().GetXmin(), pulls.GetXaxis().GetXmax())
                           observable.getMin(model_range), observable.getMax(model_range))
    # hist_pulls = ROOT.TH1F("hist_pulls", "hist pulls", nbins,
    #                        observable.getMin("full_range"), observable.getMax("full_range"))

    pull_values = pulls.GetY()
    xerr = (observable.getMax("full_range") - observable.getMin("full_range")) / (2. * nbins)  # numbins

    for i in range(pulls.GetN()):
        hist_pulls.SetBinContent(i + 1, pull_values[i])
        pulls.SetPointEXlow(i, xerr)
        pulls.SetPointEXhigh(i, xerr)

        pulls.SetPointEYlow(i, 0)
        pulls.SetPointEYhigh(i, 0)
        
    pulls.SetMarkerSize(0)
    plot_pulls.addPlotable(pulls, "PE1")

    # Messy
    plot_pulls.GetYaxis().SetTitle("Pull")
    plot_pulls.GetYaxis().CenterTitle()
    plot_pulls.GetXaxis().SetTitleSize(0.18)
    plot_pulls.GetYaxis().SetTitleSize(0.18)
    plot_pulls.GetYaxis().SetTitleOffset(0.39)
    plot_pulls.GetXaxis().SetTitleOffset(.82)
    # plot_pulls.GetXaxis().SetTitleOffset(0.2)
    plot_pulls.GetXaxis().SetLabelSize(0.12 * label_scale)
    plot_pulls.GetYaxis().SetLabelSize(0.12 * label_scale)
    # plot_pulls.GetYaxis().SetLabelOffset(0.0)
    plot_pulls.GetYaxis().SetLabelOffset(0.006)
    # plot_pulls.GetXaxis().SetLabelOffset(0.06)
    plot_pulls.GetXaxis().SetTickLength(plot_pulls.GetXaxis().GetTickLength() * 3.0)
    plot_pulls.GetYaxis().SetNdivisions(505)

    ### Equal sized ticks!!
    pad1 = canvas.GetPad(1)
    pad2 = canvas.GetPad(2)

    pad1W = pad1.GetWw() * pad1.GetAbsWNDC()
    pad1H = pad1.GetWh() * pad1.GetAbsHNDC()
    pad2W = pad2.GetWw() * pad2.GetAbsWNDC()
    pad2H = pad2.GetWh() * pad2.GetAbsHNDC()

    # print(pad1W, pad1H, pad2W, pad2H)

    frame.SetTickLength(tick_len/pad1W, "Y")
    frame.SetTickLength(tick_len/pad1H, "X")

    plot_pulls.SetTickLength(tick_len/pad1H, "Y")
    plot_pulls.SetTickLength(tick_len/pad2H, "X")

    frame.GetXaxis().SetLabelOffset(999)
    frame.GetXaxis().SetLabelSize(0)

    # set reasonable limits for the pull plots
    if hist_pulls.GetMaximum() > 3.5 or hist_pulls.GetMinimum() < -3.5:
        plot_pulls.SetMinimum(-5.5)
        plot_pulls.SetMaximum(5.5)
    else:
        plot_pulls.SetMinimum(-3.5)
        plot_pulls.SetMaximum(3.5)
    plot_pulls.SetMarkerStyle(6)
    plot_pulls.SetMarkerSize(0)
    plot_pulls.SetMarkerColor(1)  # This has to be the worst solution
    plot_pulls.Draw("")
    if model_range is "Full":
        hist_pulls.SetFillColor(33)
        hist_pulls.SetLineColor(33)
        hist_pulls.Draw("HISTsame")
    plot_pulls.Draw("Xsame")
    print("ttttteeessdst")
    line = ROOT.TLine(observable.getMin('Full'), 0, observable.getMax("Full"), 0)
    line.SetLineColor(1)
    line.SetLineStyle(2)
    line.Draw("same")

    if extra_text is not None:
        canvas.cd(1)
        if hasattr(extra_text, "Draw"):
            extra_text.Draw("Same")
        if isinstance(extra_text, list):
            for txt in extra_text:
                assert hasattr(txt, "Draw"), "Please provide extra_txt with as a ROOT object with Draw method"
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


def get_norm (nbins, N):
    """ Returns normalistion that should be used for a PDF against a dataset of N entries, with nbins.
    Args:
        nbins(int): number of bins that data is binned in
        N (int): number of entries in dataset
    Returns:
        norm (float): normalisation
    """
    return N/nbins


def plot_as_pyplot(pdf, dataset, n_bins=50, dataset_name = 'Data',fit_name = 'Fit', x_name = "data", y_name = "Entries", unit = "", figsize=None, hatches=None, fcs=None):
    """ Plots the PDF against the dataset using matplotlib.pyplot libraries
    Args:
       pdf(pyroofit.pdf.PDF): the fitted pdf to plot against a dataset
       dataset(array-like): the dataset used to train the PDF
       n_bins(int): number of bins for the dataset
       dataset_name (string): name of the dataset that will appear on the legend, default = "Data"
       fit_name (string): name of the fit that will appear on the legend, default = "Fit"
       x_name (string): title of the x axis, default = "data"
       y_name (string): first part of y axis title, appears as y_name/(bin_width unit), default = "Entries"
       unit (string): the unit to appear on x and y axes, default = ""
       figsize (tuple of float,float): size of plot as (fig_width,fig_height), if None, then (13,8.03), default = None
       hatches (list of hatch patterns): list for hatches to be used (filling patterns for components)
       fcs (list of fill colors): list for facecolors to be used (fills for components)
       figsize (tuple of float,float): size of plot as (fig_width,fig_height), if None, then (13,8.03), default = None
    Returns:
       fig (Figure): matplotlib figure object
       ax, ax_pull (array of axes.Axes): first axis contains the data/pdf plot, the second contains the pull distribution 

    """
    import matplotlib.pyplot as plt
    import  numpy as np

    # Define golden ratio for sizes
    golden = (1 + 5 ** 0.5) / 2

    STYLES_facecolor = fcs if fcs else [None, 'none', 'none', 'none', 'none', 'none']
    STYLES_hatches = hatches if hatches else [None, '///', r"\\\ ",  'xxx', '--', '++', 'o', ".+", 'xx', '//', '*',  'O', '.']

    fig, (ax, ax_pull) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [golden**2,1], 'hspace':0.05}, figsize=figsize)
    # Plot the dataset and figure out the normalisation

    y, x = np.histogram(dataset,bins=n_bins)
    err = (-0.5 + np.sqrt(np.array(y + 0.25)), +0.5 + np.sqrt(np.array(y + 0.25)))
    bin_centers = (x[1:] + x[:-1]) / 2.0
    ax.errorbar(bin_centers,y,err, color='black', label=dataset_name, fmt='o',markersize=2)
    norm = get_norm(len(bin_centers),len(dataset))

    # Plot total fit
    ax.plot(*pdf.get_curve(norm=norm), color='black', label=fit_name)

    # Plot separate contributions
    curves = pdf.get_components_curve(norm=norm)
    for count,c in enumerate(curves):
        current_hatch = STYLES_hatches[count] if count<len(STYLES_hatches)-1 else 'none'
        current_fc = STYLES_facecolor[count] if count<len(STYLES_facecolor)-1 else 'none'
        current_color = next(ax._get_lines.prop_cycler)["color"]
        ax.plot(*curves[c], color = current_color)
        ax.fill_between(*curves[c], alpha=0.5,
                        hatch     = current_hatch,
                        facecolor = current_fc,
                        edgecolor = current_color,
                        label=c)

    # Calculate pull distribution
    bin_hwidth = np.array([(bin_centers[1] - bin_centers[0])*0.5]*len(bin_centers))

    pulls = -(np.interp(bin_centers,*pdf.get_curve(norm=norm)) - y) / (y)**0.5

    #Draw pull distribution and color area under each
    line,caps,_ = ax_pull.errorbar(bin_centers,pulls, xerr = bin_hwidth,
                     fmt='ko',
                     markersize=3,
                     ecolor = 'black')
    ax_pull.bar(bin_centers,pulls,width=bin_hwidth*2,color='gray',alpha=0.5)


    #Decorations, titles, ranges and names
    # Plot legend
    ax.legend(loc='best')
    hfont = {'fontname':'sans-serif'}
    #Setlimits
    ax.set_xlim(min(dataset),max(dataset))
    ax.set_ylim(0,)

    ax_pull.set_xlim(min(dataset),max(dataset))
    ylim = max(abs(min(pulls)*1.1),abs(max(pulls)*1.1))
    ax_pull.set_ylim(-ylim,ylim)

    #Set labels
    ax.set_xticklabels([])
    ax.set_ylabel(f'{y_name} / ( {bin_hwidth[0]:.1g} {unit})',**hfont)

    ax_pull.set_ylabel('Pull',**hfont)
    ax_pull.set_xlabel(f'{x_name}, {unit}',**hfont)
    ax_pull.tick_params(which = 'both', top=True, right=True)
    ax.tick_params(which = 'both',top=True, right=True)

    fig.align_ylabels((ax,ax_pull))

    return fig, (ax, ax_pull)
