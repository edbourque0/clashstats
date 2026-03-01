from .models import BattleLogs, Members


def update_elo():
    """
    Updates ELO rankings for all battles that have not yet had their ELOs calculated.

    Reads unprocessed battles chronologically and maintains an in-memory ELO dict
    so each battle uses the most recent computed values rather than stale queryset
    values. Writes all ELO changes back to the DB in a single bulk_update call,
    and marks all processed battles as elocalculated in a second bulk_update.
    """
    # select_related avoids 4 FK-lookup queries per battle iteration
    battles_qs = (
        BattleLogs.objects
        .filter(elocalculated=False)
        .select_related("winner1", "winner2", "loser1", "loser2")
        .order_by("battleTime")
    )

    battles_list = list(battles_qs)
    if not battles_list:
        return

    # Collect all participant tags to seed the in-memory ELO dict from the DB
    participant_tags = set()
    for battle in battles_list:
        participant_tags.update([
            battle.winner1_id,
            battle.winner2_id,
            battle.loser1_id,
            battle.loser2_id,
        ])

    current_elo = {
        m.tag: float(m.elo)
        for m in Members.objects.filter(tag__in=participant_tags)
    }

    k = 32

    for battle in battles_list:
        w1_tag = battle.winner1_id
        w2_tag = battle.winner2_id
        l1_tag = battle.loser1_id
        l2_tag = battle.loser2_id

        w1_elo = current_elo.get(w1_tag, 1000.0)
        w2_elo = current_elo.get(w2_tag, 1000.0)
        l1_elo = current_elo.get(l1_tag, 1000.0)
        l2_elo = current_elo.get(l2_tag, 1000.0)

        winners_elo = (w1_elo + w2_elo) / 2
        losers_elo  = (l1_elo + l2_elo) / 2

        winners_expected = 1 / (1 + 10 ** ((losers_elo  - winners_elo) / 400))
        losers_expected  = 1 / (1 + 10 ** ((winners_elo - losers_elo)  / 400))

        # Write back to in-memory dict immediately so subsequent battles
        # involving the same player use the up-to-date value
        current_elo[w1_tag] = w1_elo + k * (1 - winners_expected)
        current_elo[w2_tag] = w2_elo + k * (1 - winners_expected)
        current_elo[l1_tag] = l1_elo + k * (0 - losers_expected)
        current_elo[l2_tag] = l2_elo + k * (0 - losers_expected)

    # Bulk-write updated ELOs — one UPDATE statement instead of 4 per battle
    members_to_update = list(Members.objects.filter(tag__in=current_elo.keys()))
    for m in members_to_update:
        m.elo = int(round(current_elo[m.tag]))
    Members.objects.bulk_update(members_to_update, ["elo"])

    # Bulk-mark all processed battles as calculated — one UPDATE statement
    BattleLogs.objects.filter(
        id__in=[b.id for b in battles_list]
    ).update(elocalculated=True)
