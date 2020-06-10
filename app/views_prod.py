from flask import render_template, redirect, Blueprint, session, url_for, request
from sqlalchemy_filters import apply_filters
from flask_login import login_required

from datetime import datetime as dt, timedelta

prod = Blueprint('prod', __name__)

from . import db, config
from .models import Deal, Checkpoint
from .forms import CheckpointForm

from .filter_manager import filter_manager as fm

#---------------------------------------------------------------------------------------------------------------------------------
# Show Deal en Prod
#---------------------------------------------------------------------------------------------------------------------------------
@prod.route("/deal/prod/show/<id>", methods=["GET"])
@login_required
def deal_prod_show(id):

	deal = Deal.query.get(id)

	session['LAST_URL'] = url_for('prod.deal_prod_show', id=id)
	
	return render_template('show_deal.html', deal=deal)

#---------------------------------------------------------------------------------------------------------------------------------
# Deal en Produccion - List
#---------------------------------------------------------------------------------------------------------------------------------
@prod.route("/deal/prod/list", methods=["GET"])
@login_required
def deal_prod_list():


	filter = request.args.get('filter')
	print(filter)

	if filter == 'default':

		fecha_ini = (dt.today() - timedelta(120)).strftime("%Y-%m-%d")
	
		session['DEAL_FILTERS'] = fm.add_filter_to_session(session,'etapa','==','PRODUCCION')
		session['DEAL_FILTERS'] = fm.add_filter_to_session(session,'fecha_pase_produccion','>=',fecha_ini)
	
	query_filter = fm.create_query_filter(session)
	query = db.session.query(Deal)
	query = apply_filters(query, query_filter)

	items = query.all()

	session['LAST_URL'] = url_for('prod.deal_prod_list')
	
	return render_template('list_deal_prod.html', items=items)

#---------------------------------------------------------------------------------------------------------------------------------
# Add Checkpoint
#---------------------------------------------------------------------------------------------------------------------------------
@prod.route("/deal/checkpoint/add/<id>", methods=['GET', 'POST'])
@login_required
def deal_checkpoint_add(id):

	deal = Deal.query.get(id)
	form = CheckpointForm()
	form.title = deal.razon_social
         
	if form.validate_on_submit():
        
		checkpoint = Checkpoint(nombre=form.nombre.data,
								fecha=form.fecha.data,
								tipo='',
								realizado=form.realizado.data,
								comentario=form.comentario.data,
								deal_id=id)

		db.session.add(checkpoint)
		db.session.commit()

		return redirect(session['LAST_URL'])

	return render_template("edit_checkpoint.html", form=form)

#---------------------------------------------------------------------------------------------------------------------------------
# Edit Checkpoint
#---------------------------------------------------------------------------------------------------------------------------------
@prod.route("/deal/checkpoint/edit/<id>", methods=['GET', 'POST'])
@login_required
def deal_checkpoint_edit(id):

	checkpoint = Checkpoint.query.get(id)
	form = CheckpointForm()
	form.title = '{}'.format(checkpoint.deal.razon_social)
         
	if form.validate_on_submit():

		deal = Deal.query.get(checkpoint.deal_id)
		al_dia, ultima_fecha = deal.al_dia()
        
		checkpoint.realizado = form.realizado.data
		checkpoint.comentario = form.comentario.data
		checkpoint.fecha_realizado = form.fecha_realizado.data
		checkpoint.estado = form.estado.data

		if checkpoint.fecha == ultima_fecha:
			deal.estado = checkpoint.estado

		db.session.commit()

		return redirect(session['LAST_URL'])

	form.realizado.data = checkpoint.realizado
	form.comentario.data = checkpoint.comentario
	form.fecha_realizado.data = dt.today().strftime("%Y-%m-%d") if checkpoint.fecha_realizado == '' else checkpoint.fecha_realizado
	form.estado.data = checkpoint.estado

	return render_template("edit_checkpoint.html", form=form, checkpoint=checkpoint)
