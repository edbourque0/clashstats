from .models import Members
from .updateelo import updateelofcn
from .clan import createclan
from .member import createmembers
from .battlelog import createbattlelog

def refreshclanfcn(clantag, url, headers):
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

    """ Refresh clan """
    createclan(clantag, url, headers)

    """ Refresh clan members """
    createmembers(clantag, url, headers)

    """ Refresh battlelog """
    for member in Members.objects.select_related('clanTag').all():
        createbattlelog(member.tag, url, headers)

    """ Update ELO """
    updateelofcn()