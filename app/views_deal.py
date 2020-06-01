import os
import copy
from flask import render_template, redirect, Blueprint, session, url_for
from sqlalchemy_filters import apply_filters

import randomcolor
from datetime import datetime as dt

import pandas as pd

deal = Blueprint('deal', __name__)

from . import db, config
from .models import Seguimiento
from .forms import SeguimientoForm, FileForm

#---------------------------------------------------------------------------------------------------------------------------------
# Show Deal
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/show/<id>", methods=["GET"])
def deal_show(id):

	deal = Seguimiento.query.get(id)

	session['LAST_URL'] = url_for('deal.deal_show', id=id)
	
	return render_template('show_deal.html', deal=deal)

#---------------------------------------------------------------------------------------------------------------------------------
# Deal - List
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/list", methods=["GET"])
def deal_list():

	if 'DEAL_FILTERS' not in session:
		session['DEAL_FILTERS'] = []	
	
	query = db.session.query(Seguimiento)
	query = apply_filters(query, session['DEAL_FILTERS'])

	items = query.all()

	session['LAST_URL'] = url_for('deal.deal_list')
	
	return render_template('list_deal.html', items=items, deal_filters=session['DEAL_FILTERS'])

#---------------------------------------------------------------------------------------------------------------------------------
# Deal - Add Filter
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/add_filter/<field>/<op>/<value>", methods=["GET"])
def deal_add_filter(field, op, value):
	
	if 'DEAL_FILTERS' not in session:
		deal_filters = []
	else:
		deal_filters = session['DEAL_FILTERS']

	value = '' if value == 'NA' else value

	if field not in [ f['field'] for f in deal_filters ]:
		deal_filters.append({'field': field, 'op': op, 'value': value})

	session['DEAL_FILTERS'] = deal_filters

	return redirect(url_for('deal.deal_list'))

#---------------------------------------------------------------------------------------------------------------------------------
# Deal - Remove Filter
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/remove_filter/<field>/<op>/<value>", methods=["GET"])
def deal_remove_filter(field, op, value):
	
	if 'DEAL_FILTERS' not in session:
		deal_filters = []
	else:
		deal_filters = session['DEAL_FILTERS']

	value = '' if value == 'NA' else value

	item = {'field': field, 'op': op, 'value': value}
	if item in deal_filters:
		deal_filters.remove(item)

	session['DEAL_FILTERS'] = deal_filters

	return redirect(url_for('deal.deal_list'))

#---------------------------------------------------------------------------------------------------------------------------------
# Deal por Field
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/list/<field>/<value>", methods=["GET"])
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
def deal_list_mes(mes):

	fecha_ini = '{}-01'.format(mes)
	fecha_fin = '{}-31'.format(mes)
	
	if 'DEAL_FILTERS' not in session:
		deal_filters = []
	else:
		deal_filters = session['DEAL_FILTERS']
		deal_filters.clear()

	deal_filters.append({'field': 'fecha_ganado', 'op': '>=', 'value': fecha_ini})
	deal_filters.append({'field': 'fecha_ganado', 'op': '<=', 'value': fecha_fin})

	session['DEAL_FILTERS'] = deal_filters

	return redirect(url_for('deal.deal_list'))


#---------------------------------------------------------------------------------------------------------------------------------
# Deal - List para un Mes y Comercial
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/list/mes/comercial/<mes>/<comercial>", methods=["GET"])
def deal_list_mes_comercial(mes, comercial):

	fecha_ini = '{}-01'.format(mes)
	fecha_fin = '{}-31'.format(mes)
	
	if 'DEAL_FILTERS' not in session:
		deal_filters = []
	else:
		deal_filters = session['DEAL_FILTERS']
		deal_filters.clear()

	deal_filters.append({'field': 'fecha_ganado', 'op': '>=', 'value': fecha_ini})
	deal_filters.append({'field': 'fecha_ganado', 'op': '<=', 'value': fecha_fin})
	deal_filters.append({'field': 'comercial', 'op': '==', 'value': comercial})

	session['DEAL_FILTERS'] = deal_filters

	return redirect(url_for('deal.deal_list'))

#---------------------------------------------------------------------------------------------------------------------------------
# Deal - List puesta en produccion en mes
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/list/mes/produccion/<mes>", methods=["GET"])
def deal_list_mes_produccion(mes):

	fecha_ini = '{}-01'.format(mes)
	fecha_fin = '{}-31'.format(mes)
	
	if 'DEAL_FILTERS' not in session:
		deal_filters = []
	else:
		deal_filters = session['DEAL_FILTERS']
		deal_filters.clear()

	deal_filters.append({'field': 'fecha_pase_produccion', 'op': '>=', 'value': fecha_ini})
	deal_filters.append({'field': 'fecha_pase_produccion', 'op': '<=', 'value': fecha_fin})

	session['DEAL_FILTERS'] = deal_filters

	return redirect(url_for('deal.deal_list'))

#---------------------------------------------------------------------------------------------------------------------------------
# Edit Seguimiento
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/edit/<id>", methods=['GET', 'POST'])
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
		seguimiento.hizo_upselling = form.hizo_upselling.data
		seguimiento.url_bsale = form.url_bsale.data		

		db.session.commit()

		return redirect(session['LAST_URL'])

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
	form.hizo_upselling.data = seguimiento.hizo_upselling
	form.url_bsale.data = seguimiento.url_bsale
	form.comentario.data = seguimiento.comentario

	return render_template("edit_deal.html", form=form)


#---------------------------------------------------------------------------------------------------------------------------------
# Load Deals
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/load", methods=['GET', 'POST'])
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

