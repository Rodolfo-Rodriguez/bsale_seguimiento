import os
import copy
from flask import render_template, redirect, Blueprint, session, url_for, request,  send_from_directory
from sqlalchemy_filters import apply_filters
from flask_login import login_required

import randomcolor
from datetime import datetime as dt
from openpyxl import Workbook

import pandas as pd

deal = Blueprint('deal', __name__)

from . import db, config
from .models import Seguimiento
from .forms import SeguimientoForm, FileForm, ConfirmForm, DealVentaForm, DealPEMForm, DealProdForm, DealBajaForm

#---------------------------------------------------------------------------------------------------------------------------------
# Show Deal
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/show/<id>", methods=["GET"])
@login_required
def deal_show(id):

	deal = Seguimiento.query.get(id)

	session['LAST_URL'] = url_for('deal.deal_show', id=id)
	
	return render_template('show_deal.html', deal=deal)

#---------------------------------------------------------------------------------------------------------------------------------
# Deal - List
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/list", methods=["GET"])
@login_required
def deal_list():

	if 'DEAL_FILTERS' not in session:
		session['DEAL_FILTERS'] = {}	

	query_filter = []
	for field, field_list in session['DEAL_FILTERS'].items():
		if len(field_list) > 1:
			if field in ['fecha_ganado', 'fecha_pase_produccion']:
				query_filter.append({'and':field_list})
			else:
				query_filter.append({'or':field_list})
		elif len(field_list)==1:
			query_filter.append(field_list[0])	
	
	query = db.session.query(Seguimiento)
	query = apply_filters(query, query_filter)

	items = query.all()

	session['LAST_URL'] = url_for('deal.deal_list')
	
	return render_template('list_deal.html', items=items)


#---------------------------------------------------------------------------------------------------------------------------------
# Deal - Add Filter
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/add_filter", methods=["GET"])
@login_required
def deal_add_filter():

	field = request.args.get('field')
	op = request.args.get('op')
	value = '' if request.args.get('value') == 'NA' else request.args.get('value')
	filter_dict = {'field': field, 'op': op, 'value': value}
	
	if 'DEAL_FILTERS' not in session:
		deal_filters = {}
	else:
		deal_filters = session['DEAL_FILTERS']

	
	if field not in deal_filters:
		deal_filters[field] = [filter_dict]
	else:
		if filter_dict not in deal_filters[field]:
			deal_filters[field].append(filter_dict)		

	session['DEAL_FILTERS'] = deal_filters

	return redirect(session['LAST_URL'])

#---------------------------------------------------------------------------------------------------------------------------------
# Deal - Remove Filter
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/remove_filter", methods=["GET"])
@login_required
def deal_remove_filter():

	field = request.args.get('field')
	op = request.args.get('op')
	value = '' if request.args.get('value') == 'NA' else request.args.get('value')
	filter_dict = {'field': field, 'op': op, 'value': value}
	
	if 'DEAL_FILTERS' not in session:
		deal_filters = {}
	else:
		deal_filters = session['DEAL_FILTERS']

	if field in deal_filters:
		deal_filters[field].remove(filter_dict)
			

	session['DEAL_FILTERS'] = deal_filters
	print(session['DEAL_FILTERS'])

	return redirect(session['LAST_URL'])

#---------------------------------------------------------------------------------------------------------------------------------
# Deal por Field
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/list/<field>/<value>", methods=["GET"])
@login_required
def deal_list_field_value(field, value):

	if 'DEAL_FILTERS' not in session:
		deal_filters = []
	else:
		deal_filters = session['DEAL_FILTERS']
		#deal_filters.clear()

	value = '' if value == 'NA' else value

	deal_filters.append({'field': field, 'op': '==', 'value': value})

	session['DEAL_FILTERS'] = deal_filters

	session['LAST_URL'] = url_for('deal.deal_list_field_value', field=field, value=value)
	
	return redirect(url_for('deal.deal_list'))


#---------------------------------------------------------------------------------------------------------------------------------
# Deal - List para un Mes
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/list/mes/<mes>", methods=["GET"])
@login_required
def deal_list_mes(mes):

	fecha_ini = '{}-01'.format(mes)
	fecha_fin = '{}-31'.format(mes)
	
	if 'DEAL_FILTERS' not in session:
		deal_filters = {}
	else:
		deal_filters = session['DEAL_FILTERS']
		deal_filters.clear()

	field_list = []
	field_list.append({'field': 'fecha_ganado', 'op': '>=', 'value': fecha_ini})
	field_list.append({'field': 'fecha_ganado', 'op': '<=', 'value': fecha_fin})
	deal_filters['fecha_ganado'] = field_list

	session['DEAL_FILTERS'] = deal_filters

	return redirect(url_for('deal.deal_list'))


