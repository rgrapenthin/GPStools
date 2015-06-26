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
from datetime import datetime

class IGSLog(object):

    #XML sub-section (and some sub-subsection) tags
    form            = "form"
    siteid          = "site-identification"
    location        = "location"
    receiver        = "receiver"
    receivers       = "receivers"
    antenna         = "antenna"
    antennas        = "antennas"
    tie             = "tied-marker"
    ties            = "ties"
    freq            = "frequency-standards"
    colocs          = "colocation-information"
    coloc           = "colocation"
    mets            = "meteorological-sensors"
    met_humid       = "humidity"
    met_press       = "pressure"
    met_temp        = "temperature"
    met_vapor       = "water-vapor-radiometer"
    met_other       = "other-instrumentation"
    conds           = "local-conditions"
    cond_interfere  = "radio-interference"
    cond_multipath  = "multipath-source"
    cond_signal     = "signal-obstruction"
    ep_effects      = "episodic-effects"
    ep_effect       = "effect"
    poc             = "poc"
    agency          = "agency"
    more            = "more"
    sec_info        = "header"
    standard        = "standard"

    #the logs contain several levels of indentations that 
    #signify a hierarchy, we need to reflect that and use
    #this map to check on these.
    indents = {1: "     ", 2: "       ", 3: "        "}

    #This maps the IGS "field names" to XML tags of my chosing
    igs2tag_map = { #FORM-SECTION
                        "Prepared by (full name)"       : 'preparer', 
                        "Date Prepared"                 : 'date',
                        "Report Type"                   : 'type',
                        "Previous Site Log"             : 'previous-log',
                        "Modified/Added Sections"       : 'modified-sections',
                    #SITE-ID SECTION
                        "Site Name"                     : 'site-name',
                        "Four Character ID"             : 'site-id',
                        "Monument Inscription"          : 'monument-inscription',
                        "IERS DOMES Number"             : 'iers-domes-number',
                        "CDP Number"                    : 'cdp-number',
                        "Monument Description"          : 'monument',
                        "Height of the Monument"        : 'height',
                        "Monument Foundation"           : 'foundation',
                        "Foundation Depth"              : 'foundation-depth',
                        "Marker Description"            : 'marker-description',
                        "Date Installed"                : 'date-installed',
                        "Geologic Characteristic"       : 'geology',
                        "Bedrock Type"                  : 'bedrock-type',
                        "Bedrock Condition"             : 'bedrock-condition',
                        "Fracture Spacing"              : 'fracture-spacing', 
                        "Fault zones nearby"            : 'fault-zones-nearby',
                        "Distance/activity"             : 'distance-activity',
                        "Additional Information"        : 'add-info',
                    #LOCATION SECTION
                        "City or Town"                  : 'city-town',
                        "State or Province"             : 'state-province',
                        "Country"                       : 'country',
                        "Tectonic Plate"                : 'tectonic-plate',
                        "Approximate Position (ITRF)"    : 'approx-position-itrf',
                        "X coordinate (m)"              : 'x-coord',
                        "Y coordinate (m)"              : 'y-coord',
                        "Z coordinate (m)"              : 'z-coord',
                        "Latitude (N is +)"             : 'latitude',
                        "Longitude (E is +)"            : 'longitude',
                        "Elevation (m,ellips.)"         : 'elevation',
                    #RECEIVER SECTION
                        "Receiver Type"                 : 'receiver-type',
                        "Satellite System"              : 'satellite-system',
                        "Serial Number"                 : 'serial-number',
                        "Firmware Version"              : 'firmware-version',
                        "Elevation Cutoff Setting"      : 'elevation-cutoff',
                        "Date Removed"                  : 'date-removed',
                        "Temperature Stabiliz."         : 'temperature-stabilization',
                    #ANTENNA SECTION
                        "Antenna Type"                  : 'antenna-type',
                        "Antenna Reference Point"       : 'antenna-reference-point',
                        "Marker->ARP Up Ecc. (m)"       : 'marker-arp-up-eccentricity',
                        "Marker->ARP North Ecc(m)"      : 'marker-arp-north-eccentricity',
                        "Marker->ARP East Ecc(m)"       : 'marker-arp-east-eccentricity',
                        "Alignment from True N"         : 'alignment-from-true-north',
                        "Antenna Radome Type"           : 'radome-type',
                        "Radome Serial Number"          : 'radome-serial-number',
                        "Antenna Cable Type"            : 'antenna-cable-type',
                        "Antenna Cable Length"          : 'antenna-cable-length',
                    #SURVEYED TIES SECTION
                        "Tied Marker Name"              : 'name',
                        "Tied Marker Usage"             : 'usage',
                        "Tied Marker CDP Number"        : 'cdp-number',
                        "Tied Marker DOMES Number"      : 'iers-domes-number',
                        "Differential Components from GNSS Marker to the tied monument (ITRS)" : 'itrs-differential-components-marker-to-tie',
                        "dx (m)"                        : 'dx-offset',
                        "dy (m)"                        : 'dy-offset',
                        "dz (m)"                        : 'dz-offset',
                        "Accuracy (mm)"                 : 'accuracy',
                        "Survey method"                 : 'survey-method',
                        "Date Measured"                 : 'date-measured',
                    #FREQUENCY STANDARD SECTION
                        "Standard Type"                 : 'type',
                        "Input Frequency"               : 'input-freq',
                        "Effective Dates"               : 'effective-dates',
                        "Notes"                         : 'notes',
                    #Collocation Information
                        "Instrumentation Type"          : 'instrumentation-type',
                        "Status"                        : 'status',
                    #METEOROLOGICAL INSTRUMENTATION SECTION
                        "Humidity Sensor Model"         : 'sensor-model',
                        "Pressure Sensor Model"         : 'sensor-model',
                        "Temp. Sensor Model"            : 'sensor-model',
                        "Water Vapor Radiometer"        : 'sensor-model',
                        "Other Instrumentation"         : 'information',
                        "Manufacturer"                  : 'manufacturer',
                        "Data Sampling Interval"        : 'data-sampling-interval',
                        "Accuracy (% rel h)"            : 'accuracy',
                        "Aspiration"                    : 'aspiration',
                        "Height Diff to Ant"            : 'height-difference-to-antenna',
                        "Calibration date"              : 'calibration-date',
                    #LOCAL CONDITIONS SECTION
                        "Radio Interferences"           : 'source',
                        "Multipath Sources"             : 'source',                        
                        "Signal Obstructions"           : 'source',
                        "Observed Degradations"         : 'observed-degradation',
                    #EPISODIC EFFECTS SECTION
                        "Date"                          : 'date',
                        "Event"                         : 'event',
                    #POINT OF CONTACT SECTION
                        "Agency"                        : 'agency',
                        "Preferred Abbreviation"        : 'preferred-abbreviation',
                        "Mailing Address"               : 'mailing-address',
                        "Primary Contact"               : 'contact-primary',
                        "Contact Name"                  : 'name',
                        "Telephone (primary)"           : 'phone-primary',
                        "Telephone (secondary)"         : 'phone-secondary',
                        "Fax"                           : 'fax',
                        "E-mail"                        : 'email',
                        "Secondary Contact"             : 'contact-secondary',
                    #MORE INFORMATION SECTION
                        "Primary Data Center"           : 'datacenter-primary',
                        "Secondary Data Center"         : 'datacenter-secondary',
                        "URL for More Information"      : 'url',
                        "Hardcopy on File"              : 'hardcopy',
                        "Site Map"                      : 'site-map',
                        "Site Diagram"                  : 'site-diagram',
                        "Horizon Mask"                  : 'horizon-mask',
                        "Site Pictures"                 : 'site-pictures',
                        "Antenna Graphics with Dimensions" : 'antenna-graphics'
                  }

    #list containing tags that allow for multi-line input
    multiple_lines = ['distance-activity', 'add-info', 'notes', 'other-instrumentation', 'mailing-address', 'antenna-graphics']
    
    #class variables
    lines           = None              #contains the full IGS log in ASCII format
    root            = None              #root node of XML-DOM
    section         = ''                #tag name for current section
    subsection      = ''                #... and subsection
    indent_level    = 1                 #current level of indentations
    addtosubnode    = False             
    skip_section    = False
    multiline       = False             #we're in multi-line input mode
    useless_indents = False             #for some sections, the indentations don't mean squat, 
                                        #need a flag for that.
    
    def __init__(self, file_name, siteid):
        with open(file_name, 'r') as f: 
            self.lines  = f.readlines()
            
        self.root   = ET.Element('igs-log', attrib={'site-id':siteid})

    def reset_section_vars(self):
        self.skip_section = False
        self.addtosubnode = False
        self.multiline    = False
        self.useless_indents = False
        self.indent_level = 1
     
    def retrieved_from(self, archive, url, local_log):
        x = ET.SubElement(self.root, 'log-source')
        a = ET.SubElement(x, 'archive')
        u = ET.SubElement(x, 'url')
        d = ET.SubElement(x, 'date')
        l = ET.SubElement(x, 'local-igs-log')
        a.text = archive
        u.text = url
        d.text = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        l.text = local_log
        
           
    #this is still in the long form and can probably be shortened, for now
    #we'll keep it in a running version
    def parse(self):
        self.section        = ''
        self.indent         = 1
        self.parent         = self.root
        
        for line in (l for l in self.lines if len(l.strip()) > 1):
            
            #decide on which section / subsection we're in for this line
            #(re)set the section variables accordingly
            #
            # NOTE: PAY ATTENTION TO THE FACT THAT SUBSECTIONS OPERATE ON
            #       SHIFTED FIELD NUMBERS. THAT'S IMPORTANT!
            if   line.startswith("0. "):
                self.reset_section_vars()
                self.section = self.form
                info    = ".".join(line.split('.')[1:]).strip()
            elif line.startswith("1. "):
                self.reset_section_vars()
                self.section      = self.siteid
                info    = ".".join(line.split('.')[1:]).strip()
            elif line.startswith("2. "):
                self.reset_section_vars()
                self.section      = self.location
                info    = ".".join(line.split('.')[1:]).strip()
            elif line.startswith("3."):
                self.reset_section_vars()
                self.section      = self.receivers
                self.subsection   = self.receiver
                info    = ".".join(line.split('.')[1:]).strip()
            elif line.startswith("4."):
                self.reset_section_vars()
                self.section      = self.antennas
                self.subsection   = self.antenna
                info    = ".".join(line.split('.')[1:]).strip()
            elif line.startswith("5."):
                self.reset_section_vars()
                self.section      = self.ties
                self.subsection   = self.tie
                info    = ".".join(line.split('.')[1:]).strip()
            elif line.startswith("6."):
                self.reset_section_vars()
                self.section = self.freq
                self.subsection = self.standard
                self.useless_indents = True
                info    = ".".join(line.split('.')[1:]).strip()
            elif line.startswith("7."):
                self.reset_section_vars()
                self.section = self.colocs
                self.subsection = self.coloc
                self.useless_indents = True
                info    = ".".join(line.split('.')[1:]).strip()
            elif line.startswith("8. "):
                self.reset_section_vars()
                self.section = self.mets
                self.useless_indents = True                
                info    = ".".join(line.split('.')[1:]).strip()
            elif line.startswith("8.1"):
                self.reset_section_vars()
                self.section = self.mets
                self.subsection = self.met_humid
                self.useless_indents = True         
                info    = ".".join(line.split('.')[2:]).strip()
            elif line.startswith("8.2"):
                self.reset_section_vars()
                self.section = self.mets
                self.subsection = self.met_press
                self.useless_indents = True                
                info    = ".".join(line.split('.')[2:]).strip()
            elif line.startswith("8.3"):
                self.reset_section_vars()
                self.section = self.mets
                self.subsection = self.met_temp
                self.useless_indents = True                
                info    = ".".join(line.split('.')[2:]).strip()
            elif line.startswith("8.4"):
                self.reset_section_vars()
                self.section = self.mets
                self.subsection = self.met_vapor
                self.useless_indents = True                
                info    = ".".join(line.split('.')[2:]).strip()
            elif line.startswith("8.5"):
                self.reset_section_vars()
                self.section = self.mets
                self.subsection = self.met_other
                self.useless_indents = True                
                info    = line.split('.')[2].strip()
                info    = ".".join(line.split('.')[2:]).strip()
            elif line.startswith("9. "):
                self.reset_section_vars()
                self.section = self.conds
                self.useless_indents = True                
                info    = ".".join(line.split('.')[1:]).strip()
            elif line.startswith("9.1"):
                self.reset_section_vars()
                self.section = self.conds
                self.subsection = self.cond_interfere
                self.useless_indents = True                
                info    = ".".join(line.split('.')[2:]).strip()
            elif line.startswith("9.2"):
                self.reset_section_vars()
                self.section = self.conds
                self.subsection = self.cond_multipath
                self.useless_indents = True                
                info    = ".".join(line.split('.')[2:]).strip()
            elif line.startswith("9.3"):
                self.reset_section_vars()
                self.section = self.conds
                self.subsection = self.cond_signal
                self.useless_indents = True                
                info    = ".".join(line.split('.')[2:]).strip()
            elif line.startswith("10."):
                self.reset_section_vars()
                self.section = self.ep_effects
                self.subsection = self.ep_effect
                info    = ".".join(line.split('.')[1:]).strip()
            elif line.startswith("11. "):
                self.reset_section_vars()
                self.section = self.poc
                info    = ".".join(line.split('.')[1:]).strip()
            elif line.startswith("12. "):
                self.reset_section_vars()
                self.section = self.agency
                info    = ".".join(line.split('.')[1:]).strip()
            elif line.startswith("13. "):
                self.reset_section_vars()
                self.section = self.more
                info    = ".".join(line.split('.')[1:]).strip()

            #if we are in any kind of section add this current line
            #accordingly
            if self.section:
                self.current_node = self.root.findall(self.section)

                if not self.current_node:
                    #if the section does not exist in current DOM, add it. 'info' parameter contains the
                    #actual IGS log information
                    self.current_node = ET.SubElement(self.parent, self.section, {'info' : info})
                    continue
                else:
                    #If the section exists in DOM, there will be only 1 entry in the list
                    #coming from the findall() function, instead of working on a list below, 
                    #extract the first (and only!) item to operate on below.
                    self.current_node = self.current_node[0]
                    
                    #If there is a subsection we currently work on, then make the last child of
                    #this section the current node and keep working on this.
                    if self.addtosubnode:
                        try:
                            self.current_node = list(self.current_node)[-1]
                        except:
                            pass

                #treat the case of 3.1, 4.2, etc. subsection stuff - but only when
                #when we're not in multiline mode! 
                if not line.startswith(" ") and not self.multiline:
                    if info.startswith("X") or info.startswith("x"):
                        self.skip_section = True
                    else:
                        self.current_node = ET.SubElement(self.current_node, self.subsection)
                        self.addtosubnode = True
                        li = list(line)
                        for i in range(len(li)):
                            if li[i] is not ' ':
                                li[i] = ' ' 
                            else:
                                break
                        line = "".join(li)

                #There's no need to add sections that start with *.X because they don't contain
                #any information. Skip these. Add all other information to the Node in the DOM    
                if not self.skip_section:
                    #Note that the whitespace after the ':' is important, otherwise times
                    #will be split too and we have to work with more than 2 fields!
                    self.addToSection(line.split(':'))

    def addToSection(self, fields):
        #Treat multi-line case right at the beginning.
        #if there is no tag in the map for the field, 
        #check whether we're working in multiline mode
        #if so, find the last node (depending on level
        #of indentation and then add text to this node's
        #text field and return.
        #if it's not a multiline case, and we don't have 
        #a tag for the field, skip it and return right away
        try:
            tag = self.igs2tag_map[fields[0].strip()]
        except KeyError:
            if self.multiline:
                try:                     
                    le = list(list(self.current_node)[-1])[-1]
                except:
                    le = list(self.current_node)[-1]
                
                joinat = 0
                
                #Believe it or not ... it can happen!
                if fields[0] == "                              ":
                    joinat = 1
                    fields[1] = fields[1].strip()
                
                #don't forget to join in case there were more ':' in the string   
                le.text = le.text+"\n"+":".join(fields[joinat:]).rstrip('\n').decode('utf8', 'ignore')
                
                return
            else:
                return

        try:
            #set multiline, if there is a possibility that's what is coming
            #else, reset
            if tag in self.multiple_lines:
                self.multiline = True
            else:
                self.multiline = False
            
            if not self.useless_indents and fields[0].startswith(self.indents[3]):
                if self.indent_level == 2:
                    self.indent_level += 1
                    le = list(list(self.current_node)[-1])[-1]
                    try:
                        #if tag has text, add "-description" tag with that text as subnode
                        if le.text.strip():
                            self.current_node = ET.SubElement(le, le.tag+"-description")
                            self.current_node.text = le.text
                            le.text = ""
                            
                        #add indented text as subnode                            
                        el      = ET.SubElement(le, tag)
                        el.text = fields[1].strip().decode('utf8', 'ignore')
                    except:
                        pass
                    return 
                if self.indent_level == 3:
                    try:
                        le = list(list(self.current_node)[-1])[-1]
                        el      = ET.SubElement(le, tag)
                        el.text = fields[1].strip().decode('utf8', 'ignore')
                    except:
                        pass
                    return 

            if not self.useless_indents and fields[0].startswith(self.indents[2]):
                if self.indent_level == 1:
                    self.indent_level += 1
                    try:
                        le = list(self.current_node)[-1]
                        #if tag has text, add "-description" tag with that text as subnode
                        if le.text.strip():
                            self.current_node = ET.SubElement(le, le.tag+"-description")
                            self.current_node.text = le.text
                            le.text = ""
                            
                        #add indented text as subnode                            
                        el      = ET.SubElement(le, tag)
                        if len(fields) == 2:
                            el.text = ":".join(fields[1:]).strip().decode('utf8', 'ignore')
                    except:
                        pass
                    return 
                if self.indent_level == 2:
                    try:
                        le = list(self.current_node)[-1]
                        el      = ET.SubElement(le, tag)
                        el.text = ":".join(fields[1:]).strip().decode('utf8', 'ignore')
                    except:
                        pass
                    return 
                    
            elif fields[0].startswith(self.indents[1]):
                if self.indent_level > 1:
                    self.indent_level = 1

            el      = ET.SubElement(self.current_node, tag)
            el.text = ":".join(fields[1:]).strip().decode('utf8', 'ignore')

               
        except (IndexError,KeyError):
            pass

    #Full Disclosure: I stole this method off the internet
    #and adapted it. Thanks, stranger!
    def indent_tree(self, elem, level=0):
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent_tree(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def write(self, filename):
        self.indent_tree(self.root)
        ET.ElementTree(self.root).write(filename, encoding="utf8", method="xml")

    def dump(self):
        self.indent_tree(self.root)
        self.indent_tree(self.root)
        ET.dump(self.root)
        
