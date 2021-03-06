from django.db.models import Q

from fb_bot.model_managers import football_team_manager, football_competition_manager
from fb_highlights.models import BlockedNotification


def add_blocked_competition_highlight(team, competition=None):
    team = football_team_manager.get_football_team(team)

    if competition:
        competition = football_competition_manager.get_football_competition(competition)

    BlockedNotification.objects.update_or_create(team=team,
                                                 competition=competition)


def is_highlight_for_competition_blocked(highlight_model):
    blocked_competitions = BlockedNotification.objects.filter(
        (
            Q(team=highlight_model.team1) |
            Q(team=highlight_model.team2)
        )
    )

    return [blocked for blocked in blocked_competitions if blocked.competition == highlight_model.category or not blocked.competition]