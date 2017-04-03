import flask
from flask import Flask, request, render_template, redirect, url_for, session
from flask_oauth import OAuth
import json

GOOGLE_CLIENT_ID = '852263075688-3u85br5hvvk6ajvrafavv3lpupns3va7.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'l7a5ztJX5bW9iZBTq81GP-pg'
REDIRECT_URI = '/oauth2callback'
SECRET_KEY = 'development key'
DEBUG = True

application = Flask(__name__)
application.debug = DEBUG
application.secret_key = SECRET_KEY
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


@application.before_request
def before_request():
    """
    This function runs at the beginning of every web request.
    (every time you enter an address in the web browser)
    """
    pass


@application.teardown_request
def teardown_request(exception):
    """
    This runs at the end of the web request.
    """
    pass


@application.route('/')
def index():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))

    access_token = access_token[0]
    from urllib2 import Request, urlopen, URLError
    headers = {'Authorization': 'OAuth '+access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    # print type(req)
    try:
        res = urlopen(req)
        print res
    except URLError, e:
        if e.code == 401:
            # Unauthorized - bad token
            session.pop('access_token', None)
            return redirect(url_for('login'))
        return res.read()

    # Extract user's information
    profile = json.loads(res.read())
    user_id = profile['id']
    family_name = profile['family_name']
    given_name = profile['given_name']
    name = profile['name']
    email = profile['email']

    return "user_id: %s  family name:%s  given name:%s  name:%s  email:%s\n"%(user_id, family_name, given_name, name, email)
    return render_template('index.html')

@application.route('/login')
def login():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback)


@application.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('index'))

@google.tokengetter
def get_access_token():
    return session.get('access_token')

@application.route('/test')
def login_button():
    return render_template('test_index.html')

if __name__ == "__main__":
    # application.run(host='0.0.0.0')
	application.run()
