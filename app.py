import os
from copy import copy

import flask
from flask_json import as_json
from werkzeug.utils import secure_filename

from database.database import db, init_database
import datetime
import locale

locale.setlocale(locale.LC_ALL, 'fr_FR')

from database.models import Product, User, Reservation

app = flask.Flask(__name__)
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


def find_users():
    return User.query.all()


def find_reservations_by_collect_date(collect_date):
    begin = datetime.datetime.fromisoformat(collect_date.isoformat())
    delta = datetime.timedelta(days=1)
    end = begin + delta
    return Reservation.query.filter(Reservation.collect_date < end).filter(Reservation.collect_date >= begin).all()


def find_reservations_with_future_collect_date(today):
    begin = datetime.datetime.fromisoformat(today.isoformat())
    delta = datetime.timedelta(days=1)
    begin += delta
    return Reservation.query.filter(Reservation.collect_date >= begin).all()


def find_future_reservations_by_user_id(today, id):
    begin = datetime.datetime.fromisoformat(today.isoformat())
    return Reservation.query.filter(Reservation.collect_date >= begin).filter(Reservation.user_id==id).all()


def find_reservations_with_old_collect_date(today):
    end = datetime.datetime.fromisoformat(today.isoformat())
    return Reservation.query.filter(Reservation.collect_date < end).all()


def find_old_reservations_by_user_id(today, id):
    end = datetime.datetime.fromisoformat(today.isoformat())
    return Reservation.query.filter(Reservation.collect_date < end).filter(Reservation.user_id==id).all()


def find_user_by_id(id):
    return User.query.filter_by(id=id).first()


def find_users_by_last_name_containing_sthg(name):
    return User.query.filter(User.last_name.like(name + '%')).all()


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


def get_old_reservations_by_user_id(id):
    reservations = find_old_reservations_by_user_id(datetime.date.today(), id)
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


def get_list_available_quantity(product):
    return [product.available_quantity_mon, product.available_quantity_tue, product.available_quantity_wed,
            product.available_quantity_thu, product.available_quantity_fri]


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

def get_future_reservations_by_user_id(id):
    reservations = find_future_reservations_by_user_id(datetime.date.today(), id)
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


def get_products():
    products = find_products()
    to_display = []
    for product in products:
        dict_prod = {"id": product.id,
                     "name": product.name,
                     "price": product.price,
                     "available_quantity": get_list_available_quantity(product)}
        if product.price_in_pack == None:
            dict_prod["price_in_pack"] = "Aucun"
        else:
            dict_prod["price_in_pack"] = product.price_in_pack
        if product.description == "":
            dict_prod["description"] = "Aucune description"
        else:
            dict_prod["description"] = product.description
        if product.image_format != None:
            dict_prod["image_url"] = flask.url_for("static", filename="/img/product" + str(
                product.id) + "." + product.image_format)
        else:
            dict_prod["image_url"] = ""
        to_display += [dict_prod]
    return to_display


def product_form_is_valid(form):
    product_id = form.get("product_id", "")
    name = form.get("product_name", "")
    description = form.get("product_description", "")
    available_quantity_mon = form.get("product_available_quantity_mon", "")
    available_quantity_tue = form.get("product_available_quantity_tue", "")
    available_quantity_wed = form.get("product_available_quantity_wed", "")
    available_quantity_thu = form.get("product_available_quantity_thu", "")
    available_quantity_fri = form.get("product_available_quantity_fri", "")
    price = form.get("product_price", "")
    price_in_pack = form.get("product_price_in_pack", "")

    if product_id is "" or name is "" or price is "" or price_in_pack is "" or available_quantity_mon is "" or available_quantity_tue is "" or available_quantity_wed is "" or available_quantity_thu is "" or available_quantity_fri is "":
        result = False
    else:
        result = True
    return result


def reservation_form_is_valid(form):
    reservation_id = form.get("reservation_id", "")
    user_id = form.get("reservation_user", "")
    product_id = form.get("reservation_product", "")
    collect_date = form.get("reservation_collect_date", "")
    bonus_product_id = 0
    if reservation_id != '0':
        old_reservation_product = find_reservation_by_id(int(reservation_id)).product_id
        if int(product_id) == old_reservation_product:
            bonus_product_id = int(product_id)
    prod_dict = get_available_products(collect_date, bonus_product_id)
    if reservation_id is "" or user_id is "" or product_id is "" or prod_dict[int(product_id)]['quantity'] <= 0:
        result = False
    else:
        result = True
    return result


