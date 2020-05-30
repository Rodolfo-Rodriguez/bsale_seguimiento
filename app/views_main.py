import os
import copy
from flask import render_template, redirect, Blueprint, session, url_for
from sqlalchemy_filters import apply_filters

import randomcolor
from datetime import datetime as dt

import pandas as pd

main = Blueprint('main', __name__)

from . import db, config
from .models import Seguimiento
from .forms import SeguimientoForm, FileForm

#---------------------------------------------------------------------------------------------------------------------------------
# Home
#---------------------------------------------------------------------------------------------------------------------------------
@main.route("/", methods=["GET"])
def home():

	mes = dt.today().date().strftime("%Y-%m")

	fecha_ini = '{}-01'.format(mes)
	fecha_fin = '{}-31'.format(mes)

	data_all = []
	totals = []
	titles = []
	colors = []

	deals = Seguimiento.query.filter(Seguimiento.fecha_ganado >= fecha_ini, Seguimiento.fecha_ganado <= fecha_fin)
	venta_total = deals.count()

	##--- Comerciales para el mes

	titles.append('Ventas por Comercial - Mes {}'.format(mes))

	comerciales = [ deal.comercial for deal in db.session.query(Seguimiento.comercial).filter(Seguimiento.fecha_ganado >= fecha_ini, Seguimiento.fecha_ganado <= fecha_fin).distinct() ]

	data = []
	meta = 12
	meta_total = 86

	for comercial in comerciales:
		ventas = len([ deal for deal in deals if deal.comercial == comercial ])
		data.append({'comercial':comercial, 'meta':meta, 'ventas':ventas, 'cumpl': int(round(100 * ventas/meta,0)) })

	data.sort(key = lambda x: x['ventas'], reverse=True)

	totals.append({'meta_total':meta_total, 'venta_total':venta_total, 'cumpl':int(round(100 * venta_total/meta_total,0))})

	data_all.append(data)

	##--- Anual
	
	meses = ['2020-01','2020-02','2020-03','2020-04','2020-05','2020-06','2020-07','2020-08','2020-09','2020-10','2020-11','2020-12']
	metas = [61,68,74,80,86,83,84,93,97,93,90,92]
	meta_anual = 1000

	titles.append('Ventas del 2020')

	data = []

	for idx, mes in enumerate(meses):
		fecha_ini = '{}-01'.format(mes)
		fecha_fin = '{}-31'.format(mes)

		ventas = Seguimiento.query.filter(Seguimiento.fecha_ganado >= fecha_ini, Seguimiento.fecha_ganado <= fecha_fin).count()
		data.append({'mes':mes, 'meta':metas[idx], 'ventas':ventas, 'cumpl': int(round(100 * ventas/metas[idx],0)), 'cumpl_anual': int(round(100 * ventas/meta_anual,0)) })

	data_all.append(data)

	meta_total = sum(metas)
	venta_total = sum([ item['ventas'] for item in data])

	totals.append({'meta_total':meta_total, 'venta_total':venta_total, 'cumpl':int(round(100 * venta_total/meta_total,0)), 'cumpl_anual':int(round(100 * venta_total/meta_anual,0))})	

	return render_template('home.html', data_all=data_all, totals=totals, titles=titles) 

#---------------------------------------------------------------------------------------------------------------------------------
# Show Deal
#---------------------------------------------------------------------------------------------------------------------------------
@main.route("/deal/show/<cpn>", methods=["GET"])
def deal_show(cpn):

	deal = Seguimiento.query.get(cpn)

	session['LAST_URL'] = url_for('main.deal_show', cpn=cpn)
	
	return render_template('show_deal.html', deal=deal)

#---------------------------------------------------------------------------------------------------------------------------------
# List Filtros
#---------------------------------------------------------------------------------------------------------------------------------
@main.route("/filtros/list", methods=["GET"])
def filtros_list():

	comerciales = [ deal.comercial for deal in db.session.query(Seguimiento.comercial).distinct() if deal.comercial != '' ]
	comerciales.sort()

	planes_bsale = [ deal.plan_bsale for deal in db.session.query(Seguimiento.plan_bsale).distinct() if deal.plan_bsale != '']
	planes_bsale.sort()

	categorias = [ deal.categoria for deal in db.session.query(Seguimiento.categoria).distinct() if deal.categoria != '' ]
	categorias.sort()

	estados = [ deal.estado for deal in db.session.query(Seguimiento.estado).distinct() if deal.estado != '' ]
	estados.sort()

	producciones = [ deal.produccion for deal in db.session.query(Seguimiento.produccion).distinct() if deal.produccion != '' ]
	producciones.sort()

	ejecutivos = [ deal.ejecutivo_pem for deal in db.session.query(Seguimiento.ejecutivo_pem).distinct() if (deal.ejecutivo_pem != None) and (deal.ejecutivo_pem !='') ]
	ejecutivos.sort()

	session['LAST_URL'] = url_for('main.filtros_list')
	
	return render_template('list_filtros.html',
							comerciales=comerciales,
							planes_bsale=planes_bsale,
							categorias=categorias,
							estados=estados,
							producciones=producciones,
							ejecutivos=ejecutivos)

#---------------------------------------------------------------------------------------------------------------------------------
# List Estados
#---------------------------------------------------------------------------------------------------------------------------------
@main.route("/estado/list", methods=["GET"])
def estado_list():

	items = [ seg.estado for seg in db.session.query(Seguimiento.estado).distinct() ]
	items.sort()

	session['LAST_URL'] = url_for('main.estado_list')
	
	return render_template('list_estado.html', items=items)