#---------------------------------------------------------------------------------------------------------------------------------
# Deal - List para un Mes y Comercial
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/list/mes/comercial/<mes>/<comercial>", methods=["GET"])
@login_required
def deal_list_mes_comercial(mes, comercial):

	fecha_ini = '{}-01'.format(mes)
	fecha_fin = '{}-31'.format(mes)
	
	if 'DEAL_FILTERS' not in session:
		deal_filters = {}
	else:
		deal_filters = session['DEAL_FILTERS']
		deal_filters.clear()

	field_list = []
	field_list.append({'field': 'fecha_ganado', 'op': '>=', 'value': fecha_ini})
	field_list.append({'field': 'fecha_ganado', 'op': '<=', 'value': fecha_fin})
	deal_filters['fecha_ganado'] = field_list

	field_list = []
	field_list.append({'field': 'comercial', 'op': '==', 'value': comercial})
	deal_filters['comercial'] = field_list

	session['DEAL_FILTERS'] = deal_filters

	return redirect(url_for('deal.deal_list'))

#---------------------------------------------------------------------------------------------------------------------------------
# Deal - List puesta en produccion en mes
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/list/mes/produccion/<mes>", methods=["GET"])
@login_required
def deal_list_mes_produccion(mes):

	fecha_ini = '{}-01'.format(mes)
	fecha_fin = '{}-31'.format(mes)
	
	if 'DEAL_FILTERS' not in session:
		deal_filters = {}
	else:
		deal_filters = session['DEAL_FILTERS']
		deal_filters.clear()

	field_list = []
	field_list.append({'field': 'fecha_pase_produccion', 'op': '>=', 'value': fecha_ini})
	field_list.append({'field': 'fecha_pase_produccion', 'op': '<=', 'value': fecha_fin})
	deal_filters['fecha_pase_produccion'] = field_list

	session['DEAL_FILTERS'] = deal_filters

	return redirect(url_for('deal.deal_list'))

#---------------------------------------------------------------------------------------------------------------------------------
# Edit Seguimiento
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/edit/<id>", methods=['GET', 'POST'])
@login_required
def deal_edit(id):

	seguimiento = Seguimiento.query.get(id)
	form = SeguimientoForm()
	form.title = seguimiento.razon_social

	form.comercial.choices = [('','NO')] + sorted([ (deal.comercial, deal.comercial) for deal in db.session.query(Seguimiento.comercial).distinct() if deal.comercial != '' ])
	form.plan_bsale.choices = [('','NO')] + sorted([ (deal.plan_bsale, deal.plan_bsale) for deal in db.session.query(Seguimiento.plan_bsale).distinct() if deal.plan_bsale != ''])
	form.estado.choices = sorted([ (deal.estado, deal.estado) for deal in db.session.query(Seguimiento.estado).distinct() ])
	form.produccion.choices = [('','NO')] + sorted([ (deal.produccion, deal.produccion) for deal in db.session.query(Seguimiento.produccion).distinct() if deal.produccion != ''])
	form.ejecutivo_pem.choices = [('','NO')] + sorted([ (deal.ejecutivo_pem, deal.ejecutivo_pem) for deal in db.session.query(Seguimiento.ejecutivo_pem).distinct() if deal.ejecutivo_pem != ''])
         
	if form.validate_on_submit():
        
		seguimiento.razon_social = form.razon_social.data
		seguimiento.comercial = form.comercial.data
		seguimiento.plan_bsale = form.plan_bsale.data
		seguimiento.categoria = form.categoria.data
		seguimiento.estado = form.estado.data
		seguimiento.produccion = form.produccion.data
		seguimiento.ejecutivo_pem = form.ejecutivo_pem.data		
		seguimiento.fecha_ganado = form.fecha_ganado.data
		seguimiento.fecha_inicio_pem = form.fecha_inicio_pem.data
		seguimiento.fecha_contacto_inicial = form.fecha_contacto_inicial.data		
		seguimiento.fecha_pase_produccion = form.fecha_pase_produccion.data		
		seguimiento.fecha_baja = form.fecha_baja.data
		seguimiento.url_bsale = form.url_bsale.data		
		seguimiento.razon_baja = form.razon_baja.data	

		db.session.commit()

		return redirect(session['LAST_URL'])

	form.razon_social.data = seguimiento.razon_social
	form.comercial.data = seguimiento.comercial
	form.plan_bsale.data = seguimiento.plan_bsale
	form.categoria.data = seguimiento.categoria
	form.estado.data = seguimiento.estado
	form.produccion.data = seguimiento.produccion
	form.ejecutivo_pem.data = seguimiento.ejecutivo_pem 
	form.fecha_ganado.data = seguimiento.fecha_ganado
	form.fecha_inicio_pem.data = seguimiento.fecha_inicio_pem
	form.fecha_contacto_inicial.data = seguimiento.fecha_contacto_inicial
	form.fecha_pase_produccion.data = seguimiento.fecha_pase_produccion
	form.fecha_baja.data = seguimiento.fecha_baja
	form.url_bsale.data = seguimiento.url_bsale
	form.comentario.data = seguimiento.comentario
	form.razon_baja.data = seguimiento.razon_baja

	return render_template("edit_deal.html", form=form)

