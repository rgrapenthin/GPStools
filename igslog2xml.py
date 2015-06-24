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
from classes.IGSLog import IGSLog

def usage():
    print "Usage: igslog2xml -i <site-id | filename> [-o <outfile>] [-h]\n\
igslog2xml, GPStools\n\n\
Author: rn grapenthin, New Mexico Tech\n\n\
OPTIONS:\n\
   -h, --help\t\tprint this help\n\
   -i, --input\t\teither 4-char site-id (file looked up under $GPS_SITE_DOC or filename.\n\
   -o, --output\t\toutput file (default: $GPS_SITE_DOC/site.xml)\n\n\
Report bugs to rg@nmt.edu\n\
"

def contains_path(filename):
    if os.path.isdir(filename):
        return True
    if os.path.dirname(filename):
        return True

    return False

############# ############# ############# 
############# MAIN STUFF
############# ############# ############# 
if __name__ == '__main__':
    try:
        #":" and "=" indicate that these parameters take arguments! Do not simply delete these!
        opts, args = getopt.getopt(sys.argv[1:], "hi:o:",["help", "input=", "output="])
    except getopt.GetoptError as e:
        sys.stderr.write("Error: {0} \n\n".format(e.msg))
        usage()
        sys.exit(2)

    ##variables used here
    in_name             = ''
    out_name            = ''
    input_is_site_id    = False
    gps_site_doc        = os.environ.get('GPS_SITE_DOC')

##interpret command line
    for opt, arg in opts:
#HELP
        if opt in ("-h", "--help"):
            usage()
            sys.exit(2)
#input
        elif opt in ("-i", "--input"):
            in_name = arg.lower()
            if not os.path.isfile(in_name):
                input_is_site_id = True
#output
        elif opt in ("-o", "--output"):
            out_name = arg.lower()
#unknown
        else:
            assert False, "unhandled option: `%s'" % opt

##consistency checks 
if not in_name:
    sys.stderr.write("\nError: `input' not specified. Use `-i' option.\n\n" )
    usage()
    sys.exit(2)

if contains_path(out_name):
    sys.stderr.write("\nError: `output' can't contain a path, must be a filename without slashes.\n\n" )
    sys.exit(2)

if input_is_site_id and not gps_site_doc and not os.path.isfile(in_name+".log"):
    sys.stderr.write("\nError: `input' seems specifies a site id. \
    I can't find a file "+in_name+".log in the current directory. \
    I also can't look up the log file in the site archive as the environment variable 'GPS_SITE_DOC' is not set.\
    Make sure your spelling is right, set GPS_SITE_DOC, or give me a log file.")
    usage()
    sys.exit(2)

##get going ...
logfile = in_name
xmlfile = in_name+".xml"
site    = in_name
        
if input_is_site_id:
    logfile = gps_site_doc+'/'+in_name+'.log'
    if not os.path.isfile(logfile):
        sys.stderr.write("\nError: Can't find a log file for site "+in_name+" in "+gps_site_doc+". Was looking for `"+logfile+"'.\nYou may have to run `get_igs_log.py -s "+in_name+"' instead.")
        sys.exit(2)
else:
    site = os.path.basename(logfile)[:4].lower()
    xmlfile = site+".xml"

if out_name:
    xmlfile = out_name

try:
    if os.path.samefile(logfile, xmlfile):
        sys.stderr.write("\nError: Input `"+logfile+"' and output `"+xmlfile+"' are the same file. Can't do that!")
        usage()
        sys.exit(2)
except OSError:
    pass

if os.path.isfile(xmlfile) or os.path.isfile(gps_site_doc+"/"+xmlfile):
    import uuid
    f_expansion = str(uuid.uuid4())    
    sys.stderr.write("\nWarning: `"+xmlfile+"' already exists. I'll write to `"+xmlfile+"."+f_expansion+"\n")
    xmlfile = xmlfile+"."+f_expansion

#read, pase, write.
log = IGSLog.IGSLog(logfile, site)
log.parse()
log.write(xmlfile)

if gps_site_doc:
    print "Moving xml file to site-log archive '"+gps_site_doc+"'"
    #os.rename won't copy across partitions
    shutil.move(xmlfile, gps_site_doc+"/"+xmlfile)
else:
    print "Environment variable 'GPS_SITE_DOC' not set. XML file remains in current directory."


