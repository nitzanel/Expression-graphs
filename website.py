import grapher
import views
import forms
import flask, flask.views
import os
import flask_sijax
import functools
import pygal

class FlaskApp:

	def __init__(self):
		path = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')
		self.app = flask.Flask(__name__.split('.')[0])
		self.app.config['SIJAX_STATIC_PATH'] = path
		self.app.config['SIJAX_JSON_URI'] = '/static/js/sijax/json2.js'
		self.app.secret_key = os.urandom(128)
		flask_sijax.Sijax(self.app)
		""" SET URL RULES """
		self.app.add_url_rule('/',
				view_func=views.Main.as_view('home'),
				methods=['GET','POST'])
		self.app.add_url_rule('/about',
				view_func=views.About.as_view('about'),
				methods=['GET'])
		self.app.add_url_rule('/genes',
				view_func=views.Genes.as_view('genes'),
				methods=['GET'])
		self.app.add_url_rule('/genes/pan_immune',
				view_func=views.Pan_Immune.as_view('pan_immune'),
				methods=['GET','POST'])
		self.app.add_url_rule('/genes/cell_type_specific',
				view_func=views.Cell_Type_Specific.as_view('cell_type_specific'),
				methods=['GET','POST'])
		self.app.add_url_rule('/login',
				view_func=views.Login.as_view('login'),
				methods=['GET','POST'])
		self.app.add_url_rule('/homepage',
				view_func=views.Homepage.as_view('homepage'),
				methods=['GET'])
		self.app.add_url_rule('/sijax_test',
				view_func=views.SijaxTest.as_view('sijax_test'),
				methods=['GET','POST'])


	def run_debug(self):
		self.app.run(debug=True)

	def run_threaded(self):
		self.app.run(threaded=True)

	def config_app(self,params):
		pass

if __name__ == '__main__':
	print 'starting app'
	App = FlaskApp().app
	App.run(threaded=True)
