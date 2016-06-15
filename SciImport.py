# -*- coding: utf-8 -*-
"""
Created on Thu Dec 18 11:08:30 2014

@author: jaudet
"""

import struct, csv, re, datetime, time, os.path, sys

import xml.etree.ElementTree as ET

class BloodCount(object):
    def __init__(self):
        return(None)
    
    def GetName(self, nameDate):
        if(len(nameDate.split("-")) > 1):
            name = nameDate.split("-")
            return(str(name[1]))
        else:
            name = nameDate.split(".")
            return(str(name[1]))
    
    def GetDate(self, nameDate, startDate):
        num = len(nameDate.split("\x00"))
        nameDate = nameDate.split("\x00")[num - 1]
        if(len(nameDate.split("-")) > 1):
            date_text = nameDate.split("-")[0]
            if(len(date_text) == 6):
                date = datetime.datetime.strptime(date_text, "%y%m%d")
            else:
                date = datetime.datetime.strptime(date_text, "%Y%m%d")
            if date > datetime.datetime.now() or (datetime.datetime.now() - date).days > 700 :
                date = datetime.datetime.strptime(date_text, "%d%m%y")
            day = (date - startDate).days
            date = date.timetuple()
            date = time.strftime("%d%b%Y", date)
            return(str(date), str(day))
        else:
            if(len(nameDate.split(".")) > 1):
                date_text = nameDate.split(".")[0]
                if(len(date_text) == 6):
                    date = datetime.datetime.strptime(date_text, "%y%m%d")
                else:
                    date = datetime.datetime.strptime(date_text, "%Y%m%d")
                if date > datetime.datetime.now() or (datetime.datetime.now() - date).days > 700 :
                    date = datetime.datetime.strptime(date_text, "%d%m%y")
                day = (date - startDate).days
                date = date.timetuple()
                date = time.strftime("%d%b%Y", date)
                return(str(date), str(day))
            else:
                return("", "")
        
    def GetNameAlt(self, nameDate):
        name = nameDate[9:]
        return(str(name))
    
    def GetDateAlt(self, nameDate, startDate):
        date = nameDate[0:8]
        date = datetime.datetime.strptime(date, "%y-%m-%d")
        day = (date - startDate).days
        date = date.timetuple()
        date = time.strftime("%d%b%Y", date)
        return(str(date), str(day))
    
    def GetNameDate(self, read, startDate):
        exp = re.compile(r"~\x00\x00(\d{4}|\d{5}|\d{6})((\x00\x00\x00)|(\x00\xcc\x00)|(\x00.\x6f\x00))(\d{6}|\d{8}).(\w*|\d{4})\x00")
        match = exp.search(read)
        if(match != None):
            match_end = len(match.group()) - 1
            nameDate = match.group()[2:match_end]
            #print nameDate
            name = self.GetName(nameDate)
            date, day = self.GetDate(nameDate, startDate)
            return(name, date, day)
        else:
            exp = re.compile(r"((o\x00)|(\(\x00)|(\xb2\xcc)|(\x91\x08))\d{2}-\d{2}-\d{2}-+\w*\x00")
            match = exp.search(read)
            if(match != None):
                match_end = len(match.group()) - 1
                nameDate = match.group()[2:match_end]
                #print nameDate
                name = self.GetNameAlt(nameDate)
                date, day = self.GetDateAlt(nameDate, startDate)
                return(name, date, day)
            else:
                exp = re.compile(r"((o\x00)|(\(\x00)|(\xb2\xcc)|(\x91\x08))(\d{2}|\d{3}|\d{4}|\d{5}|\d{6}|\d{7}|\d{8})\x00")
                match = exp.search(read)
                if(match != None):
                    match_end = len(match.group()) - 1
                    name = match.group()[2:match_end]
                    #print nameDate
                    return(name, "", "")
                else:
                    exp = re.compile(r"\xcco\x00GP-[A-Za-z ]*")
                    match = exp.search(read)
                    if(match != None):
                        match_end = len(match.group())
                        name = match.group()[3:match_end]
                        date, day = "Unkn", "Unkn"
                        return(name, date, day)
                    else:
                        exp = re.compile(r"\xcco\x00#(\d{1}|\d{2})-(\d{1}|\d{2})dpi")
                        match = exp.search(read)
                        if(match != None):
                            match_end = len(match.group())
                            name = match.group()[3:match_end]
                            date, day = "Unkn", "Unkn"
                            return(name, date, day)
                        else:
                            exp = re.compile(r"\xcco\x00(\d{3}|\d{4}|\d{5})-(\d{1}|\d{2})dpi")
                            match = exp.search(read)
                            if(match != None):
                                match_end = len(match.group())
                                name = match.group()[3:match_end]
                                date, day = "Unkn", "Unkn"
                                return(name, date, day)
                            else:
                                return("", "", "")
        
    """
    GetValues takes the string containing the binary data for 1 animal and returns the usef.ul values (reordered as below).
    File order:
        WBC, RBC, HGB (10X), HCT, MCV, MCH, MCHC (10X), PLT, PCT, MPV, ??,  PDWc, ??, RDWc, LYM, MON, NEU, LY%, MO%, NE%, ??, ??, ??, EOS, EO%, BAS, BA%
    
    Output order:
    WBC, LYM, MON, NEU, EOS, BAS, LY%, MO%, NE%, EO%, BA$, RBC, HGB (10X), HCT, MCV, MCH, MCHC (10X), RDWc, PLT, PCT, MPV, PDWc 
    so:
    0, 14, 15, 16, 23, 25, 17, 18, 19, 24, 26, 1, 2 (/10), 3, 4, 5, 6 (/10), 13, 7, 8, 9, 11
    """
    def GetValues(self, read):
        #print(read[90:100])        
        #read_data = read.split("\x99\x99@")[1]
        #print(read_data[0:10])
        #read_data = read[92:]
        read_values = read[1104:1214]
        #print read_values
        read_numbers = []
        for i in range(0, len(read_values), 4):
            if(i + 4 <= len(read_values)):
                end = i + 4
                read_numbers.append(round(struct.unpack('f', read_values[i:end])[0],2))
        
        order = [0, 14, 15, 16, 23, 25, 17, 18, 19, 24, 26, 1, 2, 3, 4, 5, 6, 13, 7, 8, 9, 11]
        #print read_numbers
        read_final = [read_numbers[i] for i in order]
        read_final[12] = read_final[12] / 10
        read_final[16] = read_final[16] / 10
        return(read_final)

    def ReadFile(self, FilePath, FileName, startDate):
        reads = open(os.path.join(FilePath, FileName), "rb").read()
        reads_sep = []
        if(len(startDate) != 9):
            raise DateFormatError("The start date is incorrectly formatted!!")
        for i in range(2152, len(reads) - 1, 2115):
            reads_sep.append(reads[i:(i + 2115)])
        startDate = datetime.datetime.strptime(startDate, "%d%b%Y")
        output = []
        for read in reads_sep:
            name, date, day = self.GetNameDate(read, startDate)
            values = self.GetValues(read)
            fin_list = []
            fin_list.append(str(name))
            fin_list.append(str(date))
            fin_list.append(str(day))
            for value in values:
                fin_list.append(str(value))
            output.append(fin_list)
        return(output)

    #def ExtractCounts(FilePath, FileNames, startDate):
        

    def Demo(self):
        return(BloodCount().ReadFile(r"F:\Blood count extraction", "saved.dat", "25Nov2014"))

