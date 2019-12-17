from flask import Flask
import os 
import numpy as np 
import pickle
from analyzer.vectorizer import vect 
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import urllib.request as request
import json
import analyzer.config as config

app = Flask(__name__)
curr_dir = os.path.dirname(__file__)
clf = pickle.load(open(os.path.join(curr_dir,'pkl_objects/classifier.pkl'),'rb'), encoding='latin1')

app.config['SECRET_KEY'] = config.secret_key
api_key = config.api_key
json_data = []
for i in range(5):
	base_url = "https://api.themoviedb.org/3/discover/movie/?api_key=" + api_key + "&page="+ str(i+1)
	api_conn = request.urlopen(base_url)
	old_json_data = json.loads(api_conn.read())
	
	json_data.append(old_json_data.copy())

# print(json_data)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

def classify(document):
	label = {0:'negative',1:'positive'}
	X = vect.transform([document])
	y = clf.predict(X)[0]
	proba = np.max(clf.predict_proba(X))
	return label[y],proba

def train(document,y):
	X = vect.transform([document])
	clf.partial_fit(X,[y])

from analyzer import routes
