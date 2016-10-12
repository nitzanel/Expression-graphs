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

# the grapher object. just a middle man for the loader.
grapher = grapher.Grapher()

bad_names = ['',' ']

# return all the gene symbols in a list.
# old autocomplete.
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

# returns a list of dictionaries, each one representing a value with a label.
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
# not used anymore
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
# this is the entrance to the site.
# redirects to pan_immune.
class Main(flask.views.MethodView):
	def get(self):
		return flask.redirect(flask.url_for('pan_immune'))
	def post(self):
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

# About view
# Displays information about the site.
class About(flask.views.MethodView):
	def get(self):
		return flask.render_template('about.html')


# Genes view
# redirects to pan_immune page.
class Genes(flask.views.MethodView):
	def get(self):
		return flask.redirect(flask.url_for('pan_immune'))

# A class that deals with autocomplete.
# used to find out if the current gene_name changed.
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

# autocomplete the typing of the gene_name.
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
# input: noise data.
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

# get the index of the column for ctc graphs.
# input: current dataset.
def get_column_index(db):
	if db.startswith('FM_IFN'):
		return 0
	if db.startswith('ImmGen'):
		return 1
	if db.startswith('Female_Male'):
		return 2
	if db.startswith('pilot8'):
		return 3
	print 'get_column_index recieved bad input: {0} .'.format(db)
	return -1

# get label name from index for ctc graphs
def get_label_name(index):
	return "DS_{0}".format(chr(index + ord('A')))


# unacceptable symbols in gene_name or cell_type
bad_symbols = ['"',"'"]

# the pattern based ctc graph address
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
		IFN_males_data = []
		IFN_females_data = []
		x_labels = []
		graphs = []
		graph = pygal.XY(stroke=False,show_y_guides=False,
								truncate_label =-1,dots_size=4,
								legend_at_bottom=True,style=styles.ctc_style)
		max_exp_value = 0.0
		for data_set in data:
			# the max expression value. used to determine the y scale of the graph.
			# get the current x index for the graphs
			index = get_column_index(data_set)
			for repeat in data[data_set]:
				current_data = data[data_set][repeat]
				for tup in current_data:
					exp_level = float(tup[1])
					if max_exp_value < exp_level:
						max_exp_value = exp_level
					parts = tup[0].split('_')
					cell = parts[0]					
					if 'M' in parts or 'male' in parts:	
						# its a male cell, check for IFN.
						if '10kIFN' in parts or '1kIFN' in parts:
							# it is an IFN cell. add to male IFN
							IFN_males_data.append((index+1,exp_level))
						else:
							# it isnt an IFN cell
							males_data.append((index+1,exp_level))
					elif 'F' in parts or 'female' in parts:
						# its a female cell, check for IFN
						if '10kIFN' in parts or '1kIFN' in parts:
							# it is an IFN cell. add to female IFN
							IFN_females_data.append((index+1,exp_level))
						else:
							females_data.append((index+1,exp_level))
			x_labels.append({ 'value': index+1,'label':get_label_name(index)})
		# set the scailing of the graph.
		max_exp_value = int(max_exp_value)
		if max_exp_value >= 5:
			graph.range = (0,max_exp_value + 1) 
		else:
			graph.range = (0,5)	
		graph.title = "{0} exp level in cell {1}".format(gene_name,cell_type)
		graph.y_title = 'exp level log2'
		graph.add('Female',females_data)
		graph.add('Male',males_data)
		graph.add('Female_IFN',IFN_females_data)
		graph.add('Males_IFN',IFN_males_data)
		graph.x_labels = x_labels
		graphs.append(graph.render_data_uri())

		messages = get_noise_message(noise_data)

		return flask.render_template('cell_type_specific.html',form=form,graphs_data=graphs,messages=messages)

