import os
from flask import render_template, redirect, Blueprint, session, url_for

import randomcolor
from datetime import datetime as dt

stats = Blueprint('stats', __name__)

from . import db
from .models import Seguimiento

#---------------------------------------------------------------------------------------------------------------------------------
# Ventas Mes
#---------------------------------------------------------------------------------------------------------------------------------
@stats.route("/stats/ventas_mes", methods=["GET"])
def stats_ventas_mes():	

	mes = dt.today().date().strftime("%Y-%m")

	fecha_ini = '{}-01'.format(mes)
	fecha_fin = '{}-31'.format(mes)

	titles = []
	colors = []

	deals = Seguimiento.query.filter(Seguimiento.fecha_ganado >= fecha_ini, Seguimiento.fecha_ganado <= fecha_fin)
	total = deals.count()

	##--- Comerciales

	titles.append('Ventas mes {} por Comercial'.format(mes))

	comerciales = [ deal.comercial for deal in db.session.query(Seguimiento.comercial).filter(Seguimiento.fecha_ganado >= fecha_ini, Seguimiento.fecha_ganado <= fecha_fin).distinct() ]

	data_all = []

	data = []
	for comercial in comerciales:
		ventas = len([ deal for deal in deals if deal.comercial == comercial ])
		data.append({'comercial':comercial, 'ventas':ventas, 'ventas_prc': int(round(100*ventas/total,0)) })

	data.sort(key = lambda x: x['ventas'], reverse=True)

	data_all.append(data)

	##--- Plan

	titles.append('Ventas mes {} por plan BSale'.format(mes))

	planes_bsale = [ deal.plan_bsale for deal in db.session.query(Seguimiento.plan_bsale).filter(Seguimiento.fecha_ganado >= fecha_ini, Seguimiento.fecha_ganado <= fecha_fin).distinct() ]

	data = []
	for plan in planes_bsale:
		ventas = len([ deal for deal in deals if deal.plan_bsale == plan ])
		data.append({'plan_bsale':plan, 'ventas':ventas, 'ventas_prc': int(round(100*ventas/total,0))})

	data.sort(key = lambda x: x['ventas'], reverse=True)

	data_all.append(data)


	##--- Categoria

	titles.append('Ventas mes {} por Categoria'.format(mes))

	categorias = [ deal.categoria for deal in db.session.query(Seguimiento.categoria).filter(Seguimiento.fecha_ganado >= fecha_ini, Seguimiento.fecha_ganado <= fecha_fin).distinct() ]

	data = []
	for categoria in categorias:
		ventas = len([ deal for deal in deals if deal.categoria == categoria ])
		data.append({'categoria':categoria, 'ventas':ventas, 'ventas_prc': int(round(100*ventas/total,0))})

	data.sort(key = lambda x: x['ventas'], reverse=True)

	data_all.append(data)


	return render_template('stats_ventas.html', data_all=data_all, total=total, titles=titles) 
	

#---------------------------------------------------------------------------------------------------------------------------------
# Ventas vs PEP
#---------------------------------------------------------------------------------------------------------------------------------
@stats.route("/stats/ventas_vs_pep/<year>", methods=["GET"])
def stats_ventas_pep(year):
	
	colors = ['#4E9AAB','#64B474','#E58C77', '#2B629F', '#59A9C6']

	meses = {
				"2020":['2020-01','2020-02','2020-03','2020-04','2020-05'],
				"2019":['2019-01','2019-02','2019-03','2019-04','2019-05','2019-06','2019-07','2019-08','2019-09','2019-10','2019-11','2019-12'],
				"2018":['2018-05','2018-06','2018-07','2018-08','2018-09','2018-10','2018-11','2018-12']
			}

	data = []

	if year in meses:

		for mes in meses[year]:
			fecha_ini = '{}-01'.format(mes)
			fecha_fin = '{}-31'.format(mes)

			deals = Seguimiento.query.filter(Seguimiento.fecha_ganado>=fecha_ini, Seguimiento.fecha_ganado<=fecha_fin)
				
			deals_vend = deals.count()
			deals_en_pem = len([deal for deal in deals if deal.estado == 'PEM'])
			deals_en_prod = len([deal for deal in deals if deal.estado == 'PRODUCCION'])
			deals_en_baja = len([deal for deal in deals if deal.estado == 'BAJA'])

			deals_pep = Seguimiento.query.filter(Seguimiento.fecha_pase_produccion>=fecha_ini, Seguimiento.fecha_pase_produccion<=fecha_fin).count()

			data.append({'mes':mes, 
						'deals_vend':deals_vend, 
						'deals_en_pem':deals_en_pem, 
						'deals_en_prod':deals_en_prod, 
						'deals_en_baja':deals_en_baja, 
						'deals_pep':deals_pep })

		total_vend = sum([ d['deals_vend'] for d in data ])

		totales = { 
					'deals_vend':sum([ d['deals_vend'] for d in data ]), 
					'deals_en_pem':sum([ d['deals_en_pem'] for d in data ]), 
					'deals_en_prod':sum([ d['deals_en_prod'] for d in data ]), 
					'deals_en_baja':sum([ d['deals_en_baja'] for d in data ]), 
					'deals_pep':sum([ d['deals_pep'] for d in data ]),
					'deals_en_pem_prc': int(round(100 * sum([ d['deals_en_pem'] for d in data ])/total_vend,0)), 
					'deals_en_prod_prc': int(round(100 * sum([ d['deals_en_prod'] for d in data ])/total_vend,0)), 
					'deals_en_baja_prc': int(round(100 * sum([ d['deals_en_baja'] for d in data ])/total_vend,0)), 
				}

	else:
		totales = []
		title = 'No hay datos para {}'.format(year)
	
	return render_template('stats_ventas_pep.html', data=data, totales=totales, colors=colors, year=year)	

