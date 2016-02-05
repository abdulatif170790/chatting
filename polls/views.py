from datetime import datetime
from json import loads
from os import environ
from time import sleep
from traceback import format_exc

import requests
from django.http import HttpResponse

FB_GROUP_FEED_URL = "https://graph.facebook.com/%s/feed/?access_token=%s&limit=2"
# FB_POST_URL = "https://www.facebook.com/groups/maslahat.uz/permalink/%s/"
FB_POST_URL = "https://www.facebook.com/1026639197392218/posts/%s"
TG_SEND_MSG_URL = "https://api.telegram.org/bot%s/sendMessage"


def index(request):
    if "FACEBOOK_API" in environ and \
                    "BOT_API" in environ and \
                    "FACEBOOK_ID" in environ and \
                    "TG_CHANNEL_ID" in environ and \
                    "LAST_POST_ID" in environ:

        fb_app_access_token = environ["FACEBOOK_API"]
        tg_bot_access_token = environ["BOT_API"]
        fb_group_id = environ["FACEBOOK_ID"]
        tg_channel_id = environ["TG_CHANNEL_ID"]
        fb_last_post_id = environ["LAST_POST_ID"]

        main(fb_app_access_token,
             tg_bot_access_token,
             fb_group_id,
             tg_channel_id,
             fb_last_post_id)

        print "SUCCESSFULLY"
    else:
        print "[0001]: One of environment variables not given."
    return HttpResponse("Salom dunyo!")


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
    # print "message"; print msg
    requests.post(url=url,
                  data={'chat_id': tg_channel_id,
                        'text': msg})

    return int(fb_post_id)


def fb_get_new_post_ids_from_feed(fb_app_access_token,
                                  fb_group_id,
                                  fb_last_post_id):
    url = FB_GROUP_FEED_URL % (fb_group_id,
                               fb_app_access_token)
    response = requests.get(url)
    json_response = loads(response.content)
    # print json_response
    posts = []

    if "data" in json_response and len(json_response["data"]) > 0:
        # print "true"
        for post in json_response["data"]:
            # print "post_id: " + post["id"]

            post_id = int(post["id"].split("_")[1])
            print "id: " + str(post_id) + "  _  last_id: " + str(fb_last_post_id)

            if fb_last_post_id < post_id:
                posts.append({"id": post_id,
                              "data": post})

        posts = sorted(posts, key=lambda k: k["id"], reverse=True)
    else:
        print "false"
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
                print "reversed_post = 0"
                sleep_time += delta_time
                if sleep_time > max_sleep_time:
                    sleep_time = max_sleep_time
            else:
                print "reversed_post > 0"
                sleep_time -= delta_time
                if sleep_time < min_sleep_time:
                    sleep_time = min_sleep_time

                for post in reversed_posts:
                    print "----"
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


