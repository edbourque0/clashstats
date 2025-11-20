# ClashStats

A Django-based REST API for tracking and analyzing Clash Royale clan statistics, member performance, and battle logs with an ELO rating system for 2v2 battles.

## Features

- **Clan Management**: Search, add, and track Clash Royale clans
- **Member Tracking**: Monitor clan members' statistics and performance
- **Battle Log Analysis**: Track 2v2 battle outcomes
- **ELO Rating System**: Calculate and update player ELO ratings based on battle results
- **Auto-refresh**: Automatically sync data with Clash Royale API

## Requirements

- Python 3.13.2
- PostgreSQL
- Clash Royale API Key ([Get one here](https://developer.clashroyale.com/))

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/edbourque0/clashstats.git
cd clashstats
```

### 2. Create and activate virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install django psycopg2 python-dotenv requests
```

### 4. Configure environment variables

Copy `prod.env.example` to `prod.env` and fill in your credentials:

```bash
cp prod.env.example prod.env
```

Edit `prod.env`:

```env
CLASH_API_KEY=your_clash_royale_api_key_here
DB_NAME=clashstats
DB_USER=postgres
DB_PASS=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Set up PostgreSQL database

```bash
createdb clashstats
```

### 6. Run migrations

```bash
python manage.py migrate
```

### 7. Start the development server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Search Clan

Search for clans by name using the Clash Royale API.

- **Endpoint**: `POST /api/v1/clan/search`
- **Parameters**:
  - `name` (string, required): Clan name to search

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/clan/search \
  -d "name=YourClanName"
```

### Add Clan

Add a clan to the database.

- **Endpoint**: `POST /api/v1/clan`
- **Parameters**:
  - `clantag` (string, required): Clan tag (e.g., `#G9JVLC2C`)

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/clan \
  -d "clantag=#G9JVLC2C"
```

### Add Members

Fetch and add all members of a clan to the database.

- **Endpoint**: `POST /api/v1/members`
- **Parameters**:
  - `clantag` (string, required): Clan tag

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/members \
  -d "clantag=#G9JVLC2C"
```

### Add Battle Log

Add battle logs for a specific player.

- **Endpoint**: `POST /api/v1/battlelog`
- **Parameters**:
  - `playertag` (string, required): Player tag (e.g., `#CJG89UPQR`)

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/battlelog \
  -d "playertag=#CJG89UPQR"
```

**Note**: Only stores 2v2 battles of type `clanMate2v2`

### Refresh Clan

Refresh all data for a clan (clan info, members, and battle logs).

- **Endpoint**: `POST /api/v1/refreshclan`
- **Parameters**:
  - `clantag` (string, required): Clan tag

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/refreshclan \
  -d "clantag=#G9JVLC2C"
```

### Update ELO Ratings

Calculate and update ELO ratings for all members based on battle results.

- **Endpoint**: `GET /api/v1/updateelo`

**Example**:
```bash
curl http://localhost:8000/api/v1/updateelo
```

**ELO Algorithm**:
- Starting ELO: 1000
- K-factor: 20
- Formula: `New ELO = Old ELO + K × (Actual Score - Expected Score)`
- Team average ELO is used for calculations

## Data Models

### Clan

- `tag` (Primary Key): Clan tag
- `name`: Clan name
- `type`: Clan type (open, inviteOnly, closed)
- `badgeId`: Badge identifier
- `location`: Country code
- `donationsPerWeek`: Weekly donation count
- `members`: Number of members

### Member

- `tag` (Primary Key): Player tag
- `clanTag` (Foreign Key): Associated clan
- `name`: Player name
- `role`: Role in clan (member, elder, coLeader, leader)
- `lastSeen`: Last seen timestamp
- `expLevel`: Experience level
- `trophies`: Current trophies
- `clanRank`: Rank in clan
- `donations`: Donations given
- `donationsReceived`: Donations received
- `elo`: ELO rating (default: 1000)

### BattleLog

- `id` (Primary Key): SHA-256 hash of battle data
- `type`: Battle type
- `battleTime`: When the battle occurred
- `gameMode`: Game mode name
- `winner1`, `winner2` (Foreign Keys): Winning team members
- `loser1`, `loser2` (Foreign Keys): Losing team members
- `elocalculated`: Whether ELO has been calculated for this battle

## Usage Example

1. **Add a clan to track**:
```bash
curl -X POST http://localhost:8000/api/v1/clan \
  -d "clantag=#G9JVLC2C"
```

2. **Add clan members**:
```bash
curl -X POST http://localhost:8000/api/v1/members \
  -d "clantag=#G9JVLC2C"
```

3. **Fetch battle logs for all members**:
```bash
# This is done automatically in refreshclan, or manually per player
curl -X POST http://localhost:8000/api/v1/battlelog \
  -d "playertag=#CJG89UPQR"
```

4. **Calculate ELO ratings**:
```bash
curl http://localhost:8000/api/v1/updateelo
```

5. **Or do everything at once**:
```bash
curl -X POST http://localhost:8000/api/v1/refreshclan \
  -d "clantag=#G9JVLC2C"
curl http://localhost:8000/api/v1/updateelo
```

## Project Structure

```
clashstats/
├── clashstats/              # Main Django app
│   ├── migrations/          # Database migrations
│   ├── models.py            # Data models
│   ├── views.py             # API endpoints
│   └── urls.py              # URL routing
├── clashstats_v2/           # Project settings
│   ├── settings.py          # Django settings
│   └── generateApiKey.py    # API key generator utility
├── templates/               # HTML templates
├── prod.env.example         # Environment variables template
├── manage.py                # Django management script
└── README.md                # This file
```

## Development

### Running Tests

```bash
python manage.py test
```

### Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## Security Notes

- **CSRF**: CSRF protection is disabled for API endpoints (decorated with `@csrf_exempt`)
- **Authentication**: No authentication is currently implemented
- **Production**: Change `DEBUG = False` and update `SECRET_KEY` before deploying
- **API Key**: Keep your Clash Royale API key secure in `prod.env`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License

## Support

For issues or questions, please open an issue on the [GitHub repository](https://github.com/edbourque0/clashstats).

## Acknowledgments

- Powered by [Clash Royale API](https://developer.clashroyale.com/)
- Built with Django and PostgreSQL