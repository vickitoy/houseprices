import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
import MySQLdb as mdb
import re
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

passfile = '/Users/vickitoy/sideprojects/houseprices/password.txt'

def password_ret(passfile=passfile):
    """
    NAME:
        password_ret
    PURPOSE:
        Parse password text file into dictionary
    INPUT:
        passfile - password txt file that is formated (database, username, password)
    """
    
    passdict = {}
    with open(passfile, 'r') as f:
        for line in f:
            idb, iuser, ipass = line.split(',')
            passdict[idb] = (iuser, ipass)
            
    return passdict

def makesqltable(tablename, csvfile):
    """
    NAME:
        makesqltable
    PURPOSE:
        Makes mySQL table for Zillow median sold houses files, makes ID auto-incremented
    INPUTS:
        tablename - name of table to make
        csvfile   - file with csv data
    ASSUMPTIONS:    
        csvfile has a header for first line
    """
    
    passdict = password_ret(passfile=passfile)
    
    # connect(host, database username, password, database)
    db = 'testdb'
    
    con = mdb.connect('localhost', passdict[db][0], passdict[db][1], db)
    
    # Don't need to do error handling or closing when using the "with"
    with con:
        
        # Creates Writers table within testdb
        cur = con.cursor()   
        sqltable = """CREATE TABLE %s (
                        ID int NOT NULL AUTO_INCREMENT,
                        regionID INT,
                        regionName VARCHAR(5),
                        city VARCHAR(50),
                        state VARCHAR(2),
                        metro VARCHAR(50),
                        countyName VARCHAR(50),
                        sizeRank INT,
                        1996_04 INT,1996_05 INT,1996_06 INT,
                        1996_07 INT,1996_08 INT,1996_09 INT,1996_10 INT,1996_11 INT,1996_12 INT,
                        1997_01 INT,1997_02 INT,1997_03 INT,1997_04 INT,1997_05 INT,1997_06 INT,
                        1997_07 INT,1997_08 INT,1997_09 INT,1997_10 INT,1997_11 INT,1997_12 INT,
                        1998_01 INT,1998_02 INT,1998_03 INT,1998_04 INT,1998_05 INT,1998_06 INT,
                        1998_07 INT,1998_08 INT,1998_09 INT,1998_10 INT,1998_11 INT,1998_12 INT,
                        1999_01 INT,1999_02 INT,1999_03 INT,1999_04 INT,1999_05 INT,1999_06 INT,
                        1999_07 INT,1999_08 INT,1999_09 INT,1999_10 INT,1999_11 INT,1999_12 INT,
                        2000_01 INT,2000_02 INT,2000_03 INT,2000_04 INT,2000_05 INT,2000_06 INT,
                        2000_07 INT,2000_08 INT,2000_09 INT,2000_10 INT,2000_11 INT,2000_12 INT,
                        2001_01 INT,2001_02 INT,2001_03 INT,2001_04 INT,2001_05 INT,2001_06 INT,
                        2001_07 INT,2001_08 INT,2001_09 INT,2001_10 INT,2001_11 INT,2001_12 INT,
                        2002_01 INT,2002_02 INT,2002_03 INT,2002_04 INT,2002_05 INT,2002_06 INT,
                        2002_07 INT,2002_08 INT,2002_09 INT,2002_10 INT,2002_11 INT,2002_12 INT,
                        2003_01 INT,2003_02 INT,2003_03 INT,2003_04 INT,2003_05 INT,2003_06 INT,
                        2003_07 INT,2003_08 INT,2003_09 INT,2003_10 INT,2003_11 INT,2003_12 INT,
                        2004_01 INT,2004_02 INT,2004_03 INT,2004_04 INT,2004_05 INT,2004_06 INT,
                        2004_07 INT,2004_08 INT,2004_09 INT,2004_10 INT,2004_11 INT,2004_12 INT,
                        2005_01 INT,2005_02 INT,2005_03 INT,2005_04 INT,2005_05 INT,2005_06 INT,
                        2005_07 INT,2005_08 INT,2005_09 INT,2005_10 INT,2005_11 INT,2005_12 INT,
                        2006_01 INT,2006_02 INT,2006_03 INT,2006_04 INT,2006_05 INT,2006_06 INT,
                        2006_07 INT,2006_08 INT,2006_09 INT,2006_10 INT,2006_11 INT,2006_12 INT,
                        2007_01 INT,2007_02 INT,2007_03 INT,2007_04 INT,2007_05 INT,2007_06 INT,
                        2007_07 INT,2007_08 INT,2007_09 INT,2007_10 INT,2007_11 INT,2007_12 INT,
                        2008_01 INT,2008_02 INT,2008_03 INT,2008_04 INT,2008_05 INT,2008_06 INT,
                        2008_07 INT,2008_08 INT,2008_09 INT,2008_10 INT,2008_11 INT,2008_12 INT,
                        2009_01 INT,2009_02 INT,2009_03 INT,2009_04 INT,2009_05 INT,2009_06 INT,
                        2009_07 INT,2009_08 INT,2009_09 INT,2009_10 INT,2009_11 INT,2009_12 INT,
                        2010_01 INT,2010_02 INT,2010_03 INT,2010_04 INT,2010_05 INT,2010_06 INT,
                        2010_07 INT,2010_08 INT,2010_09 INT,2010_10 INT,2010_11 INT,2010_12 INT,
                        2011_01 INT,2011_02 INT,2011_03 INT,2011_04 INT,2011_05 INT,2011_06 INT,
                        2011_07 INT,2011_08 INT,2011_09 INT,2011_10 INT,2011_11 INT,2011_12 INT,
                        2012_01 INT,2012_02 INT,2012_03 INT,2012_04 INT,2012_05 INT,2012_06 INT,
                        2012_07 INT,2012_08 INT,2012_09 INT,2012_10 INT,2012_11 INT,2012_12 INT,
                        2013_01 INT,2013_02 INT,2013_03 INT,2013_04 INT,2013_05 INT,2013_06 INT,
                        2013_07 INT,2013_08 INT,2013_09 INT,2013_10 INT,2013_11 INT,2013_12 INT,
                        2014_01 INT,2014_02 INT,2014_03 INT,2014_04 INT,2014_05 INT,2014_06 INT,
                        2014_07 INT,2014_08 INT,2014_09 INT,2014_10 INT,2014_11 INT,2014_12 INT,
                        2015_01 INT,2015_02 INT,2015_03 INT,2015_04 INT,2015_05 INT,2015_06 INT,
                        2015_07 INT,2015_08 INT,2015_09 INT,2015_10 INT,2015_11 INT,2015_12 INT,
                        2016_01 INT,2016_02 INT,2016_03 INT,2016_04 INT,2016_05 INT,2016_06 INT,
                        PRIMARY KEY(ID)) 
                    """  % (tablename)
        cur.execute(sqltable)
        sqlload = """LOAD DATA LOCAL INFILE '{}'
                        INTO TABLE %s
                        FIELDS TERMINATED BY ','
                        OPTIONALLY ENCLOSED BY '"'
                        LINES TERMINATED BY '\n'
                        IGNORE 1 LINES
                        (regionID,regionName,city,state,metro,countyName,sizeRank,
                        1996_04, 1996_05, 1996_06, 
                        1996_07, 1996_08, 1996_09, 1996_10, 1996_11, 1996_12, 
                        1997_01, 1997_02, 1997_03, 1997_04, 1997_05, 1997_06, 
                        1997_07, 1997_08, 1997_09, 1997_10, 1997_11, 1997_12, 
                        1998_01, 1998_02, 1998_03, 1998_04, 1998_05, 1998_06, 
                        1998_07, 1998_08, 1998_09, 1998_10, 1998_11, 1998_12, 
                        1999_01, 1999_02, 1999_03, 1999_04, 1999_05, 1999_06, 
                        1999_07, 1999_08, 1999_09, 1999_10, 1999_11, 1999_12, 
                        2000_01, 2000_02, 2000_03, 2000_04, 2000_05, 2000_06, 
                        2000_07, 2000_08, 2000_09, 2000_10, 2000_11, 2000_12, 
                        2001_01, 2001_02, 2001_03, 2001_04, 2001_05, 2001_06, 
                        2001_07, 2001_08, 2001_09, 2001_10, 2001_11, 2001_12, 
                        2002_01, 2002_02, 2002_03, 2002_04, 2002_05, 2002_06, 
                        2002_07, 2002_08, 2002_09, 2002_10, 2002_11, 2002_12, 
                        2003_01, 2003_02, 2003_03, 2003_04, 2003_05, 2003_06, 
                        2003_07, 2003_08, 2003_09, 2003_10, 2003_11, 2003_12, 
                        2004_01, 2004_02, 2004_03, 2004_04, 2004_05, 2004_06, 
                        2004_07, 2004_08, 2004_09, 2004_10, 2004_11, 2004_12, 
                        2005_01, 2005_02, 2005_03, 2005_04, 2005_05, 2005_06, 
                        2005_07, 2005_08, 2005_09, 2005_10, 2005_11, 2005_12, 
                        2006_01, 2006_02, 2006_03, 2006_04, 2006_05, 2006_06, 
                        2006_07, 2006_08, 2006_09, 2006_10, 2006_11, 2006_12, 
                        2007_01, 2007_02, 2007_03, 2007_04, 2007_05, 2007_06, 
                        2007_07, 2007_08, 2007_09, 2007_10, 2007_11, 2007_12, 
                        2008_01, 2008_02, 2008_03, 2008_04, 2008_05, 2008_06, 
                        2008_07, 2008_08, 2008_09, 2008_10, 2008_11, 2008_12, 
                        2009_01, 2009_02, 2009_03, 2009_04, 2009_05, 2009_06, 
                        2009_07, 2009_08, 2009_09, 2009_10, 2009_11, 2009_12, 
                        2010_01, 2010_02, 2010_03, 2010_04, 2010_05, 2010_06, 
                        2010_07, 2010_08, 2010_09, 2010_10, 2010_11, 2010_12, 
                        2011_01, 2011_02, 2011_03, 2011_04, 2011_05, 2011_06, 
                        2011_07, 2011_08, 2011_09, 2011_10, 2011_11, 2011_12, 
                        2012_01, 2012_02, 2012_03, 2012_04, 2012_05, 2012_06, 
                        2012_07, 2012_08, 2012_09, 2012_10, 2012_11, 2012_12, 
                        2013_01, 2013_02, 2013_03, 2013_04, 2013_05, 2013_06, 
                        2013_07, 2013_08, 2013_09, 2013_10, 2013_11, 2013_12, 
                        2014_01, 2014_02, 2014_03, 2014_04, 2014_05, 2014_06, 
                        2014_07, 2014_08, 2014_09, 2014_10, 2014_11, 2014_12, 
                        2015_01, 2015_02, 2015_03, 2015_04, 2015_05, 2015_06, 
                        2015_07, 2015_08, 2015_09, 2015_10, 2015_11, 2015_12, 
                        2016_01, 2016_02, 2016_03, 2016_04, 2016_05, 2016_06)
                        SET ID = NULL;;"""  % (tablename)               
        cur.execute(sqlload.format(csvfile))
        
