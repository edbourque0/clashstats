from .models import Clans
import requests

def createclan(clantag, url, headers):
    """
    Handles the addition of a clan to the database. It retrieves clan data
    from an external API using the provided clan tag, then updates or creates
    the clan entry in the database based on the data fetched. Only HTTP POST
    requests are allowed for this operation. In case of unsupported HTTP methods,
    a proper response is returned.

    :param request: Django HttpRequest object
    :return: JsonResponse with a success message and status 200 for valid POST
             requests, or a JsonResponse with an error message and status 405
             for unsupported methods
    """

    r = requests.get(url=f'{url}clans/%23{clantag[1:]}', headers=headers, params={'name': clantag})
    clan = r.json()

    Clans.objects.update_or_create(
        tag=clan['tag'],
        defaults={
            'name': clan['name'],
            'type': clan['type'],
            'badgeId': clan['badgeId'],
            'location': clan['location']['countryCode'],
            'donationsPerWeek': clan['donationsPerWeek'],
            'members': clan['members']
        }
    )