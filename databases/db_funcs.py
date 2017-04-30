import json, pymysql


# Get info needed for db connection
with open('databases/db_info.json') as db_info_file:
    db_info = json.load(db_info_file)

# with open('db_info_shuyang.json') as file:
#     db_info = json.load(file)


def connect_db():
    """
    Connect to AWS RDS database.
    """
    db = pymysql.connect(
        db_info['host'],
        db_info['username'],
        db_info['password'],
        db_info['db']
    )
    return db


def user_init(db, profile):
    """
    Check if user's profile is in the database.
    If not, initialize the profile, write into database.
    """
    cur = db.cursor()
    cur.execute("select * from USERS \
                 WHERE uid = %s",
                 (profile['id']))
    res = cur.fetchall()
    if not len(res):
        # Profile initialization
        try:
            cur.execute(
                "INSERT INTO USERS \
                (uid, name, email, family_name, given_name, gender, dob, bas_ctr, \
                str_ctr, car_ctr, swi_ctr, squ_ctr, total_ctr, rating, rating_ctr, login_time) \
                VALUES \
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (str(profile['id']), str(profile['name']), str(profile['email']),
                 str(profile['family_name']), str(profile['given_name']),
                 str(profile['gender']), '1992-01-01', str(0), str(0), str(0),
                 str(0), str(0), str(0), str(0.0), str(0.0), str(0.0),))
            db.commit()
        except:
            db.rollback()
        
        print "Initialized user profile."
    else:
        print "Found user profile in DB."
    return None


def find_bus(db, bus_line, time1, time2):
    """
    Query table BUS,
    Input:
        bus_line: bus line number
        time1: start time
        time2: end time
    Return:
        Query result
    """
    cur = db.cursor()
    cur.execute("select line, departure_time from BUS \
                 WHERE line=%s \
                 and departure_time > CAST(%s AS time) \
                 and departure_time < CAST(%s AS time)",
                 (str(bus_line), str(time1), str(time2),))
    
    result = cur.fetchall()    
    return result



if __name__ == '__main__':
    db = connect_db()
    print find_bus(db, 'Blue line', '08:05:00', '09:08:00')
    if len(find_bus(db, 'Blue line', '08:05:00', '09:08:00')):
        print "hahah"
    else:
        print "hohoho"