def statequery(stid='MD'):
    """
    NAME:
        statequery
    PURPOSE:
        Performs a query on the "medhousesold" table in mySQL to group based on state
    INPUT:
        stid - abbreviated state id
    OUTPUT:
        statehouse - query to mySQL
    """
    Base = automap_base()
    
    passdict = password_ret(passfile=passfile)
    
    # connect(host, database username, password, database)
    db = 'testdb'
    
    engine = sqlalchemy.create_engine('mysql://'+passdict[db][0]+':'+passdict[db][1]+'@localhost/'+db, echo=False)   
    
    Session = sessionmaker()
    session = Session()
    
    # Reflect means grab all existing tables from engine (prepare them into same class as base)
    Base.prepare(engine, reflect=True)
    
    ################## Query for all columns for a state ##################
    house = Base.classes.medhousesold
    statehouse = session.query(*[c for c in house.__table__.c]).filter(house.state == stid)
    
    return statehouse

def statehouse():
    """
    NAME:
        statehouse
    PURPOSE:
        Runs query with pandas and returns a pandas dataframe from query
    """
    passdict = password_ret(passfile=passfile)
    
    # connect(host, database username, password, database)
    db = 'testdb'
    
    engine = sqlalchemy.create_engine('mysql://'+passdict[db][0]+':'+passdict[db][1]+'@localhost/'+db, echo=False)    
    conn=engine.connect()

    a = statequery()
    
    sh = pd.read_sql(a.statement, conn)
    
    return sh
       
