import requests
from django.http import JsonResponse


def search_clan(name, url, headers):
    """
    Executes a clan search based on the provided name parameter in the POST request.
    It forwards the request to an external API and retrieves the corresponding result.

    :param name: The name of the clan to search for.
    :type name: str
    :param url: The base URL of the external API.
    :type url: str
    :param headers: The headers to include in the API request.
    :type headers: dict
    :return: A JSON response with the search results if the request is valid, an error
        message with HTTP 400 if the 'name' parameter is missing, or 405 if the
        request method is not POST.
    :rtype: JsonResponse
    """

    r = requests.get(url=f"{url}clans", headers=headers, params={"name": name})
    return JsonResponse(r.json(), status=200)
