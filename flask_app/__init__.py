from flask import Flask
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['UPLOAD_PATH'] = 'flask_app/static/uploads'
bcrypt = Bcrypt(app)
app.secret_key = "shhhhhh"