import os
from flask import render_template, redirect, Blueprint, session, url_for
from flask_login import login_required

import randomcolor
from datetime import datetime as dt, timedelta

stats = Blueprint('stats', __name__)

from . import db
from .models import Deal

#---------------------------------------------------------------------------------------------------------------------------------
# Venta vs Meta
#---------------------------------------------------------------------------------------------------------------------------------
@stats.route("/stats/ventas_vs_meta/<mes>", methods=["GET"])
@login_required
def stats_ventas_meta(mes):

	if mes == 'today':
		mes = dt.today().date().strftime("%Y-%m")

	date_mes = dt.strptime(mes, '%Y-%m').date()
	date_next = date_mes + timedelta(days=31)
	date_prev = date_mes - timedelta(days=1)
	mes_next = date_next.strftime("%Y-%m")
	mes_prev = date_prev.strftime("%Y-%m")

	fecha_ini = '{}-01'.format(mes)
	fecha_fin = '{}-31'.format(mes)

	data_all = []
	totals = []
	titles = []
	colors = []

	deals = Deal.query.filter(Deal.fecha_ganado >= fecha_ini, Deal.fecha_ganado <= fecha_fin)
	venta_total = deals.count()


	meta_mes = {'2020-01':61,
				'2020-02':68,
				'2020-03':74,
				'2020-04':80,
				'2020-05':86,
				'2020-06':83,
				'2020-07':84,
				'2020-08':93,
				'2020-09':97,
				'2020-10':93,
				'2020-11':90,
				'2020-12':92} 

	##--- Comerciales para el mes

	titles.append('Ventas por Comercial - Mes {}'.format(mes))

	comerciales = [ deal.comercial for deal in db.session.query(Deal.comercial).filter(Deal.fecha_ganado >= fecha_ini, Deal.fecha_ganado <= fecha_fin).distinct() ]

	data = []
	metas = {'2020-05':12, '2020-04':12, '2020-03':12, '2020-02':12, '2020-01':12}
	meta_total = meta_mes[mes] if mes in meta_mes else 50

	for comercial in comerciales:
		meta = metas[mes] if mes in metas else 12
		ventas = len([ deal for deal in deals if deal.comercial == comercial ])
		data.append({'comercial':comercial, 'meta':meta, 'ventas':ventas, 'cumpl': int(round(100 * ventas/meta,0)) })

	data.sort(key = lambda x: x['ventas'], reverse=True)

	cumplimiento = int(round(100 * venta_total/meta_total,0))
	restante = 100 - cumplimiento if cumplimiento < 100 else -1
	totals.append({'meta_total':meta_total, 
				'venta_total':venta_total, 
				'restante':restante, 
				'cumpl':cumplimiento})

	data_all.append(data)

	##--- Anual
	
	meses = ['2020-01','2020-02','2020-03','2020-04','2020-05','2020-06','2020-07','2020-08','2020-09','2020-10','2020-11','2020-12']

	titles.append('Ventas del 2020')

	data = []

	for mes_venta in meses:
		fecha_ini = '{}-01'.format(mes_venta)
		fecha_fin = '{}-31'.format(mes_venta)

		ventas = Deal.query.filter(Deal.fecha_ganado >= fecha_ini, Deal.fecha_ganado <= fecha_fin).count()
		data.append({'mes':mes_venta, 
					'meta':meta_mes[mes_venta], 
					'ventas':ventas, 
					'cumpl': int(round(100 * ventas/meta_mes[mes_venta],0)), 
					 })

	data_all.append(data)

	meta_total = sum([ item['meta'] for item in data])
	venta_total = sum([ item['ventas'] for item in data])

	totals.append({'meta_total':meta_total, 
				'venta_total':venta_total, 
				'cumpl':int(round(100 * venta_total/meta_total,0)), 
				'cumpl_anual':int(round(100 * venta_total/meta_total,0))})	

	return render_template('home.html', data_all=data_all, totals=totals, titles=titles, mes=mes, mes_next=mes_next, mes_prev=mes_prev) 