#---------------------------------------------------------------------------------------------------------------------------------
# List Ejecutivo
#---------------------------------------------------------------------------------------------------------------------------------
@main.route("/ejecutivo_pem/list", methods=["GET"])
def ejecutivo_pem_list():

	items = [seg.ejecutivo_pem for seg in db.session.query(Seguimiento.ejecutivo_pem).distinct() if (seg.ejecutivo_pem != None) and (seg.ejecutivo_pem !='') ]
	items.sort()

	session['LAST_URL'] = url_for('main.ejecutivo_pem_list')
	
	return render_template('list_ejecutivo_pem.html', items=items)


#---------------------------------------------------------------------------------------------------------------------------------
# Deal - List
#---------------------------------------------------------------------------------------------------------------------------------
@main.route("/deal/list", methods=["GET"])
def deal_list():

	if 'DEAL_FILTERS' not in session:
		session['DEAL_FILTERS'] = []	
	
	query = db.session.query(Seguimiento)
	query = apply_filters(query, session['DEAL_FILTERS'])

	items = query.all()

	session['LAST_URL'] = url_for('main.deal_list')
	
	return render_template('list_deal.html', items=items, deal_filters=session['DEAL_FILTERS'])

#---------------------------------------------------------------------------------------------------------------------------------
# Deal - Add Filter
#---------------------------------------------------------------------------------------------------------------------------------
@main.route("/deal/add_filter/<field>/<value>", methods=["GET"])
def deal_add_filter(field, value):
	
	if 'DEAL_FILTERS' not in session:
		deal_filters = []
	else:
		deal_filters = session['DEAL_FILTERS']

	if field not in [ f['field'] for f in deal_filters ]:
		deal_filters.append({'field': field, 'op': '==', 'value': value})

	session['DEAL_FILTERS'] = deal_filters

	return redirect(url_for('main.deal_list'))

#---------------------------------------------------------------------------------------------------------------------------------
# Deal - Remove Filter
#---------------------------------------------------------------------------------------------------------------------------------
@main.route("/deal/remove_filter/<field>/<value>", methods=["GET"])
def deal_remove_filter(field, value):
	
	if 'DEAL_FILTERS' not in session:
		deal_filters = []
	else:
		deal_filters = session['DEAL_FILTERS']

	item = {'field': field, 'op': '==', 'value': value}
	if item in deal_filters:
		deal_filters.remove(item)

	session['DEAL_FILTERS'] = deal_filters

	return redirect(url_for('main.deal_list'))


#---------------------------------------------------------------------------------------------------------------------------------
# Deal por Field
#---------------------------------------------------------------------------------------------------------------------------------
@main.route("/deal/list/<field>/<value>", methods=["GET"])
def deal_list_field_value(field, value):

	if 'DEAL_FILTERS' not in session:
		deal_filters = [{'field': field, 'op': '==', 'value': value}]
	else:
		deal_filters = session['DEAL_FILTERS']
		for item in deal_filters:
			deal_filters.remove(item)
		deal_filters.append({'field': field, 'op': '==', 'value': value})

	session['DEAL_FILTERS'] = deal_filters

	session['LAST_URL'] = url_for('main.deal_list_field_value', field=field, value=value)
	
	return redirect(url_for('main.deal_list'))


#---------------------------------------------------------------------------------------------------------------------------------
# Edit Seguimiento
#---------------------------------------------------------------------------------------------------------------------------------
@main.route("/deal/edit/<cpn>", methods=['GET', 'POST'])
def deal_edit(cpn):

	seguimiento = Seguimiento.query.get(cpn)
	form = SeguimientoForm()

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
		seguimiento.hizo_upselling = 'SI' if form.hizo_upselling.data else 'NO'
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
	form.hizo_upselling.data = True if seguimiento.hizo_upselling == 'SI' else False
	form.url_bsale.data = seguimiento.url_bsale
	form.comentario.data = seguimiento.comentario

	return render_template("edit_deal.html", form=form)


#---------------------------------------------------------------------------------------------------------------------------------
# Load Deals
#---------------------------------------------------------------------------------------------------------------------------------
@main.route("/deal/load", methods=['GET', 'POST'])
def deal_load():

	form = FileForm()
        
	if form.validate_on_submit():

		df = pd.read_sql_table('seguimiento', con=db.engine, columns=['cpn'])

		excel_file = form.filename.data
		local_excel_file = os.path.join(config['DATA_DIR'], config['DEALS_FILE'])
		excel_file.save(local_excel_file)

		df_new = pd.read_excel(excel_file, 
								usecols = ["Negocio - RUT/RUC/NIT",
											"Negocio - Título", 
											"Negocio - Propietario", 
											"Negocio - Servicio Contratado",
											"Negocio - Rubro/Actividad Económica",
											"Negocio - Fecha de ganado"],
								dtype = {"Negocio - RUT/RUC/NIT":str, "Negocio - Fecha de ganado":str})

		df_new.rename( columns = { "Negocio - RUT/RUC/NIT":"ruc",
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
		df_new.loc[:,'plan_bsale'] = df_new.loc[:,'plan_bsale'].apply(lambda x: x.replace('Plan ', ''))

		df_merge = pd.merge(df, df_new, how='outer', indicator=True)

		df_merge = df_merge[ df_merge['_merge']=='right_only']

		df_merge.drop(columns=['_merge'], inplace=True)

		df_merge.drop_duplicates(subset ='cpn', keep='first', inplace=True) 

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

		#print(df_merge)

		return redirect(url_for('main.deal_list'))

	return render_template("edit_excel_file.html", form=form)

