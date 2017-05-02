import json, pymysql


# Get info needed for db connection
# with open('db_info.json') as db_info_file:
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
    if not profile['picture']:
        profile['picture'] = "https://lh3.googleusercontent.com/-XdUIqdMkCWA/AAAAAAAAAAI/AAAAAAAAAAA/4252rscbv5M/photo.jpg"
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
                (uid, name, email, gender, family_name, given_name, photo, bas_ctr, \
                str_ctr, car_ctr, swi_ctr, squ_ctr, total_ctr, rating, rating_ctr, login_time) \
                VALUES \
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (str(profile['id']), str(profile['name']), str(profile['email']),
                 str(profile['gender'], str(profile['family_name']), str(profile['given_name']),
                 str(profile['picture']), str(0), str(0), str(0),
                 str(0), str(0), str(0), str(0.0), str(0.0), str(0.0),)))
            db.commit()
            print "[user_init]Initialized user profile."
        except:
            db.rollback()
            print '[user_init]Database rollback.'
        
        
    else:
        print "[user_init]Found user profile in DB."
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
    
    return None


def gen_random_data():
    """
    Generate random data.
    Default user picture url:
    "https://lh3.googleusercontent.com/-XdUIqdMkCWA/AAAAAAAAAAI/AAAAAAAAAAA/4252rscbv5M/photo.jpg"
    """




if __name__ == '__main__':
    with open('test_user_profile.json') as f:
        profile = json.load(f)
    db = connect_db()
    cur = db.cursor()
    cur.execute(
                "INSERT INTO USERS \
                (uid, name, email, family_name, given_name, photo, bas_ctr, \
                str_ctr, car_ctr, swi_ctr, squ_ctr, total_ctr, rating, rating_ctr, login_time) \
                VALUES \
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (str(profile['id']), str(profile['name']), str(profile['email']),
                 str(profile['family_name']), str(profile['given_name']),
                 str(profile['picture']), str(0), str(0), str(0),
                 str(0), str(0), str(0), str(0.0), str(0.0), str(0.0),))
    db.commit()
