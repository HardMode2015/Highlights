import json
import time
from datetime import datetime

import dateparser
import re

import nltk
import requests
from bs4 import BeautifulSoup

from fb_bot.highlight_fetchers import fetcher_footyroom
from fb_bot.highlight_fetchers.info import providers, sources
from fb_bot.highlight_fetchers.utils.Highlight import Highlight
from fb_bot.highlight_fetchers.utils.link_formatter import format_dailymotion_link, format_streamable_link, format_link
from fb_bot.highlight_score_fetcher import fetcher_score_ourmatch

ROOT_URL = 'http://ourmatch.net/'
PAGELET_EXTENSION = 'page/'


class OurMatchHighlight(Highlight):

    def __init__(self, link, match_name, img_link, view_count, category, time_since_added):
        super().__init__(link, match_name, img_link, view_count, category, time_since_added, [])

    def get_match_info(self, match):
        match = match.split('Highlights')[0].strip()

        match_split = match.split()
        middle_index = match_split.index('vs')

        def join(l):
            return " ".join(l)

        team1 = join(match_split[:middle_index])
        score1 = -1
        team2 = join(match_split[middle_index + 1:])
        score2 = -1

        return team1, score1, team2, score2

    def set_score(self, score1, score2):
        self.score1 = score1
        self.score2 = score2

    def set_goal_data(self, goal_data):
        self.goal_data = goal_data

    def get_source(self):
        return sources.OUR_MATCH


def fetch_highlights(num_pagelet=3, max_days_ago=7):
    """
    Fetch all the possible highlights available on ourmatch.net given a number of pagelet to look at
    (33 highlights per pagelet)

    :param num_pagelet: number of pagelet to consider
    :param max_days_ago: max age of a highlight (after this age, we don't consider the highlight)
    :return: the latests highlights available on ourmatch.net
    """

    highlights = []

    for pagelet_num in range(num_pagelet):
        highlights += _fetch_pagelet_highlights(pagelet_num + 1, max_days_ago)

    return highlights


def _fetch_pagelet_highlights(pagelet_num, max_days_ago):
    highlights = []

    page = requests.get(ROOT_URL + PAGELET_EXTENSION + str(pagelet_num))
    soup = BeautifulSoup(page.content, 'html.parser')

    # Extract videos
    for vid in soup.find_all(class_='vidthumb'):
        thumb = vid.find(class_='thumb')

        if not thumb:
            continue

        link = thumb.find('a')

        # Extract match name
        match_name = str(link.get('title'))

        if not 'vs' in match_name:
            # Check that the highlight is for a match
            continue

        # Extract view count
        video_info = vid.find(class_="count")
        view_count = 0

        if video_info:
            count = video_info.get_text()
            view_count = int(float(count.replace('K', '')) * 1000) if 'K' in count else count

        # Extract category
        info = vid.find(class_='flecha')

        if not info:
            continue

        category = str(info.get_text())

        # Extract time since video added
        date = vid.find(class_='time')

        if not date:
            continue

        now = datetime.now()

        time_since_added = str(date.get_text())
        time_since_added_date = dateparser.parse(time_since_added).replace(hour=now.hour, minute=now.minute)
        time_since_added = str(time_since_added_date)

        # If error occur while parsing date, skip
        # TODO: handle case where date malformed (special string field)
        if not time_since_added_date:
            continue

        if not fetcher_footyroom.is_recent(time_since_added_date, max_days_ago):
            continue

        # Extract image link
        image = thumb.find('img')

        if not image:
            continue

        img_link = str(image.get('src'))

        # Extract link
        link = str(link.get('href'))

        if not _is_valid_link(link):
            continue

        # Get highlight page HTML
        page = requests.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')

        video_links = _get_video_links(soup)

        if not video_links:
            continue

        score = _get_match_score(soup)

        # try:
        goal_data = fetcher_score_ourmatch.get_goal_data(soup)
        # except Exception:
        #     goal_data = []

        # Add multiple video links
        for v in video_links:
            h = OurMatchHighlight(v, match_name, img_link, view_count, category, time_since_added)
            h.set_goal_data(goal_data)

            if score:
                h.set_score(score[0], score[1])

            highlights.append(h)

    return highlights


def _is_valid_link(link):
    if not isinstance(link, str):
        return False

    # clean the URLS
    link = link.strip()

    # check if it is a football Match highlight video
    return link.startswith("http://ourmatch.net/videos/")


def _get_video_links(soup):
    video_links = []

    for script in soup.find_all('script'):
        script_text = script.text

        if 'var video_contents =' in script_text:
            regex = "src=\"(.*?)\""
            videos = re.compile(regex, 0).findall(script_text)

            regex = "\'type\':\'(.*?)\'"
            types = re.compile(regex, 0).findall(script_text)

            for i in range(len(types)):

                for accepted in ['extended highlights', 'highlights', 'short', 'alternative player', 'short highlights']:
                    # Do distance to be more robust against site typing errors
                    if nltk.edit_distance(types[i].lower(), accepted) <= 2:

                        video = videos[i]
                        video_link = ''

                        if providers.DAILYMOTION in video:
                            video_link = format_dailymotion_link(video)

                        elif providers.STREAMABLE in video:
                            video_link = format_streamable_link(video)

                        elif providers.OK_RU in video:
                            video_link = format_link(video)

                        elif providers.MATCHAT_ONLINE in video:
                            video_link = format_link(video)

                        elif providers.CONTENT_VENTURES in video:
                            video_link = video

                        # Add link if known provider
                        if video_link:
                            video_links.append(video_link)

    return video_links


def _get_match_score(soup):
    home_score = soup.find(class_='home-score spoiler').get_text()
    away_score = soup.find(class_='away-score spoiler').get_text()

    return home_score, away_score


if __name__ == "__main__":

    print("\nFetch highlights ------------------------------ \n")

    start_time = time.time()
    highlights = fetch_highlights(num_pagelet=4, max_days_ago=40)

    for highlight in highlights:
        print(highlight)

    print("Number of highlights: " + str(len(highlights)))
    print("Time taken: " + str(round(time.time() - start_time, 2)) + "s")