#---------------------------------------------------------------------------------------------------------------------------------
# Ventas Mes
#---------------------------------------------------------------------------------------------------------------------------------
@stats.route("/stats/ventas_mes/<mes>", methods=["GET"])
@login_required
def stats_ventas_mes(mes):	

	if mes=='today':
		mes = dt.today().date().strftime("%Y-%m")

	date_mes = dt.strptime(mes, '%Y-%m').date()
	date_next = date_mes + timedelta(days=31)
	date_prev = date_mes - timedelta(days=1)
	mes_next = date_next.strftime("%Y-%m")
	mes_prev = date_prev.strftime("%Y-%m")

	fecha_ini = '{}-01'.format(mes)
	fecha_fin = '{}-31'.format(mes)

	titles = []
	colors = []

	deals = Deal.query.filter(Deal.fecha_ganado >= fecha_ini, Deal.fecha_ganado <= fecha_fin)
	total = deals.count()

	##--- Comerciales

	titles.append('Ventas por Comercial')

	comerciales = [ deal.comercial for deal in db.session.query(Deal.comercial).filter(Deal.fecha_ganado >= fecha_ini, Deal.fecha_ganado <= fecha_fin).distinct() ]

	data_all = []

	data = []
	for comercial in comerciales:
		ventas = len([ deal for deal in deals if deal.comercial == comercial ])
		data.append({'comercial':comercial, 'ventas':ventas, 'ventas_prc': int(round(100*ventas/total,0)) })

	data.sort(key = lambda x: x['ventas'], reverse=True)

	data_all.append(data)

	##--- Plan

	titles.append('Ventas por plan BSale')

	planes_bsale = [ deal.plan_bsale for deal in db.session.query(Deal.plan_bsale).filter(Deal.fecha_ganado >= fecha_ini, Deal.fecha_ganado <= fecha_fin).distinct() ]

	data = []
	for plan in planes_bsale:
		ventas = len([ deal for deal in deals if deal.plan_bsale == plan ])
		data.append({'plan_bsale':plan, 'ventas':ventas, 'ventas_prc': int(round(100*ventas/total,0))})

	data.sort(key = lambda x: x['ventas'], reverse=True)

	data_all.append(data)


	##--- Categoria

	titles.append('Ventas por Categoria')

	categorias = [ deal.categoria for deal in db.session.query(Deal.categoria).filter(Deal.fecha_ganado >= fecha_ini, Deal.fecha_ganado <= fecha_fin).distinct() ]

	data = []
	for categoria in categorias:
		ventas = len([ deal for deal in deals if deal.categoria == categoria ])
		data.append({'categoria':categoria, 'ventas':ventas, 'ventas_prc': int(round(100*ventas/total,0))})

	data.sort(key = lambda x: x['ventas'], reverse=True)

	data_all.append(data)


	return render_template('stats_ventas.html', data_all=data_all, total=total, titles=titles, mes=mes, mes_next=mes_next, mes_prev=mes_prev) 
	

#---------------------------------------------------------------------------------------------------------------------------------
# Ventas vs PEP
#---------------------------------------------------------------------------------------------------------------------------------
@stats.route("/stats/ventas_vs_pep/<year>", methods=["GET"])
@login_required
def stats_ventas_pep(year):
	
	colors = ['#4E9AAB','#64B474','#E58C77', '#2B629F', '#59A9C6']

	meses = {
				"2020":['2020-01','2020-02','2020-03','2020-04','2020-05','2020-06'],
				"2019":['2019-01','2019-02','2019-03','2019-04','2019-05','2019-06','2019-07','2019-08','2019-09','2019-10','2019-11','2019-12'],
				"2018":['2018-01','2018-02','2018-03','2018-04','2018-05','2018-06','2018-07','2018-08','2018-09','2018-10','2018-11','2018-12']
			}

	data = []

	if year in meses:

		for mes in meses[year]:
			fecha_ini = '{}-01'.format(mes)
			fecha_fin = '{}-31'.format(mes)

			deals = Deal.query.filter(Deal.fecha_ganado>=fecha_ini, Deal.fecha_ganado<=fecha_fin)
				
			deals_vend = deals.count()
			deals_en_pem = len([deal for deal in deals if deal.etapa == 'PEM'])
			deals_en_prod = len([deal for deal in deals if deal.etapa == 'PRODUCCION'])
			deals_en_baja = len([deal for deal in deals if deal.etapa == 'BAJA'])

			deals = Deal.query.filter(Deal.fecha_pase_produccion>=fecha_ini, Deal.fecha_pase_produccion<=fecha_fin)
			deals_over_days = len([ deal for deal in deals if deal.dias_pem() != '' and deal.dias_pem() > 30 ])

			deals_pep = deals.count()
			if deals_pep > 0:
				tiempo_prom_pem = int(round( sum([ deal.dias_pem() for deal in deals if deal.dias_pem() != '' ]) / len([ deal.dias_pem() for deal in deals if deal.dias_pem() != '' ]) ,0))
			else:
				tiempo_prom_pem = 0

			data.append({'mes':mes, 
						'deals_vend':deals_vend, 
						'deals_en_pem':deals_en_pem, 
						'deals_en_prod':deals_en_prod, 
						'deals_en_baja':deals_en_baja, 
						'deals_pep':deals_pep,
						'deals_over_days':deals_over_days,
						'tiempo_prom_pem':tiempo_prom_pem })

		total_vend = sum([ d['deals_vend'] for d in data ])

		totales = { 
					'deals_vend':sum([ d['deals_vend'] for d in data ]), 
					'deals_en_pem':sum([ d['deals_en_pem'] for d in data ]), 
					'deals_en_prod':sum([ d['deals_en_prod'] for d in data ]), 
					'deals_en_baja':sum([ d['deals_en_baja'] for d in data ]), 
					'deals_pep':sum([ d['deals_pep'] for d in data ]),
					'deals_over_days':sum([ d['deals_over_days'] for d in data ]),
					'deals_en_pem_prc': int(round(100 * sum([ d['deals_en_pem'] for d in data ])/total_vend,0)), 
					'deals_en_prod_prc': int(round(100 * sum([ d['deals_en_prod'] for d in data ])/total_vend,0)), 
					'deals_en_baja_prc': int(round(100 * sum([ d['deals_en_baja'] for d in data ])/total_vend,0)), 
				}


		fecha_ini = '{}-01-01'.format(year)
		fecha_fin = '{}-12-31'.format(year)

		deals = Deal.query.filter(Deal.fecha_pase_produccion>=fecha_ini, Deal.fecha_pase_produccion<=fecha_fin)

		data_dias = [ {'fecha_pep':deal.fecha_pase_produccion, 'dias':deal.dias_pem()} for deal in deals if deal.dias_pem() != '']
		data_dias.sort(key= lambda x: x['fecha_pep'])

	else:
		totales = []
		title = 'No hay datos para {}'.format(year)
	
	return render_template('stats_ventas_pep.html', data=data, totales=totales, colors=colors, year=year, data_dias=data_dias)	

