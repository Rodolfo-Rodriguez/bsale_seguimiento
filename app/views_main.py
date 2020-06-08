import os
import copy
from flask import render_template, redirect, Blueprint, session, url_for
from sqlalchemy_filters import apply_filters
from flask_login import login_required

import randomcolor
from datetime import datetime as dt, timedelta

import pandas as pd

main = Blueprint('main', __name__)

from . import db, config
from .models import Deal

#---------------------------------------------------------------------------------------------------------------------------------
# Home
#---------------------------------------------------------------------------------------------------------------------------------
@main.route("/", methods=["GET"])
@login_required
def home():

	# Clear session
	#if 'DEAL_FILTERS' in session: del session['DEAL_FILTERS']

	return redirect(url_for('stats.stats_ventas_meta',mes='today'))

#---------------------------------------------------------------------------------------------------------------------------------
# List Filtros
#---------------------------------------------------------------------------------------------------------------------------------
@main.route("/filtros/list", methods=["GET"])
@login_required
def filtros_list():

	comerciales = [ deal.comercial for deal in db.session.query(Deal.comercial).distinct() ]
	comerciales.sort()
	if '' in comerciales:
		comerciales.remove('')
		comerciales.append('NA')

	planes_bsale = [ deal.plan_bsale for deal in db.session.query(Deal.plan_bsale).distinct() ]
	planes_bsale.sort()
	if '' in planes_bsale:
		planes_bsale.remove('')
		planes_bsale.append('NA')

	categorias = [ deal.categoria for deal in db.session.query(Deal.categoria).distinct() ]
	categorias.sort()
	if '' in categorias: 
		categorias.remove('')
		categorias.append('NA')

	etapas = [ deal.etapa for deal in db.session.query(Deal.etapa).distinct() ]
	etapas.sort()
	if '' in etapas:
		etapas.remove('')
		etapas.append('NA')

	estados = [ deal.estado for deal in db.session.query(Deal.estado).distinct() ]
	estados.sort()
	if '' in estados:
		estados.remove('')
		estados.append('NA')

	ejecutivos = [ deal.ejecutivo_pem for deal in db.session.query(Deal.ejecutivo_pem).distinct() if deal.ejecutivo_pem != None ]
	ejecutivos.sort()
	if '' in ejecutivos:
		ejecutivos.remove('')
		ejecutivos.append('NA')

	session['LAST_URL'] = url_for('main.filtros_list')
	
	return render_template('list_filtros.html',
							comerciales=comerciales,
							planes_bsale=planes_bsale,
							categorias=categorias,
							etapas=etapas,
							estados=estados,
							ejecutivos=ejecutivos)

#---------------------------------------------------------------------------------------------------------------------------------
# List Etapas
#---------------------------------------------------------------------------------------------------------------------------------
@main.route("/etapa/list", methods=["GET"])
@login_required
def etapa_list():

	items = [ deal.etapa for deal in db.session.query(Deal.etapa).distinct() ]
	items.sort()

	session['LAST_URL'] = url_for('main.etapa_list')
	
	return render_template('list_etapa.html', items=items)

#---------------------------------------------------------------------------------------------------------------------------------
# List Ejecutivo
#---------------------------------------------------------------------------------------------------------------------------------
@main.route("/ejecutivo_pem/list", methods=["GET"])
@login_required
def ejecutivo_pem_list():

	items = [ deal.ejecutivo_pem for deal in db.session.query(Deal.ejecutivo_pem).distinct() if (deal.ejecutivo_pem != None) and (deal.ejecutivo_pem !='') ]
	items.sort()

	session['LAST_URL'] = url_for('main.ejecutivo_pem_list')
	
	return render_template('list_ejecutivo_pem.html', items=items)

