from django.shortcuts import render

from django.http import HttpResponse

import ffmpeg_streaming
from ffmpeg_streaming import Formats, Bitrate, Representation, Size

from django.conf import settings

stream_link = 'http://ss-b.telek.xyz/a0sn?token=1JD2NZ4445NA';
_240p  = Representation(Size(426, 240), Bitrate(150 * 1024, 94 * 1024))
_360p = Representation(Size(640, 360), Bitrate(276 * 1024, 128 * 1024))
_480p = Representation(Size(854, 480), Bitrate(750 * 1024, 192 * 1024))
_720p = Representation(Size(1280, 720), Bitrate(2048 * 1024, 320 * 1024))
_1080p = Representation(Size(1920, 1080), Bitrate(4096 * 1024, 320 * 1024))


def index(request):
    return render(request, 'stream/index.html', {
        'input_video': f'{settings.STATIC_URL}video/450.mp4'
    })


def run(request):
    video = ffmpeg_streaming.input(stream_link)
    dash = video.dash(Formats.h264())
    dash.representations(_480p)
    dash.output('/app/static/stream/dash.mpd')


def stop(request):
    video = ffmpeg_streaming.input('')
    hls = video.hls(Formats.h264())
    hls.auto_generate_representations()
    hls.output('/app/static/stream/hls.m3u8')

    return HttpResponse('<h1>Stream is stopped</h1>')
