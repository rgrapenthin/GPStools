#!/usr/bin/env python

"""
add date / range of dates to request lists
"""

import sys,os
import datetime, getopt
import util.constants as const
import subprocess

from plog.plog import Logger, CleanShutdownRequest
from classes.Teqc import Teqc
from classes.StationDB import StationDB

############# ############# ############# 
############# AUX STUFF
############# ############# ############# 

def usage():
    print "Usage: raw2rinex.py --site <4-char-id> --file <e.g., trimble .dat file>\n\
Author: rn grapenthin, NMT"

############# ############# ############# 
############# MAIN STUFF
############# ############# ############# 

if __name__ == '__main__':

    raw_file = None
    site_id  = None

##read command line
    try:
        #rg ":" and "=" indicate that these parameters take arguments! Do not simply delete these!
        opts, args = getopt.getopt(sys.argv[1:], "s:f:hq", ["site=", "file=", "help", "quiet"])
    except getopt.GetoptError as e:
        sys.stderr.write("Error: {0} \n\n".format(e.msg))
        usage()
        sys.exit(2)

##interpret command line
    for opt, arg in opts:
    #HELP
        if opt in ("-h", "--help"):
            usage()
            sys.exit(2)
        elif opt in ("-s", "--site"):
            site_id = arg.upper()
#EVENT
        elif opt in ("-f", "--file"):
            raw_file = str(arg)
#quite
        elif opt in ("-q", "--quiet"):
            Logger.off()
#unknown
        else:
            assert False, "unhandled option: `%s'" % opt

    Logger.info("-"*80)
    Logger.info("Info: Working on file `%s' for site `%s'" % (raw_file, site_id))

#+# create station.info interface
    sta_db  = None

    try:
        sta_db = StationDB()
    except CleanShutdownRequest:
        print "Aborting."
        sys.exit()
    
#+# create teqc object
    teqc    = None 

    try:
        teqc = Teqc(raw_file)
    except CleanShutdownRequest:
        print "Aborting."
        sys.exit()

    teqc.operator   = "Ronni Grapenthin"
    teqc.agency     = "New Mexico Tech"

    teqc.add_commentLine("")
    teqc.add_commentLine("For more information about these data contact:")
    teqc.add_commentLine("")
    teqc.add_commentLine("Ronni Grapenthin (rg@nmt.edu)")
    teqc.add_commentLine("         Dept. Earth and Environmental Scienes")
    teqc.add_commentLine("         New Mexico Tech")
    teqc.add_commentLine("         801 Leroy Pl")
    teqc.add_commentLine("         Socorro, NM-87801")
    teqc.add_commentLine("")

    teqc.add_sv_string("-R -E -S -C -J")
    teqc.add_observables_string("+P +L2 +L1_2 +C2 +L2_2 +CA_L1 +L2C_L2")
    
    #get meta information from raw file
    meta = teqc.meta()

    #some info for the user...
    if meta[const.TEQC_sample_int] > 1.0:
        Logger.info("Info: Standard rate sampling (%s sec)" % (meta[const.TEQC_sample_int]) )

    if meta[const.TEQC_sample_int] <= 1.0:
        Logger.info("Info: High rate sampling (%s sec)" % (meta[const.TEQC_sample_int]) )

    if meta[const.TEQC_sta_id] != site_id:
        Logger.info("Info: Given site-id `%s' overrides site-id in receiver file `%s' " % (site_id, meta[const.TEQC_sta_id]))


    #extract the record that spans the correct time from station.info
    rec = sta_db.get_record(site_id=site_id, start_time=meta[const.TEQC_f_start], end_time=meta[const.TEQC_f_end])
    rec.calculate_vertical_antenna_height()

    if not rec.operator:
        rec.operator = teqc.operator
    if not rec.agency:
        rec.agency   = teqc.agency

    Logger.info("Info: Using site-record `%s'" % rec)
    
    teqc.translate(rec)
    
