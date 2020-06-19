import os
import copy
from flask import render_template, redirect, Blueprint, session, url_for, request,  send_from_directory
from sqlalchemy_filters import apply_filters
from flask_login import login_required

from datetime import datetime as dt
from openpyxl import Workbook

import pandas as pd

deal = Blueprint('deal', __name__)

from . import db, config
from .models import Deal, Checkpoint
from .forms import DealForm, FileForm, ConfirmForm, DealVentaForm, DealPEMForm, DealBajaForm, DealEtapaForm, FechaForm

from .filter_manager import filter_manager as fm
from .io_manager import io_manager

#---------------------------------------------------------------------------------------------------------------------------------
# Show Deal
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/show/<id>", methods=["GET"])
@login_required
def deal_show(id):

	deal = Deal.query.get(id)

	if deal.ruc != '':
		planes = [ {'id':d.negocio_id, 'plan':d.plan_bsale} for d in Deal.query.filter(Deal.ruc==deal.ruc).all() if deal.ruc != '']
	else:
		planes = [ {'id':deal.negocio_id, 'plan':deal.plan_bsale} ]

	session['LAST_URL'] = url_for('deal.deal_show', id=id)
	
	return render_template('show_deal.html', deal=deal, planes=planes)

#---------------------------------------------------------------------------------------------------------------------------------
# Deal - List
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/list", methods=["GET"])
@login_required
def deal_list():
	
	if 'DEAL_FILTERS' not in session:
		session['DEAL_FILTERS'] = {}	

	query_filter = fm.create_query_filter(session)
	query = db.session.query(Deal)
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

	session['DEAL_FILTERS'] = fm.add_filter_to_session(session, field, op, value)

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

	session['DEAL_FILTERS'] = fm.remove_filter_from_session(session, field, op, value)

	return redirect(session['LAST_URL'])

#---------------------------------------------------------------------------------------------------------------------------------
# Deal - Clear Filters
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/clear_filters", methods=["GET"])
@login_required
def deal_clear_filters():

	if 'DEAL_FILTERS' in session:
		del session['DEAL_FILTERS']

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

	value = '' if value == 'NA' else value

	deal_filters.append({'field': field, 'op': '==', 'value': value})

	session['DEAL_FILTERS'] = deal_filters

	session['LAST_URL'] = url_for('deal.deal_list_field_value', field=field, value=value)
	
	return redirect(url_for('deal.deal_list'))

#---------------------------------------------------------------------------------------------------------------------------------
# Deal - List Ventas en un Mes
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/list/mes/<mes>", methods=["GET"])
@login_required
def deal_list_mes(mes):

	fecha_ini = '{}-01'.format(mes)
	fecha_fin = '{}-31'.format(mes)
	
	session['DEAL_FILTERS'] = fm.add_date_range_filter_to_session(session, 'fecha_ganado', fecha_ini, fecha_fin)

	return redirect(url_for('deal.deal_list'))

#---------------------------------------------------------------------------------------------------------------------------------
# Deal - List Bajas en un Mes
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/list/bajas/mes/<mes>", methods=["GET"])
@login_required
def deal_list_bajas_mes(mes):

	fecha_ini = '{}-01'.format(mes)
	fecha_fin = '{}-31'.format(mes)
	
	session['DEAL_FILTERS'] = fm.add_date_range_filter_to_session(session, 'fecha_baja', fecha_ini, fecha_fin)

	return redirect(url_for('deal.deal_list'))

#---------------------------------------------------------------------------------------------------------------------------------
# Deal - List para un Mes y Comercial
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/list/mes/comercial/<mes>/<comercial>", methods=["GET"])
@login_required
def deal_list_mes_comercial(mes, comercial):

	fecha_ini = '{}-01'.format(mes)
	fecha_fin = '{}-31'.format(mes)
	
	session['DEAL_FILTERS'] = fm.add_date_range_filter_to_session(session, 'fecha_ganado', fecha_ini, fecha_fin)
	session['DEAL_FILTERS'] = fm.add_filter_to_session(session,'comercial','==',comercial)

	return redirect(url_for('deal.deal_list'))

