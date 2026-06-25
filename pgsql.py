import psycopg2
import logging
import logprefix

class pgsql ():
    def __init__(self, caller=None):
        self.host = None
        self.port = None
        self.user = None
        self.passwd = None
        self.dbname = None
        self.logger = logprefix.LogPrefix("{0}.{1}".format (caller, __name__) , logging.getLogger())

    def init (self, host, port, user, pwd, dbname):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = pwd
        self.dbname = dbname

    def select_query_dict (self, fields, fromclause, whereclause, dbname = None):
        name = self.dbname
        
        if dbname != None:
            name = dbname
        query = "SELECT " + ",".join(fields) + " " + fromclause + " ;"
        if len (whereclause) > 0:
            query = "SELECT " + ",".join(fields) + " " + fromclause + " " + whereclause + " ;"

        with psycopg2.connect("dbname='{0}' user='{1}' password='{2}' host='{3}' port='{4}' ".
                                    format(name, self.user, self.passwd, self.host, self.port)
                                    ) as conn:
            cursor = conn.cursor ()
            self.logger.debug(query)
            data = cursor.execute (query)
            data = cursor.fetchall()      
            self.logger.debug(data)

            result = []
            if len (data) > 0:
                for row in data:
                    rowdic = {}
                    for i in range(len(fields)):
                        rowdic[fields[i]] = row[i]
                    result.append(rowdic)    
            return result

    def select_query (self, query, dbname = None):
        name = self.dbname
        
        if dbname != None:
            name = dbname
        
        with psycopg2.connect("dbname='{0}' user='{1}' password='{2}' host='{3}' port='{4}' ".
                                    format(name, self.user, self.passwd, self.host, self.port)
                                    ) as conn:
            cursor = conn.cursor ()
            self.logger.debug(query)
            data = cursor.execute (query)
            data = cursor.fetchall()      
            self.logger.debug("query result:{0}".format(data))
            
        return data
    
    def update_query (self, query, dbname = None):
        name = self.dbname
        nbr = -1
        if dbname != None:
            name = dbname
        
        with psycopg2.connect("dbname='{0}' user='{1}' password='{2}' host='{3}' port='{4}' ".
                                    format(name, self.user, self.passwd, self.host, self.port)
                                    ) as conn:
            cursor = conn.cursor ()
            #self.logger.debug(query)
            data = cursor.execute (query)
            nbr = cursor.rowcount
            self.logger.debug("query: {1} update {0} row(s)".format(nbr, query))
            
        return nbr

