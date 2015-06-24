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

import sys, getopt, os, shutil
import urllib
from classes import IGSLog

#hash table to map data center to log file url
databases           = {}
databases['unavco'] = 'ftp://data-out.unavco.org/pub/logs'
databases['sopac']  = 'ftp://garner.ucsd.edu/pub/docs/site_logs'        
databases['igs']    = 'ftp://igscb.jpl.nasa.gov/pub/station/finallog'
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
" % (", ".join(databases.keys()))

def retrieve_log(url):
    sys.stdout.write('Retrieving '+url + '... ')
    sys.stdout.flush()
    
    f=url.split('/')[-1]
    
    try:
        urllib.urlretrieve(url, f)
    except IOError:
        sys.stdout.write("\t\tNothing found.\n")
        sys.stdout.flush()
        return False

    sys.stdout.write("\tSuccess.\n")
    sys.stdout.flush()

    return f

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
    if not databases.get(archive):
        sys.stderr.write("Error: Archive %s not in local database, must provide URL\n" % (archive))
        usage()
        sys.exit(2)
        
##get going
logfile = ''

for a in databases.keys():
    sys.stdout.write("Trying '"+a+"' archive: \t")
    
    if a == 'unavco':
        logfile  = retrieve_log(databases[a]+'/'+site+'log.txt')
        if logfile:
            break
        
    elif a == 'sopac':
        logfile  = retrieve_log(databases[a]+'/'+site+'.log.txt')
        if logfile:
            break
    #fallback:
    #see if there's a file that contains sitename in its name 
    #in the given directory at the server
    else:
        from ftplib import FTP
        #get name of file at IGS
        url = databases[a].split('//')[1].split('/')
        ftp = FTP(url[0])
        ftp.login()
        ftp.cwd("/"+"/".join(url[1:]))
        logfiles = ftp.nlst()
        sitefile = [filename for filename in logfiles if site in filename][-1]
        ftp.quit()
        
        logfile  = retrieve_log(databases[a]+'/'+sitefile)

        if logfile:
            break

if logfile:
    log = IGSLog.IGSLog(logfile, site)
    log.parse()
    log.write(site+".xml")
    
    #move files to site doc archive
    dest = os.environ.get('GPS_SITE_DOC')
    
    if dest:
        print "Moving logfiles to site-log archive '"+dest+"'"
        #os.rename won't copy across partitions
        shutil.move(logfile, dest+"/"+site+".log")
        shutil.move(site+".xml", dest+"/"+site+".xml")
    else:
        print "Environment variable 'GPS_SITE_DOC' not set. logfiles remain in current directory."


