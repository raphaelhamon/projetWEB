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
    begin = datetime.datetime.fromisoformat(collect_date.isoformat())
    delta=datetime.timedelta(days=1)
    end = begin+delta
    return Reservation.query.filter(Reservation.collect_date < end).filter(Reservation.collect_date > begin).all()


def find_reservations_with_future_collect_date(today):
    begin=datetime.datetime.fromisoformat(today.isoformat())
    delta=datetime.timedelta(days=1)
    begin+=delta
    return Reservation.query.filter(Reservation.collect_date > begin).all()


def find_reservations_with_old_collect_date(today):
    end=datetime.datetime.fromisoformat(today.isoformat())
    return Reservation.query.filter(Reservation.collect_date < end).all()


def find_user_by_id(id):
    return User.query.filter_by(id=id).first()


def find_reservation_by_id(id):
    return Reservation.query.filter_by(id=id).first()


def find_product_by_id(id):
    return Product.query.filter_by(id=id).first()


def find_products():
    return Product.query.all()


def get_old_reservations():
    reservations = find_reservations_with_old_collect_date(datetime.date.today())
    to_display = []
    for reservation in reservations:
        user = find_user_by_id(reservation.user_id)
        product = find_product_by_id(reservation.product_id)

        dict_res = {"id": reservation.id,
                    "name": user.last_name + " " + user.first_name,
                    "badge_number": user.badge_number,
                    "product_name": product.name,
                    "pack": reservation.pack,
                    "collect_date": reservation.collect_date.strftime("%a %d/%m/%Y"),
                    "collect_time": reservation.collect_date.strftime("%H:%M")}
        if reservation.pack:
            dict_res["price"] = product.price_in_pack
        else:
            dict_res["price"] = product.price
        to_display += [dict_res]
    return to_display

def get_today_reservations():
    reservations = find_reservations_by_collect_date(datetime.date.today())
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
    return to_display


def get_future_reservations():
    reservations = find_reservations_with_future_collect_date(datetime.date.today())
    to_display = []
    for reservation in reservations:
        user = find_user_by_id(reservation.user_id)
        product = find_product_by_id(reservation.product_id)

        dict_res = {"id": reservation.id,
                    "name": user.last_name + " " + user.first_name,
                    "badge_number": user.badge_number,
                    "product_name": product.name,
                    "pack": reservation.pack,
                    "date": reservation.collect_date.strftime("%a %d/%m/%Y")}
        if reservation.pack:
            dict_res["price"] = product.price_in_pack
        else:
            dict_res["price"] = product.price
        to_display += [dict_res]
    return to_display




@app.route("/bdd", methods=["GET", "POST"])
def maj_bdd():
    # Creation d'une nouvelle tache. Elle n'est visible que localement
    new_reservation = Reservation(collect_date=datetime.datetime.now(), user_id=1, product_id=1,
                                  reservation_time=datetime.datetime.now(), paid=False, collected=False, pack=False)

    # Ajout de la tache dans la base de donnees
    db.session.add(new_reservation)
    db.session.commit()  # Sauvegarde les informations dans la base de donnees


@app.route("/admin/reservations-du-jour", methods=["GET", "POST"])
def today_reservations():
    return flask.render_template("structure.html.jinja2",
                                 active_page="today_reservations")


@app.route("/admin/reservations-a-venir", methods=["GET", "POST"])
def future_reservations():
    return flask.render_template("structure.html.jinja2",
                                 active_page="future_reservations")


@app.route("/admin/reservations-passees", methods=["GET", "POST"])
def old_reservations():
    return flask.render_template("structure.html.jinja2",
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

@app.route("/admin/get_<id>", methods=["GET", "POST"])
@app.route("/admin/get_<id>/<tab>", methods=["GET", "POST"])
def get_table(id, tab='not-paid-tab'):
    if id=='old_reservations':
        to_display=get_old_reservations()
        return flask.render_template("old_reservations.html.jinja2",
                                     to_display=to_display)
    if id=='today_reservations':
        to_display=get_today_reservations()
        return flask.render_template("today_reservations.html.jinja2",
                                     tab=tab,
                                     to_display=to_display)
    if id=='future_reservations':
        to_display=get_future_reservations()
        return flask.render_template("future_reservations.html.jinja2",
                                     to_display=to_display)

@app.route("/admin/cash/<id>", methods=["GET", "POST"])
def cash(id):
    reservation=find_reservation_by_id(id)
    reservation.paid = True
    db.session.add(reservation)
    db.session.commit()
    return flask.render_template("empty.html.jinja2")


@app.route("/admin/collect/<id>", methods=["GET", "POST"])
def collect(id):
    reservation=find_reservation_by_id(id)
    reservation.collected = True
    db.session.add(reservation)
    db.session.commit()
    return flask.render_template("empty.html.jinja2")


if __name__ == '__main__':
    app.run()
