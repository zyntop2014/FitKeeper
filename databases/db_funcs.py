import json, pymysql, datetime, numpy, os

# path of db_info.json
db_info_filename = os.path.join(os.path.dirname(__file__), 'db_info.json')


DEFAULT_PIC_URL = "https://lh3.googleusercontent.com/-XdUIqdMkCWA/AAAAAAAAAAI/AAAAAAAAAAA/4252rscbv5M/photo.jpg"


# Read RDS info from file, connect to DB.
try:
    with open(db_info_filename) as db_info_file:
        db_info = json.load(db_info_file)
        db_info_file.close()
except IOError:
    with open('db_info.json') as db_info_file:
        print "[db_funcs.py]IO Error???"
        db_info = json.load(db_info_file)
        db_info_file.close()


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
    If not, initialize new user's profile, 
    and write into database.
    """
    if not profile['picture']:
        profile['picture'] = DEFAULT_PIC_URL
    cur = db.cursor()
    cur.execute("select * from USERS \
                 WHERE uid = %s",
                 (profile['id']))
    res = cur.fetchall()
    if not len(res):
        # No profile in DB of this user. Create new one.
        today = datetime.datetime.today()
        signup_date = str(today.year) + '-' + str(today.month) + '-' + str(today.day)
        try:
            cur.execute(
                "INSERT INTO USERS \
                (uid, name, email, family_name, given_name, photo, bas_ctr, \
                str_ctr, car_ctr, swi_ctr, squ_ctr, rating, rating_ctr, signup_date) \
                VALUES \
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (str(profile['id']), str(profile['name']), str(profile['email']),
                 str(profile['family_name']), str(profile['given_name']),
                 str(profile['picture']), str(0.0), str(0.0),
                 str(0.0), str(0.0), str(0.0), str(0), str(0), str(signup_date),))
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
    (address(lat & lng) is empty OR dob is empty).
    """
    cur = db.cursor()
    cur.execute("SELECT given_name, family_name, gender, dob, lat, lng \
                 FROM USERS \
                 WHERE uid = %s",
                 (str(id),))
    result = cur.fetchall()[0]
    # print result
    cur.close()
    
    for attr in result:
        if not attr:
            return False
    return True


def find_by_id(db, id):
    """
    Query profile database by user's id.
    **result: the entire row, no attribute missing.
    Return: None
    """
    cur = db.cursor()
    cur.execute("SELECT * FROM USERS \
                 WHERE uid = %s",
                 (str(id),))
    result = cur.fetchall()
    print result
    cur.close()
    return None


def update_profile(db, uid, fn, ln, bas_ctr, str_ctr,
                   car_ctr, swi_ctr, squ_ctr, 
                   gender, lat, lng, dob):
    """
    Update user's profile.
    fn: First Name / Given Name
    ln: Last Name / Family name
    """
    cur = db.cursor()
    full_name = fn + ' ' + ln
    
    try:
        cur.execute("UPDATE USERS \
                     SET lat = %s, lng = %s, name = %s, dob = %s, \
                         given_name = %s, family_name = %s, \
                         bas_ctr = %s, str_ctr = %s, car_ctr = %s, \
                         swi_ctr = %s, squ_ctr = %s, \
                         gender = %s \
                     WHERE uid = %s",
                    (str(lat), str(lng), str(full_name), str(dob), str(fn),
                     str(ln), str(bas_ctr), str(str_ctr), str(car_ctr), 
                     str(swi_ctr), str(squ_ctr), str(gender), str(uid),))
        db.commit()
        print "[USERS DB] Updated user's profile."
    except:
        db.rollback()
        print "[USERS DB] Update failed. Rollback Database."
    cur.close()
    return None


def get_user_email(db, uid):
    """
    Read user's email from profile DB.
    """
    cur = db.cursor()
    num_records = cur.execute("SELECT email \
                               FROM USERS \
                               WHERE uid = %s",
                               (str(uid),))
    record = cur.fetchall()[0]
    cur.close()

    return record[0]


def read_db_to_ml(db):
    """
    Read ALL data from database,
    then parse data (to "a list of tuple" format).
    Input:
        db: database object
    Return:
        res: Parsed format of each row,
             in "a list of tuples" format.
             This returned value can directly passed
             into K-means model.
    """
    cur = db.cursor()
    # Read id, ctrs of ALL data
    # num_rows: # of rows returned
    # iterate "cur" to get each row of returned data
    num_rows = cur.execute("SELECT uid, bas_ctr, str_ctr, car_ctr, swi_ctr, squ_ctr \
                            FROM USERS")
    res = []
    for row in cur:
        r = (row[0], row[1], row[2], row[3], row[4], row[5])
        res.append(r)
    cur.close()
    # print res
    return res


