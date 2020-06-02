from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, FloatField, IntegerField, TextAreaField, DateField, BooleanField, PasswordField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import Required, DataRequired, InputRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError

class SeguimientoForm(FlaskForm):
	title = 'Edit'

	razon_social = StringField('Razón Social')
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
	hizo_upselling = SelectField('Hizo Upselling', choices=[ ('SI','SI'),('NO','NO')])
	url_bsale = StringField('URL BSale')
	comentario = TextAreaField('Comentario')
	razon_baja = SelectField('Razón Baja', choices=[('','NO'), 
													('ACTIVACION TEMPORAL','ACTIVACION TEMPORAL'),
													('BAJA PLAN ECOMMERCE','BAJA PLAN ECOMMERCE'),
													('CAMBIO DE RUC','CAMBIO DE RUC'),
													('CAMBIO PROVEEDOR','CAMBIO PROVEEDOR'),
													('CIERRE DE NEGOCIO','CIERRE DE NEGOCIO'),
													('DEUDA','DEUDA'),
													('FALTA SEGUIMIENTO USO','FALTA SEGUIMIENTO USO'),
													('FUNCIONALIDAD','FUNCIONALIDAD'),
													('MAL CALCE','MAL CALCE'),
													('PEM','PEM'),
													('PRECIO','PRECIO')])

	submit = SubmitField('Submit')


class FileForm(FlaskForm):
	title = 'Cargar desde Excel'

	filename = FileField('Archivo')

	submit = SubmitField('Submit')


class LoginForm(FlaskForm):

	username = StringField('User', validators=[Required()])
	password = PasswordField('Password', validators=[Required()])
	remember_me = BooleanField('Keep me logged in')

	submit = SubmitField('Login')

class ConfirmForm(FlaskForm):

	title = 'Confirm'
	submit = SubmitField('Borrar')
