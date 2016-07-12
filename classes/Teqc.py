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

#search in parent directory
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))


import subprocess
import datetime
import re
import util.constants as const

from plog.plog import Logger

class Teqc(object):
    
    operator     = "Anonymous"
    agency       = "Anonymous"
    sv_string    = "-R -E -S -C -J"  #default: no GLONASS, Galileo, SBAS, Compass, QZSS
    obs_string   = "+P +L2 +L1_2 +C2 +L2_2 +CA_L1 +L2C_L2" 
    comment      = []
    meta_info    = {}
    __raw_file__ = None
    epoch        = datetime.datetime(1980, 1, 6)
    utcHour2char = [ 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 
                     'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x' ]

    #binaries we'll use
    teqc_bin     = None
    gzip_bin     = None

    def __init__(self, raw_file):
        #assign file name        
        if os.path.isfile(raw_file):
            self.__raw_file__ = raw_file
        else:
            Logger.error("File `%s' does not exist." % raw_file, 23)        

        #figure out paths to binaries
        proc = subprocess.Popen(['which', 'teqc'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.teqc_bin, err = proc.communicate()
        
        if len(self.teqc_bin) == 0 :
            Logger.error("Can't find teqc binary", 2)

        if err != None:
            Logger.error(err, 3)

        proc = subprocess.Popen(['which', 'teqc'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.gzip_bin, err = proc.communicate()
        
        if len(self.gzip_bin) == 0 :
            Logger.error("Can't find gzip binary", 2)


    def __sv_match__(self, sv_string, search=re.compile(r'[^\-\+RESCJG ]').search):
        '''
            Ensure that the space vehicle list is actually supported by teqc
        '''
        return not bool(search(sv_string))

    def __obs_match__(self, obs_string, search=re.compile(r'[^\-\+PL125678CA_ ]').search):
        '''
            Ensure that the space vehicle list is actually supported by teqc - yes, this can be improved
        '''
        return not bool(search(obs_string))


    def meta(self):
        '''
        reads teqc meta output into dictionary that can be accessed with the 
        strings defined in util.const.py
        '''
        
        #do this only once!
        if not self.meta_info:

            teqc_run = subprocess.Popen(['teqc', '+quiet', '+meta', self.__raw_file__], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            out, err = teqc_run.communicate()

            lines=out.split("\n")

            for l in lines:
                #only split first pair, note that times have ':' too!
                o = l.split(':',1 )
                
                #need exactly 2 elements
                if len(o) == 2:
                    #convert dates
                    if o[0] == const.TEQC_f_start or o[0] == const.TEQC_f_end:
                        self.meta_info[o[0]] = datetime.datetime.strptime(o[1].strip(), const.TEQC_date_format)
                    #convert floats
                    elif o[0] == const.TEQC_sample_int or \
                         o[0] == const.TEQC_lon or\
                         o[0] == const.TEQC_lat or\
                         o[0] == const.TEQC_elev or\
                         o[0] == const.TEQC_ant_height:
                        self.meta_info[o[0]] = float(o[1])
                    #convert ints
                    elif o[0] == const.TEQC_miss_epochs or\
                         o[0] == const.TEQC_f_size:
                        self.meta_info[o[0]] = int(o[1])
                    #rest remains string
                    else:
                       self.meta_info[o[0]] = o[1].strip();
        
            #set gpsweek
            self.meta_info[const.GPSweek] = (int((self.meta_info[const.TEQC_f_start] - self.epoch).days) / 7 )
            
        return self.meta_info

    def add_commentLine(self, line):
        '''
            each string added here will be included as a 
            single comment line to the header of the rinex file
        '''
        self.comment.append(line)
        
    def comment_string(self):
        the_string = ""
        
        for l in self.comment:
            the_string += "+O.c '%s' " %l
            
        return the_string

    def add_sv_string(self, sv_string):
        if self.__sv_match__(sv_string):
            self.sv_string = sv_string
        else:
            Logger.warning("`%s' not supported by teqc, check `teqc -help'. Using default `%s' " % (sv_string, self.sv_string))

    def add_observables_string(self, obs_string):
        if self.__obs_match__(obs_string):
            self.obs_string = obs_string
        else:
            Logger.warning("`%s' not supported by teqc, check `teqc -help'. Using default `%s' " % (obs_string, self.obs_string))

    def get_hour_logged(self):
        if self.meta_info[const.TEQC_sample_int] <= 1.0:
            return self.utcHour2char[self.meta_info[const.TEQC_f_start].hour]
        else:
            return '0'

    def translate(self, site_record):
        '''
            runs the actual translation of the file from some native 
            format into rinex (output to standard rinex file name)
        '''
        #ensure we have meta info...
        if not self.meta_info:
            self.meta()

        #figure out what receiver we are translating    
        format_code = const.TEQC_format_translation_map[self.meta_info[const.TEQC_f_format]]

        #make rinex filenames     
        file_base = "%s%s%s.%s" % ( site_record.site_id.lower(), 
                                    self.meta_info[const.TEQC_f_start].strftime("%j"),
                                    self.get_hour_logged(),
                                    self.meta_info[const.TEQC_f_start].strftime("%y"))

        rnx_file  = file_base + "o"
        nav_file  = file_base + "n"


        subprocess.call("teqc "+
                            format_code+" "+
                            self.obs_string+" "+
                            self.sv_string+" "+
                            "-week %d " % self.meta_info[const.GPSweek] +
                            "+nav %s "  % nav_file +
                            "-O.mo %s " % site_record.site_id.upper() +
                            "-O.mn %s " % site_record.site_id.upper() +
                            "-O.rt '%s' " % site_record.rcx_type +
                            "-O.rn %s " % site_record.rcx_sn +
                            "-O.at '%s' " % site_record.ant_type +
                            "-O.an %s " % site_record.ant_sn +
                            "-O.pe %f %f %f " % (site_record.vert_ht, site_record.ant_east, site_record.ant_north) +
                            "-O.o  '%s' " % site_record.operator +
                            "-O.ag '%s' " % site_record.agency +
                            self.comment_string() +
                            self.__raw_file__ +" > %s " % rnx_file, shell=True)
    
        subprocess.call("gzip -f "+ rnx_file, shell=True)
        subprocess.call("gzip -f "+ nav_file, shell=True)

        Logger.info("Info: created `%s.gz' and `%s.gz'" % (rnx_file, nav_file))

