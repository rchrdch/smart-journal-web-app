import datetime
import flask
from flask_login.login_manager import LoginManager
from flask_login.utils import login_required
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from flask import Flask, blueprints, render_template, request, url_for, redirect, session
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import EmotionOptions, Features, EntitiesOptions, KeywordsOptions, SentimentOptions
import json, urllib.request
import requests
import db
from authlib.integrations.flask_client import OAuth
import calendar
import htmlCalendar

app = Flask(__name__)

app.config.from_object('config')


# ------------------------------------------------------------------------------------------------------------
# OAUTH CONFIGURATION
CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth = OAuth(app)
json_resp = oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# ------------------------------------------------------------------------------------------------------------
@app.route("/")
def home_page():
    user = session.get('user')
    return render_template("home_page.html")

@app.route("/login")
def login():
    redirect_uri = url_for('auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/auth')
def auth():
    
    json_token = oauth.google.authorize_access_token()
    user_name = oauth.google.parse_id_token(json_token)['name']
    
    access_token = json_token['access_token']
    id_token = json_token['id_token']

    session['user'] = user_name

    return redirect('/form')

@app.route("/logout")
def logout():  
    session.pop('user', None)   
    return redirect("/")

@app.route("/home")
def home_page_2():
    return render_template("home_page.html")

@app.route("/about")
def about_page():
    return render_template("about_page.html")

@app.route("/overview")
def overview_page():
    html_calendar = htmlCalendar.MonthlyCalendar()

    return render_template("overview_page.html", form = html_calendar.create(), value = session.get('user'))

@app.route("/form", methods=['GET', 'POST'])
def form_page():
    
    if session.get('user') is None:
        return redirect("/login")

    # If the journal is filled out and submitted
    if request.form.getlist('journalentry') != [] or None:
        entry = request.form.getlist('journalentry')
        entry = entry[0]
        
        authenticator = IAMAuthenticator('')
        natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2021-08-01',
        authenticator=authenticator
        )
        natural_language_understanding.set_service_url('https://api.us-east.natural-language-understanding.watson.cloud.ibm.com')

        response = natural_language_understanding.analyze(
            text=entry,
            features=Features(
                emotion=EmotionOptions(),
                sentiment=SentimentOptions(),
            ),
            language="en"
        ).get_result()

        # db.db.collection.remove({}) 

        # Send to database
        db.db.collection.insert_one({"name": session.get('user'), "date": datetime.datetime.now().strftime("%m/%d/%Y"), "entry": entry, "sentiment": response['sentiment']['document']['score'], "emotions": response['emotion']['document']['emotion']})

    # If the journal is not filled out yet
    else:
        entry = ''

    # Using freeware code for custom calendars
    html_calendar = htmlCalendar.MonthlyCalendar()

    return render_template("form_page.html", value = session.get('user'))

# ------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