def new_product(name,
                description,
                available_quantities,
                price,
                price_in_pack,
                file):
    product = Product(name=name,
                      description=description,
                      available_quantity_mon=available_quantities[0],
                      available_quantity_tue=available_quantities[1],
                      available_quantity_wed=available_quantities[2],
                      available_quantity_thu=available_quantities[3],
                      available_quantity_fri=available_quantities[4],
                      price=price,
                      price_in_pack=price_in_pack)
    db.session.add(product)
    db.session.commit()
    if file:  # on vérifie qu'un fichier a bien été envoyé
        if '.' in file.filename and file.filename.rsplit('.', 1)[1] in (
                'png', 'jpg', 'jpeg'):  # on vérifie que son extension est valide
            product = find_products()[-1]
            file.save('static/img/product' + str(product.id) + '.' + file.filename.rsplit('.', 1)[1])
            product.image_format = file.filename.rsplit('.', 1)[1]
            db.session.add(product)
            db.session.commit()


def update_product(id,
                   name,
                   description,
                   available_quantities,
                   price,
                   price_in_pack,
                   file):
    product = find_product_by_id(id)
    product.name = name
    product.description = description
    product.available_quantity_mon = available_quantities[0]
    product.available_quantity_tue = available_quantities[1]
    product.available_quantity_wed = available_quantities[2]
    product.available_quantity_thu = available_quantities[3]
    product.available_quantity_fri = available_quantities[4]
    product.price = price
    product.price_in_pack = price_in_pack
    if file:  # on vérifie qu'un fichier a bien été envoyé
        if '.' in file.filename and file.filename.rsplit('.', 1)[1] in (
                'png', 'jpg', 'jpeg'):  # on vérifie que son extension est valide
            file.save('static/img/product' + str(id) + '.' + file.filename.rsplit('.', 1)[1])
            product.image_format = file.filename.rsplit('.', 1)[1]
    db.session.add(product)
    db.session.commit()


def new_reservation(user_id,
                    product_id,
                    pack,
                    paid,
                    collect_date):
    reservation = Reservation(user_id=user_id,
                              product_id=product_id,
                              pack=pack,
                              paid=paid,
                              collect_date=collect_date,
                              collected=False,
                              reservation_time=datetime.datetime.now())
    db.session.add(reservation)
    db.session.commit()


def update_reservation(id,
                       user_id,
                       product_id,
                       pack,
                       paid,
                       collect_date):
    reservation = find_reservation_by_id(id)
    reservation.user_id = user_id
    reservation.collect_date = collect_date
    reservation.paid = paid
    reservation.pack = pack
    reservation.product_id = product_id
    db.session.add(reservation)
    db.session.commit()


def delete_product(id):
    product = find_product_by_id(id)
    db.session.delete(product)
    db.session.commit()


def delete_reservation(id):
    reservation = find_reservation_by_id(id)
    db.session.delete(reservation)
    db.session.commit()


def extension_is_valid(file_name):
    return '.' in file_name and file_name.rsplit('.', 1)[1] in ('png', 'jpg', 'jpeg')


def get_available_products(date_iso, product_id_bonus):
    dict_prod = {}
    if date_iso != '0' and date_iso != 'null':
        date = datetime.date.fromisoformat(date_iso)
        reservations = find_reservations_by_collect_date(date)
        products = find_products()
        for product in products:
            quantity = get_list_available_quantity(product)[date.weekday()]
            if quantity > 0:
                dict_prod[product.id] = {'name': product.name,
                                         'quantity': quantity,
                                         'image_format': product.image_format,
                                         'description': product.description,
                                         'price': product.price,
                                         'price_in_pack': product.price_in_pack}
        for reservation in reservations:
            dict_prod[reservation.product_id]['quantity'] -= 1
        if product_id_bonus != 0:
            dict_prod[product_id_bonus]['quantity'] += 1
    return dict_prod


def get_begin_reservations_date():
    file = open("begin_reservation_date.txt", "r")
    content = file.read()
    file.close()
    date = datetime.date.fromisoformat(content)
    return date


def today_reservation_enabled():
    today = datetime.date.today()
    return get_begin_reservations_date() <= today


@app.route('/reserver')
def user_reservation_page():
    return flask.render_template("user_reserve.html.jinja2",
                                 active_page="user_reservation")


@app.route('/mes-reservations')
def user_future_reservations_page():
    to_display = get_future_reservations_by_user_id(1)
    return flask.render_template("user_reservations.html.jinja2",
                                 to_display=to_display,
                                 active_page="user_future_reservations")


@app.route('/reservations-passees')
def user_old_reservations_page():
    to_display = get_old_reservations_by_user_id(1)
    return flask.render_template("user_old_reservations.html.jinja2",
                                 to_display=to_display,
                                 active_page="user_old_reservations")

