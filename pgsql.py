import psycopg2

class pgsql ():
    def __init__(self):
        self.host = None
        self.port = None
        self.user = None
        self.passwd = None
        self.dbname = None

    def init (self, host, port, user, pwd, dbname):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = pwd
        self.dbname = dbname

    def select_query (self, query, dbname = None):
        
        if dbname != None:
            name = dbname
        else:
            name = self.dbname
        with psycopg2.connect("dbname='{0}' user='{1}' password='{2}' host='{3}' port='{4} ".
                                    format(dbname, self.user, self.passwd, self.host, self.port)
                                    ) as conn:
            cursor = conn.cursor ()
            data = cursor.execute (query)
            data = cursor.fetchall()      
            conn.close ()
            
        return data

