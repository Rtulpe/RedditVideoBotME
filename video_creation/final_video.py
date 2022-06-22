#!/usr/bin/env python3
import os
from os.path import exists

import ffmpeg
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    ImageClip,
    concatenate_videoclips,
    CompositeVideoClip,
)
from moviepy.video.io import ffmpeg_tools
from rich.console import Console

from reddit.subreddit import save_data

from utils.console import print_step, print_substep

console = Console()

W, H = 1080, 1920


def make_final_video(number_of_clips, length):
    opacity = os.getenv("OPACITY")

    print_step("Creating the final video 🎥")
    bg_in = ffmpeg.input("assets/temp/background.mp4")
    # todo implement bg_a = bg_in.audio
    bg_v = bg_in.video.scale(size='hd1080').crop(x=656, y=0, h=1080, w=608).scale(h=H, w=W)

    fg_a = ffmpeg.input("assets/temp/mp3/title.mp3").audio
    for i in range(number_of_clips):
        fg_a = ffmpeg.avfilters.concat(fg_a, ffmpeg.input(f"assets/temp/mp3/{i}.mp3").audio, v=0, a=1)

    final = bg_v.output(fg_a, 'assets/temp/prev.mp4', video_bitrate='8000k')
    final.run()

    prev_clip = VideoFileClip("assets/temp/prev.mp4")

    # todo switch to ffmpeg
    # Lenght approximation
    audio_clips = []
    audio_clips.insert(0, AudioFileClip("assets/temp/mp3/title.mp3"))
    for i in range(0, number_of_clips):
        audio_clips.append(AudioFileClip(f"assets/temp/mp3/{i}.mp3"))

    # Get sum of all clip lengths
    total_length = sum([clip.duration for clip in audio_clips])
    # round total_length to an integer
    int_total_length = round(total_length)
    # Output Length
    console.log(f"[bold green] Video Will Be: {int_total_length} Seconds Long")

    # add title to video
    image_clips = []
    # Gather all images
    if opacity is None or float(opacity) >= 1:  # opacity not set or is set to one OR MORE
        image_clips.insert(
            0,
            ImageClip("assets/temp/png/title.png")
            .set_duration(audio_clips[0].duration)
            .set_position("center")
            .resize(width=W - 100),
        )
    else:
        image_clips.insert(
            0,
            ImageClip("assets/temp/png/title.png")
            .set_duration(audio_clips[0].duration)
            .set_position("center")
            .resize(width=W - 100)
            .set_opacity(float(opacity)),
        )

    for i in range(0, number_of_clips):
        if opacity is None or float(opacity) >= 1:  # opacity not set or is set to one OR MORE
            image_clips.append(
                ImageClip(f"assets/temp/png/comment_{i}.png")
                .set_duration(audio_clips[i + 1].duration)
                .set_position("center")
                .resize(width=W - 100),
            )
        else:
            image_clips.append(
                ImageClip(f"assets/temp/png/comment_{i}.png")
                .set_duration(audio_clips[i + 1].duration)
                .set_position("center")
                .resize(width=W - 100)
                .set_opacity(float(opacity)),
            )

    image_concat = concatenate_videoclips(image_clips).set_position(("center", "center"))

    # Change bg sound with volumex
    final = CompositeVideoClip([prev_clip, image_concat])

    def get_video_title() -> str:
        title = os.getenv("VIDEO_TITLE") or "final_video"
        if len(title) <= 35:
            return title
        else:
            return title[0:30] + "..."

    filename = f"{get_video_title()}.mp4"
    save_data()

    if not exists("./results"):
        print_substep("the results folder didn't exist so I made it")
        os.mkdir("./results")

    final.write_videofile("assets/temp/temp.mp4", fps=24, audio_codec="aac", audio_bitrate="192k", threads=8,
                          preset="ultrafast")
    ffmpeg_tools.ffmpeg_extract_subclip(
        "assets/temp/temp.mp4", 0, length, targetname=f"results/{filename}"
    )

    print_substep("See result in the results folder!")

    print_step(
        f"Reddit title: {os.getenv('VIDEO_TITLE')} \n Background Credit: {os.getenv('background_credit')}"
    )