#---------------------------------------------------------------------------------------------------------------------------------
# Edit Deal - Venta
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/edit_venta/<id>", methods=['GET', 'POST'])
@login_required
def deal_edit_venta(id):

	seguimiento = Seguimiento.query.get(id)
	form = DealVentaForm()
	form.title = seguimiento.razon_social

	form.comercial.choices = [('','NO')] + sorted([ (deal.comercial, deal.comercial) for deal in db.session.query(Seguimiento.comercial).distinct() if deal.comercial != '' ])
	form.plan_bsale.choices = [('','NO')] + sorted([ (deal.plan_bsale, deal.plan_bsale) for deal in db.session.query(Seguimiento.plan_bsale).distinct() if deal.plan_bsale != ''])
	form.estado.choices = sorted([ (deal.estado, deal.estado) for deal in db.session.query(Seguimiento.estado).distinct() ])
         
	if form.validate_on_submit():
        
		seguimiento.cpn = form.cpn.data
		seguimiento.ruc = form.ruc.data
		seguimiento.razon_social = form.razon_social.data
		seguimiento.comercial = form.comercial.data
		seguimiento.plan_bsale = form.plan_bsale.data
		seguimiento.categoria = form.categoria.data
		seguimiento.fecha_ganado = form.fecha_ganado.data
		seguimiento.estado = form.estado.data

		db.session.commit()

		return redirect(session['LAST_URL'])

	form.cpn.data = seguimiento.cpn
	form.ruc.data = seguimiento.ruc
	form.razon_social.data = seguimiento.razon_social
	form.comercial.data = seguimiento.comercial
	form.plan_bsale.data = seguimiento.plan_bsale
	form.categoria.data = seguimiento.categoria
	form.fecha_ganado.data = seguimiento.fecha_ganado
	form.estado.data = seguimiento.estado


	return render_template("edit_deal_venta.html", form=form)

#---------------------------------------------------------------------------------------------------------------------------------
# Edit Deal - PEM
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/edit_pem/<id>", methods=['GET', 'POST'])
@login_required
def deal_edit_pem(id):

	seguimiento = Seguimiento.query.get(id)
	form = DealPEMForm()
	form.title = seguimiento.razon_social

	form.ejecutivo_pem.choices = [('','NO')] + sorted([ (deal.ejecutivo_pem, deal.ejecutivo_pem) for deal in db.session.query(Seguimiento.ejecutivo_pem).distinct() if deal.ejecutivo_pem != ''])
         
	if form.validate_on_submit():
        
		seguimiento.ejecutivo_pem = form.ejecutivo_pem.data		
		seguimiento.fecha_inicio_pem = form.fecha_inicio_pem.data
		seguimiento.fecha_contacto_inicial = form.fecha_contacto_inicial.data		

		db.session.commit()

		return redirect(session['LAST_URL'])

	form.ejecutivo_pem.data = seguimiento.ejecutivo_pem 
	form.fecha_inicio_pem.data = seguimiento.fecha_inicio_pem
	form.fecha_contacto_inicial.data = seguimiento.fecha_contacto_inicial

	return render_template("edit_deal_pem.html", form=form)

#---------------------------------------------------------------------------------------------------------------------------------
# Edit Deal Produccion
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/edit_prod/<id>", methods=['GET', 'POST'])
@login_required
def deal_edit_prod(id):

	seguimiento = Seguimiento.query.get(id)
	form = DealProdForm()
	form.title = seguimiento.razon_social

	form.produccion.choices = [('','NO')] + sorted([ (deal.produccion, deal.produccion) for deal in db.session.query(Seguimiento.produccion).distinct() if deal.produccion != ''])
         
	if form.validate_on_submit():
        
		seguimiento.produccion = form.produccion.data
		seguimiento.fecha_pase_produccion = form.fecha_pase_produccion.data		
		seguimiento.url_bsale = form.url_bsale.data		

		db.session.commit()

		return redirect(session['LAST_URL'])

	form.produccion.data = seguimiento.produccion
	form.fecha_pase_produccion.data = seguimiento.fecha_pase_produccion
	form.url_bsale.data = seguimiento.url_bsale

	return render_template("edit_deal_prod.html", form=form)

