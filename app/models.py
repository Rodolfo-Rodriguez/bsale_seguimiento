
from datetime import datetime as dt, timedelta
from . import db, login_manager

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

seguimientos = {
                'Seguimiento Pasa a Produccion':3,
                'Seguimiento dia 15':15,
                'Seguimiento dia 30':30,
                'Seguimiento dia 60':60,
                }

#---------------------------------------------------------------------------------------------------------------------------------------------------------------
# Deal Class
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
class Deal(db.Model):
    __tablename__ = 'deals'
    negocio_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    cpn = db.Column(db.Integer, nullable=True)
    ruc = db.Column(db.String, nullable=True)
    comercial = db.Column(db.String, nullable=True)
    razon_social = db.Column(db.String, nullable=True)
    plan_bsale = db.Column(db.String, nullable=True)
    categoria = db.Column(db.String, nullable=True)
    etapa = db.Column(db.String, nullable=True)
    estado = db.Column(db.String, nullable=True)
    fecha_ganado = db.Column(db.String, nullable=True)
    fecha_inicio_pem = db.Column(db.String, nullable=True)
    ejecutivo_pem = db.Column(db.String, nullable=True)
    fecha_contacto_inicial = db.Column(db.String, nullable=True)
    fecha_pase_produccion = db.Column(db.String, nullable=True)
    url_bsale = db.Column(db.String, nullable=True)
    url_cliente = db.Column(db.String, nullable=True)
    comentario = db.Column(db.String, nullable=True)
    razon_baja = db.Column(db.String, nullable=True)
    fecha_baja = db.Column(db.String, nullable=True)
    checkpoints = db.relationship('Checkpoint', backref='deal', lazy='dynamic', cascade="delete")

    def __repr__(self):
        return f'<Deal (id={self.negocio_id}, (cpn={self.cpn}, ruc={self.ruc})>'

    def set_fecha_pase_produccion(self, fecha):
        self.fecha_pase_produccion = fecha

        for nombre, dias in seguimientos.items():

            if self.fecha_pase_produccion != '':
                fecha_dt = dt.strptime(self.fecha_pase_produccion, '%Y-%m-%d').date() + timedelta(days=dias)
                fecha_str = fecha_dt.strftime("%Y-%m-%d")
            else:
                fecha_str = ''
            
            checkpoint = Checkpoint.query.filter(Checkpoint.nombre==nombre, Checkpoint.deal_id==self.negocio_id).first()
            checkpoint.fecha = fecha_str

        #db.session.commit()


    def anio(self):
        if self.fecha_inicio_pem:
            return (self.fecha_inicio_pem[0:4] if len(self.fecha_inicio_pem) >=4 else '')
        else:
            return('')

    def mes_anio(self):
        if self.fecha_ganado:
            return (self.fecha_ganado[0:7] if len(self.fecha_ganado) >=7 else '')
        else:
            return('')

    def dias_ganado(self):

        try:
            return ((dt.today().date() - dt.strptime(self.fecha_ganado, '%Y-%m-%d').date()).days)
        except:
            return('')

    def dias_pem(self):

        if self.etapa in ['PEM']:
            try:
                return ((dt.today().date() - dt.strptime(self.fecha_inicio_pem, '%Y-%m-%d').date()).days)
            except:
                return('')
        else:
            try:
                return((dt.strptime(self.fecha_pase_produccion, '%Y-%m-%d').date() - dt.strptime(self.fecha_inicio_pem, '%Y-%m-%d').date()).days)
            except:
                return('')

    def pem_excedido(self):

        return(  True if (self.dias_pem() != '' and self.dias_pem() > 30) else False )
        

    def dias_prod(self):

        if self.etapa == 'PRODUCCION':
            try:
                return ((dt.today().date() - dt.strptime(self.fecha_pase_produccion, '%Y-%m-%d').date()).days)
            except:
                return('')
        else:
            try:
                return((dt.strptime(self.fecha_baja, '%Y-%m-%d').date() - dt.strptime(self.fecha_pase_produccion, '%Y-%m-%d').date()).days)
            except:
                return('')

    def dias_baja(self):

        if self.etapa == 'BAJA':
            try:
                return ((dt.today().date() - dt.strptime(self.fecha_baja, '%Y-%m-%d').date()).days)
            except:
                return('')
        else:
            return('')

    def tiene_url(self):
        
        return ( self.url_bsale.startswith('http') if self.url_bsale else False)


    def tiene_url_cliente(self):
        
        return ( self.url_cliente.startswith('http') if self.url_cliente else False )

    def checkpoint(self, idx):

        checkpoints = sorted(self.checkpoints, key=lambda x:x.fecha)

        return checkpoints[idx]

    def al_dia(self):

        fecha_hoy = dt.today().strftime("%Y-%m-%d")

        al_dia = False
        ultima_fecha = ''
        for cp in self.checkpoints:
            if cp.fecha and cp.fecha < fecha_hoy:
                al_dia = cp.realizado
                ultima_fecha = cp.fecha
            else:
                break

        return( ('SI',ultima_fecha) if al_dia else ('NO',ultima_fecha) )

    def etapa_txt(self):

        return( self.etapa if self.etapa != '' else 'Vendido')

    def etapa_dias_txt(self):

        dias_gan = self.dias_ganado() if self.dias_ganado() != '' else '?'
        dias_pem = self.dias_pem() if self.dias_pem() != '' else '?'
        dias_prod = self.dias_prod() if self.dias_prod() != '' else '?'
        dias_baja = self.dias_baja() if self.dias_baja() != '' else '?'

        dias_pem_txt = '{} Día en PEM'.format(dias_pem) if dias_pem==1 else '{} Días en PEM'.format(dias_pem)
        dias_prod_txt = '{} Día en PRO'.format(dias_prod) if dias_prod==1 else '{} Días en PRO'.format(dias_prod)
        dias_baja_txt = '{} Día en BAJA'.format(dias_baja) if dias_baja==1 else '{} Días en BAJA'.format(dias_baja)
        dias_gan_txt = '{} Día'.format(dias_gan) if dias_gan==1 else '{} Días'.format(dias_gan)

        if self.etapa == 'PEM':
            dias_txt = '{}'.format(dias_pem_txt)
        elif self.etapa == 'PRODUCCION':
            dias_txt = '{}, {}'.format(dias_pem_txt, dias_prod_txt)
        elif self.etapa == 'BAJA':
            dias_txt = '{} - {} - {}'.format(dias_pem_txt, dias_prod_txt, dias_baja_txt)
        else:
            dias_txt = '{}'.format(dias_gan_txt)

        return(dias_txt)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------
# Checkpoint Class
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
class Checkpoint(db.Model):
    __tablename__ = 'checkpoints'
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    nombre = db.Column(db.String, nullable=True)
    fecha = db.Column(db.String, nullable=True)
    realizado = db.Column(db.Boolean, default=False)
    fecha_realizado = db.Column(db.String, nullable=True)
    estado = db.Column(db.String, nullable=True)
    comentario = db.Column(db.String, nullable=True)
    deal_id = db.Column(db.Integer, db.ForeignKey('deals.negocio_id'))
    
    def __repr__(self):
        return f'<Checkpoint (id={self.id}, (nombre={self.nombre}>'

    def expirado(self):

        if self.fecha and self.fecha != '':
            return (dt.strptime(self.fecha, '%Y-%m-%d').date() < dt.today().date())
        else:
            return False

#---------------------------------------------------------------------------------------------------------------------------------------------------------------
# Role Class
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    def __repr__(self):
        return '<Role %r>' % self.name

#---------------------------------------------------------------------------------------------------------------------------------------------------------------
# User Class
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(64), unique=True, index=True) 
    username = db.Column(db.String(64), unique=True, index=True) 
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

