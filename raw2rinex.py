#!/usr/bin/env python

"""
add date / range of dates to request lists
"""

import sys,os
import datetime, getopt
import  subprocess 
import util.constants as const
from plog.plog import Logger

############# ############# ############# 
############# AUX STUFF
############# ############# ############# 

def usage():
    print "Usage: raw2rinex.py --site \n\
Author: rn grapenthin, NMT"

############# ############# ############# 
############# MAIN STUFF
############# ############# ############# 

if __name__ == '__main__':

    file_id = None
    site_id = None

# find teqc binary
    proc = subprocess.Popen(['which', 'teqc'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    teqc_bin, err = proc.communicate()
    
    if len(teqc_bin) == 0 :
        Logger.error("Error: Can't find teqc binary", 2)

    if err != None:
        Logger.error(err, 2)
        
##read command line
    try:
        #rg ":" and "=" indicate that these parameters take arguments! Do not simply delete these!
        opts, args = getopt.getopt(sys.argv[1:], "s:f:h", ["site=", "file=", "help"])
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
            file_id = str(arg)
#unknown
        else:
            assert False, "unhandled option: `%s'" % opt

    #TODO: Move this stuff into its own class... teqc.py call: meta = teqc.meta(file_id)
    meta = subprocess.Popen(['teqc', '+quiet', '+meta', file_id], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    out, err = meta.communicate()

    lines=out.split("\n")
    meta = {}

    for l in lines:
        #only split first pair, note that times have ':' too!
        o = l.split(':',1 )
        
        #need exactly 2 elements
        if len(o) == 2:
            #convert dates
            if o[0] == const.TEQC_f_start or o[0] == const.TEQC_f_end:
                meta[o[0]] = datetime.datetime.strptime(o[1].strip(), const.TEQC_date_format)
            #convert floats
            elif o[0] == const.TEQC_sample_int or \
                 o[0] == const.TEQC_lon or\
                 o[0] == const.TEQC_lat or\
                 o[0] == const.TEQC_elev or\
                 o[0] == const.TEQC_ant_height:
                meta[o[0]] = float(o[1])
            #convert ints
            elif o[0] == const.TEQC_miss_epochs or\
                 o[0] == const.TEQC_f_size:
                meta[o[0]] = int(o[1])
            #rest remains string
            else:
                meta[o[0]] = o[1].strip();

    #some info for the user...
    if meta[const.TEQC_sample_int] > 1.0:
        Logger.info("Info: Standard rate sampling (%s sec)" % (meta[const.TEQC_sample_int]) )

    if meta[const.TEQC_sample_int] <= 1.0:
        Logger.info("Info: High rate sampling (%s sec)" % (meta[const.TEQC_sample_int]) )

    if meta[const.TEQC_sta_id] != site_id:
        Logger.info("Info: Given site-id `%s' overrides site-id in receiver file `%s' " % (site_id, meta[const.TEQC_sta_id]))

#    print meta
    
    

