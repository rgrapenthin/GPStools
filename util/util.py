import sys, os, shutil
import urllib
sys.path.append( '../classes' )

from classes.IGSLog import IGSLog

databases = {}

#hash table to map data center to log file url -- these are the defaults, could add more for individual applications
databases['unavco'] = 'ftp://data-out.unavco.org/pub/logs'
databases['sopac']  = 'ftp://garner.ucsd.edu/pub/docs/site_logs'        
databases['igs']    = 'ftp://igscb.jpl.nasa.gov/pub/station/finallog'

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

def get_site_log(archive='', site='', url=''):

    ##get going
    logfile = ''

    for a in databases.keys():
        sys.stdout.write("Trying '"+a+"' archive: \t")

        file_from = ''
        file_url  = ''
        
        if a == 'unavco':
            file_url  = databases[a]+'/'+site+'log.txt'
            logfile   = retrieve_log(file_url)
            if logfile:
                file_from=a
                break
            
        elif a == 'sopac':
            file_url  = databases[a]+'/'+site+'.log.txt'
            logfile  = retrieve_log(file_url)
            if logfile:
                file_from=a
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
            ftp.quit()

            try:
                sitefile = [filename for filename in logfiles if site in filename][-1]
                file_url = databases[a]+'/'+sitefile
                logfile  = retrieve_log(file_url)
            except IndexError:
                sys.stdout.flush()
                sys.stderr.write("Couldn't find site `"+site.upper()+"'. Bye.\n")
                sys.exit(2)

            if logfile:
                file_from=a
                break

    if logfile:
        local_log = site+"."+file_from+".log"
        xml_log   = site+".xml"
        log = IGSLog(logfile, site)
        log.parse()
        log.retrieved_from(file_from, file_url, local_log)
        log.write(xml_log)
        
        #move files to site doc archive
        dest = os.environ.get('GPS_SITE_DOC')
        
        if dest:
            print "Moving logfiles to site-log archive '"+dest+"'"
            #os.rename won't copy across partitions
            shutil.move(logfile, dest+"/"+local_log)
            shutil.move(xml_log, dest+"/"+xml_log)
        else:
            print "Environment variable 'GPS_SITE_DOC' not set. logfiles remain in current directory."
