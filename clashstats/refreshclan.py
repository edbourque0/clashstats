from .models import Members, Refresh, Clans
from .updateelo import updateelofcn
from .clan import createclan
from .member import createmembers
from .battlelog import createbattlelog


def refreshclanfcn(clantag, url, headers, source="api"):
    """
    Handles the refreshing of clan data, clan member details, and their battlelogs
    by making API requests. This function is primarily triggered by a POST request
    and processes the clan information using the provided clantag.

    :param clantag:
    :param url:
    :param headers:
    :param request: Django HTTP request object
    :type request: HttpRequest
    :return: JSON response indicating success or failure of the operation
    :rtype: JsonResponse
    """
    createclan(clantag, url, headers)
    createmembers(clantag, url, headers)
    for member in Members.objects.select_related("clanTag").all():
        createbattlelog(member.tag, url, headers)

    updateelofcn()
    Refresh.objects.create(clanTag=Clans.objects.get(tag=clantag), source=source)
