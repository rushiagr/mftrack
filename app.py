from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from flask import request
from flask import render_template
from flask import flash

#from db import api as db_api

app = Flask(__name__)

# TODO: put this sensitive information into a new configuration file
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:nova@localhost/rushi'
app.secret_key = 'Aenergee kayn needher beey creyaitaid nohr beiy deistroid'


db = SQLAlchemy(app)


import engine


@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method =='POST':
        engine.store_transactions(request.form.get('inputText'), 1)
        flash('OK. Saved in DB.')
        mf_dict, stats = engine.get_summary(1)
        fund_families = engine.get_all_fund_families()
        return render_template('index.html',
                               mf_dict=mf_dict,
                               stats=stats,
                               fund_families=fund_families)
    elif request.method == 'GET':
        mf_dict, stats = engine.get_summary(1)
        fund_families = engine.get_all_fund_families()
        return render_template('index.html',
                               mf_dict=mf_dict,
                               stats=stats,
                               fund_families=fund_families)


if __name__ == "__main__":
    print engine.db.fund_id_from_keywords('icici prudential technology growth direct'.split())
    app.run(debug=True, port=5010)