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
from .models import Seguimiento
from .forms import SeguimientoForm, FileForm, LoginForm

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

	comerciales = [ deal.comercial for deal in db.session.query(Seguimiento.comercial).distinct() ]
	comerciales.sort()
	if '' in comerciales:
		comerciales.remove('')
		comerciales.append('NA')

	planes_bsale = [ deal.plan_bsale for deal in db.session.query(Seguimiento.plan_bsale).distinct() ]
	planes_bsale.sort()
	if '' in planes_bsale:
		planes_bsale.remove('')
		planes_bsale.append('NA')

	categorias = [ deal.categoria for deal in db.session.query(Seguimiento.categoria).distinct() ]
	categorias.sort()
	if '' in categorias: 
		categorias.remove('')
		categorias.append('NA')

	estados = [ deal.estado for deal in db.session.query(Seguimiento.estado).distinct() ]
	estados.sort()
	if '' in estados:
		estados.remove('')
		estados.append('NA')

	producciones = [ deal.produccion for deal in db.session.query(Seguimiento.produccion).distinct() ]
	producciones.sort()
	if '' in producciones:
		producciones.remove('')
		producciones.append('NA')

	ejecutivos = [ deal.ejecutivo_pem for deal in db.session.query(Seguimiento.ejecutivo_pem).distinct() if deal.ejecutivo_pem != None ]
	ejecutivos.sort()
	if '' in ejecutivos:
		ejecutivos.remove('')
		ejecutivos.append('NA')

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
@login_required
def estado_list():

	items = [ seg.estado for seg in db.session.query(Seguimiento.estado).distinct() ]
	items.sort()

	session['LAST_URL'] = url_for('main.estado_list')
	
	return render_template('list_estado.html', items=items)

#---------------------------------------------------------------------------------------------------------------------------------
# List Ejecutivo
#---------------------------------------------------------------------------------------------------------------------------------
@main.route("/ejecutivo_pem/list", methods=["GET"])
@login_required
def ejecutivo_pem_list():

	items = [seg.ejecutivo_pem for seg in db.session.query(Seguimiento.ejecutivo_pem).distinct() if (seg.ejecutivo_pem != None) and (seg.ejecutivo_pem !='') ]
	items.sort()

	session['LAST_URL'] = url_for('main.ejecutivo_pem_list')
	
	return render_template('list_ejecutivo_pem.html', items=items)