#t = BloodCount().ReadFile(r"F:\h-14-001", "17Jun2015.dat", "17Jun2015")

#FilePath = r"F:\blood count"
#FileName = "20NovTo15Jan.dat"
class DateFormatError(Exception):
    def __init__(self, mismatch):
        Exception.__init__(self, mismatch)



class BloodBiochem(object):
    def __init__(self):
        return(None)
    
    def GetDate(self, nameDate, startDate):
        date = datetime.datetime.strptime(nameDate, "%Y%m%d")
        day = (date - startDate).days
        date = date.timetuple()
        date = time.strftime("%d%b%Y", date)
        return(str(date), str(day))

    def ReadFile(self, FilePath, FileName, startDate):
        if(len(startDate) != 9):
            raise DateFormatError("The start date is incorrectly formatted!!")
        startDate = datetime.datetime.strptime(startDate, "%d%b%Y")
        data = open(os.path.join(FilePath, FileName), "r").read()
        ##There is a weird, invisible character before character 1 and some crap at the end of the file
        ##Remove them
        data = data[1:(len(data) - 9)]
        data = "<" + data
        root = ET.fromstring(data)
        output = []
        for result in root.findall("records/result"):
            data = []
            date, day = self.GetDate(result.find("sampleInfo/runDate").text, startDate)
            ID = result.find("sampleInfo/patientControlId").text
            data.append(ID)
            data.append(date)
            data.append(day)
            temp = ["ID", "Date", "Day"]
            for param in result.findall("analyteResults/analyte"):
                data.append(param.find("value").text)
                if(len(output) < 1):
                    temp.append(param.find("name").text)
            if(len(output) < 1):            
                output.append(temp)
            output.append(data)
        return(output)

    #def ExtractCounts(FilePath, FileNames, startDate):
        

def Demo(self):
    BloodCount().ExtractCounts("G:\\Blood count extraction", ["saved.dat"], "25Nov2014")