let autocomplete;

function initAutoComplete() {
    autocomplete = new google.maps.places.Autocomplete(
        document.getElementById('id_address'), {
            types: ['geocode', 'establishment'],
            //default in this app is "IN" - add your country code
            componentRestrictions: {
                'country': ['PK']
            },
        })
    // function to specify what should happen when the prediction is clicked
    autocomplete.addListener('place_changed', onPlaceChanged);
}
setTimeout(function () {
    initAutoComplete();
}, 1000);

function onPlaceChanged() {
    var place = autocomplete.getPlace();

    // User did not select the prediction. Reset the input field or alert()
    if (!place.geometry) {
        document.getElementById('id_address').placeholder = "Start typing...";
    } else {
        console.log('place name=>', place.name)
    }
    // get the address components and assign them to the fields
    var geocoder = new google.maps.Geocoder();
    var address = document.getElementById('id_address').value

    geocoder.geocode({
        address: address
    }, function (results, status) {
        if (status === google.maps.GeocoderStatus.OK) {
            var latitude = results[0].geometry.location.lat();
            var longitude = results[0].geometry.location.lng();
            $('#id_longitude').val(longitude);
            $('#id_latitude').val(latitude);

        }
    })
    console.log(place.address_components);

    // loop through address components
    place.address_components.forEach(function (component) {
        component.types.forEach(function (type) {
            if (type === 'country') {
                $('#id_country').val(component.long_name);
            }
            if (type === 'administrative_area_level_2') {
                $('#id_city').val(component.long_name);
            }
            if (type === 'administrative_area_level_1') {
                $('#id_state').val(component.long_name);
            }
            if (type === 'postal_code') {
                $('#id_pin_code').val(component.long_name);
            }
        });
    });

}


$(document).ready(function () {
    // Add to cart
    $('.add_to_cart').on('click', function (e) {
        e.preventDefault();
        food_id = $(this).attr('data-id')
        url = $(this).attr('url-id')


        $.ajax({
            type: 'GET',
            url: url,
            success: function (response) {
                if (response.status === 'login_required') {
                    swal('Login Required', 'Please Login to add items to cart', 'info').then(function () {
                        window.location = '../accounts/login';
                    });
                } else if (response.status === 'failed') {
                    swal('Failed', response.message, 'error');
                } else {
                    $('#cart_counter').html(response.cart_count);
                    $('#qty-' + food_id).html(response.qty);
                    console.log(response.cart_amount)
                    // sub_total, tax and grand_total
                    applyCartAmount(response.cart_amount.sub_total, response.cart_amount.tax_dict, response.cart_amount.grand_total)
                }
            }
        })
    })


    // Place cart item quantity on load
    $('.item_qty').each(function () {
        var the_id = $(this).attr('id');
        var quantity = $(this).attr('data-qty');
        $('#' + the_id).html(quantity);
    })

    // Decrease Cart
    $('.decrease_cart').on('click', function (e) {
        e.preventDefault();
        food_id = $(this).attr('data-id')
        url = $(this).attr('url-id')


        $.ajax({
            type: 'GET',
            url: url,
            success: function (response) {
                if (response.status === 'login_required') {
                    swal('Login Required', 'Please login to remove items from cart', 'info').then(function () {
                        window.location = '../accounts/login';
                    });
                } else if (response.status === 'failed') {
                    swal('Failed', response.message, 'error');
                } else {
                    $('#cart_counter').html(response.cart_count);
                    $('#qty-' + food_id).html(response.qty);
                    if (response.qty <= 0) {
                        removeCartItem(food_id);
                    }
                    // sub_total, tax and grand_total
                    applyCartAmount(response.cart_amount.sub_total, response.cart_amount.tax_dict, response.cart_amount.grand_total)
                }
            }
        })
    })

    // Delete Cart
    $('.delete_cart').on('click', function (e) {
        e.preventDefault();
        cart_id = $(this).attr('data-id')
        url = $(this).attr('url-id')


        $.ajax({
            type: 'GET',
            url: url,
            success: function (response) {
                if (response.status === 'failed') {
                    swal('Failed', response.message, 'error');
                } else {
                    $('#cart_counter').html(response.cart_count);
                    swal(response.status, response.message, 'success');
                    removeCartItem(cart_id);
                    // sub_total, tax and grand_total
                    applyCartAmount(response.cart_amount.sub_total, response.cart_amount.tax_dict, response.cart_amount.grand_total)
                }
            }
        })
    })

    // Remove Cart item
    function removeCartItem(cart_id) {
        if (window.location.pathname == '/marketplace/cart/') {
            document.getElementById('cart-item-' + cart_id).remove();
            var cartCounter = $('#cart_counter');

            var cartCount = parseInt(cartCounter.text().trim(), 10);
            var cartList = $('#menu-item-list-6272');

            if (cartCount === 0) {
                cartList.html('<h3 class="text-center p-5">No items in cart</h3>');
            }
        }
    }

    // Cart Amount display
    function applyCartAmount(sub_total, tax_dict, grand_total) {
        if (window.location.pathname == '/marketplace/cart/') {
            $('#sub_total').html(sub_total);
            $('#grand_total').html(grand_total);
            for (key1 in tax_dict) {
                for (key2 in tax_dict[key1]) {
                    $('#tax-' + key1).html(tax_dict[key1][key2]);
                }
            }
        }
    }

    // Add opening hours
    $('.add_hours').on('click', function (e) {
        e.preventDefault();
        var day = document.getElementById('id_day').value;
        var from_hour = document.getElementById('id_from_hour').value;
        var to_hour = document.getElementById('id_to_hour').value;
        var is_closed = document.getElementById('id_is_closed').checked;
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        if (is_closed) {
            is_closed = 'True';
            condition = "day!==''";
        } else {
            is_closed = 'False';
            condition = "day!=='' && from_hour!=='' && to_hour!==''";
        }
        if (eval(condition)) {
            $.ajax({
                type: 'POST',
                url: document.getElementById('add_hours_url').value,
                data: {
                    'day': day,
                    'from_hour': from_hour,
                    'to_hour': to_hour,
                    'is_closed': is_closed,
                    'csrfmiddlewaretoken': csrf_token
                },
                success: function (response) {
                    if (response.status === 'success') {
                        if (response.is_closed) {
                            html = '<tr id="hour-"' + response.id + '><td><b>' + response.day + '</b></td> <td>Closed</td> <td><a href="#" class="delete_hour" data-url="/accounts/vendor/opening_hours/delete/' + response.id + '">Remove</a></td></tr>'
                        } else {
                            html = '<tr id="hour-' + response.id + '"><td><b>' + response.day + '</b></td> <td>' + response.from_hour + ' - ' + response.to_hour + '</td> <td><a href="#" class="delete_hour" data-url="/accounts/vendor/opening_hours/delete/' + response.id + '">Remove</a></td></tr>'
                        }

                        $('.opening_hours').append(html);
                        document.getElementById('opening_hours').reset();
                    } else {
                        swal('Field', response.message, 'error');
                    }
                }
            })
        } else {
            swal('Field Missing', "Please fill all the fields", 'info');
        }
    })


    $(document).on('click', '.delete_hour', function (e) {
        e.preventDefault();
        url = $(this).attr('data-url');
        $.ajax({
            type: 'GET',
            url: url,
            success: function (response) {
                if (response.status === 'success') {
                    document.getElementById('hour-' + response.id).remove();
                }
            }
        })
    })
});