from flask import Flask, render_template, request, g, redirect, url_for, session, flash
from flask_oauth import OAuth
import sqlite3 as sql
from functools import wraps
import psycopg2, json, datetime
import os, json
from werkzeug.utils import secure_filename
import pymysql
from datetime import datetime as dt
import sys
sys.path.append('calendar/')
sys.path.append('databases/')
sys.path.append('ml/')
from mycalendar import *
from db_funcs import *
from recommendation import *

#import transloc

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


UPLOAD_FOLDER = 'static/img/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
GOOGLE_CLIENT_ID = '852263075688-3u85br5hvvk6ajvrafavv3lpupns3va7.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'l7a5ztJX5bW9iZBTq81GP-pg'
REDIRECT_URI = '/oauth2callback'
SECRET_KEY = '8(2:W\x909\x01\xb3F\xd0\x11\x85\xc56\xd1h\xf5\x1bu\r[\xab\x9f'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = SECRET_KEY

oauth = OAuth()
google = oauth.remote_app(
	'google',
	base_url='https://www.google.com/accounts/',
	authorize_url='https://accounts.google.com/o/oauth2/auth',
	request_token_url=None,
	request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/calendar',
		                'response_type': 'code'},
	access_token_url='https://accounts.google.com/o/oauth2/token',
	access_token_method='POST',
	access_token_params={'grant_type': 'authorization_code'},
	consumer_key=GOOGLE_CLIENT_ID,
	consumer_secret=GOOGLE_CLIENT_SECRET
)

# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            #flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap


# complete profile info required decorator
def comp_profile_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'comp_info' in session:
            print "Profile completion check passed."
            return f(*args, **kwargs)
        else:
            return redirect(url_for('comp_info'))
    return wrap


@app.route('/google')
def g_index():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('google_login'))

    access_token = access_token[0]  # secret = access_token[1]
    from urllib2 import Request, urlopen, URLError
    headers = {'Authorization': 'OAuth '+access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    req_cal = Request('https://www.googleapis.com/calendar/v3/calendars/primary/events',
                      None, headers)

    try:
        res = urlopen(req)
        res_cal = urlopen(req_cal)
        # print (res)
        # print 'res_cal: ',res_cal
    except URLError, e:
        if e.code == 401:
            # Unauthorized - bad token
            session.pop('access_token', None)
            return redirect(url_for('google_login'))
        return res.read()

    # Successful login. Extract user information
    session['logged_in'] = True  
    profile = json.loads(res.read())
    print json.dumps(profile, indent=4, sort_keys=True)
    google_calendar = json.loads(res_cal.read())
    session['profile'] = profile
    session['user_id'] = profile['id']
    # if is_in_dynamo(session['user_id']) == False:
    #     # No unhandled ratings in Dynamo
    #     session['unhandled_rating'] = False
    # else:
    #     session['unhandled_rating'] = True

    # session['calendar'] = google_calendar['items']  # When not commented out, buslist cannot be accessed
    # add_event(google, session['access_token'][0], start_time='0.0', end_time='0.0', summary='')
    # print get_busy_time(session['calendar'])
    
    db = get_db()
    user_init(db, profile)


    if is_profile_complete(db, session['user_id']) is False:
        return render_template('information_submit.html')
    else:
        session['comp_info'] = True


    return render_template('index.html')


######## Google Authorization Functions #############
@app.route('/google_login')
def google_login():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback)

@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('g_index'))

@google.tokengetter
def get_access_token():
    return session.get('access_token')
#####################################################


@app.route('/welcome')
def welcome():
    return render_template('welcome.html') 


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    user_password = False

    if request.method == 'POST':

        # db = get_db()
        # cur=db.cursor()
        # cur.execute("select * from Users")
        # rows= cur.fetchall();
        #
        # for row in rows:
        #     if request.form['username'] == row[2] and request.form['password'] == row[3]:
        #        user_password = True

        if request.form['username'] == 'admin' and request.form['password'] == 'admin':
            user_password = True

        if user_password:
            session['logged_in'] = True
            #flash('You were logged in.')
            return redirect(url_for('index'))

        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    session.pop('logged_in', None)
    session.pop('profile', None)
    session.pop('calendar', None)
    session.pop('comp_info', None)
    session.pop('unhandled_rating', None)
    flash('You were logged out.')
    return redirect(url_for('welcome'))


