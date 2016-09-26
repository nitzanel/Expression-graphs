import grapher
import views
import forms
import flask, flask.views
import os
import flask_sijax
import functools
import pygal
import zipfile

class FlaskApp(object):


	def create_empty_chart(self,number):
		chart = pygal.Bar()
		chart.title = str(number)
		return chart.render_data_uri()


	def __init__(self):
		# extract the database
		print "extracting database..."
		zfile = zipfile.ZipFile('database/db.zip')
		zfile.extractall('database')
		print "database extracted..."
		# configure the site.
		path = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')
		self.app = flask.Flask(__name__.split('.')[0])
		self.app.config['SIJAX_STATIC_PATH'] = path
		self.app.config['SIJAX_JSON_URI'] = '/static/js/sijax/json2.js'
		self.app.secret_key = os.urandom(128)
		print "setting sijax..."
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

		""" some sort of a simplified REST ideas """

		self.app.add_url_rule('/genes/cell_type_specific/<gene_name>/<cell_type>',
				view_func=views.CTCGraphs.as_view('ctcgraphs'),
				methods=['GET','POST'])
		self.app.add_url_rule('/genes/pan_immune/<gene_name>',
				view_func=views.PIGraphs.as_view('pigraphs'),
				methods=['GET','POST'])
		
		""" Cool error handles """ 
		
		@self.app.errorhandler(403)
		def page_not_found(e):
			chart = pygal.Bar()
			chart.title = ''.join([str(403),' Forbidden']) 
			graph = chart.render_data_uri()
			return flask.render_template('error.html',graph=graph), 403
		
		@self.app.errorhandler(404)
		def page_not_found(e):
			chart = pygal.Bar()
			chart.title = ''.join([str(404),' Not Found']) 
			graph = chart.render_data_uri()
			return flask.render_template('error.html',graph=graph), 404

		@self.app.errorhandler(410)
		def page_not_found(e):
			chart = pygal.Bar()
			chart.title = ''.join([str(410),' Gone']) 
			graph = chart.render_data_uri()
			return flask.render_template('error.html',graph=graph), 410

		@self.app.errorhandler(500)
		def page_not_found(e):
			chart = pygal.Bar()
			chart.title = ''.join([str(500),' Internal Server Error']) 
			graph = chart.render_data_uri()
			return flask.render_template('error.html',graph=graph), 500



	def run_debug(self):
		self.app.run(debug=True)

	def run_threaded(self):
		self.app.run(threaded=True)

	def config_app(self,params):
		pass

if __name__ == '__main__':
	print 'starting app'
	App = FlaskApp().app
	App.run(threaded=True,port=5001)
