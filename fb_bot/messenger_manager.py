import json
from urllib.parse import quote

import highlights.settings
import highlights.settings
from fb_bot import client
from fb_bot.logger import logger
from fb_bot.messages import *
from fb_bot.model_managers import latest_highlight_manager, football_team_manager, user_manager
from highlights import settings

ACCESS_TOKEN = highlights.settings.get_env_var('MESSENGER_ACCESS_TOKEN')

MAX_QUICK_REPLIES = 10


### MESSAGES ###

def send_help_message(fb_id):
    return send_facebook_message(fb_id, create_message(HELP_MESSAGE))


def send_thank_you_message(fb_id):
    return send_facebook_message(fb_id, create_message(THANK_YOU))


def send_cancel_message(fb_id):
    return send_facebook_message(fb_id, create_message(CANCEL_MESSAGE))


def send_done_message(fb_id):
    return send_facebook_message(fb_id, create_message(DONE_MESSAGE))


def send_search_highlights_message(fb_id):
    return send_facebook_message(fb_id, create_message(SEARCH_HIGHLIGHTS_MESSAGE))


def send_notification_message(fb_id, teams):
    formatted_teams = ""
    quick_reply_buttons = [ADD_TEAM_BUTTON, REMOVE_TEAM_BUTTON, DONE_TEAM_BUTTON]

    if len(teams) == 0:
        formatted_teams = NO_TEAM_REGISTERED_MESSAGE
        quick_reply_buttons.remove(REMOVE_TEAM_BUTTON)
    elif len(teams) == MAX_QUICK_REPLIES:
        quick_reply_buttons.remove(ADD_TEAM_BUTTON)

    for i in range(len(teams)):
        if i > 0:
            formatted_teams += "\n"

        formatted_teams += "-> {}".format(teams[i])

    return send_facebook_message(
        fb_id, create_quick_text_reply_message(NOTIFICATION_MESSAGE.format(formatted_teams), quick_reply_buttons))


def send_add_team_message(fb_id):
    return send_facebook_message(fb_id, create_message(ADD_TEAM_MESSAGE))


def send_delete_team_message(fb_id, teams):
    return send_facebook_message(fb_id, create_quick_text_reply_message(DELETE_TEAM_MESSAGE, teams + [CANCEL_BUTTON]))


def send_recommended_team_message(fb_id, recommended):
    return send_facebook_message(fb_id, create_quick_text_reply_message(TEAM_RECOMMEND_MESSAGE, recommended[:9] + [OTHER_BUTTON, CANCEL_BUTTON]))


def send_team_not_found_message(fb_id):
    return send_facebook_message(fb_id, create_quick_text_reply_message(TEAM_NOT_FOUND_MESSAGE, [TRY_AGAIN_BUTTON, CANCEL_BUTTON]))


def send_team_added_message(fb_id, success, team):
    if success:
        return send_facebook_message(fb_id, create_message(TEAM_ADDED_SUCCESS_MESSAGE.format(team)))
    else:
        return send_facebook_message(fb_id, create_message(TEAM_ADDED_FAIL_MESSAGE.format(team)))


def send_team_to_delete_not_found_message(fb_id, teams):
    return send_facebook_message(fb_id, create_quick_text_reply_message(DELETE_TEAM_NOT_FOUND_MESSAGE, teams + [CANCEL_BUTTON]))


def send_team_deleted_message(fb_id, teams):
    return send_facebook_message(fb_id, create_message(TEAM_DELETED_MESSAGE.format(teams)))


def send_getting_started_message(fb_id, user_name):
    return send_facebook_message(fb_id, create_message(GET_STARTED_MESSAGE.format(user_name)))


def send_getting_started_message_2(fb_id):
    return send_facebook_message(fb_id, create_message(GET_STARTED_MESSAGE_2))


def send_error_message(fb_id):
    return send_facebook_message(fb_id, create_message(ERROR_MESSAGE))


def send_highlight_message_for_team(fb_id, team):
    return send_facebook_message(fb_id, get_highlights_for_team(fb_id, team))


# For TUTORIAL

def send_tutorial_message(fb_id, team):
    return send_facebook_message(fb_id, create_message(TUTORIAL_MESSAGE.format(team)))


def send_recommended_team_tutorial_message(fb_id, recommended):
    return send_facebook_message(fb_id, create_quick_text_reply_message(TEAM_RECOMMEND_MESSAGE, recommended[:9] + [OTHER_BUTTON]))


def send_team_not_found_tutorial_message(fb_id):
    return send_facebook_message(fb_id, create_message(TEAM_NOT_FOUND_MESSAGE))


# FIXME: duplication with real search
def send_tutorial_highlight(fb_id, team):
    highlights = latest_highlight_manager.get_highlights_for_team(team)

    if highlights == []:
        # Case no highlight found for the team, use example such as PSG, Barcelona, Real Madrid
        highlights = latest_highlight_manager.get_highlights_for_team('psg') \
                     + latest_highlight_manager.get_highlights_for_team('barcelona') \
                     + latest_highlight_manager.get_highlights_for_team('real madrid')

    # Eliminate duplicates
    highlights = latest_highlight_manager.get_unique_highlights(highlights)

    # Order highlights by date and take the first one
    highlight = sorted(highlights, key=lambda h: h.get_parsed_time_since_added(), reverse=True)[0]

    return send_facebook_message(fb_id, create_generic_attachment(highlights_to_json(fb_id, [highlight])))


