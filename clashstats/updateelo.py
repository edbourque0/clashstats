from .models import BattleLogs, Members


def update_elo():
    """
    Updates ELO rankings for all battles that have not yet had their ELOs calculated.

    This function retrieves all BattleLogs, sorts them by battle time, and iterates
    through each battle that has not been marked as ELO-calculated. For each battle,
    it computes and updates the ELO ratings of the winners and losers based on the
    ELO calculation formula. Once the ratings are updated, the battle is flagged as
    ELO-calculated. The updates are applied to the Members database. If the request
    method is not GET, a response indicating the method is not allowed is returned.

    :type request: HttpRequest
    :return: JsonResponse indicating the success or failure of the operation.
    :rtype: JsonResponse
    """
    sorted_battles = BattleLogs.objects.all().order_by("battleTime")

    for battle in sorted_battles:
        if not battle.elocalculated:
            """Define common variables"""
            winners_elo = (battle.winner1.elo + battle.winner2.elo) / 2
            losers_elo = (battle.loser1.elo + battle.loser2.elo) / 2
            winners_expected = 1 / (1 + 10 ** ((losers_elo - winners_elo) / 400))
            losers_expected = 1 / (1 + 10 ** ((winners_elo - losers_elo) / 400))

            """ Compute and update ELO of winners """
            winner1_new_elo = battle.winner1.elo + 32 * (1 - winners_expected)
            winner2_new_elo = battle.winner2.elo + 32 * (1 - winners_expected)
            Members.objects.filter(tag=battle.winner1.tag).update(elo=winner1_new_elo)
            Members.objects.filter(tag=battle.winner2.tag).update(elo=winner2_new_elo)

            """ Compute and update ELO of losers """
            looser1_new_elo = battle.loser1.elo + 32 * (0 - losers_expected)
            looser2_new_elo = battle.loser2.elo + 32 * (0 - losers_expected)
            Members.objects.filter(tag=battle.loser1.tag).update(elo=looser1_new_elo)
            Members.objects.filter(tag=battle.loser2.tag).update(elo=looser2_new_elo)

            """ Mark battle as elo-calculated """
            BattleLogs.objects.filter(id=battle.id).update(elocalculated=True)
