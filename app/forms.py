from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, FloatField, IntegerField, TextAreaField, DateField, BooleanField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError

class SeguimientoForm(FlaskForm):
	title = 'Edit'

	comercial = SelectField('Comercial', choices=[ ('','NO')])
	plan_bsale = SelectField('Plan BSale', choices=[ ('','NO')])
	categoria = StringField('Categoria')
	estado = SelectField('Estado', choices=[('','NO')])
	produccion = SelectField('Produccion', choices=[('','NO')])
	ejecutivo_pem = SelectField('Ejecutivo PEM', choices=[('','NO')])
	fecha_ganado = StringField('Fecha Ganado')
	fecha_inicio_pem = StringField('Fecha Inicio PEM')
	fecha_contacto_inicial = StringField('Fecha de Contacto Inicial')
	fecha_pase_produccion = StringField('Fecha de Pase a Produccion')
	hizo_upselling = BooleanField('Hizo Upselling')
	url_bsale = StringField('URL BSale')
	comentario = TextAreaField('Comentario')

	submit = SubmitField('Submit')


class FileForm(FlaskForm):
	title = 'Cargar desde Excel'

	filename = FileField('Archivo')

	submit = SubmitField('Submit')
