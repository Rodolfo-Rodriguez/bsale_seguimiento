from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, FloatField, IntegerField, TextAreaField, DateField, BooleanField, PasswordField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import Required, DataRequired, InputRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError

class DealForm(FlaskForm):
	title = 'Edit'

	razon_social = StringField('Razón Social')
	comercial = SelectField('Comercial', choices=[ ('','NO')])
	plan_bsale = SelectField('Plan BSale', choices=[ ('','NO')])
	categoria = StringField('Categoria')
	etapa = SelectField('Etapa', choices=[('','NO')])
	estado = SelectField('Estado', choices=[('','NO')])
	ejecutivo_pem = SelectField('Ejecutivo PEM', choices=[('','NO')])
	fecha_ganado = StringField('Fecha Ganado')
	fecha_inicio_pem = StringField('Fecha Inicio PEM')
	fecha_contacto_inicial = StringField('Fecha de Contacto Inicial')
	fecha_pase_produccion = StringField('Fecha de Pase a Produccion')
	fecha_baja = StringField('Fecha de Baja')
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


class DealEtapaForm(FlaskForm):
	title = 'Edit'

	etapa = SelectField('Etapa', choices=[('','NO')])

	submit = SubmitField('Submit')

class DealVentaForm(FlaskForm):
	title = 'Edit'

	cpn = StringField('CPN')
	ruc = StringField('RUC')
	razon_social = StringField('Razón Social')
	comercial = SelectField('Comercial', choices=[ ('','NO')])
	plan_bsale = SelectField('Plan BSale', choices=[ ('','NO')])
	categoria = StringField('Categoria')
	etapa = SelectField('Etapa', choices=[('','NO')])
	fecha_ganado = StringField('Fecha Ganado')

	submit = SubmitField('Submit')

class DealPEMForm(FlaskForm):
	title = 'Edit'

	ejecutivo_pem = SelectField('Ejecutivo PEM', choices=[('','NO')])
	fecha_inicio_pem = StringField('Fecha Inicio PEM')
	fecha_contacto_inicial = StringField('Fecha de Contacto Inicial')
	fecha_pase_produccion = StringField('Fecha de Pase a Produccion')
	url_bsale = StringField('URL BSale')

	submit = SubmitField('Submit')


class DealBajaForm(FlaskForm):
	title = 'Edit'

	fecha_baja = StringField('Fecha de Baja')
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


class CheckpointForm(FlaskForm):
	title = 'Edit'

	fecha_realizado = StringField('Fecha')
	realizado = BooleanField('Realizado')
	comentario = TextAreaField('Comentario')
	estado = SelectField('Estado', choices=[('','NO'),('CON USO','CON USO'),('SIN USO','SIN USO'),('BLOQUEADO','BLOQUEADO')])

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
