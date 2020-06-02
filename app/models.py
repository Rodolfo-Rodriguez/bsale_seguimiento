
from datetime import datetime as dt
from . import db, login_manager

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Seguimiento(db.Model):
    __tablename__ = 'seguimiento'
    negocio_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    cpn = db.Column(db.Integer, nullable=True)
    ruc = db.Column(db.String, nullable=True)
    comercial = db.Column(db.String, nullable=True)
    razon_social = db.Column(db.String, nullable=True)
    plan_bsale = db.Column(db.String, nullable=True)
    categoria = db.Column(db.String, nullable=True)
    estado = db.Column(db.String, nullable=True)
    produccion = db.Column(db.String, nullable=True)
    fecha_ganado = db.Column(db.String, nullable=True)
    fecha_inicio_pem = db.Column(db.String, nullable=True)
    ejecutivo_pem = db.Column(db.String, nullable=True)
    fecha_contacto_inicial = db.Column(db.String, nullable=True)
    fecha_pase_produccion = db.Column(db.String, nullable=True)
    hizo_upselling = db.Column(db.String, nullable=True)
    url_bsale = db.Column(db.String, nullable=True)
    comentario = db.Column(db.String, nullable=True)
    razon_baja = db.Column(db.String, nullable=True)
    fecha_baja = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f'<Seguimiento (cpn={self.cpn}, ruc={self.ruc})>'

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

    def dias_pem(self):

        if self.estado == 'PEM':
            try:
                return ((dt.today().date() - dt.strptime(self.fecha_inicio_pem, '%Y-%m-%d').date()).days)
            except:
                return('')
        else:
            try:
                return((dt.strptime(self.fecha_pase_produccion, '%Y-%m-%d').date() - dt.strptime(self.fecha_inicio_pem, '%Y-%m-%d').date()).days)
            except:
                return('')

    def tiene_url(self):
        
        return (self.url_bsale.startswith('http'))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    def __repr__(self):
        return '<Role %r>' % self.name

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