#---------------------------------------------------------------------------------------------------------------------------------
# Deal - List puesta en produccion en mes
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/list/mes/produccion/<mes>", methods=["GET"])
@login_required
def deal_list_mes_produccion(mes):

	fecha_ini = '{}-01'.format(mes)
	fecha_fin = '{}-31'.format(mes)
	
	session['DEAL_FILTERS'] = fm.add_date_range_filter_to_session(session, 'fecha_pase_produccion', fecha_ini, fecha_fin)

	return redirect(url_for('deal.deal_list'))

#---------------------------------------------------------------------------------------------------------------------------------
# Edit Deal
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/edit/<id>", methods=['GET', 'POST'])
@login_required
def deal_edit(id):

	deal = Deal.query.get(id)
	form = DealForm()
	form.title = deal.razon_social

	form.comercial.choices = [('','NO')] + sorted([ (deal.comercial, deal.comercial) for deal in db.session.query(Deal.comercial).distinct() if deal.comercial != '' ])
	form.plan_bsale.choices = [('','NO')] + sorted([ (deal.plan_bsale, deal.plan_bsale) for deal in db.session.query(Deal.plan_bsale).distinct() if deal.plan_bsale != ''])
	form.etapa.choices = sorted([ (deal.etapa, deal.etapa) for deal in db.session.query(Deal.etapa).distinct() ])
	form.estado.choices = [('','NO')] + sorted([ (deal.estado, deal.estado) for deal in db.session.query(Deal.estado).distinct() if deal.estado != ''])
	form.ejecutivo_pem.choices = [('','NO')] + sorted([ (deal.ejecutivo_pem, deal.ejecutivo_pem) for deal in db.session.query(Deal.ejecutivo_pem).distinct() if deal.ejecutivo_pem != ''])
         
	if form.validate_on_submit():
        
		deal.razon_social = form.razon_social.data
		deal.comercial = form.comercial.data
		deal.plan_bsale = form.plan_bsale.data
		deal.categoria = form.categoria.data
		deal.etapa = form.etapa.data
		deal.estado = form.estado.data
		deal.ejecutivo_pem = form.ejecutivo_pem.data		
		deal.fecha_ganado = form.fecha_ganado.data
		deal.fecha_inicio_pem = form.fecha_inicio_pem.data
		deal.fecha_contacto_inicial = form.fecha_contacto_inicial.data		
		deal.set_fecha_pase_produccion(form.fecha_pase_produccion.data)
		deal.fecha_baja = form.fecha_baja.data
		deal.url_bsale = form.url_bsale.data		
		deal.razon_baja = form.razon_baja.data	

		db.session.commit()

		return redirect(session['LAST_URL'])

	form.razon_social.data = deal.razon_social
	form.comercial.data = deal.comercial
	form.plan_bsale.data = deal.plan_bsale
	form.categoria.data = deal.categoria
	form.etapa.data = deal.etapa
	form.estado.data = deal.estado
	form.ejecutivo_pem.data = deal.ejecutivo_pem 
	form.fecha_ganado.data = deal.fecha_ganado
	form.fecha_inicio_pem.data = deal.fecha_inicio_pem
	form.fecha_contacto_inicial.data = deal.fecha_contacto_inicial
	form.fecha_pase_produccion.data = deal.fecha_pase_produccion
	form.fecha_baja.data = deal.fecha_baja
	form.url_bsale.data = deal.url_bsale
	form.comentario.data = deal.comentario
	form.razon_baja.data = deal.razon_baja

	return render_template("edit_deal.html", form=form)

