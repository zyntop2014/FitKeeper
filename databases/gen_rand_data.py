import names, random, datetime, json, pymysql

DEFAULT_PIC_URL = "https://lh3.googleusercontent.com/-XdUIqdMkCWA/AAAAAAAAAAI/AAAAAAAAAAA/4252rscbv5M/photo.jpg"

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

def gen_lat_lng():
    """
    Generate Latitude and longitude randomly.
    Upper west to Midtown.
    """
    LAT_1 = 40.755433
    LNG_1 = -73.977127
    LAT_2 = 40.801709
    LNG_2 = -73.964767

    lat = random.uniform(LAT_1, LAT_2)
    lng = random.uniform(LNG_1, LNG_2)

    return lat, lng


def gen_profile(id):
    """
    Generate a profile in random.
    Return:
        p: a profile, in dict format.
    
    ### TODO ###
        1. Add latitude & longitude generater
           (around Columbia)
        
    """
    p = {}  # store profile info
    
    # Write ID
    p['id'] = id

    # Write user picture url
    p['picture'] = DEFAULT_PIC_URL
    
    # Generate date of birth
    today = datetime.datetime.today()
    idc = random.random()   #idc: indicator
    if idc < 0.65:
        delta = random.randint(19, 26)
    elif idc < 0.7:
        delta = random.randint(16, 18)
    elif idc < 0.95:
        delta = random.randint(27, 55)
    else:
        delta = random.randint(56, 70)
    dob = today - datetime.timedelta(days=delta*365)
    p['dob'] = str(dob.year) + '-' + str(dob.month) + '-' + str(dob.day)
    
    # Generate name (first+last) and gender
    genders = ('male', 'female')
    gender = genders[random.randint(0,1)]
    fn = names.get_first_name(gender=gender)
    ln = names.get_last_name()
    p['first_name'] = fn
    p['last_name'] = ln
    p['full_name'] = fn + ' ' + ln
    p['gender'] = gender
    
    # Generate email address
    prefix = fn[0].lower() + ln[0].lower() + str(random.randint(1000,9999))
    suffix = '@example.com'
    p['email'] = prefix + suffix

    # Generate workout record
    MIN = 0
    MAX = 50
    A = random.randint(MIN, MAX)
    B = random.randint(MIN, MAX)
    C = random.randint(MIN, MAX)
    D = random.randint(MIN, MAX)
    E = random.randint(MIN, MAX)
    total = A + B + C + D + E
    p['bas_times'] = A
    p['str_times'] = B
    p['car_times'] = C
    p['swi_times'] = D
    p['squ_times'] = E
    p['total_times'] = total
    
    # Generate signup date
    delta = random.randint(total, 365)
    sd = today - datetime.timedelta(days=delta)   # sd: signup date
    p['signup_date'] = str(sd.year) + '-' + str(sd.month) + '-' + str(sd.day)
    
    # Generate ratings
    def gen_ratings():
        """
        Generate each user's ratings.
        Distribution:
            70%: 3~5
            30%: 1~3
        """
        idc = random.random()  # idc: indicator
        if idc >= 0.3:
            rating = random.uniform(3,5)
        else:
            rating = random.uniform(1,3)
        return rating
    
    rating = gen_ratings()
    p['num_rating_times'] = int(total*random.uniform(1, 3))
    p['total_rating'] = int(rating*p['num_rating_times'])
    
    # Generate home address location (lat & lng)
    p['lat'], p['lng'] = gen_lat_lng()
    
    return p


def write_to_db(db, p):
    """
    Write profile to DB.
    """
    cur = db.cursor()
    try:
        cur.execute(
            "INSERT INTO USERS \
            (uid, name, email, dob, gender, family_name, given_name, photo, bas_ctr, \
            str_ctr, car_ctr, swi_ctr, squ_ctr, ctr, rating, rating_ctr, signup_date, lat, lng) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (str(p['id']), str(p['full_name']), str(p['email']), str(p['dob']),
             str(p['gender']), str(p['last_name']), str(p['first_name']),
             str(p['picture']), str(p['bas_times']), str(p['str_times']), str(p['car_times']),
             str(p['swi_times']), str(p['squ_times']), str(p['total_times']), str(p['total_rating']), 
             str(p['num_rating_times']), str(p['signup_date']), str(p['lat']), str(p['lng']),))
        db.commit()

    except:
        db.rollback()

    

if __name__ == '__main__':
    db = connect_db()
    for i in range(1, 201):
        p = gen_profile(i)
        write_to_db(db, p)