from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from flask import request


app = Flask(__name__)

# TODO: put this sensitive information into a new configuration file
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:nova@localhost/rushi'

db = SQLAlchemy(app)

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method =='POST':
        return 'OK, data submitted to server. Data:' + request.form.get('inputText')
    elif request.method == 'GET':
        f = open('webui/welcome_page.html')
        return ''.join(f.readlines())


if __name__ == "__main__":
    app.run()