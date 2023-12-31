from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.db.models import Q
from django.http import HttpRequest
from django.shortcuts import render

from vendor.models import Vendor


# "/"
def home(request: HttpRequest) -> render:
    location_coordinates = get_set_current_location(request)
    if location_coordinates:
        lng, lat = location_coordinates
        pnt = GEOSGeometry(f"POINT({lng} {lat})")
        vendors = (
            Vendor.objects.filter(
                Q(
                    is_approved=True,
                    user__is_active=True,
                ),
                user_profile__location__distance_lte=(pnt, D(km=1000)),
            )
            .annotate(distance=Distance("user_profile__location", pnt))
            .order_by("distance")
        )
        for vendor in vendors:
            vendor.kms = round(vendor.distance.km, 1)
    else:
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    context = {
        "vendors": vendors,
    }
    return render(request, "home.html", context)


def get_set_current_location(request: HttpRequest) -> tuple or None:
    if "lat" in request.GET and "lng" in request.GET:
        request.session["lat"] = request.GET["lat"]
        request.session["lng"] = request.GET["lng"]
        return request.session["lng"], request.session["lat"]
    if "lat" in request.session and "lng" in request.session:
        lat = request.session["lat"]
        lng = request.session["lng"]
        return lng, lat
    return None
