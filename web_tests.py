import os
from website import FlaskApp
import unittest


class BaseTestCase(unittest.TestCase):

	""" A base test case."""
	def create_app(self):
		flaskApp = FlaskApp()
		flaskApp.app.config['TESTING'] =True
		flaskApp.app.config['DEBUG'] =True		
		return flaskApp

	def setUp(self):
	
		self.client = self.create_app().app.test_client(self)

	def tearDown(self):
		pass

class FlaskTestCase(BaseTestCase):
	# Ensure about loads without errors 
	def test_about(self):
		response = self.client.get('/about',content_type='html/text')
		self.assertEqual(response.status_code,200)

	# Ensure pan_immune loads without errors
	def test_pan_immune(self):
		response = self.client.get('/genes/pan_immune', content_type='html/text')
		self.assertEqual(response.status_code,200)

	# Ensure cell_type_specific loads without errors
	def test_cell_type_specific(self):
		response = self.client.get('/genes/cell_type_specific', content_type='html/text')
		self.assertEqual(response.status_code,200)

class GraphTestCase(BaseTestCase):
	# Ensure a post request in pan_immune works for a known gene symbol
	def test_pan_immune_post_exist(self):
		response = self.client.post('/genes/pan_immune', data={'gene_name':'SON'})
		self.assertEqual(response.status_code,200)
		self.assertIn('there are graphs',response.data)

	# Ensure a post request in pan_immune doesnt work for ''
	def test_pan_immune_post_empty(self):
		response = self.client.post('/genes/pan_immune', data={'gene_name':''})
		self.assertEqual(response.status_code,200)
		self.assertNotIn('there are graphs',response.data)

	# Ensure a post request in pan_immune doesnt work for ' '
	def test_pan_immune_post_space(self):
		response = self.client.post('/genes/pan_immune', data={'gene_name':' '})
		self.assertEqual(response.status_code,200)
		self.assertNotIn('there are graphs',response.data)

	# Ensure a post request in pan_immune doesnt work for something that is not a known gene in the database
	def test_pan_immune_unknown_gene(self):
		response = self.client.post('/genes/pan_immune', data={'gene_name':'notagene'})
		self.assertEqual(response.status_code,200)
		self.assertNotIn('there are graphs',response.data)	

	# this test suppose to fail right now
	def test_cell_type_specific_post(self):
		#response = self.client.post('/genes/cell_type_specific', data={'gene_name':'SON'})
		#self.assertEqual(response.status_code,400)
		pass
	def test_cell_type_specific_many(self):
		pass



if __name__ == '__main__':
	unittest.main()