# For scheduler
def send_highlight_messages(fb_ids, highlight_models):
    attachments = [create_generic_attachment(highlights_to_json(fb_id, highlight_models)) for fb_id in fb_ids]
    return send_batch_facebook_message(fb_ids, attachments)


def send_highlight_for_team_messages(fb_ids, team_name=None):
    messages = []

    for id in fb_ids:
        user_name = user_manager.get_user(id).first_name
        message = NEW_HIGHLIGHT_TEAM_MESSAGE.format(user_name, team_name) if team_name else NEW_HIGHLIGHT_TEAMS_MESSAGE.format(user_name)
        messages.append(create_message(message))

    return send_batch_facebook_message(fb_ids, messages)


### MAIN METHOD ###

def send_batch_facebook_message(fb_ids, messages):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=' + ACCESS_TOKEN
    response_msgs = []

    for i in range(len(fb_ids)):
        response_msgs.append(json.dumps(
            {
                "recipient": {
                    "id": fb_ids[i]
                },
                "message": messages[i]
            })
        )

    if not highlights.settings.DEBUG:
        client.send_fb_messages_async(post_message_url, response_msgs)
    else:
        logger.log(response_msgs)

    return response_msgs


def send_facebook_message(fb_id, message):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=' + ACCESS_TOKEN
    response_msg = json.dumps(
        {
            "recipient": {
                "id": fb_id
            },
            "message": message
        })

    if not highlights.settings.DEBUG:
        client.send_fb_message(post_message_url, response_msg)
    else:
        logger.log(response_msg)

    return response_msg


def send_typing(fb_id):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=' + ACCESS_TOKEN
    response_msg = json.dumps(
        {
            "recipient": {
                "id": fb_id
            },
            "sender_action": "typing_on"
        })

    if not highlights.settings.DEBUG:
        client.send_fb_message(post_message_url, response_msg)


#
# Highlights getters
#

def has_highlight_for_team(team):
    return latest_highlight_manager.get_highlights_for_team(team)


# FIXME: code duplicated for tutorial
def get_highlights_for_team(fb_id, team, highlight_count=10):
    highlights = latest_highlight_manager.get_highlights_for_team(team)

    if highlights == []:
        # Case no highlight found for the team
        return create_quick_text_reply_message(NO_HIGHLIGHTS_MESSAGE, [SEARCH_AGAIN_HIGHLIGHTS_BUTTON,
                                                                       HELP_BUTTON,
                                                                       CANCEL_BUTTON])

    if not highlights:
        # Case no team name matched
        similar_team_names = football_team_manager.similar_football_team_names(team)
        similar_team_names = [team_name.title() for team_name in similar_team_names]

        # Check if name of team was not properly written
        if similar_team_names:
            return create_quick_text_reply_message(NO_MATCH_FOUND_TEAM_RECOMMENDATION, similar_team_names[:9]
                                                   + [HELP_BUTTON,
                                                      CANCEL_BUTTON])
        else:
            return create_quick_text_reply_message(NO_MATCH_FOUND, [SEARCH_AGAIN_HIGHLIGHTS_BUTTON,
                                                                    HELP_BUTTON,
                                                                    CANCEL_BUTTON])

    # Eliminate duplicates
    highlights = latest_highlight_manager.get_unique_highlights(highlights)

    # Order highlights by date and take the first 10
    highlights = sorted(highlights, key=lambda h: h.get_parsed_time_since_added(), reverse=True)[:highlight_count]

    return create_generic_attachment(highlights_to_json(fb_id, highlights))


#
# Highlights to json
#


def highlights_to_json(fb_id, highlight_models):
    return list(map(lambda h: highlight_to_json(fb_id, h), highlight_models))


def highlight_to_json(fb_id, highlight_model):
    return {
        "title": highlight_model.get_match_name(),
        "image_url": highlight_model.img_link,
        "subtitle": highlight_model.get_formatted_date() + ' - ' + highlight_model.category.title(),
        "default_action": {
            "type": "web_url",
            "url": create_tracking_link(fb_id, highlight_model),
            "messenger_extensions": "false",
            "webview_height_ratio": "full"
        }
    }


# Essential method for link creation and redirection to website (and tracking)
def create_tracking_link(fb_id, highlight_model):
    # Form correct url to redirect to server
    link = settings.BASE_URL + "/highlight?team1={}&score1={}&team2={}&score2={}&date={}&user_id=".format(
        quote(highlight_model.team1.name.lower()),
        highlight_model.score1,
        quote(highlight_model.team2.name.lower()),
        highlight_model.score2,
        highlight_model.get_parsed_time_since_added().date()
    )

    tracking_link = link + str(fb_id)

    return tracking_link


#
# JSON message formatter
#

def create_message(text):
    return {
        "text": text
    }


def create_quick_text_reply_message(text, quick_replies):
    formatted_quick_replies = []

    for quick_reply in quick_replies:
        formatted_quick_replies.append({
            "content_type": "text",
            "title": quick_reply,
            "payload": "NO_PAYLOAD"
        })

    return {
        "text": text,
        "quick_replies": formatted_quick_replies
    }


def create_list_attachement(elements):
    return {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "list",
                "top_element_style": "compact",
                "elements": elements
            }
        }
    }


def create_generic_attachment(elements):
    return {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": elements
            }
        }
    }
