import grapher
import forms
import flask, flask.views
import os
import functools
import flask_sijax
import pygal
from pygal.style import LightenStyle, SaturateStyle
import styles
import random

grapher = grapher.Grapher()

bad_names = ['',' ']

# return all the gene symbols in a list.
def auto_complete_from_file():
	genes = [line.strip('\n') for line in open('database/genes.txt','r')]
	return genes	
# returns a static url for a file in a subdirectory of the static folder.
# input:
# filedir - a string of the file path from the static folder.
def get_static_url(filedir):
	file = ''
	if filedir.startswith('static'):
		file = filedir.split('static/')[1]
	else:
		file = filedir
	return flask.url_for('static',filename=file)
# returns a list of dictionarys, each one representing a value with a label.
# input: 
# x_labels - a list of labels.
# x_index - a list of x values.
def get_x_labels(x_index,x_labels):
	labels_list = []
	for x,label in zip(x_index,x_labels):
		labels_list.append({'label': label,'value': x})
	x_labels_tuple = tuple(labels_list)
	return x_labels_tuple

# arrange bars on the x axis
# input:
# data - a dictionary of lists of bars data
def get_bars_values(data):
	arranged_data = {}

	x_labels = []
	bar_width = 0.5
	x_loc = 0
	for key in data:
		female_count = 0
		male_count = 0
		arranged_data[key] = []
		current_serie = data[key]
		for val in current_serie:
			x_label_name = ''
			if key.startswith('m'):
				x_label_name = '_'.join([key,str(male_count)])
				male_count += 1
			else:
				x_label_name = '_'.join([key,str(female_count)])
				female_count +=1
				
			x_labels.append({'label': x_label_name,'value':x_loc})
			yx1x2 = (val,x_loc,x_loc+bar_width)
			bar_properties = {'value': yx1x2}
			arranged_data[key].append(bar_properties)
			x_loc += 1


	values = {'data':arranged_data,'x_labels': x_labels}
	return values

# unfinished - legacy
def get_bar_label(key,vals):
	pass

# arrnages data for graphs - legacy
# input:
# data - a  dictionary of lists of male and female data
def arrange_data(data):
	if data == -1:
		return -1

	arranged_data = {}
	for key in data:
		#get female data
		name = ''.join(['female ',key])
		arranged_data[name] = data[key][::2]
		name = ''.join(['male ',key])
		arranged_data[name] = data[key][1::2]

	return arranged_data

# returns a tuple of point data with label, tooltip, and xy position. - legacy
# input:
# values - a list of xy tuples
def get_dots_labels(values):
	labels = []
	for xy in values:
		labels.append({'label':'test','tooltip':'tooltip','value':(1,xy[1])})
	return tuple(labels)

# The Main view
# at the moment is redirects to pan_immune page.
# has a post method for legacy AJAX
class Main(flask.views.MethodView):
	def get(self):
		#return flask.render_template('homepage.html')
		return flask.redirect(flask.url_for('pan_immune'))
	def post(self):
		#def say_hi(obj_response):
		#	obj_response.alert('Hello')
		# test sijax
		#if flask.g.sijax.is_sijax_request:
		#	flask.g.sijax.register_callback('say_hi',say_hi)
		#	print 'sijax request'
		#	return flask.g.sijax.process_request()
		
		#return flask.render_template('homepage.html')
		print 'someone post to main?'
		return flask.redirect(flask.url_for('pan_immune'))		

# return address of ctc graph
def get_ctc_address(gene_name,cell_type):
	return '/'.join(['/genes','cell_type_specific',gene_name,cell_type])

# return address of pi graph
def get_pi_address(gene_name):
	return '/'.join(['/genes','pan_immune',gene_name])


# Homepage view
# redirect to pan_immune page.
class Homepage(flask.views.MethodView):
	def get(self):
		#return flask.render_template('homepage.html')
		return flask.redirect(flask.url_for('pan_immune'))

