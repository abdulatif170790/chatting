#!/usr/bin/env python

from os import environ
from time import sleep
from json import loads
from datetime import datetime
from traceback import format_exc

import requests


FB_GROUP_FEED_URL = "https://graph.facebook.com/v2.5/%s/feed/?access_token=%s&since=%s&limit=1000"
FB_POST_URL = "https://www.facebook.com/groups/maslahat.uz/permalink/%s/"
TG_SEND_MSG_URL = "https://api.telegram.org/bot%s/sendMessage"


def get_date():
    return datetime.utcnow().strftime("%Y-%m-%d")


def tg_send_msg(tg_bot_access_token,
                tg_channel_id,
                fb_post):

    url = TG_SEND_MSG_URL % tg_bot_access_token

    fb_post_id = fb_post["id"]
    fb_post_msg = fb_post["data"]["message"]

    fb_post_url = FB_POST_URL % str(fb_post_id)
    msg = "%s\n\n%s" % (fb_post_msg,
                        fb_post_url)
    
    requests.post(url=url,
                  data={'chat_id': tg_channel_id,
                        'text': msg})

    return int(fb_post_id)


def fb_get_new_post_ids_from_feed(fb_app_access_token,
                                  fb_group_id,
                                  fb_last_post_id):

    url = FB_GROUP_FEED_URL % (fb_group_id,
                               fb_app_access_token,
                               get_date())

    response = requests.get(url)
    json_response = loads(response.content)

    posts = []

    if "data" in json_response and len(json_response["data"]) > 0:
        for post in json_response["data"]:
            post_id = int(post["id"].split("_")[1])

            if fb_last_post_id < post_id:
                posts.append({"id": post_id,
                              "data": post})

        posts = sorted(posts, key=lambda k: k["id"], reverse=True)

    return posts


def main(fb_app_access_token,
         tg_bot_access_token,
         fb_group_id,
         tg_channel_id,
         fb_last_post_id):

    error_sleep_time = 30
    sleep_time = 10
    delta_time = 5

    max_sleep_time = 120
    min_sleep_time = 10

    while True:
        post_ids = []
        try:
            reversed_posts = fb_get_new_post_ids_from_feed(fb_app_access_token,
                                                           fb_group_id,
                                                           fb_last_post_id)
            # Fetching FB group post with polling time management
            if len(reversed_posts) == 0:
                sleep_time += delta_time
                if sleep_time > max_sleep_time:
                    sleep_time = max_sleep_time
            else:
                sleep_time -= delta_time
                if sleep_time < min_sleep_time:
                    sleep_time = min_sleep_time

                for post in reversed_posts:
                    post_id = tg_send_msg(tg_bot_access_token,
                                          tg_channel_id,
                                          post)
                    post_ids.append(post_id)
                fb_last_post_id = post_ids[-1]

        except:
            sleep_time = error_sleep_time
            tb = format_exc()
            print "=" * 80
            print "[0002]: Error"
        else:
            tb = "\n".join(["SEND POST: %s" % str(_id) for _id in post_ids])
        finally:
            print "=" * 80
            print tb
            
        sleep(sleep_time)


if __name__ == "__main__":

    if "FACEBOOK_APP_ACCESS_TOKEN" in environ and \
       "TELEGRAM_BOT_ACCESS_TOKEN" in environ and \
       "FACEBOOK_GROUP_ID" in environ and \
       "TELEGRAM_CHANNEL_ID" in environ and \
       "FACEBOOK_LAST_POST_ID" in environ:

        fb_app_access_token = environ["FACEBOOK_APP_ACCESS_TOKEN"]
        tg_bot_access_token = environ["TELEGRAM_BOT_ACCESS_TOKEN"]
        fb_group_id = environ["FACEBOOK_GROUP_ID"]
        tg_channel_id = environ["TELEGRAM_CHANNEL_ID"]
        fb_last_post_id = environ["FACEBOOK_LAST_POST_ID"]

        main(fb_app_access_token,
             tg_bot_access_token,
             fb_group_id,
             tg_channel_id,
             fb_last_post_id)
    else:
        print "[0001]: One of environment variables not given."