#---------------------------------------------------------------------------------------------------------------------------------
# PEM por Ejecutivo
#---------------------------------------------------------------------------------------------------------------------------------
@stats.route("/stats/pem/<ejecutivo>/<range_id>", methods=["GET"])
def stats_pem(ejecutivo, range_id):

	##-- Stats
	ejecutivos = [ deal.ejecutivo_pem for deal in db.session.query(Seguimiento.ejecutivo_pem).filter(Seguimiento.estado=='PEM').distinct() ]

	day_ranges = [(0,15),(15,30),(30,60),(60,5000)]
	range_names = ['0-15d', '15-30d', '30-60d', '>60d', 'Total']
	colors = ['#64B474', '#4E9AAB', '#F5C150', '#E58C77']

	data = []
	totales = [0,0,0,0]

	for eje in ejecutivos:
		deals_eje = Seguimiento.query.filter(Seguimiento.estado=='PEM', Seguimiento.ejecutivo_pem==eje)
		deals_range = []
		for idx, dr in enumerate(day_ranges):
			deals = len([deal for deal in deals_eje if (deal.dias_pem() > dr[0] and deal.dias_pem() <= dr[1])])
			deals_range.append(deals)
			totales[idx] = totales[idx] + deals 

		deals_range.append(deals_eje.count())

		data.append({'ejecutivo':eje, 'deals_range':deals_range})

	deals_tot = Seguimiento.query.filter(Seguimiento.estado=='PEM').count()
	totales.append(deals_tot)

	totales_prc = [ int(round(100 * tot / totales[4],0)) for tot in totales[0:4] ]
	
	#-- List

	if ejecutivo == 'todos':
		show_list = False
		items = []
		title = ''
	else:
		show_list = True

		deals = Seguimiento.query.filter(Seguimiento.ejecutivo_pem==ejecutivo, Seguimiento.estado=='PEM').all()

		if int(range_id) < 4:
			items = [ item for item in deals if (item.dias_pem() > day_ranges[int(range_id)][0] and item.dias_pem() <= day_ranges[int(range_id)][1]) ]
			title = '{} [ {} ]'.format(ejecutivo,range_names[int(range_id)])
		else:
			items = deals
			title = '{} [ Todos ]'.format(ejecutivo)

	return render_template('stats_pem.html', 
							data=data, 
							totales=totales,
							totales_prc=totales_prc,
							range_names=range_names,
							colors=colors,
							show_list=show_list, 
							items=items,
							title=title)	

#---------------------------------------------------------------------------------------------------------------------------------
# Churn
#---------------------------------------------------------------------------------------------------------------------------------
@stats.route("/stats/churn", methods=["GET"])
def stats_churn():
	
	colors = ['#4E9AAB','#64B474','#E58C77', '#2B629F']

	meses = ['2019-10','2019-11','2019-12','2020-01','2020-02','2020-03','2020-04','2020-05']

	data = []

	for mes in meses:
		fecha_ini = '{}-01'.format(mes)
		fecha_fin = '{}-31'.format(mes)

		deals = Seguimiento.query.filter(Seguimiento.fecha_inicio_pem>=fecha_ini, Seguimiento.fecha_inicio_pem<=fecha_fin)
			
		deals_vend = deals.count()
		deals_en_baja = len([deal for deal in deals if deal.estado == 'BAJA'])

		data.append({'mes':mes, 'deals_vend':deals_vend, 'deals_en_baja':deals_en_baja })

	totales = [ sum([ d['deals_vend'] for d in data ]), 
				sum([ d['deals_en_baja'] for d in data ]) ]

	
	return render_template('stats_churn.html', data=data, totales=totales, colors=colors)	