#---------------------------------------------------------------------------------------------------------------------------------
# Edit Deal Baja
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/edit_baja/<id>", methods=['GET', 'POST'])
@login_required
def deal_edit_baja(id):

	seguimiento = Seguimiento.query.get(id)
	form = DealBajaForm()
	form.title = seguimiento.razon_social
         
	if form.validate_on_submit():
        
		seguimiento.fecha_baja = form.fecha_baja.data
		seguimiento.razon_baja = form.razon_baja.data	
		seguimiento.comentario = form.comentario.data

		db.session.commit()

		return redirect(session['LAST_URL'])

	form.fecha_baja.data = seguimiento.fecha_baja
	form.razon_baja.data = seguimiento.razon_baja
	form.comentario.data = seguimiento.comentario

	return render_template("edit_deal_baja.html", form=form)

#---------------------------------------------------------------------------------------------------------------------------------
# Deal - Delete
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/delete/<id>", methods=["GET","POST"])
@login_required
def deal_delete(id):

	deal = Seguimiento.query.get(id)

	form = ConfirmForm()

	form.title = 'Borrar - {} - {}'.format(deal.negocio_id,deal.razon_social)

	if form.validate_on_submit():

		db.session.delete(deal)

		db.session.commit()

		return redirect(session['LAST_URL'])


	return render_template('delete_deal.html', form=form)

#---------------------------------------------------------------------------------------------------------------------------------
# Deal - Download
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/download", methods=["GET"])
@login_required
def deal_download():

	if 'DEAL_FILTERS' not in session:
		session['DEAL_FILTERS'] = {}	

	query_filter = []
	for field, field_list in session['DEAL_FILTERS'].items():
		if len(field_list) > 1:
			if field in ['fecha_ganado', 'fecha_pase_produccion']:
				query_filter.append({'and':field_list})
			else:
				query_filter.append({'or':field_list})
		elif len(field_list)==1:
			query_filter.append(field_list[0])	
	
	query = db.session.query(Seguimiento)
	query = apply_filters(query, query_filter)

	items = query.all()

	today = dt.today().strftime("%Y-%m-%d-%H%M%S")
	filename = 'deals-{}.xlsx'.format(today)
	filepath = 'export/{}'.format(filename)

	wb = Workbook()
	ws = wb.active
	ws.title = 'Deals'

	ws.cell(column=1, row=1).value = 'ID NEgocio'
	ws.cell(column=2, row=1).value = 'RUC'
	ws.cell(column=3, row=1).value = 'CPN'
	ws.cell(column=4, row=1).value = 'Comercial'
	ws.cell(column=5, row=1).value = 'Razon Social'
	ws.cell(column=6, row=1).value = 'Plan BSale'
	ws.cell(column=7, row=1).value = 'Categoria'
	ws.cell(column=8, row=1).value = 'Estado'
	ws.cell(column=9, row=1).value = 'Produccion'
	ws.cell(column=10, row=1).value = 'Ejecutivo PEM'
	ws.cell(column=11, row=1).value = 'Fecha Ganado'
	ws.cell(column=12, row=1).value = 'Fecha Inicio PEM'
	ws.cell(column=13, row=1).value = 'Fecha Contacto Inicial'
	ws.cell(column=14, row=1).value = 'Fecha Pase a Produccion'
	ws.cell(column=15, row=1).value = 'Dias en PEM'
	ws.cell(column=16, row=1).value = 'URL BSale'
	ws.cell(column=17, row=1).value = 'Fecha de Baja'
	ws.cell(column=18, row=1).value = 'Razon de Baja'
	ws.cell(column=19, row=1).value = 'Comentario'
	for row, item in enumerate(items):
		print(row)
		ws.cell(column=1, row=row+2).value = item.negocio_id
		ws.cell(column=2, row=row+2).value = item.ruc
		ws.cell(column=3, row=row+2).value = item.cpn
		ws.cell(column=4, row=row+2).value = item.comercial
		ws.cell(column=5, row=row+2).value = item.razon_social
		ws.cell(column=6, row=row+2).value = item.plan_bsale
		ws.cell(column=7, row=row+2).value = item.categoria
		ws.cell(column=8, row=row+2).value = item.estado
		ws.cell(column=9, row=row+2).value = item.produccion
		ws.cell(column=10, row=row+2).value = item.ejecutivo_pem
		ws.cell(column=11, row=row+2).value = item.fecha_ganado
		ws.cell(column=12, row=row+2).value = item.fecha_inicio_pem
		ws.cell(column=13, row=row+2).value = item.fecha_contacto_inicial
		ws.cell(column=14, row=row+2).value = item.fecha_pase_produccion
		ws.cell(column=15, row=row+2).value = item.dias_pem()
		ws.cell(column=16, row=row+2).value = item.url_bsale
		ws.cell(column=17, row=row+2).value = item.fecha_baja
		ws.cell(column=18, row=row+2).value = item.razon_baja
		ws.cell(column=19, row=row+2).value = item.comentario

	wb.save(filename = filepath)
	
	return send_from_directory('../export', filename, cache_timeout=0, as_attachment=True)

