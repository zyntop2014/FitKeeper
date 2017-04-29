from flask import Flask, render_template, request, g, redirect, url_for, session, flash
from flask_oauth import OAuth
import sqlite3 as sql
from functools import wraps
import psycopg2, json
import os
from werkzeug.utils import secure_filename
import pymysql
from datetime import datetime as dt
#import transloc

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


UPLOAD_FOLDER = 'static/img/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

GOOGLE_CLIENT_ID = '852263075688-3u85br5hvvk6ajvrafavv3lpupns3va7.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'l7a5ztJX5bW9iZBTq81GP-pg'
REDIRECT_URI = '/oauth2callback'
SECRET_KEY = 'development key'

app.secret_key = SECRET_KEY
oauth = OAuth()

google = oauth.remote_app(
	'google',
	base_url='https://www.google.com/accounts/',
	authorize_url='https://accounts.google.com/o/oauth2/auth',
	request_token_url=None,
	request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
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

@app.route('/google')
def g_index():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('google_login'))

    access_token = access_token[0]
    from urllib2 import Request, urlopen, URLError
    headers = {'Authorization': 'OAuth '+access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    # print type(req)
    try:
        res = urlopen(req)
        print (res)
    except URLError, e:
        if e.code == 401:
            # Unauthorized - bad token
            session.pop('access_token', None)
            return redirect(url_for('google_login'))
        return res.read()

    # Login successfully. Extract user's information
    session['logged_in'] = True
    profile = json.loads(res.read())
    user_id = profile['id']
    family_name = profile['family_name']
    given_name = profile['given_name']
    name = profile['name']
    email = profile['email']
    photo_url = profile['picture']
    #gender = profile['gender']
    #link = profile['link']

    print "user_id: %s  family name:%s  given name:%s  name:%s  email:%s\n"%(user_id, family_name, given_name, name, email)
    return render_template('index.html')

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


@app.route('/welcome')
def welcome():
    return render_template('welcome.html')  # render a template

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
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('welcome'))

cnx= {'host': 'west-2-mysql-gymplanner.csssif3kpxyv.us-west-2.rds.amazonaws.com',
  'username': 'awsuser',
  'password': 'zsy13654522998',
  'db': 'GymPlanner'}
  
#DATABASE = 'abc.sql'
def get_db():
    db = pymysql.connect(cnx['host'],cnx['username'],cnx['password'], cnx['db'])
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/reservation', methods=['GET', 'POST'])
@login_required
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
def buslist2():
    bus_line = None
    time1 = None
    time2=None
    if request.method == 'POST':
        bus_line=request.form['bus_line']
        time1=request.form['time1']
        time2=request.form['time2']

    db = get_db()
    cur=db.cursor()
    cur.execute("select line, departure_time from BUS WHERE line=%s and departure_time > CAST(%s AS time) and departure_time < CAST(%s AS time)",(str(bus_line),str(time1),str(time2),))
    #cur.execute("select line, departure_time from BUS WHERE line=%s",str(bus_line))
    result = cur.fetchall()
        
    return render_template("buslist/index.html", rows=result)

@app.route('/profile')
def form():
    return render_template('form_submit.html')


@app.route('/post/', methods=['POST'])
def post():
    name=request.form['yourname']
    email=request.form['youremail']
    address=request.form['youraddress']
    gender=request.form['gender']
    age=request.form['yourage']
    #return render_template('form_action.html', age=age, name=name, email=email, gender=gender, address=address)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
