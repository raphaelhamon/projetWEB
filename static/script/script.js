let active_page;

function set_active_page(new_active_page) {
    active_page=new_active_page;
}

function refresh(active_page) {
    if(active_page=='today_reservations'){
        active_page+=get_tab()
    }
    $('#table-content').load('/././admin/get_' + active_page, function () {
        //alert('Mise à jour de ' + active_page + ' réussie');
    });
}

function get_tab(){
    tabs=$('[role="tab"]')
    let tab="#not-paid"
    for(let i=0; i<tabs.length; i++) {
        if(tabs[i].ariaSelected=="true"){
            tab="/"+tabs[i].id;
        }
    }
    return tab
}

function cash(reservation_id) {
    $.ajax({
        type: 'GET',
        url: '/././admin/cash/' + reservation_id,
        timeout: 3000,
        success: function (){
            refresh('today_reservations')
        },
        error: function (){
            display_error("Un problème est survenu. L'encaissement n'a pas eu lieu")
        }
    });
}

function collect(reservation_id) {
    $.ajax({
        type: 'GET',
        url: '/././admin/collect/' + reservation_id,
        timeout: 3000,
        success: function (){
            refresh('today_reservations')
        },
        error: function (){
            display_error("Un problème est survenu. Le produit n'a pas pu être marqué comme récupéré")
        }
    });
}

function display_error(error) {
    alert(error);
}

$(function () {


    /*
    $('#majPremier').click(function () {
        $('#premier').load('maj1.html', function () {
            alert('La première zone a été mise à jour');
        });
    });

    $('#majDeuxieme').click(function () {
        $('#deuxieme').load('maj2.html', function () {
            alert('La deuxième zone a été mise à jour');
        });
    });
     */
});