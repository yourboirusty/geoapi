from django.http import HttpResponse, HttpRequest


def healthcheck(request: HttpRequest) -> HttpResponse:
    """
    Simple heathcheck endpoint.
    """
    return HttpResponse("ok", status=200)
