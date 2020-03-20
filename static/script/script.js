let active_page;

function set_active_page(new_active_page) {
    active_page = new_active_page;
}

function refresh() {
    if (active_page == 'today_reservations') {
        active_page_tab = active_page + get_tab()
    }else{
        active_page_tab=active_page
    }
    $('#table-content').load('/././admin/get_' + active_page_tab, function () {
        //alert('Mise à jour de ' + active_page + ' réussie');
    });
}

function get_tab() {
    tabs = $('[role="tab"]')
    let tab = ""
    for (let i = 0; i < tabs.length; i++) {
        if (tabs[i].ariaSelected == "true") {
            tab = "/" + tabs[i].id;
        }
    }
    return tab
}

function cash(reservation_id) {
    $.ajax({
        type: 'GET',
        url: '/././admin/cash/' + reservation_id,
        timeout: 3000,
        success: function () {
            refresh()
        },
        error: function () {
            display_error("Un problème est survenu. L'encaissement n'a pas eu lieu")
        }
    });
}

function collect(reservation_id) {
    $.ajax({
        type: 'GET',
        url: '/././admin/collect/' + reservation_id,
        timeout: 3000,
        success: function () {
            refresh()
        },
        error: function () {
            display_error("Un problème est survenu", "Le produit n'a pas pu être marqué comme récupéré")
        }
    });
}

function delete_product(id, name) {
    display_error("Supprimer le produit", "Vous êtes sur le point de supprimer le produit " + name + ".", "Confirmer",
        function () {
            $.ajax({
                type: 'GET',
                url: '/././admin/delete_product/' + id,
                timeout: 3000,
                success: function () {
                    refresh()
                    $('#errorBox').modal('hide')
                },
                error: function () {
                    display_error("Un problème est survenu", "Le produit n'a pas pu être supprimé")
                }
            })
        }
    )

}

function delete_reservation(id) {
    display_error("Supprimer la réservation", "Vous êtes sur le point de supprimer cette réservation.", "Confirmer",
        function () {
            $.ajax({
                type: 'GET',
                url: '/././admin/delete_reservation/' + id,
                timeout: 3000,
                success: function () {
                    refresh()
                    $('#errorBox').modal('hide')
                },
                error: function () {
                    display_error("Un problème est survenu", "La réservation n'a pas pu être supprimée.")
                }
            })
        }
    )

}

function suppress_product_image(product_id) {
    $.ajax({
        type: 'GET',
        url: '/././admin/supress_product_image/' + product_id,
        timeout: 3000,
        success: function () {
            refresh()
            display_error("L'image a bien été retirée.")
        },
        error: function () {
            display_error("Le produit n'a pas pu être retiré. Vérifiez qu'il ne soit présent dans aucune réservation.")
        }
    });
}


function update_user_selection(id = 0) {
    $('#reservation_user_selector').load('/././admin/get_user_selection/' + id + '/' + $('#reservation_user_name_search').val(), function () {
    });
}

function update_product_selection(id = 0) {
    date_iso=$('#reservation_date_selector > select').val()
    if(date_iso==""){
        date_iso=0
    }
    $('#reservation_product_selector').load('/././admin/get_product_selection/' + date_iso + '/' + id, function () {
    });
}

function display_error(error_title, error_body, error_button = null, error_button_action = null) {
    $('#errorBoxTitle').html(error_title)
    $('#errorBoxBody').html(error_body)
    if (error_button == null) {
        $('#errorButton').css('display', 'none');
    } else {
        $('#errorButton').html(error_button);
        $('#errorButton').css('display', 'block');
        $('#errorButton').click(error_button_action);

    }
    $('#errorBox').modal('show')
}

function open_product_modal(id = '') {
    $('#itemModal').load('/././admin/get_product_form/' + id, function () {
        //alert('Mise à jour de ' + active_page + ' réussie');
    });
    $('#itemModal').modal('show');

}

function open_reservation_modal(id = 0) {
    $('#itemModal').load('/././admin/get_reservation_form/' + id, function () {
        update_user_selection(id)
        update_product_selection(id)
    });
    $('#itemModal').modal('show');

}

function update_price_displayed_reservation_form() {
    id = $('#reservation_product').val()
    pack = $('[name=reservation_pack]:checked').val()
    if (id != null) {
        $('#reservation_price').load('/././admin/get_price/' + id + '/' + pack, function () {
            //alert('Mise à jour de ' + active_page + ' réussie');
        });
    }
}


function close_reservations(){
    $.ajax({
        type: 'GET',
        url: '/././admin/close_today_reservations',
        timeout: 3000,
        success: function () {
            $('#action_reservations').addClass('btn-outline-danger')
            $('#action_reservations').removeClass('btn-danger')
            $('#action_reservations').text('Rouvrir les réservations')
            $("#action_reservations").attr("onclick","open_reservations()");
        },
        error: function () {
            display_error("Erreur", "L'action n'a pas pu être réalisée")
        }
    });
}


function open_reservations(){
    $.ajax({
        type: 'GET',
        url: '/././admin/open_today_reservations',
        timeout: 3000,
        success: function () {
            $('#action_reservations').addClass('btn-danger')
            $('#action_reservations').removeClass('btn-outline-danger')
            $('#action_reservations').text('Clôturer les réservations')
            $("#action_reservations").attr("onclick","close_reservations()");
        },
        error: function () {
            display_error("Erreur", "L'action n'a pas pu être réalisée")
        }
    });
}


$(function () {
    update_user_selection(0);
});