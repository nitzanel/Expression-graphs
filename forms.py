from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, SelectField
from wtforms.validators import DataRequired

class GeneSearchForm(Form):
	gene_name = StringField('gene_symbol',validators=[DataRequired()],render_kw={'placeholder':'Enter gene symbol'})

class CellTypeSpecificForm(Form):
	gene_name = StringField('gene_symbol',validators=[DataRequired()])
	cell_type = SelectField('cell',choices=[('GN','GN'),('MF','MF'),('DC','DC'),('B1ab','B1ab'),('CD19','CD19'),('NK','NK'),('T8','T8'),('T4','T4'),('Treg','Treg'),('NKT','NKT'),('Tgd','Tgd')])

class LoginForm(Form):
    openid = StringField('openid', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)
