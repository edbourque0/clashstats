from .models import Arena, GameMode, Clan, Card, Player, Battle


Arenas = Arena.objects.all().values()
Gamemodes = GameMode.objects.all().values()
Clans = Clan.objects.all().values()
Cards = Card.objects.all().values()
Players = Player.objects.all().values()
Battles = Battle.objects.all().values()

print(Battles.team.name)















# import requests


# APIKEY = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImQ0YmNiMzEzLTRmZjYtNDJhZC05YTRkLWY5YjU1YmU5NzhlZCIsImlhdCI6MTcxMjI2OTg2OCwic3ViIjoiZGV2ZWxvcGVyLzNkNjhmM2MyLWM4ZmItNDAyYy0zZTU4LTk0YjIzMGY1Y2IzZCIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyI3NC4xMi4xNjkuMjMwIl0sInR5cGUiOiJjbGllbnQifV19.-bksJLAGJNvzXkxR5rrDkzUVgxMDYC7OQFFhKDOvimXboDA1ggddmbVod8qREXbq4yCYp8adTXOtNUy1YCFhMg'
# headers = {
#     'Authorization': 'Bearer ' + APIKEY,
# }

# r = requests.get(f'https://api.clashroyale.com/v1/players/%23CJG89UPQR/battlelog', headers=headers)

# rawdata = r.json()

# for int, battle in enumerate(rawdata):
#     data = rawdata[int]
#     for int, opponent in enumerate(data['opponent']): 
#         print(data['opponent'][int]['clan'])