#---------------------------------------------------------------------------------------------------------------------------------
# Load Deals
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/load", methods=['GET', 'POST'])
@login_required
def deal_load():

	form = FileForm()
        
	if form.validate_on_submit():

		df = pd.read_sql_table('seguimiento', con=db.engine, columns=['negocio_id'])

		excel_file = form.filename.data
		local_excel_file = os.path.join(config['DATA_DIR'], config['DEALS_FILE'])
		excel_file.save(local_excel_file)

		df_new = pd.read_excel(excel_file, 
								usecols = ["Negocio - ID",
											"Negocio - RUT/RUC/NIT",
											"Negocio - Título", 
											"Negocio - Propietario", 
											"Negocio - Servicio Contratado",
											"Negocio - Rubro/Actividad Económica",
											"Negocio - Fecha de ganado"],
								dtype = {"Negocio - RUT/RUC/NIT":str, "Negocio - Fecha de ganado":str})

		df_new.rename( columns = { "Negocio - ID":"negocio_id",
								"Negocio - RUT/RUC/NIT":"ruc",
								"Negocio - Título":"razon_social",
								"Negocio - Propietario":"comercial",
								"Negocio - Servicio Contratado":"plan_bsale",
								"Negocio - Rubro/Actividad Económica":"categoria",
								"Negocio - Fecha de ganado":"fecha_ganado"}, 
						inplace=True)
		

		df_new.fillna( value = {'ruc':'',
							'razon_social':'',
							'comercial':'',
							'plan_bsale':'',
							'categoria':'',
							'fecha_ganado':''}, 
						inplace=True)
		
		df_new.loc[:,'cpn'] = df_new.loc[:,'razon_social'].apply(lambda x: int(x[-6:-1]) if x[-6:-1].isdigit() else ( int(x[-5:]) if x[-5:].isdigit() else 0 ) )
		df_new.loc[:,'fecha_ganado'] = df_new.loc[:,'fecha_ganado'].apply(lambda x: x[0:10])
		df_new.loc[:,'comercial'] = df_new.loc[:,'comercial'].apply(lambda x: x.split(' ')[0].upper() + ' ' + x.split(' ')[1][0].upper())
		
		planes = {
					"Plan Estándar PV":"Estándar PV",
					"Módulo Ecommerce":"Módulo Ecommerce",
					"Plan Estándar TO":"Estándar TO",
					"Plan Básico":"Básico",
					"Plan Full":"Omnicanal"
		}

		df_new.loc[:,'plan_bsale'] = df_new.loc[:,'plan_bsale'].apply(lambda x: planes[x] if x in planes else '')

		df_merge = pd.merge(df, df_new, how='outer', indicator=True)

		df_merge = df_merge[ df_merge['_merge']=='right_only']

		df_merge.drop(columns=['_merge'], inplace=True)

		#df_merge.drop_duplicates(subset ='cpn', keep='first', inplace=True)

		if not df_merge.empty:
			df_merge.loc[:,'estado'] = ''
			df_merge.loc[:,'produccion'] = ''
			df_merge.loc[:,'ejecutivo_pem'] = ''
			df_merge.loc[:,'fecha_inicio_pem'] = ''
			df_merge.loc[:,'fecha_contacto_inicial'] = ''
			df_merge.loc[:,'fecha_pase_produccion'] = ''
			df_merge.loc[:,'hizo_upselling'] = ''
			df_merge.loc[:,'url_bsale'] = ''
			df_merge.loc[:,'comentario'] = 'Nuevo'

			df_merge.to_sql('seguimiento', con=db.engine, if_exists='append', index=False)

		return redirect(url_for('main.home'))

	return render_template("edit_excel_file.html", form=form)

