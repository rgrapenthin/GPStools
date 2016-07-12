#####################################################################################
# Teqc.py part of GPStools 
#
# Defines Interface to teqc binary
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

#get to packages above
import os.path, sys
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))


import subprocess
import datetime
import util.constants as const

from plog.plog import Logger

class StationRecord(object):

    line        = None
    site_id     = None
    site_name   = None
    sess_start  = None
    sess_end    = None
    ant_ht      = None
    vert_ht     = None
    ant_north   = None
    ant_east    = None
    ht_code     = None
    rcx_type    = None
    rcx_sn      = None
    ant_type    = None
    ant_sn      = None
    operator    = ""
    agency      = ""

    def __init__(self, line):
    
        self.line        = line
        self.site_id     = line[1:5].strip()
        self.site_name   = line[7:25].strip()
        self.sess_start  = datetime.datetime.strptime(line[25:44].strip(), '%Y %j %H %M %S')

        #the end data requires some attention as continuous sites are markes as
        #"9999 999 00 00 00" for open ending periods
        try:
            self.sess_end    = datetime.datetime.strptime(line[44:63].strip(), '%Y %j %H %M %S')
        except ValueError:
            if line[44:63].strip().startswith('9999'):
                self.sess_end    = datetime.datetime.utcnow()
                    
        self.ant_ht      = float(line[65:72])
        self.ht_code     = line[72:79].strip()
        self.ant_north   = float(line[79:88])
        self.ant_east    = float(line[88:97])
        self.rcx_type    = line[97:119].strip()
        self.rcx_sn      = line[148:170].strip()
        self.ant_type    = line[170:187].strip()
        self.ant_dome    = line[187:194].strip()

        try:
            self.ant_sn      = line[194:216].strip()
        except Error:
            self.ant_sn      = line[194:].strip()

        try:
            self.operator    = line[216:240].strip()
        except Error:
            self.operator    = line[216:].strip()

        try:
          self.agency        = line[240:].strip()
        except Error:
            pass

    def calculate_vertical_antenna_height(self):
        if (self.ht_code != "DHARP"):
            p1 = subprocess.Popen([ "slant2vert_height.sh", "%s" % (self.ant_ht), 
                                    "%s" % (self.ant_type), "%s" % (self.ht_code)], 
                                    stdout=subprocess.PIPE)
            output,err = p1.communicate()

            #Error Checking
            if len(output) == 0:
                Logger.error("Couldn't calculate vertical height for %s with \
                              antenna type %s and height code %s " % 
                              (self.site_id, self.ant_type, self.ht_code), 4)

            if err != None:
                Logger.error(err, 3)

            #done!            
            self.vert_ht = float(output)

    def __str__(self):
        ret_str = "%4s  %17s %17s %17s  %1.4f %6s %5s %1.4f %1.4f %22s %22s %17s %5s  %22s" % (   
                            self.site_id, 
                            self.site_name, 
                            self.sess_start.strftime("%Y-%m-%d %H:%M:%S"), 
                            self.sess_end.strftime("%Y-%m-%d %H:%M:%S"),
                            self.ant_ht,
                            self.vert_ht,
                            self.ht_code,
                            self.ant_north,
                            self.ant_east,
                            self.rcx_type,
                            self.rcx_sn,
                            self.ant_type,
                            self.ant_dome,
                            self.ant_sn,
                            )
 
        if self.operator:
            ret_str += " %23s" %self.operator

        if self.agency:
            ret_str += " %s" %self.agency

        return ret_str
 
class StationDB(object):
    '''
        This class operates on a file called station.info that is expected
        either in the current directory or the directory pointed to by the environment variable
        GIPSY_STA_INFO. If the file can't be found, CleanShutdownRequest exception is
        thrown. The format of station.info is an expanded version of the GAMIT station / 
        session database:
        
*SITE  Station Name      Session Start      Session Stop       Ant Ht   HtCod  Ant N    Ant E    Receiver Type         Vers                  SwVer  Receiver SN           Antenna Type     Dome   Antenna SN            [ Observer     ]         [Agency
*2     8                 26                 45                 64       73     80       89       98                    120                   142    149                   171              188    195                   217                     241
*0047  GEONET0047        2011  60  0  0  0  9999 999  0  0  0   0.0000  DHARP   0.0000   0.0000  TPS NETG3             3.4 EG3 Jul,02,2010    3.40  --------------------  TRM29659.00      GSI    --------------------  [optional, name]         [optional, institution]
        
        The second line indicates the column number in which each record starts. Note that
        the second value for the dates is the day-of-year.
        
        The actual parsing of a record, i.e. a line, is done in StationRecord.
    '''
    
    sta_db = './station.info'
    record = {}

    def __init__(self):
        '''
            Attempts to set station.info location to directory in the 
            environment variable GIPSY_STA_INFO. If it can't find the file, 
            logs error, which throws CleanShutDownRequest.
        '''
        if os.environ['GIPSY_STA_INFO']:
            self.sta_db = os.environ['GIPSY_STA_INFO']+'/station.info'
        
        if not os.path.isfile(self.sta_db):
            Logger.error("  Can't find station database at `%s'. Please check and adjust code / links accordingly.\n\
            Note that this is a fixed-width formatted file!", 23)

    def get_record(self, site_id, start_time, end_time):
        '''
        Reads station.info file, finds site, creates record
        '''
        p1          = subprocess.Popen(["grep", "^ "+site_id, self.sta_db], stdout=subprocess.PIPE)
        output,err  = p1.communicate()

        #Error Checking
        if len(output) == 0:
            Logger.error("Couldn't find %s in %s" % (site_id, self.sta_db), 4)

        if err != None:
            Logger.error(err, 3)

        for l in output.splitlines():
            rec  = StationRecord(l)

            #return the record that covers the current start time
            if start_time >= rec.sess_start and end_time <= rec.sess_end:
                return rec
        
        Logger.warning("Could not find an entry for site %s between %s - %s in station db %s ." % (site_id, start_time, end_time, self.sta_db))
        

