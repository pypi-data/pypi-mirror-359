from typing import List
from sqlalchemy import select, update
from ATG.models import Player, Account
from ATG.api import get_account_by_riot_id

def link_pro(session, pro_name, soloq, RIOT_API, inactive=False, region="NA1"):
    try:
        player = session.execute(select(Player).where(Player.name == pro_name)).scalar_one()
    except:
        print(f"Unable to find associated player for {pro_name}")
        return
    name, tagline = soloq.split("#")
    details = get_account_by_riot_id(name, tagline, RIOT_API).json()
    new_acc = Account(puuid=details['puuid'], name=details['gameName'], tagline=details['tagLine'], region=region, player_id=player.id, skip_update = inactive)
    session.add(new_acc)
    try:
        session.commit()
        print(f"Linked {pro_name} with {name}#{tagline}")
    except:
        session.rollback()
        print(f"Account {details['gameName']}#{details['tagLine']} already linked")
def list_accounts(session, pro_name):
    try:
        player = session.execute(select(Player).where(Player.name == pro_name)).scalar_one()
    except:
        print(f"Unable to find associated player for {pro_name}")
        return
    print(["#".join(_) for _ in list(session.execute(select(Account.name, Account.tagline).where(Account.player_id == player.id)).all())])

def create_player(session, pro_name):
    player = session.execute(select(Player).where(Player.name == pro_name)).scalar_one_or_none()
    if player is not None:
        print(f"Player with name {player.name} already exists")
        return
    new_player = Player(name=pro_name)
    session.add(new_player)
    session.commit()
    print(f"Created new player {new_player.name} with id {new_player.id}")