# testing sijax ajax with flask.
class SijaxTest(flask.views.MethodView):
	def get(self):
		form = forms.GeneSearchForm()
		return flask.render_template('sijax_test.html',form=form)

	def post(self):
		form = forms.GeneSearchForm()
		def testing(obj_response):
			obj_response.alert('Click registerd')
		if flask.g.sijax.is_sijax_request:
			flask.g.sijax.register_callback('testing',testing)
			print 'sijax request'
			return flask.g.sijax.process_request()
		print 'post'
		return flask.render_template('sijax_test.html',form=form)


# About view
# Displays information about the site.
class About(flask.views.MethodView):
	def get(self):
		return flask.render_template('about.html')


# Genes view
# shows links to pan_immune and cell_type_specific.
# should be removed probably.
class Genes(flask.views.MethodView):
	def get(self):
		#return flask.render_template('genes.html')
		return flask.redirect(flask.url_for('pan_immune'))

class ACHandler(object):
	def __init__(self):
		self.last_value = ''
		self.last_options = []
	def change_last(self,value,options):
		self.last_value = value
		self.last_options = options

ac_handler = ACHandler()
# Login view
# allows admin to login to the site.
# currently does nothing and just redirect to Homepage
class Login(flask.views.MethodView):
	def get(self):
		form = forms.LoginForm()
		return flask.render_template('login.html',title='Sign In',form=form)
	def post(self):
		return flask.redirect(flask.url_for('home'))

def autocomplete(obj_response, value): 
	if len(value) < 1:
		return
	if '"' in value or "'" in value or '?' in value or '!' in value or '%' in value or '&' in value:
		return		
	options = []
	if ac_handler.last_value == value:
		return
	else:
		options = grapher.autocomplete(value)
		options = list(map(create_tag, options))
		ac_handler.change_last(value,options)
	# fill options according to value
	# create a list of tags
	# add autocomplete options, and clear the previous ones.
	obj_response.html('#genes_datalist','')
	obj_response.html_append('#genes_datalist',''.join(options))	
	print options	

# get noise message filter.
def get_noise_message(noise_data):
	# find which repeats didnt pass the filter
	filtered = []
	for key in noise_data:
		for rep, noise_val in enumerate(noise_data[key]):
			if noise_val[0] == '0':
				# increment rep so it start at 1 instead of 0 (repeat 1, repeat 2 ...)
				filtered.append(str(rep+1))
	# remove duplicates			
	filtered = list(set(filtered))		
	repeat_text = 'repeat'
	if len(filtered) == 0:
		return ['']
	if len(filtered) > 1:
		repeat_text = 'repeats'
	filtered = ','.join(filtered)
	message = 'Please note that the expression levels of this gene in {0}: {1} are very low'.format(repeat_text, filtered)
	return [message]

# get dataset new name DS_A DS_B and so on
def get_ds_name(db):
	if db.startswith('FM_IFN'):
		return 'DS_A'
	elif db.startswith('ImmGen'):
		return 'DS_B'
	elif db.startswith('Female_Male'):
		return 'DS_C'
	elif db.startswith('pilot8'):
		return 'DS_D'
	print 'get_db_name recieved bad input: {0} .'.format(db)
	return 'unknown db'

# get sorted graphs_list to display graphs according to ds_a rep 1, rep 2 ... ds_b rep 1, .... 
def sort_graphs(graphs_list):
	sorted_graphs = sorted(graphs_list,key=lambda graph: graph.title.split(':'))
	return sorted_graphs

# get sorted x_labels
def sort_labels(x_labels):
	sorted_labels = sorted(x_labels)
	return sorted_labels

def sort_columns(values):
	pass

# get label name from index for ctc graphs
def get_label_name(index):
	return "DS_{0}".format(chr(index + ord('A')))