@app.route('/admin/<action>_today_reservations')
def action_today_reservations(action):
    if action == 'close':
        today = datetime.date.today()
        date = today + datetime.timedelta(days=1)
    else:
        date = datetime.date.today()
    file = open("begin_reservation_date.txt", "w")
    file.write(date.isoformat())
    file.close()
    return flask.render_template("empty.html.jinja2")


@app.route('/admin/get_product_selection/<date_iso>/<int:reservation_id_selected>')
def get_product_selection(date_iso, reservation_id_selected=0):
    if reservation_id_selected != 0:
        product_id = find_reservation_by_id(reservation_id_selected).product_id
    else:
        product_id = 0
    products = get_available_products(date_iso, product_id)
    return flask.render_template("get_product_selection.html.jinja2",
                                 products=products,
                                 selected_id=product_id)


@app.route('/admin/get_price/<int:id>/<pack>')
def get_price(id, pack):
    product = find_product_by_id(id)
    if pack == 'pack':
        return str(product.price_in_pack)
    else:
        return str(product.price)


@app.route('/admin/get_user_selection/<int:selected_reservation_id>/')
@app.route('/admin/get_user_selection/<int:selected_reservation_id>/<name>')
def get_user_selection(selected_reservation_id, name=""):
    if selected_reservation_id == 0:
        user_id = 0
    else:
        user_id = find_reservation_by_id(selected_reservation_id).user_id
    users = find_users_by_last_name_containing_sthg(name)
    if name == "":
        empty = True
    else:
        empty = False
    return flask.render_template("get_user_selection.html.jinja2",
                                 users=users,
                                 selected_id=user_id,
                                 empty=empty)


@app.route("/bdd", methods=["GET", "POST"])
def maj_bdd():
    # Creation d'une nouvelle tache. Elle n'est visible que localement
    new_reservation = Reservation(collect_date=datetime.datetime.now(), user_id=1, product_id=1,
                                  reservation_time=datetime.datetime.now(), paid=False, collected=False, pack=False)

    # Ajout de la tache dans la base de donnees
    db.session.add(new_reservation)
    db.session.commit()  # Sauvegarde les informations dans la base de donnees


@app.route("/admin/reservations-<date>", methods=["GET", "POST"])
def reservations_management(date):
    if flask.request.method == "POST":
        if reservation_form_is_valid(flask.request.form):
            collect_date = datetime.datetime.fromisoformat(flask.request.form.get("reservation_collect_date"))
            paid = False
            if flask.request.form.get("reservation_paid") == 'paid':
                paid = True
            pack = False
            if flask.request.form.get("reservation_pack") == 'pack':
                pack = True
            if flask.request.form.get("reservation_id") == '0':
                new_reservation(flask.request.form.get("reservation_user"),
                                flask.request.form.get("reservation_product"),
                                pack,
                                paid,
                                collect_date)
            else:
                update_reservation(flask.request.form.get("reservation_id"),
                                   flask.request.form.get("reservation_user"),
                                   flask.request.form.get("reservation_product"),
                                   pack,
                                   paid,
                                   collect_date)
        return flask.redirect(flask.url_for('reservations_management', date=date))
    reservation_enabled = today_reservation_enabled()
    active_page = ''
    if date == 'passees':
        active_page = "old_reservations"
    elif date == 'a-venir':
        active_page = "future_reservations"
    elif date == 'du-jour':
        active_page = "today_reservations"
    return flask.render_template("structure.html.jinja2",
                                 active_page=active_page,
                                 reservation_enabled=reservation_enabled)


@app.route("/admin/produits", methods=["GET", "POST"])
def products_management():
    if flask.request.method == "POST":
        if product_form_is_valid(flask.request.form):
            if flask.request.form.get("product_id") == '0':
                new_product(flask.request.form.get("product_name"),
                            flask.request.form.get("product_description"),
                            [flask.request.form.get("product_available_quantity_mon"),
                             flask.request.form.get("product_available_quantity_tue"),
                             flask.request.form.get("product_available_quantity_wed"),
                             flask.request.form.get("product_available_quantity_thu"),
                             flask.request.form.get("product_available_quantity_fri")],
                            flask.request.form.get("product_price"),
                            flask.request.form.get("product_price_in_pack"),
                            flask.request.files['product_image'])
            else:
                update_product(flask.request.form.get("product_id"),
                               flask.request.form.get("product_name"),
                               flask.request.form.get("product_description"),
                               [flask.request.form.get("product_available_quantity_mon"),
                                flask.request.form.get("product_available_quantity_tue"),
                                flask.request.form.get("product_available_quantity_wed"),
                                flask.request.form.get("product_available_quantity_thu"),
                                flask.request.form.get("product_available_quantity_fri")],
                               flask.request.form.get("product_price"),
                               flask.request.form.get("product_price_in_pack"),
                               flask.request.files['product_image'])
        return flask.redirect(flask.url_for('products_management'))
    else:
        return flask.render_template("structure.html.jinja2",
                                     active_page="products_management")


