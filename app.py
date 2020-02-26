from flask import Flask
import flask
from database.database import db, init_database
import datetime
import locale

locale.setlocale(locale.LC_ALL, 'fr_FR')

from database.models import Product, User, Reservation

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database/database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "secret_key1234"

db.init_app(app)

with app.test_request_context():
    init_database()


def save_object_to_db(db_object):
    db.session.add(db_object)
    db.session.commit()


def remove_object_from_db(db_object):
    db.session.delete(db_object)
    db.session.commit()


def find_reservations():
    return Reservation.query.all()


def find_reservations_by_collect_date(collect_date):
    return Reservation.query.filter(Reservation.collect_date.strftime("%Y-%m-%d")==collect_date).all()


def find_reservations_with_future_collect_date(today):
    return Reservation.query.filter(Reservation.collect_date > today).all()


def find_reservations_with_old_collect_date(today):
    return Reservation.query.filter(Reservation.collect_date < today).all()


def find_user_by_id(id):
    return User.query.filter_by(id=id).first()


def find_product_by_id(id):
    return Product.query.filter_by(id=id).first()


def find_products():
    return Product.query.all()


def table_display(reservations):
    to_display = []
    for reservation in reservations:
        user = find_user_by_id(reservation.user_id)
        product = find_product_by_id(reservation.product_id)
        dict_res = {"id": reservation.id,
                    "name": user.last_name + " " + user.first_name,
                    "badge_number": user.badge_number,
                    "product_name": product.name,
                    "date": datetime.date.fromisoformat(reservation.collect_date).strftime("%d/%m/%Y")}
        to_display += [dict_res]
    return to_display


@app.route("/admin/reservations-du-jour", methods=["GET", "POST"])
def today_reservations():
    reservations = find_reservations_by_collect_date(datetime.datetime.now().strftime("%Y-%m-%d"))
    to_display = {"not_paid": [], "paid": [], "collected": []}
    for reservation in reservations:
        user = find_user_by_id(reservation.user_id)
        product = find_product_by_id(reservation.product_id)

        dict_res = {"id": reservation.id,
                    "name": user.last_name + " " + user.first_name,
                    "badge_number": user.badge_number,
                    "product_name": product.name,
                    "pack": reservation.pack}
        if reservation.pack:
            dict_res["price"] = product.price_in_pack
        else:
            dict_res["price"] = product.price

        if reservation.paid and reservation.collected:
            to_display["collected"] += [dict_res]


        elif reservation.paid:
            to_display["paid"] += [dict_res]
        else:
            to_display["not_paid"] += [dict_res]
    return flask.render_template("show_today_reservations.html.jinja2",
                                 to_display=to_display,
                                 active_page="today_reservations")


@app.route("/admin/reservations-a-venir", methods=["GET", "POST"])
def future_reservations():
    reservations = find_reservations_with_future_collect_date(datetime.date.today().isoformat())
    to_display = []
    for reservation in reservations:
        user = find_user_by_id(reservation.user_id)
        product = find_product_by_id(reservation.product_id)

        dict_res = {"id": reservation.id,
                    "name": user.last_name + " " + user.first_name,
                    "badge_number": user.badge_number,
                    "product_name": product.name,
                    "pack": reservation.pack,
                    "date": datetime.date.fromisoformat(reservation.collect_date).strftime("%a %d/%m/%Y")}
        if reservation.pack:
            dict_res["price"] = product.price_in_pack
        else:
            dict_res["price"] = product.price
        to_display += [dict_res]
    return flask.render_template("show_future_reservations.html.jinja2",
                                 to_display=to_display,
                                 active_page="future_reservations")


@app.route("/admin/reservations-passees", methods=["GET", "POST"])
def old_reservations():
    reservations = find_reservations_with_old_collect_date(datetime.date.totimestamp())
    to_display = []
    for reservation in reservations:
        user = find_user_by_id(reservation.user_id)
        product = find_product_by_id(reservation.product_id)

        dict_res = {"id": reservation.id,
                    "name": user.last_name + " " + user.first_name,
                    "badge_number": user.badge_number,
                    "product_name": product.name,
                    "pack": reservation.pack,
                    "date": datetime.date.fromtimestamp(int(reservation.collect_date)).strftime("%a %d/%m/%Y")}
        if reservation.pack:
            dict_res["price"] = product.price_in_pack
        else:
            dict_res["price"] = product.price
        to_display += [dict_res]
    return flask.render_template("show_old_reservations.html.jinja2",
                                 to_display=to_display,
                                 active_page="old_reservations")


@app.route("/admin/produits", methods=["GET", "POST"])
def products_management():
    products = find_products()
    to_display = []
    for product in products:

        dict_prod = {"id": product.id,
                     "name": product.name,
                     "price": product.price,
                     "quantity_available": product.quantity_available}
        if product.price_in_pack == None:
            dict_prod["price_in_pack"] = "Aucun"
        else:
            dict_prod["price_in_pack"] = product.price_in_pack
        if product.description == None:
            dict_prod["description"] = "Aucune description"
        else:
            dict_prod["description"] = product.description
        to_display += [dict_prod]
    return flask.render_template("show_products.html.jinja2",
                                 to_display=to_display,
                                 active_page="products_management")


if __name__ == '__main__':
    app.run()
