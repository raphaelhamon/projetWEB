from database.database import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.Text)
    first_name = db.Column(db.Text)
    badge_number = db.Column(db.Text)
    reservations = db.relationship('Reservation', backref='user', lazy='dynamic')


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    quantity_available = db.Column(db.Integer)
    price = db.Column(db.Float)
    price_in_pack = db.Column(db.Float)
    reservations = db.relationship('Reservation', backref='product', lazy='dynamic')


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    collect_date = db.Column(db.Text)
    reservation_time=db.Column(db.Text)
    paid = db.Column(db.Boolean)
    collected = db.Column(db.Boolean)
    pack = db.Column(db.Boolean)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
