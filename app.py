from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from flask import request
from flask import render_template
from flask import flash

import utils

conf = utils.get_mftrack_config()

#from db import api as db_api

app = Flask(__name__)

# TODO: put this sensitive information into a new configuration file
app.config['SQLALCHEMY_DATABASE_URI'] = conf['db_uri']
app.secret_key = conf['secret_key']


db = SQLAlchemy(app)

import engine


@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method =='POST':
        engine.store_transactions(request.form.get('inputText'),
                                      request.form.get('amc'), 1)
        flash('OK. Saved in DB.')
        mf_dict, stats = engine.get_summary(1)
        return render_template('index.html', mf_dict=mf_dict, stats=stats)
    elif request.method == 'GET':
        mf_dict, stats = engine.get_summary(1)
        return render_template('index.html', mf_dict=mf_dict, stats=stats)


if __name__ == "__main__":
#    from db import models
    app.run(debug=conf['debug'], port=conf['port'])