# unacceptable symbols in gene_name or cell_type
bad_symbols = ['"',"'"]
# the pattern based ctc graph address
# TODO: fix order
class CTCGraphs(flask.views.MethodView):
	def get(self, gene_name, cell_type):
		form = forms.CellTypeSpecificForm()
		# check for bad symbols in address.
		gene_name = gene_name.upper()
		if gene_name == '':
			flask.flash('please enter gene symbol')
			return flask.render_template('cell_type_specific.html',form=form)
		for symbol in bad_symbols:
			if symbol in gene_name or symbol in cell_type:
				flask.flash('Symbol not valid.')
				return flask.render_template('cell_type_specific.html',form=form)

		data, noise_data = grapher.ctc_plot(gene_name,cell_type)

		# check if there is data. if not, alert the user the gene doesnt exist.
		if data == -1:
			flask.flash('gene not found.')
			return flask.render_template('cell_type_specific.html',form=form)
		# create graphs for the data.

		males_data = []
		females_data = []
		x_labels = []
		graphs = []
		graph = pygal.XY(stroke=False,show_y_guides=False,
								truncate_label =-1,dots_size=4,
								legend_at_bottom=True)

		for index, 
		 in enumerate(data):
			for repeat in data[data_set]:
				current_data = data[data_set][repeat]
				for tup in current_data:
					exp_level = float(tup[1])
					parts = tup[0].split('_')
					cell = parts[0]					
					if 'M' in parts or 'male' in parts:	
						# its a male cell, add to male_data
						males_data.append((index+1,exp_level))
					elif 'F' in parts or 'female' in parts:
						# its a female cell
						females_data.append((index+1,exp_level))
			x_labels.append({ 'value': index+1,'label':get_label_name(index)})
		graph.title = "{0} exp level in cell {1}".format(gene_name,cell_type)
		graph.y_title = 'exp level log2'
		graph.add('Female',females_data)
		graph.add('Male',males_data)
		graph.x_labels = x_labels
		graphs.append(graph.render_data_uri())

		messages = get_noise_message(noise_data)

		return flask.render_template('cell_type_specific.html',form=form,graphs_data=graphs,messages=messages)

		#return flask.render_template('cell_type_specific.html',form=form,data=data,graphs_data=graphs_data, messages=messages)
	def post(self, gene_name, cell_type): 
		return "{} {}".format(gene_name,cell_type)
# the pattern based pi graph address
class PIGraphs(flask.views.MethodView):
	def get(self,gene_name):
		
		form = forms.CellTypeSpecificForm()
		# check for bad symbols in address.
		
		gene_name = gene_name.upper()

		for symbol in bad_symbols:
			if symbol in gene_name:
				flask.flash('Symbol not valid.')
				return flask.render_template('pan_immune.html',form=form)

		data, noise_data = grapher.new_plot(gene_name)
		# if there is no data, there is no gene with this symbol. alert the user.

		if data == -1:
			flask.flash('Gene not found.')	
			return flask.render_template('pan_immune.html',form=form)			
		
		graphs = []
		for data_set in data:		
			for data_tuple_key in data[data_set]:
				# current_data holds a list of tuples with column names and values		
				current_data = data[data_set][data_tuple_key][5:] 
				graph = pygal.XY(stroke=False,show_y_guides=False,
								truncate_label =-1,dots_size=4,
								legend_at_bottom=True)
				current_male_x = 0
				current_female_x = 0
				current_x = 0
				margin = 2
				last_female_cell = ''
				last_male_cell = ''
				# the data will be arranged as a list of tuples, each tuple will be as (X,Y)
				males_data = []
				females_data = []
				x_labels = []
				for tup in current_data:
					exp_level = float(tup[1])
					parts = tup[0].split('_')
					cell = parts[0]
					# check if it is a male or female cell.
					if 'M' in parts or 'male' in parts:
						# its a male cell
						if cell != last_male_cell:
							last_male_cell = cell
							current_male_x += 2
							current_x = current_male_x
						males_data.append((current_male_x,exp_level))
					elif 'F' in parts or 'female' in parts:
						# its a female cell
						if cell != last_female_cell:
							last_female_cell = cell
							current_female_x += 2
							current_x = current_female_x
						females_data.append((current_female_x,exp_level))
					x_labels.append({ 'value': current_x,'label':cell })
				# remove the last label in x_labels, because it is 'noise' and it obscures the label before it.
				x_labels.pop()
				# send data for labels if needed.
				graph.title = ' '.join([gene_name,'exp level dataset:',get_ds_name(data_set),data_tuple_key])
				graph.y_title = 'exp level log2'
				graph.add('Female',females_data)
				graph.add('Male',males_data)
				graph.x_labels = x_labels
				graphs.append(graph)
		graphs = sort_graphs(graphs)
		graphs = list(map(lambda graph: graph.render_data_uri(),graphs))
		messages = get_noise_message(noise_data)
		return flask.render_template('pan_immune.html',form=form,graphs=graphs,messages=messages)

	def post(self,gene_name):
		return "{}".format(gene_name)
