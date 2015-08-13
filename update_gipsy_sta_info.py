#!/usr/bin/env python
# -*- coding: utf_8 -*-
#
#      update_gipsy_sta_info.py
#
##BRIEF
# update_gipsy_sta_info.py updates the local version of GIPSY's sta_info database from local logs
#
##AUTHOR
# Ronni Grapenthin
#
##DATE
# 2015-06-26
#
##DETAILS
# start by reading in the existing logs and sta_info records
#
##CHANGELOG
#
###########################################################################

import sys, getopt, os, shutil
import datetime as DT
from classes.XML_LogReader import XML_LogReader
from classes.GIPSY import StaInfo_interface as sif
import util.util as util

def usage(error=None):
    print "Usage: update_gipsy_sta_info.py -s <site-id> [-h | --help] [-p | --pos] [-v | --arp-vector] [--gipsy-id] [--gipsy-pos] [--gipsy-svec]\n\
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
    if error:
        print "\nError: "+error+"\n\n"

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
    site                = None
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
#site
        elif opt in ("-s", "--site"):
            site    = arg.lower()
            xmlfile = gps_site_doc+"/"+site+".xml"
        else:
            assert False, "unhandled option: `%s'" % opt

    if not site: 
        usage(error="Need to give site id")
        sys.exit(2)
        
###----------------------
#+#READ XML log
###----------------------
    try:
        log = XML_LogReader(xmlfile, site)
    except IOError as e:
        #file not found, try FTP download from usual archives
        sys.stderr.write("Site `"+site+"' not in local database; trying remote retrieval ...\n")
        util.get_site_log(site=site)              
        log = XML_LogReader(xmlfile, site)
    except Exception as e:
        #I guess we're doomed!
        sys.stderr.write("\nSomething went wrong ... \n\n")
        sys.stderr.write("%s\n\n" % e)
        sys.stderr.write(" ... better try again.\n")
        sys.exit(2)    

    print "Updating site `"+site+"' ("+log.site_name()+")"

###----------------------
#+#Connect to GIPSY sta_info database
###----------------------
    sta_info = sif.sta_info_interface()
    sta_info.connect()

    #Update STA ID TABLE
    if not sta_info.got_sta_id(log.site()):
        sta_info.add_sta_id(log.site(), log.site_number(), log.site_full_name())

#    sta_info.dump_sta_id()
    #Update SVEC TABLE
    sta_info.update_svec(log.site(), log.antennas())
    
#    sta_info.dump_svec()

    #Update POS TABLE
    sta_info.add_pos(log.site(), log.first_installed(), log.XPos(), log.YPos(), log.ZPos(), log.XVel(), log.YVel(), log.ZVel())
    sta_info.dump_sta_pos()
    
    sta_info.close()