# the pattern based pi graph address.
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
								legend_at_bottom=True,style=styles.pi_style)
				max_exp_value = 0.0
				current_male_x = 0
				current_female_x = 0
				current_x = 0
				margin = 2
				last_female_cell = ''
				last_male_cell = ''
				# the data will be arranged as a list of tuples, each tuple will be as (X,Y)
				females_data = []
				males_data = []
				IFN_females_data = []
				IFN_males_data = []

				x_labels = []
				for tup in current_data:
					exp_level = float(tup[1])
					if max_exp_value < exp_level:
						max_exp_value = exp_level
					parts = tup[0].split('_')
					cell = parts[0]
					# check if it is a male or female cell.
					if 'M' in parts or 'male' in parts:
						# its a male cell
						if cell != last_male_cell:
							last_male_cell = cell
							current_male_x += 2
							current_x = current_male_x
						if '10kIFN' in parts or '1kIFN' in parts:
							# IFN cell
							IFN_males_data.append((current_male_x,exp_level))
						else:
							# not IFN cell
							males_data.append((current_male_x,exp_level))	
					elif 'F' in parts or 'female' in parts:
						# its a female cell
						if cell != last_female_cell:
							last_female_cell = cell
							current_female_x += 2
							current_x = current_female_x
						if '10kIFN' in parts or '1kIFN' in parts:
							# IFN cell
							IFN_females_data.append((current_female_x,exp_level))
						else:
							# not IFN cell
							females_data.append((current_female_x,exp_level))	
					x_labels.append({ 'value': current_x,'label':cell })
				# remove the last label in x_labels, because it is 'noise' and it obscures the label before it.
				x_labels.pop()
				# send data for labels if needed.
				max_exp_value = int(max_exp_value)
				if max_exp_value >= 5:
					graph.range = (0,max_exp_value + 1) 
				else:
					graph.range = (0,5)	
				graph.title = ' '.join([gene_name,'exp level dataset:',get_ds_name(data_set),data_tuple_key])
				graph.y_title = 'exp level log2'
				graph.add('Female',females_data)
				graph.add('Male',males_data)
				graph.add('IFN_Female',IFN_females_data)
				graph.add('IFN_Male',IFN_males_data)
				graph.x_labels = x_labels
				graphs.append(graph)
		graphs = sort_graphs(graphs)
		graphs = list(map(lambda graph: graph.render_data_uri(),graphs))
		messages = get_noise_message(noise_data)
		return flask.render_template('pan_immune.html',form=form,graphs=graphs,messages=messages)

# Cell_Type_Specific view
# search genes and cells for expression level graphs.
# post method to submit forms and return the data.
class Cell_Type_Specific(flask.views.MethodView):
	def get(self):
		form = forms.CellTypeSpecificForm()
		return flask.render_template('cell_type_specific.html',form=form)

	def post(self):			
		# autocomplete current symbols	
		if flask.g.sijax.is_sijax_request:
			print flask.g.sijax.get_js()
			flask.g.sijax.register_callback('autocomplete',autocomplete)
			return flask.g.sijax.process_request()
		form = forms.CellTypeSpecificForm()
		# get the gene_name and cell_type input
		gene_name = flask.request.form['gene_name']	
		gene_name = gene_name.upper()
		cell_type = flask.request.form['cell_type']

		# check for bad symbols in gene_name
		if gene_name == '-' or '"' in gene_name or "'" in gene_name :
			flask.flash('Symbol no valid.')
			return flask.render_template('cell_type_specific.html',form=form)
		# redirect to the address of the wanted graph
		return flask.redirect(get_ctc_address(gene_name,cell_type))	
		
		
# creates a html option tag, for the autocomplete.
# input: gene_symbol - an autocomplete string.
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
		# autocomplete current symbols
		if flask.g.sijax.is_sijax_request:
			flask.g.sijax.register_callback('autocomplete',autocomplete)
			return flask.g.sijax.process_request()
		form = forms.GeneSearchForm()
		# get the gene_name input.
		gene_name = flask.request.form['gene_name'].upper()
		gene_name = gene_name.upper()
		# check for bad symbols in gene_name
		if gene_name == '-' or '"' in gene_name or "'" in gene_name :
			flask.flash('Symbol not valid.')	
			return flask.render_template('pan_immune.html',form=form)			
		# redirect to the address of the wanted graphs
		return flask.redirect(get_pi_address(gene_name))
		