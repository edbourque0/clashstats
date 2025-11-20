import requests
from django.http import JsonResponse


def searchclanfnc(name, url, headers):
    """
    Executes a clan search based on the provided name parameter in the POST request.
    It forwards the request to an external API and retrieves the corresponding result.

    :param request: The HTTP request object containing details about the client's request.
    :type request: HttpRequest
    :return: A JSON response with the search results if the request is valid, an error
        message with HTTP 400 if the 'name' parameter is missing, or 405 if the
        request method is not POST.
    :rtype: JsonResponse
    """
    r = requests.get(url=f"{url}clans", headers=headers, params={"name": name})
    return JsonResponse(r.json(), status=200)
