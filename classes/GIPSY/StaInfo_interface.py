# -*- coding: utf_8 -*-
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

import datetime as DT 
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
    sta_id          = "sta_id"      #In this file, a given station name is associated with a station identifier and a station number.
    sta_pos         = "sta_pos"     #This file associates the station identifier with the station coordinates at some epoch and the station velocity. 
    sta_svec        = "sta_svec"    #This file associates the station identifier with the sta vector and antenna type at some epoch.

    #for table sta_svec    
    sta_svec_colinit= "(to_sta TEXT, from_sta TEXT, year INTEGER, month INTEGER, day INTEGER, hour INTEGER, minute INTEGER, second REAL, \
                        duration REAL, antenna TEXT, arp_vec_east REAL, arp_vec_north REAL, arp_vec_up REAL, antenna_height REAL, \
                        sys_flag TEXT, comment TEXT, date TIMESTAMP)"
    sta_svec_columns= "(to_sta, from_sta, year, month, day, hour, minute, second, \
                        duration, antenna, arp_vec_east, arp_vec_north, arp_vec_up, antenna_height, \
                        sys_flag, comment, date)"
    sta_svec_values= " (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    #for table sta_id
    sta_id_colinit= "(sta_id TEXT PRIMARY KEY, sta_number INTEGER, comment TEXT)"
    sta_id_columns= "(sta_id, sta_number, comment)"
    sta_id_values= " (?, ?, ?)"

    #for table sta_pos
    sta_pos_colinit= "(sta_id TEXT, year INTEGER, month INTEGER, day INTEGER, hour INTEGER, minute INTEGER, second REAL, \
                        duration REAL, pos_x REAL, pos_y REAL, pos_z REAL, vel_x REAL, vel_y REAL, vel_z REAL, comment TEXT, date TIMESTAMP)"
    sta_pos_columns= "(sta_id, year, month, day, hour, minute, second, \
                        duration, pos_x, pos_y, pos_z, vel_x, vel_y, vel_z, comment, date)"
    sta_pos_values= " (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    db          = None
    db_cursor   = None

    force       = True

    def __init__(self):
        #
        self.sta_info_path = os.environ.get('GIPSY_STA_INFO')
        
        if self.sta_info_path is None:
            sys.stderr.write("GIPSY_STA_INFO environment variable not set, trying default GIPSY sta_info database at $GOA_VAR\n")

            self.sta_info_path = os.environ.get('GOA_VAR')

            if self.sta_info_path is None:
                raise ("Neither GIPSY_STA_INFO nor GOA_VAR environment variables set, can't connect to a database.\n")
            else:
                self.sta_info_path += "/sta_info"
                sys.stderr.write("Warning: working on original GIPSY sta_info database, changes may be overwritten on system update.\n")

        self.sta_id   = self.sta_info_path+"/"+self.sta_id
        self.sta_pos  = self.sta_info_path+"/"+self.sta_pos
        self.sta_svec = self.sta_info_path+"/"+self.sta_svec
        
        #set up in-memory SQLite database
        self.db       = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.db.text_factory = str
        self.db_cursor= self.db.cursor()
        #create respective tables
        self.db.execute("CREATE TABLE sta_svec "+self.sta_svec_colinit)
        self.db.execute("CREATE TABLE sta_id "  +self.sta_id_colinit)
        self.db.execute("CREATE TABLE sta_pos " +self.sta_pos_colinit)
        self.db.commit()

    def connect(self):
        with open(self.sta_svec) as f:
            for x in f.readlines():
                if not x.startswith('#'):
                    self.add_svec_line(x)

        with open(self.sta_id) as f:
            for x in f.readlines():
                if not x.startswith('#'):
                    self.add_id_line(x)
    
        with open(self.sta_pos) as f:
            for x in f.readlines():
                if not x.startswith('#'):
                    self.add_pos_line(x)

    def close(self):
        '''
        writes all changes made in memory back to database files.
        if this function is not called, all changes are lost!
        '''
        print "closing"  
        self.db_cursor.close()

