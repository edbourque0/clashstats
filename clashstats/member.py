from .models import Clans, Members
import requests


def createmembers(clantag, url, headers):
    """
    Adds and updates clan members in the database based on a POST request.

    This function fetches the list of members in a specified clan from an external
    API using the supplied clan tag. It updates the database with the current state
    of the members or creates new entries if required. If the request method is
    not POST, it returns an appropriate response indicating that the method is not
    allowed.

    :param request: Django's HTTP request object containing request data and context.
    :type request: HttpRequest
    :return: JSON response containing a message indicating the result of the operation.
    :rtype: JsonResponse
    """
    r = requests.get(url=f"{url}clans/%23{clantag[1:]}/members", headers=headers)

    members = r.json()["items"]
    for member in members:
        Members.objects.update_or_create(
            tag=member["tag"],
            defaults={
                "clanTag": Clans.objects.get(tag=clantag),
                "name": member["name"],
                "role": member["role"],
                "lastSeen": member["lastSeen"],
                "expLevel": member["expLevel"],
                "trophies": member["trophies"],
                "clanRank": member["clanRank"],
                "donations": member["donations"],
                "donationsReceived": member["donationsReceived"],
            },
        )
