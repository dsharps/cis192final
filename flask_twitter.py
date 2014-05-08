from flask import Flask, request, jsonify, session, g, redirect, url_for, abort, render_template, flash
import json
from twitterstats import TwitterUser

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    SECRET_KEY='Farts',
    DEBUG=True))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


@app.route('/')
@app.route('/home')
def home():
    return render_template('search.html')

@app.route('/<username>/stats_for')
def stats_for(username=None):
    error = None
    # if request.method == 'POST':
    #     if request.form['username'] != None:
    #         username = request.form['username']
    #         flash('Thanks!')
    #     else:
    #         error = "Enter your username!"
    return render_template('user.html', handle=username)

@app.route('/stats', methods=['POST'])
def stats(username=None):
    error = None
    if request.method == 'POST':
        if request.form['username'] != None:
            username = request.form['username']
            print request.form['username']
            print type(request.form['username'])
            print request.form['username'] == 'dsharps'
            flash('Thanks!')
        else:
            error = "Enter your username!"
    
    user = TwitterUser(username)

    return render_template('user.html', twitter_user=user)

if __name__ == '__main__':
    app.run()