#---------------------------------------------------------------------------------------------------------------------------------
# Edit Deal Etapa
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/edit_etapa/<id>", methods=['GET', 'POST'])
@login_required
def deal_edit_etapa(id):

	fecha_today = dt.today().strftime("%Y-%m-%d")

	deal = Deal.query.get(id)
	form = DealEtapaForm()
	form.title = deal.razon_social
         
	form.etapa.choices = [('','NO')] + sorted([ (deal.etapa, deal.etapa) for deal in db.session.query(Deal.etapa).distinct() if deal.etapa != ''])

	if form.validate_on_submit():
        
		deal.etapa = form.etapa.data

		if (form.etapa.data == 'PEM') and (deal.fecha_inicio_pem == ''):
			deal.fecha_inicio_pem = fecha_today
		elif (form.etapa.data == 'PRODUCCION') and (deal.fecha_pase_produccion == ''):
			deal.set_fecha_pase_produccion(fecha_today)
		elif (form.etapa.data == 'BAJA') and (deal.fecha_baja)=='':
			deal.fecha_baja = fecha_today

		db.session.commit()

		return redirect(session['LAST_URL'])

	form.etapa.data = deal.etapa

	return render_template("edit_deal_etapa.html", form=form)

#---------------------------------------------------------------------------------------------------------------------------------
# Edit Deal - Venta
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/edit_venta/<id>", methods=['GET', 'POST'])
@login_required
def deal_edit_venta(id):

	deal = Deal.query.get(id)
	form = DealVentaForm()
	form.title = deal.razon_social

	form.comercial.choices = [('','NO')] + sorted([ (deal.comercial, deal.comercial) for deal in db.session.query(Deal.comercial).distinct() if deal.comercial != '' ])
	form.plan_bsale.choices = [('','NO')] + sorted([ (deal.plan_bsale, deal.plan_bsale) for deal in db.session.query(Deal.plan_bsale).distinct() if deal.plan_bsale != ''])
	form.etapa.choices = sorted([ (deal.etapa, deal.etapa) for deal in db.session.query(Deal.etapa).distinct() ])
         
	if form.validate_on_submit():
        
		deal.cpn = form.cpn.data
		deal.ruc = form.ruc.data
		deal.razon_social = form.razon_social.data
		deal.comercial = form.comercial.data
		deal.plan_bsale = form.plan_bsale.data
		deal.categoria = form.categoria.data
		deal.fecha_ganado = form.fecha_ganado.data
		deal.etapa = form.etapa.data

		db.session.commit()

		return redirect(session['LAST_URL'])

	form.cpn.data = deal.cpn
	form.ruc.data = deal.ruc
	form.razon_social.data = deal.razon_social
	form.comercial.data = deal.comercial
	form.plan_bsale.data = deal.plan_bsale
	form.categoria.data = deal.categoria
	form.fecha_ganado.data = deal.fecha_ganado
	form.etapa.data = deal.etapa


	return render_template("edit_deal_venta.html", form=form)

#---------------------------------------------------------------------------------------------------------------------------------
# Edit Deal - PEM
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/edit_pem/<id>", methods=['GET', 'POST'])
@login_required
def deal_edit_pem(id):

	deal = Deal.query.get(id)
	form = DealPEMForm()
	form.title = deal.razon_social

	form.ejecutivo_pem.choices = [('','NO')] + sorted([ (deal.ejecutivo_pem, deal.ejecutivo_pem) for deal in db.session.query(Deal.ejecutivo_pem).distinct() if deal.ejecutivo_pem != ''])
         
	if form.validate_on_submit():
        
		deal.ejecutivo_pem = form.ejecutivo_pem.data		
		deal.fecha_inicio_pem = form.fecha_inicio_pem.data
		deal.fecha_contacto_inicial = form.fecha_contacto_inicial.data		
		deal.set_fecha_pase_produccion(form.fecha_pase_produccion.data)
		deal.url_bsale = form.url_bsale.data		
		deal.url_cliente = form.url_cliente.data		

		db.session.commit()

		return redirect(session['LAST_URL'])

	form.ejecutivo_pem.data = deal.ejecutivo_pem 
	form.fecha_inicio_pem.data = deal.fecha_inicio_pem
	form.fecha_contacto_inicial.data = deal.fecha_contacto_inicial
	form.fecha_pase_produccion.data = deal.fecha_pase_produccion
	form.url_bsale.data = deal.url_bsale
	form.url_cliente.data = deal.url_cliente

	return render_template("edit_deal_pem.html", form=form)


