from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from flask import request

import engine
#from db import api as db_api

app = Flask(__name__)

# TODO: put this sensitive information into a new configuration file
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:nova@localhost/rushi'

db = SQLAlchemy(app)

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method =='POST':
        engine.store_transactions(request.form.get('inputText'),
                                      request.form.get('amc'), 1)
        return 'OK. Saved in DB.'
#        return 'OK, data submitted to server. Data:</br>' + request.form.get('inputText')
    elif request.method == 'GET':
#        print 'boom'
#        print engine.get_txns()
        f = open('webui/welcome_page.html')
        return ''.join(f.readlines())


if __name__ == "__main__":
    app.run(debug=True)