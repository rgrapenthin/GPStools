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
    tree            = None              #contains the full IGS log in ASCII format
    root            = None              #root node of XML-DOM
    siteid          =''                 #need a flag for that.
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

###LOG-SOURCE
    def url(self):
        return self.log_source(which='url')

    def archive(self):
        return self.log_source(which='archive')

    def local_log(self):
        return self.log_source(which='local-igs-log')

    def date(self):
        return DT.datetime.strptime(self.log_source(which='date'), '%Y-%m-%dT%H:%MZ')

    def log_source(self, which='archive'):
        return self.root.findall('log-source')[0].findall(which)[0].text

###LOCATION
    def loc_city(self):
        return self.location(which='city-town')

    def loc_state(self):
        return self.location(which='state-province')

    def loc_country(self):
        return self.location(which='country')
        
    def location(self, which='city-town'):
        return self.root.findall('location')[0].findall(which)[0].text

###ARP
    def arp_vector(self, direction="east"):
        tag = 'marker-arp-up-eccentricity'

        if direction == "east":
            tag = "marker-arp-east-eccentricity"
        elif direction == "north":
            tag = "marker-arp-north-eccentricity"
        elif direction == "up":
            tag = "marker-arp-up-eccentricity"
        else:
            raise Exception("Direction `"+direction+"' in arp_vector is not valid. Choose `east', `north', or `up'.")
            
        try:
            return float(self.root.findall('antennas')[0].findall('antenna')[-1].findall(tag)[0].text)
        except TypeError:
            return 0.0
    
    def to_text(self, elem):
        return elem.text if elem is not None else ''

    def to_float(self, elem):
        #first get the string if element exists
        x = elem.text if elem is not None else 0.0
        
        #then convert to float if sensible value in string
        try:
            return float(x) if x is not None else 0.0
        except ValueError:
            return 0.0

    def to_date(self, elem):
        x = elem.text if elem is not None else None

        try:
            return DT.datetime.strptime(x, '%Y-%m-%dT%H:%MZ')
        except ValueError:
            return None

    def antennas(self):
        ants = []
        for ant in self.root.findall('antennas')[0].findall('antenna'):
                ants.append({
                    'type':             self.to_text(ant.findall('antenna-type')[0]), 
                    'serial':           self.to_text(ant.findall('serial-number')[0]), 
                    'arp':              self.to_text(ant.findall('antenna-reference-point')[0]), 
                    'arp_vec_east':     self.to_float(ant.findall('marker-arp-east-eccentricity')[0]),
                    'arp_vec_north':    self.to_float(ant.findall('marker-arp-north-eccentricity')[0]),
                    'arp_vec_up':       self.to_float(ant.findall('marker-arp-up-eccentricity')[0]),
                    'north-deviation':  self.to_float(ant.findall('alignment-from-true-north')[0]),
                    'radome-type':      self.to_text(ant.findall('radome-type')[0]),
                    'radome-serial':    self.to_text(ant.findall('radome-serial-number')[0]), 
                    'cable-type':       self.to_text(ant.findall('antenna-cable-type')[0]), 
                    'cable-length':     self.to_float(ant.findall('antenna-cable-length')[0]), 
                    'installed':        self.to_date(ant.findall('date-installed')[0]),
                    'removed':          self.to_date(ant.findall('date-removed')[0])
                    })

        return ants
