# ClashStats

A Django web app for tracking and analyzing Clash Royale 2v2 battle with an ELO rating system and weekly ELO scores.

## Project status

\- Active Django project that stores 2v2 battles, calculates ELO and records weekly ELO snapshots that become fixed after a week ends. Weekly snapshots are updated in\-place while the week is ongoing and locked once the week finishes.

## Key features

\- Clan management and member tracking.  
\- Clan 2v2 battle log ingestion.  
\- ELO rating system for 2v2: team average ELO used for match expectation.  
\- Weekly ELO snapshots: `WeeklyElo` model stores each player's ELO per week; entries are updated until the week ends, then marked fixed.  
\- Utilities for determining week start from any `datetime`.

## Requirements

\- Python 3.13.2  
\- PostgreSQL

# Docker compose installation:



## API endpoints (high level)

\- `POST /api/v1/clan/search` \- search clans by name.  
\- `POST /api/v1/clan` \- add a clan to track (parameter: `clantag`).  
\- `POST /api/v1/members` \- fetch and add/update clan members (parameter: `clantag`).  
\- `POST /api/v1/battlelog` \- add battle logs for a player (parameter: `playertag`). Only 2v2 clanMate2v2 battles are stored.  
\- `POST /api/v1/refreshclan` \- refresh clan, members, and battle logs.  
\- `GET /api/v1/updateelo` \- run full ELO recalculation across stored battles.  
\- `POST /api/v1/updateweeklyelo` \- update weekly ELO snapshots (updates ongoing week entries, fixes past weeks).  
\- `GET /api/v1/weeklyelo` \- query weekly ELO snapshots (filters: player, week_start).

## ELO algorithm

\- Starting ELO: 1000.  
\- K factor: 32.
\- Team ELOs are calculating using the average of each player

## Weekly ELO behavior

\- The `WeeklyElo` model records per\-player ELO for the week identified by its `week_start` (the start of the week datetime).  
\- While the current week is ongoing, the entry for that player's week is updated in\-place as new battles are processed.  
\- Once the week ends, entries are marked fixed and no longer auto\-updated.  
\- `WeeklyElo` may reference the `BattleLog` (or store `battleTime`) to associate updates with the correct battle timestamp.

## Data models (high level)

\- `Clan` \- basic clan info. See `clashstats/models.py`.  
\- `Member` \- player record with `elo` field (default 1000).  
\- `BattleLog` \- stores 2v2 battles with `battleTime`, participants (`winner1`, `winner2`, `loser1`, `loser2`), and `elocalculated` flag.  
\- `WeeklyElo` \- per\-player weekly snapshot: `player` (FK), `week_start` (datetime), `elo` (int), `is_fixed` (bool), optional relation to `BattleLog` or `battleTime`.

## Utilities

\- Helper to compute week start from a `datetime` (used to normalize week buckets). Implemented in utilities module and used by ELO updater and weekly snapshot updater.  
\- `update_elo` logic processes battles in chronological order; `update_weekly_elo` updates weekly snapshots and fixes weeks that have ended.

## Development

\- Project tested with `python manage.py test`.  
\- Use `PyCharm 2025.2.4` on Windows for development. Virtualenv workflows and run configurations are supported.  
\- Branching: current branch `clean-up`. Remotes: `main`, `edbourque0`.

## Notes

\- Keep your Clash Royale API key in `.env`.  
\- Weekly fixation logic: ensure server timezone and week boundary logic are consistent across deployments.

## Contributing

\- Fork, create a branch, commit, push, and open a PR against `master`.

## License

\- MIT
