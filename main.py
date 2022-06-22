import threading
import time

from subprocess import Popen
from dotenv import load_dotenv
from os import getenv, name
from reddit.subreddit import get_subreddit_threads
from utils.cleanup import cleanup
from utils.console import print_markdown, print_step
from video_creation.background import download_background, chop_background_video
from video_creation.final_video import make_final_video
from video_creation.screenshot_downloader import download_screenshots_of_reddit_posts
from video_creation.voices import save_text_to_mp3
from plyer import notification

VERSION = 2.1
print(
    """
██████╗ ███████╗██████╗ ██████╗ ██╗████████╗    ██╗   ██╗██╗██████╗ ███████╗ ██████╗     ███╗   ███╗ █████╗ ██╗  ██╗███████╗██████╗
██╔══██╗██╔════╝██╔══██╗██╔══██╗██║╚══██╔══╝    ██║   ██║██║██╔══██╗██╔════╝██╔═══██╗    ████╗ ████║██╔══██╗██║ ██╔╝██╔════╝██╔══██╗
██████╔╝█████╗  ██║  ██║██║  ██║██║   ██║       ██║   ██║██║██║  ██║█████╗  ██║   ██║    ██╔████╔██║███████║█████╔╝ █████╗  ██████╔╝
██╔══██╗██╔══╝  ██║  ██║██║  ██║██║   ██║       ╚██╗ ██╔╝██║██║  ██║██╔══╝  ██║   ██║    ██║╚██╔╝██║██╔══██║██╔═██╗ ██╔══╝  ██╔══██╗
██║  ██║███████╗██████╔╝██████╔╝██║   ██║        ╚████╔╝ ██║██████╔╝███████╗╚██████╔╝    ██║ ╚═╝ ██║██║  ██║██║  ██╗███████╗██║  ██║
╚═╝  ╚═╝╚══════╝╚═════╝ ╚═════╝ ╚═╝   ╚═╝         ╚═══╝  ╚═╝╚═════╝ ╚══════╝ ╚═════╝     ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
"""
)
load_dotenv()
# Modified by JasonLovesDoggo
print_markdown(
    "### Thanks for using this tool! [Feel free to contribute to this project on GitHub!](https://lewismenelaws.com) If you have any questions, feel free to reach out to me on Twitter or submit a GitHub issue. You can find solutions to many common problems in the [Documentation](https://luka-hietala.gitbook.io/documentation-for-the-reddit-bot/)"
)

time.sleep(1)

client_id = getenv("REDDIT_CLIENT_ID")
client_secret = getenv("REDDIT_CLIENT_SECRET")
username = getenv("REDDIT_USERNAME")
password = getenv("REDDIT_PASSWORD")
reddit2fa = getenv("REDDIT_2FA")


def main():
    cleanup()

    def get_obj():
        reddit_obj = get_subreddit_threads()
        return reddit_obj

    reddit_object = get_obj()
    length, number_of_comments = save_text_to_mp3(reddit_object)

    # Run in parallel
    t1 = threading.Thread(target=download_screenshots_of_reddit_posts, args=[reddit_object, number_of_comments])
    t2 = threading.Thread(target=chop_background_video, args=[length])

    t1.start()
    t2.start()
    t1.join()
    t2.join() #Waits before proceeding

    # download_background() # no need to call repeatedly
    make_final_video(number_of_comments, length)
    re_run()


def run_many(times):
    for x in range(times):
        x = x + 1
        print_step(
            f'on the {x}{("st" if x == 1 else ("nd" if x == 2 else ("rd" if x == 3 else "th")))} iteration of {times}'
        )  # correct 1st 2nd 3rd 4th 5th....
        main()
        Popen("cls" if name == "nt" else "clear", shell=True).wait()


def re_run():
    notification.notify(
        title="Done Rendering",
        message="Less goo",
        timeout=20
    )
    if input("Press enter to re-run, else exit > ").strip().casefold() == "":
        return main()
    return


if __name__ == "__main__":
    try:
        if getenv("TIMES_TO_RUN") and isinstance(int(getenv("TIMES_TO_RUN")), int):
            run_many(int(getenv("TIMES_TO_RUN")))
        else:
            main()
    except KeyboardInterrupt:
        print_markdown("## Clearing temp files")
        cleanup()
        exit()
