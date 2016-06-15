# -*- coding: utf-8 -*-
"""
Created on Sat Dec 20 21:47:44 2014

@author: jonau_000
"""
import sys, os
sys.path.append(os.getcwd())
from SciImport import BloodCount, BloodBiochem
import wx, csv, time
import xml.etree.ElementTree as ET
#include <wx/wx.h>

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)
        # Associate some events with methods of this class
        panel = wx.Panel(self, -1)
        lblFolder = wx.StaticText(panel, -1, "Folder path:")
        lblFiles = wx.StaticText(panel, -1, "Files list:")
        lblDate = wx.StaticText(panel, -1, "Exeriment start date\n DDMmmYYYY:")
        self.Messages = wx.TextCtrl(panel, -1, style = wx.TE_READONLY|wx.TE_MULTILINE, value = "Enter the data and\n click 'Extract ***'.")
        self.folder = wx.TextCtrl(panel, -1, style = wx.TE_LEFT)
        self.files = wx.TextCtrl(panel, -1, style = wx.TE_MULTILINE, size = (250, -1))
        self.Date = wx.TextCtrl(panel, -1, style = wx.TE_LEFT)
        self.CountSub = wx.Button(panel, -1, "Extract Blood Counts")
        self.CountSub.Bind(wx.EVT_BUTTON, self.ProcessBloodCounts)
        self.BiochemSub = wx.Button(panel, -1, "Extract Blood Biochemistry")
        self.BiochemSub.Bind(wx.EVT_BUTTON, self.ProcessBloodBiochem)
        self.panel = panel
        
        sizer = wx.FlexGridSizer(5, 2, 5, 5)
        sizer.Add(lblFolder)
        sizer.Add(self.folder)
        sizer.Add(lblFiles)
        sizer.Add(self.files)
        sizer.Add(lblDate)
        sizer.Add(self.Date)
        sizer.Add(self.CountSub)
        sizer.Add(self.BiochemSub)
        sizer.Add(self.Messages)

        border = wx.BoxSizer()
        border.Add(sizer, 0, wx.ALL, 15)
        panel.SetSizerAndFit(border)
        self.Fit()

    def ProcessBloodCounts(parent, event):
        folder = parent.folder.GetLineText(0)
        files_num = parent.files.GetNumberOfLines()
        startDate = parent.Date.GetLineText(0)
        counts = []
        counts.append(["Animal", "Date", "Day", "WBC", "LYM", "MON", "NEU", "EOS", "BAS", "LY%", "MO%", "NE%", "EO%", "BA%", "RBC", "HGB", "HCT", "MCV", "MCH", "MCHC", "RDWc", "PLT", "PCT", "MPV", "PDWc"])
        for i in range(files_num):
            counts.extend(BloodCount().ReadFile(folder, parent.files.GetLineText(i), startDate))
        outfile = open(os.path.join(folder, "BloodCounts.csv"), "w")
        writer = csv.writer(outfile, dialect = 'excel')
        parent.Messages.SetValue("Data read in.\nWait to finish writing...")
        wx.Yield()
        writer.writerows(counts)
        outfile.close()
        time.sleep(2)
        message = "Done! Wrote " + str(len(counts) - 1) + " rows of data."
        parent.Messages.SetValue(message)
        
    def ProcessBloodBiochem(parent, event):
        folder = parent.folder.GetLineText(0)
        files_num = parent.files.GetNumberOfLines()
        startDate = parent.Date.GetLineText(0)
        counts = []
        for i in range(files_num):
            if(len(counts) < 1):
                try:
                    counts.extend(BloodBiochem().ReadFile(folder, parent.files.GetLineText(i), startDate))
                    outfile = open(os.path.join(folder, "BloodBiochem.csv"), "w")
                    writer = csv.writer(outfile, dialect = 'excel')
                    parent.Messages.SetValue("Data read in.\nWait to finish writing...")
                    wx.Yield()
                    writer.writerows(counts)
                    outfile.close()
                    time.sleep(2)
                    message = "Done! Wrote " + str(len(counts) - 1) + " rows of data."
                    parent.Messages.SetValue(message)
                except ET.ParseError, e:
                    z = e
                    message = "There was a problem!\nOne of your files is malformed.\nMessage:\n" + str(z.message)
                    parent.Messages.SetValue(message)
#                except:
#                    e = sys.exc_info()[0]
#                    message = "There was a problem!\nMessage:\n{0}".format(e)
#                    parent.Messages.SetValue(message)
            else:
                try:
                    counts.extend(BloodBiochem().ReadFile(folder, parent.files.GetLineText(i), startDate)[1:])
                    outfile = open(os.path.join(folder, "BloodBiochem.csv"), "w")
                    writer = csv.writer(outfile, dialect = 'excel')
                    parent.Messages.SetValue("Data read in.\nWait to finish writing...")
                    wx.Yield()
                    writer.writerows(counts)
                    outfile.close()
                    time.sleep(2)
                    message = "Done! Wrote " + str(len(counts) - 1) + " rows of data."
                    parent.Messages.SetValue(message)
                except ET.ParseError, e:
                    z = e
                    message = "There was a problem!\nOne of your files is malformed.\nMessage:\n" + str(z.message)
                    parent.Messages.SetValue(message)
                except:
                    e = sys.exc_info()[0]
                    message = "There was a problem!\nMessage:\n{0}".format(e)
                    parent.Messages.SetValue(message)


class MyApp(wx.App):

    # wxWindows calls this method to initialize the application
    def OnInit(self):

        # Create an instance of our customized Frame class
        frame = MyFrame(None, -1, "Blood data extraction")
        frame.Show(True)

        # Tell wxWindows that this is our main window
        self.SetTopWindow(frame)

        # Return a success flag
        return True



app = MyApp(0)     # Create an instance of the application class
app.MainLoop()