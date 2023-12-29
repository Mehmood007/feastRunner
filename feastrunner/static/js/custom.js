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
                }
            }
        })
    })
})