#---------------------------------------------------------------------------------------------------------------------------------
# Edit Deal Baja
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/edit_baja/<id>", methods=['GET', 'POST'])
@login_required
def deal_edit_baja(id):

	deal = Deal.query.get(id)
	form = DealBajaForm()
	form.title = deal.razon_social
         
	if form.validate_on_submit():
        
		deal.fecha_baja = form.fecha_baja.data
		deal.razon_baja = form.razon_baja.data	
		deal.comentario = form.comentario.data

		db.session.commit()

		return redirect(session['LAST_URL'])

	form.fecha_baja.data = deal.fecha_baja
	form.razon_baja.data = deal.razon_baja
	form.comentario.data = deal.comentario

	return render_template("edit_deal_baja.html", form=form)

#---------------------------------------------------------------------------------------------------------------------------------
# Deal - Delete
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/delete/<id>", methods=["GET","POST"])
@login_required
def deal_delete(id):

	deal = Deal.query.get(id)

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

	query_filter = fm.create_query_filter(session)
	query = db.session.query(Deal)
	query = apply_filters(query, query_filter)

	items = query.all()

	today = dt.today().strftime("%Y-%m-%d-%H%M%S")
	filename = 'deals-{}.xlsx'.format(today)
	filepath = 'export/{}'.format(filename)

	io_manager.deal_download(items, filepath)
	
	return send_from_directory('../export', filename, cache_timeout=0, as_attachment=True)

#---------------------------------------------------------------------------------------------------------------------------------
# Load Deals
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/load", methods=['GET', 'POST'])
@login_required
def deal_load():

	form = FileForm()
        
	if form.validate_on_submit():

		excel_file = form.filename.data
		local_excel_file = os.path.join(config['DATA_DIR'], config['DEALS_FILE'])
		excel_file.save(local_excel_file)

		io_manager.deal_load(excel_file, db)
						
		return redirect(url_for('main.home'))

	return render_template("edit_excel_file.html", form=form)

#---------------------------------------------------------------------------------------------------------------------------------
# Update Deals
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/update", methods=['GET', 'POST'])
@login_required
def deal_update():

	form = FileForm()
        
	if form.validate_on_submit():

		excel_file = form.filename.data
		local_excel_file = os.path.join(config['DATA_DIR'], config['UPDATE_DEALS_FILE'])
		excel_file.save(local_excel_file)

		return redirect(url_for('deal.deal_update_selected'))

	return render_template("edit_excel_file.html", form=form)

#---------------------------------------------------------------------------------------------------------------------------------
# Update Selected
#---------------------------------------------------------------------------------------------------------------------------------
@deal.route("/deal/update/selected", methods=['GET', 'POST'])
@login_required
def deal_update_selected():
        
	local_excel_file = os.path.join(config['DATA_DIR'], config['UPDATE_DEALS_FILE'])

	columns = io_manager.get_file_cols(local_excel_file)
	if 'ID' in columns:
		columns.remove('ID')
	if 'Dias en PEM' in columns:
		columns.remove('Dias en PEM')
	if 'Dias en Prod.' in columns:
		columns.remove('Dias en Prod.')
	
	if request.method == 'POST':

		import_columns = [ col for col in columns if request.form.get(col)=='y' ]	

		deals_updated = io_manager.deal_update(local_excel_file, db, import_columns)

		return render_template('list_deal_updated.html', items=deals_updated, columns=import_columns)

	return render_template('edit_fields_to_update.html', columns=columns)

