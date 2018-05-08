# -*- coding: utf-8 -*-
""" Plot function for the PDF class..

    This is displays the full ugliness of ROOT.
    It should serve as a reminder for future generations to create better software.

"""
from __future__ import print_function

import ROOT


def get_optimal_bin_size(n):
    """
    This function calculates the optimal amount of bins for the number of events n.
    :param      n:  number of Events
    :return:        optimal bin size

    """
    return int(2 * n**(1/3.0))


def set_root_style(font_scale=1.0, label_scale=1.0):
    """  Setting a general style that one can look at plots without getting eye-cancer.

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


def pull_plot(model, data, z, filename, pdf_sig=None, pdf_bkg=None, pdf_filled=None,
              nbins=None, data_bkg=None, extra_info=None,
              color_sig=ROOT.kRed - 7, color_bkg=ROOT.kAzure + 5, line_color_sig=ROOT.kRed + 2,
              line_color_bkg=ROOT.kAzure - 1, fill_style_sig=1001,
              fill_style_bkg=3354, lw=2, size=1280, average=True, pi_label=False, font_scale=1.0, label_scale=1.0):
    """

        Yes this is only one large function doing all the magic stuff :/

    Args:
        model:
        data:
        z:
        filename:
        pdf_sig:
        pdf_bkg:
        pdf_filled:
        nbins:
        data_bkg:
        extra_info:
        color_sig:
        color_bkg:
        line_color_sig:
        line_color_bkg:
        fill_style_sig:
        fill_style_bkg:
        lw:
        size:
        average (bool): Integrate over the bin for the pull
        pi_label: change the label int divisions of pi

    Returns:

    """
    set_root_style(font_scale, label_scale)

    numbins = get_optimal_bin_size(data.numEntries()) if nbins is None else nbins
    frame = z.frame(ROOT.RooFit.Title("Fit Result"), ROOT.RooFit.Bins(numbins))

    data.plotOn(frame, ROOT.RooFit.Name("Data"), ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))
    model.plotOn(frame, ROOT.RooFit.Name("Model"), ROOT.RooFit.LineColor(1))

    if pdf_sig is not None:
        pdf_sig[0].plotOn(frame, ROOT.RooFit.LineColor(color_sig),
                          ROOT.RooFit.Normalization(pdf_sig[1], 2),
                          ROOT.RooFit.FillColor(color_sig), ROOT.RooFit.FillStyle(fill_style_sig),
                          #ROOT.RooFit.LineWidth(5),
                          ROOT.RooFit.DrawOption("F"))
        pdf_sig[0].plotOn(frame, ROOT.RooFit.LineColor(line_color_sig),
                          ROOT.RooFit.Normalization(pdf_sig[1], 2), ROOT.RooFit.FillColor(46),
                          ROOT.RooFit.LineWidth(lw), )# ROOT.RooFit.DrawOption("F")) #4050
    if pdf_bkg is not None:
        pdf_bkg[0].plotOn(frame, ROOT.RooFit.LineColor(color_bkg),
                          ROOT.RooFit.Normalization(pdf_bkg[1], 2),
                          ROOT.RooFit.FillColor(color_bkg), ROOT.RooFit.FillStyle(fill_style_bkg),
                          ROOT.RooFit.LineWidth(0), ROOT.RooFit.DrawOption("F"),
                          #ROOT.RooFit.FillStyle(3008), ROOT.RooFit.FillColor(2), ROOT.RooFit.VLines(), ROOT.RooFit.DrawOption("F")
                          )
        pdf_bkg[0].plotOn(frame, ROOT.RooFit.LineColor(line_color_bkg), ROOT.RooFit.LineStyle(2),
                          ROOT.RooFit.Normalization(pdf_bkg[1], 2),
                          ROOT.RooFit.FillColor(color_bkg),
                          ROOT.RooFit.LineWidth(lw),
                          #ROOT.RooFit.FillStyle(3008), ROOT.RooFit.FillColor(2), ROOT.RooFit.VLines(), ROOT.RooFit.DrawOption("F")
                          )
    if data_bkg is not None:
        data_bkg.plotOn(frame, ROOT.RooFit.MarkerColor(36), ROOT.RooFit.LineColor(36))

    if pdf_filled is not None:
        pdf_filled.plotOn(frame, ROOT.RooFit.LineColor(color_bkg),
                          ROOT.RooFit.FillColor(color_bkg), ROOT.RooFit.FillStyle(fill_style_bkg),
                          ROOT.RooFit.LineWidth(0), ROOT.RooFit.DrawOption("F"),
                          #ROOT.RooFit.FillStyle(3008), ROOT.RooFit.FillColor(2), ROOT.RooFit.VLines(), ROOT.RooFit.DrawOption("F")
                          )

    model.plotOn(frame, ROOT.RooFit.Name("Model"), ROOT.RooFit.LineColor(1))
    data.plotOn(frame, ROOT.RooFit.Name("Data"), ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))

    # Create Canvas
    canvas = ROOT.TCanvas("plot", "plot", size, size)
    canvas.Divide(1, 2)
    canvas.GetPad(1).SetPad(0.0, 0.25, 1, 1)
    canvas.GetPad(1).SetBottomMargin(0.05)
    canvas.GetPad(1).SetRightMargin(0.05)
    canvas.GetPad(2).SetPad(0.0, 0.0, 1, 0.25)
    canvas.GetPad(2).SetBottomMargin(0.32)
    canvas.GetPad(2).SetRightMargin(0.05)

    # Pi label because of Ishikawa-san..
    if pi_label:
        pifactor = 1 if z.getMax() > 1.9 else 2
        ylabel = "Events / ( %.2f #pi rad )"%(1.0/float(pifactor*numbins))
        frame.SetYTitle(ylabel)

    # Draw All The Stuff
    canvas.cd(1)
    frame.Draw()

    # Draw Pull
    canvas.cd(2)
    pulls = frame.pullHist("Data", "Model", average)
    plot_pulls = z.frame(ROOT.RooFit.Name("Pull_distribution"),
                         ROOT.RooFit.Title("Pull distribution"),
                         ROOT.RooFit.Range("full_range"))

    hist_pulls =  ROOT.TH1F("hist_pulls", "hist pulls", numbins,
                            z.getMin("full_range"), z.getMax("full_range"))
    pull_values = pulls.GetY()
    xerr = (z.getMax("full_range") - z.getMin("full_range")) / (2. * numbins) #numbins
    for i in range(numbins):
        hist_pulls.SetBinContent(i + 1, pull_values[i])
        pulls.SetPointEXlow(i, xerr)
        pulls.SetPointEXhigh(i, xerr)

    plot_pulls.addPlotable(pulls, "PE1")
    # Messy shit
    plot_pulls.GetYaxis().SetTitle("Pull")
    plot_pulls.GetYaxis().CenterTitle()
    plot_pulls.GetXaxis().SetTitleSize(0.18)
    plot_pulls.GetYaxis().SetTitleSize(0.18)
    plot_pulls.GetYaxis().SetTitleOffset(0.39)
    plot_pulls.GetXaxis().SetTitleOffset(0.74)
    #plot_pulls.GetXaxis().SetTitleOffset(0.2)
    plot_pulls.GetXaxis().SetLabelSize(0.12*label_scale)
    plot_pulls.GetYaxis().SetLabelSize(0.12*label_scale)
    #plot_pulls.GetYaxis().SetLabelOffset(0.0)
    plot_pulls.GetYaxis().SetLabelOffset(0.006)
    #plot_pulls.GetXaxis().SetLabelOffset(0.06)
    plot_pulls.GetXaxis().SetTickLength(plot_pulls.GetXaxis().GetTickLength() * 3.0)
    plot_pulls.GetYaxis().SetNdivisions(505)
    # set reasonable limits for the pull plots
    if (hist_pulls.GetMaximum() > 3.5 or hist_pulls.GetMinimum() < -3.5):
        plot_pulls.SetMinimum(-5.5)
        plot_pulls.SetMaximum(5.5)
    else:
        plot_pulls.SetMinimum(-3.5)
        plot_pulls.SetMaximum(3.5)

    plot_pulls.Draw("")
    hist_pulls.SetFillColor(33)
    hist_pulls.SetLineColor(33)
    hist_pulls.Draw("HISTsame")
    plot_pulls.Draw("same")

    if extra_info is not None:
        canvas.cd(1)
        box = ROOT.TPaveText(0.2, 0.75, 0.4, 0.9, "NDC")
        box.SetFillColor(10)
        box.SetBorderSize(0)
        box.SetTextAlign(12)
        box.SetTextSize(0.04)
        box.SetFillStyle(1001)
        box.SetFillColor(10)
        for info in extra_info:
            print(info)
            try:
                box.AddText(info[0]+' = %.2f #pm %.2f' % (info[1], info[2]))
            except IndexError:
                print("NO no no")

        box.Draw("same")

    canvas.SaveAs(filename)


color_palette = [ROOT.kRed - 7, ROOT.kAzure + 5, ROOT.kMagenta+1, ROOT.kGreen-2, ROOT.kYellow]
fill_styles = [1001, 3004,  3005, 3009, 3006]
def pull_plot2(model, data, z, filename, components=None,
                  nbins=None, data_bkg=None, extra_info=None,
                  color_sig=ROOT.kRed - 7, color_bkg=ROOT.kAzure + 5, line_color_sig=ROOT.kRed + 2,
                  line_color_bkg=ROOT.kAzure - 1, fill_style_sig=1001,
                  fill_style_bkg=3354, lw=2, size=1280, average=True, pi_label=False, font_scale=1.0, label_scale=1.0):


    """

        Yes this is only one large function doing all the magic stuff :/

    Args:
        model:
        data:
        z:
        filename:
        pdf_sig:
        pdf_bkg:
        pdf_filled:
        nbins:
        data_bkg:
        extra_info:
        color_sig:
        color_bkg:
        line_color_sig:
        line_color_bkg:
        fill_style_sig:
        fill_style_bkg:
        lw:
        size:
        average (bool): Integrate over the bin for the pull
        pi_label: change the label int divisions of pi

    Returns:

    """
    set_root_style(font_scale, label_scale)

    numbins = get_optimal_bin_size(data.numEntries()) if nbins is None else nbins
    frame = z.frame(ROOT.RooFit.Title("Fit Result"), ROOT.RooFit.Bins(numbins))

    data.plotOn(frame, ROOT.RooFit.Name("Data"), ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))
    model.plotOn(frame, ROOT.RooFit.Name("Model"), ROOT.RooFit.LineColor(1))

    n_col = 0
    for c, ni in components:
        c.plotOn(frame,
                 ROOT.RooFit.LineColor(color_palette[n_col]+1),
                 ROOT.RooFit.Normalization(ni, 2),
                 ROOT.RooFit.FillColor(color_palette[n_col]),
                 ROOT.RooFit.FillStyle(fill_styles[n_col]),
                 ROOT.RooFit.DrawOption("F"))

        c.plotOn(frame,
                 ROOT.RooFit.LineColor(color_palette[n_col]+1),
                 ROOT.RooFit.Normalization(ni, 2),
                 ROOT.RooFit.FillColor(color_palette[n_col]),
                 ROOT.RooFit.LineWidth(lw), )  # ROOT.RooFit.DrawOption("F")) #4050

        n_col += 1


    model.plotOn(frame, ROOT.RooFit.Name("Model"), ROOT.RooFit.LineColor(1))
    data.plotOn(frame, ROOT.RooFit.Name("Data"), ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))

    # Create Canvas
    canvas = ROOT.TCanvas("plot", "plot", size, size)
    canvas.Divide(1, 2)
    canvas.GetPad(1).SetPad(0.0, 0.25, 1, 1)
    canvas.GetPad(1).SetBottomMargin(0.05)
    canvas.GetPad(1).SetRightMargin(0.05)
    canvas.GetPad(2).SetPad(0.0, 0.0, 1, 0.25)
    canvas.GetPad(2).SetBottomMargin(0.32)
    canvas.GetPad(2).SetRightMargin(0.05)

    # Pi label because of Ishikawa-san..
    if pi_label:
        pifactor = 1 if z.getMax() > 1.9 else 2
        ylabel = "Events / ( %.2f #pi rad )" % (1.0 / float(pifactor * numbins))
        frame.SetYTitle(ylabel)

    # Draw All The Stuff
    canvas.cd(1)
    frame.Draw()

    # Draw Pull
    canvas.cd(2)
    pulls = frame.pullHist("Data", "Model", average)
    plot_pulls = z.frame(ROOT.RooFit.Name("Pull_distribution"),
                         ROOT.RooFit.Title("Pull distribution"),
                         ROOT.RooFit.Range("full_range"))

    hist_pulls = ROOT.TH1F("hist_pulls", "hist pulls", numbins,
                           z.getMin("full_range"), z.getMax("full_range"))
    pull_values = pulls.GetY()
    xerr = (z.getMax("full_range") - z.getMin("full_range")) / (2. * numbins)  # numbins
    for i in range(numbins):
        hist_pulls.SetBinContent(i + 1, pull_values[i])
        pulls.SetPointEXlow(i, xerr)
        pulls.SetPointEXhigh(i, xerr)

    plot_pulls.addPlotable(pulls, "PE1")
    # Messy shit
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
    if (hist_pulls.GetMaximum() > 3.5 or hist_pulls.GetMinimum() < -3.5):
        plot_pulls.SetMinimum(-5.5)
        plot_pulls.SetMaximum(5.5)
    else:
        plot_pulls.SetMinimum(-3.5)
        plot_pulls.SetMaximum(3.5)

    plot_pulls.Draw("")
    hist_pulls.SetFillColor(33)
    hist_pulls.SetLineColor(33)
    hist_pulls.Draw("HISTsame")
    plot_pulls.Draw("same")

    if extra_info is not None:
        canvas.cd(1)
        box = ROOT.TPaveText(0.2, 0.75, 0.4, 0.9, "NDC")
        box.SetFillColor(10)
        box.SetBorderSize(0)
        box.SetTextAlign(12)
        box.SetTextSize(0.04)
        box.SetFillStyle(1001)
        box.SetFillColor(10)
        for info in extra_info:
            print(info)
            try:
                box.AddText(info[0] + ' = %.2f #pm %.2f' % (info[1], info[2]))
            except IndexError:
                print("NO no no")

        box.Draw("same")

    canvas.SaveAs(filename)