def ushouse(month='1996_06'):
    """
    NAME:
        ushouse
    PURPOSE:
        Direct SQL query to find average of each state (removing zip codes with no sold houses)
        and returning pandas dataframe
    INPUT:
        month - month to run query for in YYYY_MM format
    """

    passdict = password_ret(passfile=passfile)
    
    # connect(host, database username, password, database)
    db = 'testdb'
    
    engine = sqlalchemy.create_engine('mysql://'+passdict[db][0]+':'+passdict[db][1]+'@localhost/'+db, echo=False)    
    conn=engine.connect()

    sql = 'SELECT state,AVG(%s) as avg_house from medhousesold WHERE %s >0 GROUP BY state;' % (month, month)
    
    ush = pd.read_sql_query(sql, conn)
    
    return ush

def stateabbr():
    """
    NAME:
        stateabbr
    PURPOSE:
        Direct SQL query to find average of each state (removing zip codes with no sold houses)
        and returning pandas dataframe
    INPUT:
        month - month to run query for in YYYY_MM format
    """

    passdict = password_ret(passfile=passfile)
    
    # connect(host, database username, password, database)
    db = 'testdb'
    
    engine = sqlalchemy.create_engine('mysql://'+passdict[db][0]+':'+passdict[db][1]+'@localhost/'+db, echo=False)    
    conn=engine.connect()

    sql = 'SELECT * from states;'
    
    states = pd.read_sql_query(sql, conn)
    
    return states
