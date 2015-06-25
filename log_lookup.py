#!/usr/bin/env python
#
#      log_lookup.py
#
##BRIEF
# log_lookup.py takes a given IGS log file and converts it to an XML representation.
#
##AUTHOR
# Ronni Grapenthin
#
##DATE
# 2015-06-24
#
##DETAILS
#
##CHANGELOG
#
###########################################################################

import sys, getopt, os, shutil
import datetime as DT
from classes.XML_LogReader import XML_LogReader

def usage():
    print "Usage: log_lookup.py -s <site-id> [-h | --help] [-p | --pos] [-v | --arp-vector] [--gipsy-id] [--gipsy-pos] [--gipsy-svec]\n\
log_lookup.py, GPStools\n\n\
Author: rn grapenthin, New Mexico Tech\n\n\
OPTIONS:\n\
   -h, --help\t\tprint this help\n\
   -p, --pos\t\tget site positition in Gipsy site_pos format\n\
   -s, --site\t\t4-char site id\n\
   -v, --arp-vector\t\tget benchmark to antenna reference point vector dE dN dU)\n\n\
GIPSY-SPECIFIC OPTIONS:\n\
       --gipsy-pos\t\tget site positition in Gipsy site_pos format\n\
       --gipsy-id\t\tget site information in Gipsy site_id format\n\n\
Report bugs to rg@nmt.edu\n\
"

############# ############# ############# 
############# MAIN STUFF
############# ############# ############# 

if __name__ == '__main__':
    try:
        #":" and "=" indicate that these parameters take arguments! Do not simply delete these!
        opts, args = getopt.getopt(sys.argv[1:], "hps:v",["arp-vector", "help", "pos", "site=", "gipsy-id", "gipsy-pos", "gipsy-svec"])
    except getopt.GetoptError as e:
        sys.stderr.write("Error: {0} \n\n".format(e.msg))
        usage()
        sys.exit(2)

    ##variables used here
    site                = ''
    xmlfile             = ''
    gps_site_doc        = os.environ.get('GPS_SITE_DOC')
    arp_vector          = False
    pos                 = False

    gipsy_pos           = False
    gipsy_sta_id        = False
    gipsy_svec          = False

    if not gps_site_doc:
        sys.stderr.write("\nError: GPS_SITE_DOC environment variable must be set and point to log directory")
        sys.exit(2)        

###----------------------
#+#interpret command line
###----------------------
    for opt, arg in opts:
#HELP
        if opt in ("-h", "--help"):
            usage()
            sys.exit(2)
#get sta_pos
        elif opt in ("-p", "--pos"):
            pos = True
#site
        elif opt in ("-s", "--site"):
            site    = arg.lower()
            xmlfile = gps_site_doc+"/"+site+".xml"
#get arp=vector
        elif opt in ("-v", "--arp-vector"):
            arp_vector = True
#get gipsy sta_pos
        elif opt in ("--gipsy-pos"):
            gipsy_pos = True
#get gipsy sta_id
        elif opt in ("--gipsy-id"):
            gipsy_sta_id = True
#get gipsy svec
        elif opt in ("--gipsy-svec"):
            gipsy_svec = True
#unknown
        else:
            assert False, "unhandled option: `%s'" % opt

###----------------------
#+#consistency checks
###----------------------
if not site:
    sys.stderr.write("\nError: `site' not specified.\n\n" )
    usage()
    sys.exit(2)

if not os.path.isfile(xmlfile):
    sys.stderr.write("\nError: Can't find record for site `"+site+"' in GPS_SITE_DOC. `"+xmlfile+"' does not exist.\n")
    sys.stderr.write("Attempting retrieval ...\n")
    os.system("./get_site_log.py -s %s" % site)
    
    #still nothing ...
    if not os.path.isfile(xmlfile):
        sys.exit(2)
    

###----------------------
#+#READ XML log
###----------------------
try:
    log = XML_LogReader(xmlfile, site)
except Exception as e:
    sys.stderr.write("\nSomething went wrong ... \n\n")
    sys.stderr.write("%s\n\n" % e)
    sys.stderr.write(" ... better try again.\n")
    sys.exit(2)


###----------------------
#+#OUTPUT functions
###----------------------

#print site_pos format, if asked for
if pos:
    print "%15.4f %15.4f %15.4f" % ( log.XPos(), log.YPos(), log.ZPos() )

#print benchmark->arp vector
if arp_vector:
    print "%15.4f %15.4f %15.4f" % \
            ( log.arp_vector(direction="east"), log.arp_vector(direction="north"), log.arp_vector(direction="up") )


###----------------------
#+#GIPSY specific stuff
###----------------------

#print site_pos format, if asked for
if gipsy_pos:
    print " %.4s %.4d %.2d %.2d %.2d %.2d %5.2f %10.2f %15.4f %15.4f %15.4f %15.8E %15.8E %15.8E %.30s" % \
            ( 
             log.site().upper(),
             log.year(), log.month(),  log.day(), 
             log.hour(), log.minute(), log.second(),
             log.duration(),
             log.XPos(), log.YPos(), log.ZPos(),
             log.XVel(), log.YVel(), log.ZVel(),
             log.comment()
            )

#print site_id format, if asked for
if gipsy_sta_id:
    #some of these may not exist and hence return None
    station_name = [log.site_name(), log.loc_city(), log.loc_state(), log.loc_country()]
    station_name = [s for s in station_name if s is not None]
    
    print " %.4s %6d %.60s" % \
            ( 
             log.site().upper(),
             log.sta_number(),
             ", ".join(station_name)
            )

#print site vector and antenna type for all entries
if gipsy_svec:
    #get all antenna records
    antennas = log.antennas()
    
    svec_string             = []
    prev_antenna_installed  = None
    
    #start putting them together starting from the newest
    for antenna in reversed(antennas):
        dt = prev_antenna_installed - antenna['installed'] if prev_antenna_installed is not None else DT.timedelta(seconds=946080000.00)
        
        svec_string.append( " %.4s %.4s %.4d %.2d %.2d %.2d %.2d %5.2f %12.2f %.9s %11.4f %11.4f %11.4f %11.4f %.1s %.30s" % 
                            (log.site().upper(), log.site().upper(),
                            antenna['installed'].year, antenna['installed'].month,  antenna['installed'].day, 
                            antenna['installed'].hour, antenna['installed'].minute, antenna['installed'].second,
                            (dt.days*86400+dt.seconds+dt.microseconds/1000.0), antenna['type'][:9],
                            antenna['arp_vec_east'], antenna['arp_vec_north'], antenna['arp_vec_up'], 
                            0.0, 'l', 'add comment')
                            
                          )

    #put them out in chronological order
    for svec in reversed(svec_string):
        print svec

