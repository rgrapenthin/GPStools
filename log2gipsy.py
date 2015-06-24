#!/usr/bin/env python
#
#      igslog2xml.py
#
##BRIEF
# igslog2xml.py takes a given IGS log file and converts it to an XML representation.
#
##AUTHOR
# Ronni Grapenthin
#
##DATE
# 2015-05-13
#
##DETAILS
# The IGS log file can either be given via the -f 
#
##CHANGELOG
#
###########################################################################

import sys, getopt, os, shutil
from classes.XML_LogReader import XML_LogReader

def usage():
    print "Usage: log2gipsy -s <site-id> [-h] [-p]\n\
igslog2xml, GPStools\n\n\
Author: rn grapenthin, New Mexico Tech\n\n\
OPTIONS:\n\
   -h, --help\t\tprint this help\n\
   -p, --pos\t\tget site positition in Gipsy site_pos format\n\
   -s, --site\t\t4-char site id\n\n\
Report bugs to rg@nmt.edu\n\
"

############# ############# ############# 
############# MAIN STUFF
############# ############# ############# 

if __name__ == '__main__':
    try:
        #":" and "=" indicate that these parameters take arguments! Do not simply delete these!
        opts, args = getopt.getopt(sys.argv[1:], "hips:",["help", "id", "pos", "site="])
    except getopt.GetoptError as e:
        sys.stderr.write("Error: {0} \n\n".format(e.msg))
        usage()
        sys.exit(2)

    ##variables used here
    site                = ''
    xmlfile             = ''
    gps_site_doc        = os.environ.get('GPS_SITE_DOC')
    pos                 = False
    sta_id              = False

    if not gps_site_doc:
        sys.stderr.write("\nError: GPS_SITE_DOC environment variable must be set and point to log directory")
        sys.exit(2)        

##interpret command line
    for opt, arg in opts:
#HELP
        if opt in ("-h", "--help"):
            usage()
            sys.exit(2)
#get sta_id
        elif opt in ("-i", "--id"):
            sta_id = True
#get sta_pos
        elif opt in ("-p", "--pos"):
            pos = True
#site
        elif opt in ("-s", "--site"):
            site    = arg.lower()
            xmlfile = gps_site_doc+"/"+site+".xml"
#unknown
        else:
            assert False, "unhandled option: `%s'" % opt

##consistency checks
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
    
##get going ...

#read, pase, write.
try:
    log = XML_LogReader(xmlfile, site)
except Exception as e:
    sys.stderr.write("\nSomething went wrong ... \n\n")
    sys.stderr.write("%s\n\n" % e)
    sys.stderr.write(" ... better try again.\n")
    sys.exit(2)

#print site_pos format, if asked for
if pos:
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
if sta_id:
    #some of these may not exist and hence return None
    station_name = [log.site_name(), log.loc_city(), log.loc_state(), log.loc_country()]
    station_name = [s for s in station_name if s is not None]
    

    print " %.4s %6d %.60s" % \
            ( 
             log.site().upper(),
             log.sta_number(),
             ", ".join(station_name)
            )