##STA_POS FUNCTIONS
    def add_pos_line(self, line):
        import re
        x    = re.split(r'[: ]+',line.strip()) #need to split multiple separators here
        line = x[:14]
        line.append(' '.join(x[14:]))
        line.append(DT.datetime(int(line[1]), int(line[2]), int(line[3]), int(line[4]), int(line[5]), int(line[6].split('.')[0]))) 
        self.db.execute(''' INSERT INTO sta_pos ''' + self.sta_pos_columns + ''' VALUES ''' + self.sta_pos_values, line)
        self.db.commit()

    def got_pos(self, sta_id):
        self.db_cursor.execute('SELECT sta_id FROM sta_pos WHERE sta_id = "'+sta_id+'"')
        if self.db_cursor.fetchone() is None:
            return False
        else:
            return True


    def add_pos(self, sta_id, installed, X, Y, Z, Xvel, Yvel, Zvel):
        if self.got_pos(sta_id):
            #is it the same position as this one?
            for row in self.db_cursor.execute('SELECT * FROM sta_pos WHERE sta_id = "'+sta_id+'"'):
            	if installed == row[-1]:
            	    if row[8]!=X or row[9]!=Y or row[10]!=Z:
                        sys.stderr.write("We've already got an entry with a different position for station `%s' in sta_pos:\n" % sta_id)
                        sys.stderr.write("\t"+" ".join(str(e) for e in row)+"\n")
                        sys.stderr.write("\t Position to be added: %f, %f, %f \n"%(X,Y,Z))
                        sys.stderr.write("Please handle this manually!\n\n")
            	        
            	if installed < row[-1]:
            	    dt = row[-1] - installed
                    self.add_new_pos(sta_id, installed, X, Y, Z, Xvel, Yvel, Zvel)                
                    self.db_cursor.execute(' UPDATE sta_pos SET duration = ?  WHERE sta_id = ? AND date = ?', 
                                    (dt.days+dt.total_seconds()/86400.0, sta_id, installed))                    

            	if installed > row[-1]:
            	    dt = installed - row[-1]
                    self.add_new_pos(sta_id, installed, X, Y, Z, Xvel, Yvel, Zvel)                
                    self.db_cursor.execute(' UPDATE sta_pos SET duration = ?  WHERE sta_id = ? AND date = ?', 
                                    (dt.days+dt.total_seconds()/86400.0, sta_id, row[-1]))                    

        else:
            self.add_new_pos(sta_id, installed, X, Y, Z, Xvel, Yvel, Zvel)
            
    def add_new_pos(self, sta_id, installed, X, Y, Z, Xvel, Yvel, Zvel):
        self.db.execute(''' INSERT INTO sta_pos ''' + self.sta_pos_columns + ''' VALUES ''' + self.sta_pos_values, 
                            [ sta_id, installed.year, installed.month, installed.day, \
                              installed.hour, installed.minute, installed.second,\
                              1000001.00, X, Y, Z, Xvel, Yvel, Zvel,\
                              'updated through GPStools StaInfo_interface.py', installed])        

    def dump_sta_pos(self):
        #get all unique stations
        for sta in self.db.execute('SELECT DISTINCT sta_id FROM sta_pos'): 
            #get all rows for stations, print them ordered by datetime, which will not be printed!
            for row in self.db.execute("SELECT * FROM sta_pos WHERE sta_id = '" + sta[0] + "' ORDER BY date ASC"):
            	print " %.4s %.4d %.2d %.2d %.2d %.2d %5.2f %10.2f  %14.4f %14.4f %14.4f %15.7E %14.7E %14.7E %-30.30s" % row[:-1]

##STA_ID FUNCTIONS
    def add_id_line(self, line):
        x    = line.split()
        line = x[:2]
        line.append(' '.join(x[2:]))
        self.db.execute(''' INSERT INTO sta_id ''' + self.sta_id_columns + ''' VALUES ''' + self.sta_id_values, line)
        self.db.commit()

    def got_sta_id(self, sta_id):
        self.db_cursor.execute('SELECT sta_id FROM sta_id WHERE sta_id = "'+sta_id+'"')
        if self.db_cursor.fetchone() is None:
            return False
        else:
            return True
            
    def add_sta_id(self, sta_id, sta_number, sta_name):
        self.db_cursor.execute('INSERT OR IGNORE INTO sta_id '+self.sta_id_columns+' VALUES ("%s", 0, "%s")' % (sta_id, sta_name))

    def dump_sta_id(self):
        for row in self.db.execute("SELECT * FROM sta_id ORDER BY sta_id ASC"):
            	print " %.4s %6.6s %-60.60s" % row[:]

