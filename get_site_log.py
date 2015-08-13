#!/usr/bin/env python
#
#      get_site_log.py
#
##BRIEF
# get_site_log.py will look up a sitelog at a given database,
# grab the sitelog and convert it to XML. Both sitelog and 
# XML files are stored in a local directory
#
##AUTHOR
# Ronni Grapenthin
#
##DATE
# 2015-05-13
#
##DETAILS
#
##CHANGELOG
#
###########################################################################

import sys, getopt
import util.util as util

site                = ''
archive             = ''
url                 = ''

def usage():
    print "Usage: get_site_log -s <site-id> [-a <archive> -u <archive-url>]\n\
get_site_log, GPStools\n\n\
Author: rn grapenthin, New Mexico Tech\n\n\
OPTIONS:\n\
   -a, --archive\tarchive-id - valid choices: %s.\n\
   -h, --help\t\tprint this help\n\
   -s, --site\t\t4 character site-id\n\
   -u, --url\t\tdatabase url.\n\n\
Report bugs to rg@nmt.edu\n\
" % (", ".join(util.databases.keys()))

############# ############# ############# 
############# MAIN STUFF
############# ############# ############# 

if __name__ == '__main__':
    try:
        #":" and "=" indicate that these parameters take arguments! Do not simply delete these!
        opts, args = getopt.getopt(sys.argv[1:], "a:hs:u:",["archive=", "help", "site=", "url="])
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
#archive
        elif opt in ("-a", "--archive"):
            archive = arg.lower()
#site
        elif opt in ("-s", "--site"):
            site = arg.lower()
#url
        elif opt in ("-u", "--url"):
            url = arg
#unknown
        else:
            assert False, "unhandled option: `%s'" % opt

##consistency checks 
if not site:
    sys.stderr.write("\nError: `site' not specified.\n\n" )
    usage()
    sys.exit(2)
    
if archive and not url:
    if not util.databases.get(archive):
        sys.stderr.write("Error: Archive %s not in local database, must provide URL\n" % (archive))
        usage()
        sys.exit(2)

      
util.get_site_log(archive=archive, site=site, url=url)


