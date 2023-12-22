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