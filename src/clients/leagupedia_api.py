import os
from dotenv import load_dotenv
from mwrogue.esports_client import EsportsClient
from mwrogue.auth_credentials import AuthCredentials

from src.models import Player, Team

load_dotenv()


class LeaguepediaAPI():
    def __init__(self):
        username = os.getenv("LEAGUEPEDIA_USERNAME")
        bot_password = os.getenv("LEAGUEPEDIA_BOT_PASSWORD")

        if not username or not bot_password:
            print("Leaguepedia credentials are not set")

        credentials = AuthCredentials(username=username, password=bot_password)
        self._site = EsportsClient('lol', credentials=credentials)

    @staticmethod
    def _parse_bool(value: str | None) -> bool | None:
        if value == '1':
            return True
        elif value == '0':
            return False

        elif value == 'Yes':
            return True
        elif value == 'No':
            return False

        return None

    @staticmethod
    def _escape_sql(value: str) -> str:
        return value.replace("'", "''")

    def fetch_current_competitions(self) -> list[str]:
        response = self._site.cargo_client.query(
            tables='CurrentLeagues=CL',
            fields='CL.Event',
            group_by='CL.Event'
        )

        return [event['Event'] for event in response]

    def fetch_competition_team_names(self, competition: str) -> list[str]:
        response = self._site.cargo_client.query(
            tables="CurrentLeagues=CL, TournamentRosters=TR",
            fields="TR.Team",
            where=f"CL.Event='{competition}' OR CL.OverviewPage='{competition}'",
            join_on="CL.OverviewPage=TR.OverviewPage",
            group_by="TR.Team"
        )

        return [team['Team'] for team in response]

    def fetch_teams_info(self, team_names: list[str]) -> list[Team]:
        if not team_names:
            return []

        escaped_names = [f"'{LeaguepediaAPI._escape_sql(name)}'" for name in team_names]
        names_str = ", ".join(escaped_names)

        print('here', names_str)

        response = self._site.cargo_client.query(
            tables="Teams=T",
            fields="T.Name, T.OverviewPage, T.Short, T.Location, T.Region",
            where=f"T.Name IN ({names_str}) OR T.OverviewPage IN ({names_str})"
        )

        if not response:
            print(f"Failed to fetch teams: {team_names}")
            return []

        return [
            Team(
                name=r['Name'],
                overview_page=r['OverviewPage'],
                short=r.get('Short'),
                org_location=r.get('Location'),
                region=r.get('Region')
            )
            for r in response
        ]

    def fetch_competition_teams(self, competition: str) -> list[Team]:
        team_names = self.fetch_competition_team_names(competition)
        return self.fetch_teams_info(team_names)

    def fetch_team_roster(self, team: Team) -> None:
        if team is None:
            raise ValueError("Team cannot be None")

        if team.overview_page:
            team_name = team.overview_page

        else:
            team_name = team.name

        try:
            response = self._site.cargo_client.query(
                tables="PlayerRedirects=PR, Players=P",
                fields="P.ID, P.OverviewPage, P.Role, P.IsSubstitute",
                where=f"(P.Team = '{team_name}' OR P.Team2 = '{team_name}') AND P.Role IN ('Top', 'Jungle', 'Mid', 'Bot', 'Support') AND P.RoleLast HOLDS P.Role",
                join_on="PR.OverviewPage=P.OverviewPage",
                group_by="P.OverviewPage"
            )

        except Exception as e:
            print(f"Failed to fetch team roster for {team_name}: {e}")
            return

        players = [dict(player) for player in response]
        players = [Player(name=p['ID'],
                          overview_page=p['OverviewPage'],
                          role=p.get('Role'),
                          is_substitute=LeaguepediaAPI._parse_bool(p.get('IsSubstitute')))
                   for p in players]

        for p in players:
            team.assign_player(p)

    def fetch_teams_rosters(self, teams: list[Team]) -> None:
        if not teams:
            return

        team_names = []
        for team in teams:
            name = team.overview_page or team.name
            team_names.append(name.strip())

        escaped_names = [f"'{LeaguepediaAPI._escape_sql(name)}'" for name in team_names]
        names_str = ", ".join(escaped_names)

        try:
            response = self._site.cargo_client.query(
                tables="PlayerRedirects=PR, Players=P",
                fields="P.ID, P.OverviewPage, P.Team, P.Team2, P.Role, P.IsSubstitute",
                where=f"""
                    (P.Team IN ({names_str}) OR P.Team2 IN ({names_str}))
                    AND P.Role IN ('Top', 'Jungle', 'Mid', 'Bot', 'Support')
                    AND P.RoleLast HOLDS P.Role
                """,
                join_on="PR.OverviewPage=P.OverviewPage",
                group_by="P.OverviewPage"
            )
        except Exception as e:
            print(f"Failed to fetch rosters: {e}")
            return

        if not response:
            return

        team_map = {}
        for team in teams:
            team_map[team.overview_page or team.name] = team
            team_map[team.name] = team

        for p in response:
            player = Player(
                name=p['ID'],
                overview_page=p['OverviewPage'],
                role=p.get('Role'),
                is_substitute=LeaguepediaAPI._parse_bool(p.get('IsSubstitute'))
            )

            team = team_map.get(p['Team']) or team_map.get(p['Team2'])
            if team:
                team.assign_player(player)

    def fetch_player_lolpros_name(self, player) -> str | None:
        response = self._site.cargo_client.query(
            tables="Players=P, PlayerRedirects=PR",
            fields="P.Lolpros",
            join_on="PR.OverviewPage=P.OverviewPage",
            group_by="P.OverviewPage",
            where=f"P.Player='{player}'",
        )

        if response:
            lolpros_url = response[0]['Lolpros']
            lolpros_name = lolpros_url.rstrip('/').split('/')[-1]
            return lolpros_name

        else:
            return None

    def fetch_latest_roster(self, team_name: str) -> list[str]:
        response = self._site.cargo_client.query(
            tables="TournamentRosters=TR, CurrentLeagues=CL",
            fields="TR.RosterLinks",
            where=f"TR.Team='{team_name}'",
            join_on="CL.OverviewPage=TR.OverviewPage",
        )

        if not response:
            return []

        members_list = [r['RosterLinks'] for r in response]

        return members_list[0].split(';;')


if __name__ == "__main__":
    leaguepedia = LeaguepediaAPI()

    rift_names = leaguepedia.fetch_competition_team_names('Rift Legends 2026 Spring')
    print(rift_names)
    print(leaguepedia.fetch_teams_info(rift_names))

    print(leaguepedia.fetch_latest_roster('Bomba Team'))
    print(leaguepedia.fetch_tournament_roster('StormMedia Fajnie Mieć Skład', 'Rift Legends 2026 Spring'))
