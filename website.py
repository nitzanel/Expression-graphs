import grapher
import views
import forms
import flask, flask.views
import os
#import flask_sijax
import functools
import pygal


path = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')

app = flask.Flask(__name__.split('.')[0])
#app.config['SIJAX_STATIC_PATH'] = path
#app.config['SIJAX_JSON_URI'] = '/static/js/sijax/json2.js'
#flask_sijax.Sijax(app)

app.secret_key = os.urandom(128)

app.add_url_rule('/',
				view_func=views.Main.as_view('home'),
				methods=['GET','POST'])
app.add_url_rule('/about',
				view_func=views.About.as_view('about'),
				methods=['GET'])
app.add_url_rule('/genes',
				view_func=views.Genes.as_view('genes'),
				methods=['GET'])
app.add_url_rule('/genes/pan_immune',
				view_func=views.Pan_Immune.as_view('pan_immune'),
				methods=['GET','POST'])
app.add_url_rule('/genes/cell_type_specific',
				view_func=views.Cell_Type_Specific.as_view('cell_type_specific'),
				methods=['GET','POST'])
app.add_url_rule('/login',
				view_func=views.Login.as_view('login'),
				methods=['GET','POST'])
app.add_url_rule('/homepage',
					view_func=views.Homepage.as_view('homepage'),
					methods=['GET'])

"""
app.add_url_rule('/genes/pan_immune_old',
		view_func=views.Pan_Immune_old.as_view('pan_immune_2'),
		methods=['GET','POST'])
"""
if __name__ == '__main__':
	app.run(debug=True)

