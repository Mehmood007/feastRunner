from django.http import HttpRequest
from django.shortcuts import render


# "/"
def home(request: HttpRequest) -> render:
    return render(request, "home.html")
