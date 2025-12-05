from .models import Members, Refresh, Clans
from .updateelo import update_elo
from .clan import create_clan
from .member import create_members
from .battlelog import create_battlelog


def refresh_clan(clan_tag, url, headers, source="api"):
    """
    Handles the refreshing of clan data, clan member details, and their battlelogs
    by making API requests. This function is primarily triggered by a POST request
    and processes the clan information using the provided clantag.

    :param clan_tag:
    :param url:
    :param headers:
    :type request: HttpRequest
    :return: JSON response indicating success or failure of the operation
    :rtype: JsonResponse
    """
    create_clan(clan_tag, url, headers)
    create_members(clan_tag, url, headers)

    for member in Members.objects.select_related("clanTag").all():
        create_battlelog(member.tag, url, headers)

    update_elo()
    Refresh.objects.create(clanTag=Clans.objects.get(tag=clan_tag), source=source)