# Cell_Type_Specific view
# search genes and cells for expression level graphs.
# post method to submit forms and return the data.


class Cell_Type_Specific(flask.views.MethodView):
	def get(self):
		form = forms.CellTypeSpecificForm()
		return flask.render_template('cell_type_specific.html',form=form)

	def post(self):				
		if flask.g.sijax.is_sijax_request:
			print flask.g.sijax.get_js()
			flask.g.sijax.register_callback('autocomplete',autocomplete)
			return flask.g.sijax.process_request()
		form = forms.CellTypeSpecificForm()
		gene_name = flask.request.form['gene_name']	
		gene_name = gene_name.upper()
		cell_type = flask.request.form['cell_type']

		if gene_name == '-' or '"' in gene_name or "'" in gene_name :
			flask.flash('Symbol no valid.')
			return flask.render_template('cell_type_specific.html',form=form)
		
		return flask.redirect(get_ctc_address(gene_name,cell_type))	
		
		data, noise_data = grapher.new_bar_plot(gene_name,cell_type)

		if data == -1:
			flask.flash('Gene not found.')
			return flask.render_template('cell_type_specific.html',form=form)		
	
		male_data = []
		female_data = []
		female_names = []
		male_names = []
		width = 1
		for data_set in data:
			for data_tuple_key in data[data_set]:
				current_data = data[data_set][data_tuple_key]
				exp_males = []
				exp_females = []

				for tup in current_data:
					exp_level = float(tup[1])
					#if exp_level != 0:
					if True:
						parts = tup[0].split('_')
						if 'M' in parts or 'male' in parts:
							exp_males.append(exp_level)
						elif 'M' in parts or 'female' in parts:
							exp_females.append(exp_level)
 
				male_data.append(exp_males)
				female_data.append(exp_females)
				male_names.append(' '.join(['males',data_set,data_tuple_key]))
				female_names.append(' '.join(['females',data_set,data_tuple_key]))
				#graph.add(' '.join(['males',data_set,data_tuple_key]),exp_males)
				#graph.add(' '.join(['females',data_set,data_tuple_key]),exp_females)
		male_bars = []
		female_bars = []
		x_counter = 0

		def set_bars_color(tup_list,color_type = ''):
			r = lambda: random.randint(0,80)
			if color_type == 'red':
				color = '#EE%02X%02X' % (r(),r())
			elif color_type == 'blue':
				color = '#%02X%02XEE' % (r(),r())
			elif color_type == 'green':
				color = '#%02XEE%02X' % (r(),r())
			else:
				color = '#%02X%02X%02X' % (r(),r(),r())
			colored_bars = []
			for tup in tup_list:
				colored_bars.append({'value':tup,'color':color})
			return colored_bars

		for exp_data in male_data:
			# a function that embed colors in the graphs.


			bars_data = []
			for value in exp_data:
				bars_data.append((value,x_counter,x_counter + width))
				x_counter += width
			bars_data = set_bars_color(bars_data,'blue')
			male_bars.append(bars_data)

		x_counter += width
		
		for exp_data in female_data:
			bars_data = []
			for value in exp_data:
				bars_data.append((value,x_counter,x_counter + width))
				x_counter += width
			
			bars_data = set_bars_color(bars_data,'red')
			female_bars.append(bars_data)


		graph = pygal.Histogram(show_x_labels=False,show_y_guides=False,legend_at_bottom=True)


		for name, bars in zip(male_names,male_bars):
			graph.add(name,bars)
		for name, bars in zip(female_names,female_bars):
			graph.add(name,bars)

		messages = get_noise_message(noise_data)

		graph.title = ' '.join([gene_name,'expression level in',cell_type])
		graph.y_title = 'expression level log2'
		graphs_data = []
		graphs_data.append(graph.render_data_uri())

		red_style = LightenStyle('#%02X%02X%02X' % (150,0,0))
		blue_style = LightenStyle('#%02X%02X%02X' % (20,25,80))

		# bar graphs for each:
		graph = pygal.Histogram(show_x_labels=False,show_y_guides=False,style=blue_style,legend_at_bottom=True)
		for name,bars in zip(male_names,male_bars):
			new_bars = []
			for bar in bars:
				new_bars.append(bar['value'])
			graph.add(name,new_bars)
		graph.title = ' '.join([gene_name, 'expression level in male',cell_type])
		graph.y_title = 'expression level log2'

		graphs_data.append(graph.render_data_uri())

		graph = pygal.Histogram(show_x_labels=False,show_y_guides=False,style=red_style,legend_at_bottom=True)
		for name,bars in zip(female_names,female_bars):
			new_bars = []
			for bar in bars:
				new_bars.append(bar['value'])
			graph.add(name,new_bars)
		graph.title = ' '.join([gene_name, 'expression level in female',cell_type])
		graph.y_title = 'expression level log2'
		graphs_data.append(graph.render_data_uri())

		return flask.render_template('cell_type_specific.html',form=form,data=data,graphs_data=graphs_data, messages=messages)


