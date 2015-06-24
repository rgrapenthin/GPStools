#####################################################################################
# IGSLog.py part of GPStools 
#
# Parses IGS station log text files into XML. No Validation of the IGS input file
# occurs. Checking of both input and output is recommended.
#
# author:   Ronni Grapenthin
#           Dept. Earth and Environmental Science
#           New Mexico Tech
#           801 Leroy Place
#           Socorro, NM-87801
#
# email:    rg@nmt.edu
#
#####################################################################################

import xml.etree.ElementTree as ET
import datetime as DT
import os

class XML_LogReader(object):

    #class variables
    tree           = None              #contains the full IGS log in ASCII format
    root            = None              #root node of XML-DOM
    siteid          =''                  #need a flag for that.
    filename        =''
    
    def __init__(self, xml_file, siteid):
        self.filename   = xml_file
        self.siteid     = siteid

        parser = ET.XMLParser(encoding="utf-8")

        with open(self.filename, 'r') as xml_f:
            self.tree       = ET.parse(xml_f, parser=parser)
            
        self.root       = self.tree.getroot()
        
        #uups, that'd be an interesting screw-up (given site-id not the one in XML file)
        if self.root.findall('site-identification')[0].findall('site-id')[0].text.lower() != self.siteid.lower():
            raise Exception("Site-id in `"+xml_file+"' is `"+self.root.findall('site-identification')[0].findall('site-id')[0].text+"' when we are looking for `"+self.siteid+"'")
        
        self.prepdate   = DT.datetime.strptime(self.root.findall('form')[0].findall('date')[0].text, '%Y-%m-%d')

    def site(self):
        return self.siteid.upper()

    def year(self):
        return self.prepdate.year

    def month(self):
        return self.prepdate.month

    def day(self):
        return self.prepdate.day

    def hour(self):
        return self.prepdate.hour

    def minute(self):
        return self.prepdate.minute

    def second(self):
        return self.prepdate.second+self.prepdate.microsecond

    def duration(self):
        #this is the standard in GIPSY sta_pos file
        return 1000001.00

    def XPos(self):
        return float(self.root.findall('location')[0].findall('approx-position-itrf')[0].findall('x-coord')[0].text)

    def YPos(self):
        return float(self.root.findall('location')[0].findall('approx-position-itrf')[0].findall('y-coord')[0].text)

    def ZPos(self):
        return float(self.root.findall('location')[0].findall('approx-position-itrf')[0].findall('z-coord')[0].text)

    def XVel(self):
        #no place for velocities in IGS Log
        return 0.0

    def YVel(self):
        #no place for velocities in IGS Log
        return 0.0

    def ZVel(self):
        #no place for velocities in IGS Log
        return 0.0

    def comment(self):
        agency = self.root.findall('poc')[0].findall('agency')[0].text
        
        if len(agency)+len(self.filename) < 30 :
            return agency + " " + self.filename

        return agency

    def site_name(self):
        return self.root.findall('site-identification')[0].findall('site-name')[0].text

    def sta_number(self):
        #official GPS stataion numbers do not yet exist
        return 0

    def loc_city(self):
        return self.location(which='city-town')

    def loc_state(self):
        return self.location(which='state-province')

    def loc_country(self):
        return self.location(which='country')
        
    def location(self, which='city-town'):
        return self.root.findall('location')[0].findall(which)[0].text

