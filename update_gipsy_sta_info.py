#!/usr/bin/env python
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


def usage():
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
        else:
            assert False, "unhandled option: `%s'" % opt

    sta_info = sif.sta_info_interface()
    sta_info.connect()
    sta_info.add_svec_line("ZWE2 ZWEN 2009 09 22 00 00  0.00 946080000.00 AOAD/M_T       0.0000      0.0000      0.0460      0.0000 l bkg3.zwen_20040929.log ")
    sta_info.dump()