def create_tag(gene_symbol):
	tag = ''.join(["<option value='",gene_symbol,"'></option>"])
	return tag


# Pan_Immune view
# Search for genes and see expression levels graphs for each gene in every dataset for all cells.
class Pan_Immune(flask.views.MethodView):
	def get(self):
		form = forms.GeneSearchForm()
		return flask.render_template('pan_immune.html',form=form)
	def post(self):
		if flask.g.sijax.is_sijax_request:
			flask.g.sijax.register_callback('autocomplete',autocomplete)
			return flask.g.sijax.process_request()
		form = forms.GeneSearchForm()
		gene_name = flask.request.form['gene_name'].upper()
		if gene_name == '-' or '"' in gene_name or "'" in gene_name :
			flask.flash('Symbol not valid.')	
			return flask.render_template('pan_immune.html',form=form)			
		return flask.redirect(get_pi_address(gene_name))
		data, noise_data = grapher.new_plot(gene_name)
		# if there is no data, there is no gene with this symbol. alert the user.

		if data == -1:
			flask.flash('Gene not found.')	
			return flask.render_template('pan_immune.html',form=form)			
		
		graphs = []
		for data_set in data:		
			for data_tuple_key in data[data_set]:
				# current_data holds a list of tuples with column names and values		
				current_data = data[data_set][data_tuple_key][5:] 
				graph = pygal.XY(stroke=False,show_y_guides=False,
								truncate_label =-1,dots_size=4,
								legend_at_bottom=True)
				current_male_x = 0
				current_female_x = 0
				current_x = 0
				margin = 2
				last_female_cell = ''
				last_male_cell = ''
				# the data will be arranged as a list of tuples, each tuple will be as (X,Y)
				males_data = []
				females_data = []
				x_labels = []
				for tup in current_data:
					exp_level = float(tup[1])
					parts = tup[0].split('_')
					cell = parts[0]
					# check if it is a male or female cell.
					if 'M' in parts or 'male' in parts:
						# its a male cell
						if cell != last_male_cell:
							last_male_cell = cell
							current_male_x += 2
							current_x = current_male_x
						males_data.append((current_male_x,exp_level))
					elif 'F' in parts or 'female' in parts:
						# its a female cell
						if cell != last_female_cell:
							last_female_cell = cell
							current_female_x += 2
							current_x = current_female_x
						females_data.append((current_female_x,exp_level))
					x_labels.append({ 'value': current_x,'label':cell })
				# send data for labels if needed.
				graph.title = ' '.join([gene_name,'exp level dataset:',data_set,data_tuple_key])
				graph.y_title = 'exp level log2'
				graph.add('Female',females_data)
				graph.add('Male',males_data)
				graph.x_labels = x_labels
				graphs.append(graph.render_data_uri())
		messages = get_noise_message(noise_data)
		return flask.render_template('pan_immune.html',form=form,graphs=graphs,messages=messages)
