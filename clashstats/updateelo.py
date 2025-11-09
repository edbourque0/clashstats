from .models import BattleLogs, Members

def updateelofcn():
    """
    Updates ELO rankings for all battles that have not yet had their ELOs calculated.

    This function retrieves all BattleLogs, sorts them by battle time, and iterates
    through each battle that has not been marked as ELO-calculated. For each battle,
    it computes and updates the ELO ratings of the winners and losers based on the
    ELO calculation formula. Once the ratings are updated, the battle is flagged as
    ELO-calculated. The updates are applied to the Members database. If the request
    method is not GET, a response indicating the method is not allowed is returned.

    :param request: HTTP request object containing details of the incoming request.
    :type request: HttpRequest
    :return: JsonResponse indicating the success or failure of the operation.
    :rtype: JsonResponse
    """
    sortedbattles = BattleLogs.objects.all().order_by('battleTime')

    for battle in sortedbattles:
        if not battle.elocalculated:
            """ Define common variables """
            winnerselo = (battle.winner1.elo + battle.winner2.elo) / 2
            loserselo = (battle.loser1.elo + battle.loser2.elo) / 2
            winnersexpectedscore = 1 / (1 + 10 ** ((loserselo - winnerselo) / 400))
            losersexpectedscore = 1 / (1 + 10 ** ((winnerselo - loserselo) / 400))

            """ Compute and update ELO of winners """
            w1newelo = battle.winner1.elo + 32 * (1 - winnersexpectedscore)
            w2newelo = battle.winner2.elo + 32 * (1 - winnersexpectedscore)
            Members.objects.filter(tag=battle.winner1.tag).update(elo=w1newelo)
            Members.objects.filter(tag=battle.winner2.tag).update(elo=w2newelo)

            """ Compute and update ELO of losers """
            l1newelo = battle.loser1.elo + 32 * (0 - losersexpectedscore)
            l2newelo = battle.loser2.elo + 32 * (0 - losersexpectedscore)
            Members.objects.filter(tag=battle.loser1.tag).update(elo=l1newelo)
            Members.objects.filter(tag=battle.loser2.tag).update(elo=l2newelo)

            """ Mark battle as elo-calculated """
            BattleLogs.objects.filter(id=battle.id).update(elocalculated=True)