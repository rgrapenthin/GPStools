#####################################################################################
# sta_info_interface.py part of GPStools 
#
# Parses GIPSY sta_info `database' reads and writes to it.
#
# author:   Ronni Grapenthin
#           Dept. Earth and Environmental Science
#           New Mexico Tech
#           801 Leroy Place
#           Socorro, NM-87801
#
# email:    rg@nmt.edu
#
#####################################################################################

from datetime import datetime
import os,sys
import sqlite3

class sta_info_interface(object):
    """
        This class provides an interface to GIPSY's sta_info database for 
        automated updating from IGS log files, or other records. 
        
        The sta_info database consists of three files that are kept in
        $GOA_VAR/sta_info under version control.  The files are in formatted ASCII
        records, so that they may be easily viewed and modified by a person
        using an editor.  Each file is stored in inverse chronological order and
        read from the top down.  This means that the most up to date information
        is encountered first when reading the files and that new information
        should be added to the tops of the files.
    """

    #
    sta_info_path   = None        #path to "database"
    
    #database files - Yes some of the comments are straight from $GOA/file_formats/sta_info ... 
    pcenter         = "pcenter"     #Antenna phase center offsets
    sta_id          = "sta_id"      #In this file, a given station name is associated with a station identifier and a station number.
    sta_pos         = "sta_pos"     #This file associates the station identifier with the station coordinates at some epoch and the station velocity. 
    sta_svec        = "sta_svec"    #This file associates the station identifier with the site vector and antenna type at some epoch.
    
    sta_svec_columns= "(to_site TEXT, from_site TEXT, year INTEGER, month INTEGER, day INTEGER, hour INTEGER, minute INTEGER, second REAL, \
                        duration REAL, antenna TEXT, arp_vec_east REAL, arp_vec_north REAL, arp_vec_up REAL, antenna_height REAL, \
                        sys_flag TEXT, comment TEXT)"
    sta_svec_columns2= "(to_site, from_site, year, month, day, hour, minute, second, \
                        duration, antenna, arp_vec_east, arp_vec_north, arp_vec_up, antenna_height, \
                        sys_flag, comment)"
    sta_svec_values= " (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    
    db          = None
    db_cursor   = None

    def __init__(self):
        #
        self.sta_info_path = os.environ.get('GIPSY_STA_INFO')
        
        if self.sta_info_path is None:
            sys.stderr.write("GIPSY_STA_INFO environment variable not set, trying GIPSY sta_info database\n")

            self.sta_info_path = os.environ.get('GOA_VAR')

            if self.sta_info_path is None:
                raise ("Neither GIPSY_STA_INFO nor GOA_VAR environment variables set, can't connect to a database\n")
            else:
                self.sta_info_path += "/sta_info"
                sys.stderr.write("Warning: working on original GIPSY sta_info database, changes may be overwritten on system update.\n")

        self.pcenter  = self.sta_info_path+"/"+self.pcenter
        self.sta_id   = self.sta_info_path+"/"+self.sta_id
        self.sta_pos  = self.sta_info_path+"/"+self.sta_pos
        self.sta_svec = self.sta_info_path+"/"+self.sta_svec
        
        #set up in-memory SQLite database
        self.db       = sqlite3.connect(':memory:')
        self.db_cursor= self.db.cursor()
        #create respective tables
        self.db.execute("CREATE TABLE sta_svec "+self.sta_svec_columns)
        self.db.commit()

    def connect(self):
        with open(self.sta_svec) as f:
            for x in f.readlines():
                x = x.rstrip('\n').split()
                l = x[:15]
                l.append(' '.join(x[15:]))
                self.db_cursor.execute(''' INSERT INTO sta_svec ''' + self.sta_svec_columns2 + ''' VALUES ''' + self.sta_svec_values , l)
                self.db.commit()

    def dump(self, table="sta_svec"):
        for row in self.db_cursor.execute('SELECT * FROM '+table):
            print " %.4s %.4s %.4d %.2d %.2d %.2d %.2d %5.2f %12.2f %-9.9s %11.4f %11.4f %11.4f %11.4f %.1s %-60.60s" % row
        

        