##SVEC FUNCTIONS
    def add_svec_line(self, line):
        x    = line.split()
        line = x[:15]
        line.append(' '.join(x[15:]))
        line.append(DT.datetime(int(line[2]), int(line[3]), int(line[4]), int(line[5]), int(line[6]), int(line[7].split('.')[0]))) 
        self.db.execute(''' INSERT INTO sta_svec ''' + self.sta_svec_columns + ''' VALUES ''' + self.sta_svec_values, line)
        self.db.commit()

    def update_svec(self, sta_id, antenna_info):
        for antenna in antenna_info:
            #as I am updating for each record, I need to refetch after the update
            self.db_cursor.execute('SELECT * FROM sta_svec WHERE to_sta = "'+sta_id+'" AND from_sta = "'+sta_id+'"')
            svec_data  = self.db_cursor.fetchall()

            #new entry for station
            if not svec_data: 
                self.add_new_svec(sta_id, antenna)
                continue
                
            #station already has entry
            else:            
                #check whether the record already exists and if not, where
                #to insert it and what the time difference 
                (got_record, insert_after, insert_before) = self.got_svec(antenna, svec_data)

                #if I don't have a record I need to figure out where to insert it
                #otherwise all is well
                if not got_record:
                    self.insert_svec(sta_id, antenna, svec_data, insert_after, insert_before)

    def got_svec(self, antenna, svec_data):
        got_record    = False
        insert_before = None
        insert_after  = -1
        
        #I need access to the indices of svec data
        for i in range(len(svec_data)):
            svec = svec_data[i]
            
            if antenna['installed'] == svec[-1]:
                got_record = True
                break 
            elif antenna['installed'] < svec[-1]:
                insert_after = i-1
                insert_before = i
                break

        return (got_record, insert_after, insert_before)

    def insert_svec(self, sta_id, antenna, svec_data=None, insert_after=-1, insert_before=None):
        
        #if we have pre-exisitng fields for this site we need to adjust the duration fields
        if svec_data is not None:
            dt = antenna['installed']-svec_data[insert_after][-1]
            
            #update prior record's duration field
            self.db_cursor.execute(' UPDATE sta_svec SET duration = ? WHERE to_sta = ? AND from_sta = ? AND date = ?', 
                                    (dt.total_seconds(), sta_id, sta_id, svec_data[insert_after][-1]))

            #insert myself into database
            self.add_new_svec(sta_id, antenna)

            #update my own duration unless I am the last entry
            if insert_before is not None:
                dt = svec_data[insert_before][-1] - antenna['installed']
    
                self.db_cursor.execute(' UPDATE sta_svec SET duration = ? WHERE to_sta = ? AND from_sta = ? AND date = ?', 
                                    (dt.total_seconds(), sta_id, sta_id, antenna['installed']))

        #else just add the new record
        else:        
            self.add_new_svec(sta_id, antenna)

    def add_new_svec(self, sta_id, antenna):
        self.db_cursor.execute('INSERT INTO sta_svec '+self.sta_svec_columns+' VALUES '+self.sta_svec_values, \
                  [ sta_id, sta_id, antenna['installed'].year, antenna['installed'].month, antenna['installed'].day, \
                    antenna['installed'].hour, antenna['installed'].minute, antenna['installed'].second,\
                    946080000.00, antenna['type'], antenna['arp_vec_east'], antenna['arp_vec_north'], antenna['arp_vec_up'],\
                    0.0, 'l', 'updated through GPStools StaInfo_interface.py', antenna['installed']])        

        
    def dump_svec(self, table="sta_svec"):
        #get all unique stations
        for sta in self.db.execute('SELECT DISTINCT to_sta FROM sta_svec'): 
            #get all rows for stations, print them ordered by datetime, which will not be printed!
            for row in self.db.execute("SELECT * FROM "+table+" WHERE to_sta = '" + sta[0] + "' ORDER BY date ASC"):
            	print " %.4s %.4s %.4d %.2d %.2d %.2d %.2d %5.2f %12.2f %-9.9s %11.4f %11.4f %11.4f %11.4f %.1s %-60.60s" % row[:-1]
        

        