@app.route("/admin/suppress_product_image/<int:id>", methods=["GET", "POST"])
def suppress_product_image(id):
    product = find_product_by_id(id)
    extension = copy(product.image_format)
    product.image_format = None
    db.session.add(product)
    db.session.commit()
    os.remove("static/img/product" + str(id) + '.' + extension)
    return flask.render_template("empty.html.jinja2")


@app.route("/admin/delete_product/<int:id>", methods=["GET", "POST"])
def delete_product_page(id):
    delete_product(id)
    return flask.render_template("empty.html.jinja2")


@app.route("/admin/delete_reservation/<int:id>", methods=["GET", "POST"])
def delete_reservation_page(id):
    delete_reservation(id)
    return flask.render_template("empty.html.jinja2")


@app.route("/admin/get_old_reservations", methods=["GET", "POST"])
def get_old_reservations_table():
    to_display = get_old_reservations()
    return flask.render_template("old_reservations.html.jinja2",
                                 to_display=to_display)


@app.route("/admin/get_today_reservations", methods=["GET", "POST"])
@app.route("/admin/get_today_reservations/<tab>", methods=["GET", "POST"])
def get_today_reservations_table(tab='not-paid-tab'):
    to_display = get_today_reservations()
    return flask.render_template("today_reservations.html.jinja2",
                                 tab=tab,
                                 to_display=to_display)


@app.route("/admin/get_future_reservations", methods=["GET", "POST"])
def get_future_reservations_table():
    to_display = get_future_reservations()
    return flask.render_template("future_reservations.html.jinja2",
                                 to_display=to_display)


@app.route("/admin/get_products_management", methods=["GET", "POST"])
def get_products_management_table():
    to_display = get_products()
    return flask.render_template("products.html.jinja2",
                                 to_display=to_display)


@app.route("/admin/get_product_form/<int:id>", methods=["GET", "POST"])
@app.route("/admin/get_product_form/", methods=["GET", "POST"])
def get_product_form(id=None):
    if id == None:
        product = None
    else:
        product = find_product_by_id(id)
    return flask.render_template("product_form.html.jinja2",
                                 product=product)


@app.route("/admin/get_reservation_form/<int:id>", methods=["GET", "POST"])
@app.route("/admin/get_reservation_form/", methods=["GET", "POST"])
def get_reservation_form(id=0):
    dates = []
    begin_reservations = get_begin_reservations_date()
    today = datetime.date.today()
    if today < begin_reservations:
        first = begin_reservations
    else:
        first = today
    day = first.isoweekday()
    if day == 6:
        date = first + datetime.timedelta(days=2)
    elif day == 7:
        date = first + datetime.timedelta(days=1)
    else:
        date = first
    if day < 5 or today.isoweekday() != 5:
        while date.isoweekday() < 6:
            dates += [{'iso': date.isoformat(), 'long_format': date.strftime('%A %d/%m')}]
            date += datetime.timedelta(days=1)
    if id == 0:
        return flask.render_template("reservation_form.html.jinja2",
                                     reservation=None,
                                     dates=dates)
    else:
        reservation = find_reservation_by_id(id)
        selected_date = reservation.collect_date.strftime('%Y-%m-%d')
        if reservation.pack:
            price = reservation.product.price_in_pack
        else:
            price = reservation.product.price
        return flask.render_template("reservation_form.html.jinja2",
                                     reservation=reservation,
                                     price=price,
                                     dates=dates,
                                     selected_date=selected_date)


@app.route("/admin/cash/<id>", methods=["GET", "POST"])
def cash(id):
    reservation = find_reservation_by_id(id)
    reservation.paid = True
    db.session.add(reservation)
    db.session.commit()
    return flask.render_template("empty.html.jinja2")


@app.route("/admin/collect/<id>", methods=["GET", "POST"])
def collect(id):
    reservation = find_reservation_by_id(id)
    reservation.collected = True
    db.session.add(reservation)
    db.session.commit()
    return flask.render_template("empty.html.jinja2")


if __name__ == '__main__':
    app.run()