#---------------------------------------------------------------------------------------------------------------------------------
# PEM por Ejecutivo
#---------------------------------------------------------------------------------------------------------------------------------
@stats.route("/stats/pem/<ejecutivo>/<range_id>", methods=["GET"])
@login_required
def stats_pem(ejecutivo, range_id):

	##-- Stats
	ejecutivos = [ deal.ejecutivo_pem for deal in db.session.query(Deal.ejecutivo_pem).filter(Deal.etapa=='PEM').distinct() if deal.ejecutivo_pem != '']

	day_ranges = [(0,15),(15,30),(30,60),(60,5000)]
	range_names = ['0-15d', '15-30d', '30-60d', '>60d', 'Total']
	colors = ['#64B474', '#4E9AAB', '#F5C150', '#E58C77']

	data = []
	totales = [0,0,0,0]

	for eje in ejecutivos:
		deals_eje = Deal.query.filter(Deal.etapa=='PEM', Deal.ejecutivo_pem==eje)
		deals_range = []
		for idx, dr in enumerate(day_ranges):
			deals = len([deal for deal in deals_eje if (deal.dias_pem() != '' and deal.dias_pem() > dr[0] and deal.dias_pem() <= dr[1])])
			deals_range.append(deals)
			totales[idx] = totales[idx] + deals 

		deals_range.append(deals_eje.count())

		data.append({'ejecutivo':eje, 'deals_range':deals_range})

	deals_tot = Deal.query.filter(Deal.etapa=='PEM').count()
	totales.append(deals_tot)

	totales_prc = [ int(round(100 * tot / totales[4],0)) for tot in totales[0:4] ]
	
	#-- List

	if ejecutivo == 'todos':
		show_list = False
		items = []
		title = ''
	else:
		show_list = True

		deals = Deal.query.filter(Deal.ejecutivo_pem==ejecutivo, Deal.etapa=='PEM').all()

		if int(range_id) < 4:
			items = [ item for item in deals if (item.dias_pem()!='' and item.dias_pem() > day_ranges[int(range_id)][0] and item.dias_pem() <= day_ranges[int(range_id)][1]) ]
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
@login_required
def stats_churn():
	
	colors = ['#64B474', '#E58C77', '#F5C150', '#4E9AAB']

	meses = ['2020-01','2020-02','2020-03','2020-04','2020-05','2020-06']

	data = []

	for mes in meses:
		fecha_ini = '{}-01'.format(mes)
		fecha_fin = '{}-31'.format(mes)

		deals_vend_d1 = Deal.query.filter(Deal.fecha_ganado<=fecha_ini)
		deals_vend_m = Deal.query.filter(Deal.fecha_ganado>=fecha_ini, Deal.fecha_ganado<=fecha_fin)

		deals_baja_d1 = Deal.query.filter(Deal.fecha_baja<=fecha_ini, Deal.fecha_baja != '')
		deals_baja_m = Deal.query.filter(Deal.fecha_baja>=fecha_ini, Deal.fecha_baja<=fecha_fin)
			
		tot_clientes_d1 = deals_vend_d1.count()
		tot_clientes_m = deals_vend_m.count()
		tot_clientes = tot_clientes_d1 + tot_clientes_m
		tot_bajas_d1 = deals_baja_d1.count()
		tot_bajas_m = deals_baja_m.count()
		tot_bajas = tot_bajas_d1 + tot_bajas_m
		neto = tot_clientes_m - tot_bajas_m

		churn = round(100 * tot_bajas_m / tot_clientes_d1, 1)

		data.append({'mes':mes, 
					'clientes_d1':tot_clientes_d1, 
					'clientes_m':tot_clientes_m ,
					'clientes':tot_clientes, 
					'bajas_d1':tot_bajas_d1, 
					'bajas_mes':tot_bajas_m, 
					'bajas':tot_bajas,
					'neto':neto,
					'churn':churn })
	
	return render_template('stats_churn.html', data=data, colors=colors)	

