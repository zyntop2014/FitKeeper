import json, pymysql, faker, datetime, numpy
from faker import Factory

DEFAULT_PIC_URL = "https://lh3.googleusercontent.com/-XdUIqdMkCWA/AAAAAAAAAAI/AAAAAAAAAAA/4252rscbv5M/photo.jpg"
# Get info needed for db connection
# with open('db_info.json') as db_info_file:
try:
    with open('databases/db_info.json') as db_info_file:
        db_info = json.load(db_info_file)
except IOError:
    with open('db_info.json') as db_info_file:
        db_info = json.load(db_info_file)


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
    if not profile['picture']:
        profile['picture'] = DEFAULT_PIC_URL
    cur = db.cursor()
    cur.execute("select * from USERS \
                 WHERE uid = %s",
                 (profile['id']))
    res = cur.fetchall()
    if not len(res):
        # Profile initialization
        today = datetime.datetime.today()
        signup_date = str(today.year) + '-' + str(today.month) + '-' + str(today.day)
        try:
            cur.execute(
                "INSERT INTO USERS \
                (uid, name, email, gender, family_name, given_name, photo, bas_ctr, \
                str_ctr, car_ctr, swi_ctr, squ_ctr, ctr, rating, signup_date) \
                VALUES \
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (str(profile['id']), str(profile['name']), str(profile['email']),
                 str(profile['gender'], str(profile['family_name']), str(profile['given_name']),
                 str(profile['picture']), str(0), str(0), str(0),
                 str(0), str(0), str(0), str(0), str(signup_date),)))
            db.commit()
            print "[user_init]Initialized user profile."
        except:
            db.rollback()
            print '[user_init]Database rollback.'
        
        
    else:
        print "[user_init]Found user profile in DB."
    cur.close()
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
    cur.execute("SELECT line, departure_time FROM BUS \
                 WHERE line=%s \
                 AND departure_time > CAST(%s AS time) \
                 AND departure_time < CAST(%s AS time)",
                 (str(bus_line), str(time1), str(time2),))
    result = cur.fetchall()
    cur.close()
    return result


def is_profile_complete(db, id):
    """
    Check if user's profile is complete
    (address is not None OR dob is not None).
    """
    cur = db.cursor()
    cur.execute("SELECT addr, dob FROM USERS \
                 WHERE uid = %s",
                 (str(id)))
    result = cur.fetchall()
    # if result == ((None, None),)
    cur.close()
    if (not result[0][0]) or (not result[0][1]):
        return False
    return True


def find_by_id(db, id):
    cur = db.cursor()
    cur.execute("SELECT * FROM USERS  \
                 WHERE uid = %s",
                 (str(id)))
    result = cur.fetchall()
    print result
    cur.close()
    return None


def update_profile(db, id, addr, dob):
    """
    Update user's profile.
    Write (or overwrite) attributes "addr", "dob", etc.
    """
    cur = db.cursor()
    try:
        cur.execute("UPDATE USERS \
                    SET addr = %s, dob = %s",
                    (str(addr), str(dob)))
        db.commit()
        print "Updated user's profile."
    except:
        db.rollback()
    cur.close()
    return None


def read_db_to_ml(db):
    """
    Read data from database,
    parse data (to "a list of tuple" format).
    Input:
        db: database object

    """
    cur = db.cursor()
    # Read id, ctrs of all data
    # data: # of rows returned
    # iterate "cur" to get each row of returned data
    num_rows = cur.execute("SELECT uid, bas_ctr, str_ctr, car_ctr, swi_ctr, squ_ctr, ctr \
                        FROM USERS")
    res = []
    for row in cur:
        s = float(row[6])
        r = (row[0], row[1]/s, row[2]/s, row[3]/s, row[4]/s, row[5]/s,)
        res.append(r)
    cur.close()
    # print res
    return res


def calculate_age(born):
    """
    Compute age according to two datetime.date()
    """
    today = datetime.date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def read_db_to_filter(db, ids):
    """
    Read data from database according to input ids,
    parse query result, and send them to filter.
    Attributes to read:
        dob, lat & lng, ctr, rating
    Return:
        res: A list of tuples.
        each tuple:
            (uid, age, avg_rating, avg_usage(times per day), (lat, lng))
    """
    today = datetime.date.today()
    cur = db.cursor()
    query = "SELECT uid, dob, ctr, rating, signup_date, lat, lng \
             FROM USERS \
             WHERE uid IN (%s)" % ','.join(ids)
    num_rows = cur.execute(query)
    cur.close()
    res = []
    for row in cur:
        birth_date = datetime.datetime.strptime(row[1], '%Y-%m-%d').date()
        age = calculate_age(birth_date)    # filter feature
        avg_rating = float(row[3]) / row[2]   # filter feature
        signup_date = datetime.datetime.strptime(row[4]).date()
        avg_usage = float(row[2]) / (today-signup_date).days   # filter feature
        lat, lng = row[5], row[6]
        r = (row[0], age, avg_rating, avg_usage, (lat, lng))
        res.append(r)
    
    return res


def read_basic_info(db, ids):
    """
    Query basic infomation of each user (whose id in 'ids'),
    Queried result is for display purposes.

    """
    cur = db.cursor()
    # Substitute attributes below to required ones
    query = "SELECT uid, dob, ctr, rating, signup_date, lat, lng \
             FROM USERS \
             WHERE uid IN (%s)" % ','.join(ids)
    num_rows = cur.execute(query)
    cur.close()
    res = []
    for row in cur:
        id = row[0]
        r = (id)
        res.append(r)

    return res


def update_records(db, uid, ctr=0, rating=0, bas_ctr=0, str_ctr=0,
                   car_ctr=0, swi_ctr=0, squ_ctr=0):
    """
    After each workout/hangout, update workout & rating
    records. 
    """
    cur = db.cursor()
    cur.execute("SELECT uid, bas_ctr, str_ctr, car_ctr, swi_ctr, \
                        squ_ctr, ctr, rating \
                 FROM USERS \
                 WHERE uid = %s",
                (str(uid))
                )
    res = cur.fetchall()[0]

    # Update records
    bas_ctr += res[1]
    str_ctr += res[2]
    car_ctr += res[3]
    swi_ctr += res[4]
    squ_ctr += res[5]
    ctr += res[6]
    rating += res[7]
    data = (str(bas_ctr), str(str_ctr),
            str(car_ctr), str(swi_ctr), str(squ_ctr),
            str(ctr), str(rating), str(uid))
    try:
        cur.execute("UPDATE USERS \
                    SET bas_ctr = %s, str_ctr = %s, car_ctr = %s, \
                        swi_ctr = %s, squ_ctr = %s, ctr = %s, \
                        rating = %s \
                    WHERE uid = %s",
                    data)
        db.commit()
    except:
        db.rollback()
    
    cur.close()
    return None


if __name__ == '__main__':
    import sys
    sys.path.append('../ml/')
    from kmeans import kmeans
    db = connect_db()
    rows = read_db_to_ml(db)
    (g, ggm) = kmeans(rows)
    print '[group]'
    print json.dumps(g, indent=4, sort_keys=True)
    print '[get group member]'
    print json.dumps(ggm, indent=4, sort_keys=True)
    print ggm['1']