def get_db():
    """
    Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'mysql_db'):
        g.mysql_db = connect_db()
    return g.mysql_db


@app.teardown_appcontext
def close_connection(exception):
    """
    Close databases' connections.
    """
    db = getattr(g, 'mysql_db', None)
    if db is not None:
        db.close()


@app.route('/', methods=['GET', 'POST'])
#@login_required
#@comp_profile_required
def index():
    interest = None
    if request.method == 'POST':
        interest = request.form['interests']
    print interest

    return render_template('index.html', selected=interest)


@app.route('/friends', methods=['GET', 'POST'])
#@login_required
#@comp_profile_required
def friends():
    """
    Recommend workout partners to user using K-means.
    Then, sort recommendation result based on
    all "filtering" attributes.

    Data to display on webpage:
        filter_result: A dict of "list of dicts"s, containing all 4 filtering results.
                       (age, rating, frequency, home address distance)
            * filter_result['filter_by_age']: a list of dicts. Every element in the list
                corresponds to a user/partner. It's represented in dict format, every
                key-value pair correspond to one attribute in profile DB.
            * filter_result['filter_by_rating']: Same as above.
            * filter_result['filter_by_freq']: Same as above.
            * filter_result['filter_by_dist']: Same as above.
            * filter_result['filter_by_cor']: Same as above.

    """
    user_id = session['user_id']   # Current user's id
    db = get_db()

    all_data = read_db_to_ml(db)   # Get all data from Profile DB
    group, get_group_member = kmeans(all_data)   # Run K-means
    user_cluster = group[user_id]   # Get the idx of cluster that current user is in
    user_neighbors = get_group_member[str(user_cluster)]   # Get all users' IDs in that cluster
    user_neighbors_data = read_db_to_filter(db, user_neighbors)   # Read their profiles based on IDs
    filter_result = filtering(user_id, user_neighbors_data)   # Sorting

    return render_template('friends/friends_index.html')


@app.route('/reservation', methods=['GET', 'POST'])
@login_required
@comp_profile_required
def reservation():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print "save"
            return redirect(url_for('reservation',filename=filename))
    return render_template('reservations/index.html')


@app.route('/buslist', methods=['GET', 'POST'])
@login_required
@comp_profile_required
def buslist2():
    bus_line = None
    time1 = None
    time2 = None
    if request.method == 'POST':
        bus_line = request.form['bus_line']
        time1 = request.form['time1']
        time2 = request.form['time2']

    db = get_db()
    result = find_bus(db, bus_line, time1, time2)
    return render_template("buslist/index.html", rows=result)


@app.route('/comp_info')
def comp_info():
    """
    information_submit.html: 
        page of supplementing user's profile.
    """
    return render_template('information_submit.html')


@app.route('/post/', methods=['POST'])
def supplement_profile():
    """
    Receive info from page "information_submit.html",
    Update user's profile.
    'POST' method.
    """
    fn = request.form['yourfirstname'].title()   # title(): Uppercase the first letter
    ln = request.form['yourlastname'].title()
    address = request.form['youraddress']
    gender = request.form['gender']
    birthdate = request.form['yourdate']

    # Extract lat & lng from 'address'
    latlng = address.strip('()').split()
    lat, lng = latlng[0], latlng[1]

    # Update profile database
    db = get_db()
    update_profile(db, session['user_id'], fn, ln, gender, lat, lng, birthdate)
    if is_profile_complete(db, session['user_id']):
        session['comp_info'] = True

    # return render_template('form_action.html',  gender=gender, address=address)# ,name=name, email=email)
    return render_template('index.html')


# @app.route('***', methods=['POST'])
def send_invitations():
    """
    Send invitations based on user's choices,
    and save application records to DynamoDB.
    """
    ######### PARSE USER'S CHOICES ###########
    pass
    invitees = ['1','2','3','4']
    ##########################################
    ####### SEND INVITATION EMAILS ###########
    for uid in invitees:
        pass
    ##########################################
    inv_group = [session['user_id']] + invitees
    append_inv_records(inv_group)

    return None


# @app.route('***', methods=['POST'])
def rate_partners():
    """
    Rate partners. 
    Enter this function by clicking "Rate!" button.
    """
    db = get_db()
    utr = query_dynamo(session['user_id'])   # utr: users to rate
    utr_profiles = read_profile(db, utr)   # Profiles of these users

    ### Send 'utr_profiles' to frontend ###

    #######################################
    ######## Receive User's rating ########

    #######################################
    session['unhandled_rating'] = False
    # Update user's profile, pay attention to user's workout catagory
    update_records(db=db, uid=session['user_id'], ctr=1, bas_ctr=1)
    # Update partner's profile.
    update_records(db=db, uid=partner_id, rating=4, rating_ctr=1)

if __name__ == '__main__':
    app.run(debug=True)
