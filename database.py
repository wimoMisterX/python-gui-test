import sqlite3

def connect():
    return sqlite3.connect('wimo.db')

def require_db(func):
    '''
    Decorator for encapsulating a function with a db connection
    '''
    def db_wrap(*args, **kwargs):
        connection = connect()
        cursor = connection.cursor()
        output = func(cursor, *args, **kwargs)
        connection.commit()
        connection.close()
        return output
    return db_wrap

@require_db
def initialize_db(cursor):
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS `tickets` (
            `TICKET_NO`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            `TICKET_DATE`	TEXT NOT NULL,
            `TICKET_TIME`	TEXT NOT NULL,
            `TICKET_INFORMED_BY`	TEXT NOT NULL,
            `TICKET_DESCRIPTION`	TEXT NOT NULL
        )
        '''
    )

@require_db
def query(cursor, query_string, *args):
    '''
    Executes a query on the database and returns the results
    '''
    cursor.execute(query_string, *args)
    return cursor.fetchall()

def get_all_records():
    return query(
        '''
        SELECT * FROM `tickets`
        '''
    )

def get_record(number):
    return query(
        '''
        SELECT * FROM `tickets` WHERE `TICKET_NO`={}
        '''.format(number)
    )[0]

def add_record(record):
    query(
        '''
        INSERT INTO `tickets` (`TICKET_DATE`, `TICKET_TIME`, `TICKET_INFORMED_BY`, `TICKET_DESCRIPTION`) VALUES(?,?,?,?)
        ''',
        record
    )

def update_record(number, record):
    query(
        '''
        UPDATE `tickets` SET TICKET_DATE=?, TICKET_TIME=?, TICKET_INFORMED_BY=?, TICKET_DESCRIPTION=? WHERE `TICKET_NO`={}
        '''.format(number),
        record
    )