def calculate_age(born):
    """
    Compute age according to 2 datetime.date objects.
    Input:
        born: user's DOB, in datetime.date format
    Return:
        User's age
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
    query = "SELECT uid, dob, rating, rating_ctr, signup_date, lat, lng,\
             bas_ctr, str_ctr, car_ctr, swi_ctr, squ_ctr \
             FROM USERS \
             WHERE uid IN (%s)" % ','.join(ids)
    num_rows = cur.execute(query)
    res = []

    for row in cur:
        uid = row[0]
        birth_date = row[1]
        age = calculate_age(birth_date)    # filter feature
        avg_rating = (float(row[2])/row[3]) if row[3] else 0.0   # filter feature
        signup_date = row[4]
        # days_delta = (today-signup_date).days
        # freq = (float(row[2])/days_delta) if days_delta else 0.0   # filter feature
        lat, lng = row[5], row[6]
        # bas_ratio = (float(row[8])/row[2]) if row[2] else 0
        # str_ratio = (float(row[9])/row[2]) if row[2] else 0
        # car_ratio = (float(row[10])/row[2]) if row[2] else 0
        # swi_ratio = (float(row[11])/row[2]) if row[2] else 0
        # squ_ratio = (float(row[12])/row[2]) if row[2] else 0
        bas_ctr = row[7]
        str_ctr = row[8]
        car_ctr = row[9]
        swi_ctr = row[10]
        squ_ctr = row[11]
        r = (uid, age, avg_rating, (lat, lng), 
             (bas_ctr, str_ctr, car_ctr, swi_ctr, squ_ctr))
        res.append(r)

    cur.close()
    return res


def read_profile(db, ids):
    """
    Query profile DB using input IDs,
    return the entire row of each ID.
    Input:
        ids: A list of IDs
    Return:

    """
    cur = db.cursor()
    res = []
    for uid in ids:
        query = "SELECT * \
                FROM USERS \
                WHERE uid = %s" %(uid)
        num_rows = cur.execute(query)   
        row = cur.fetchall()[0]
        r = {}
        # Original Data
        r['uid'] = row[0]
        r['name'] = row[1]
        r['email'] = row[2]
        r['photo'] = row[3]
        r['family_name'] = row[4]
        r['given_name'] = row[5]
        r['gender'] = row[6]
        r['dob'] = row[7]
        r['bas_ctr'] = row[8]
        r['str_ctr'] = row[9]
        r['car_ctr'] = row[10]
        r['swi_ctr'] = row[11]
        r['squ_ctr'] = row[12]
        r['rating'] = row[13]
        r['rating_ctr'] = row[14]
        r['signup_date'] = row[15]
        r['lat'] = row[16]
        r['lng'] = row[17]
        # Derived Data
        r['avg_rating'] = (row[13] / float(row[14])) if row[14] else 0.0
        r['age'] = calculate_age(row[7])
        r['addr'] = (row[16], row[17])
        res.append(r)
    
    cur.close()
    return res


def update_photo(db, uid, url):
    """
    Update user's photo url.
    """
    cur = db.cursor()
    try:
        cur.execute("UPDATE USERS \
                    SET photo = %s \
                    WHERE uid = %s", 
                    (str(url), str(uid),))
        db.commit()
        print "[USERS DB] Updated phoo URL."
    except:
        db.rollback()
        print "[USERS DB] Update failed. Rollback Database."
    cur.close()
    return None



def update_records(db, uid, ctr=0, rating=0, rating_ctr=0, bas_ctr=0, str_ctr=0,
                   car_ctr=0, swi_ctr=0, squ_ctr=0):
    """
    After each workout/hangout, update workout & rating
    records.
    """
    cur = db.cursor()

    # Read record to be updated
    cur.execute("SELECT uid, bas_ctr, str_ctr, car_ctr, swi_ctr, \
                        squ_ctr, rating, rating_ctr \
                 FROM USERS \
                 WHERE uid = %s",
                (str(uid),)
                )
    res = cur.fetchall()[0]

    # Update record
    bas_ctr += res[1]
    str_ctr += res[2]
    car_ctr += res[3]
    swi_ctr += res[4]
    squ_ctr += res[5]
    rating += res[6]
    rating_ctr += res[7]
    data = (str(bas_ctr), str(str_ctr),
            str(car_ctr), str(swi_ctr), str(squ_ctr),
            str(rating), str(rating_ctr), str(uid),)
    try:
        cur.execute("UPDATE USERS \
                    SET bas_ctr = %s, str_ctr = %s, car_ctr = %s, \
                        swi_ctr = %s, squ_ctr = %s, \
                        rating = %s, rating_ctr = %s \
                    WHERE uid = %s",
                    data)
        db.commit()
    except:
        db.rollback()
    
    cur.close()
    return None


if __name__ == '__main__':
    db = connect_db()
    print is_profile_complete(db, '12')
    