import flask
from flask import Flask, request
application = Flask(__name__)


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
	return render_template('index.html')


if __name__ == "__main__":
    # application.run(host='0.0.0.0')
	application.run()
