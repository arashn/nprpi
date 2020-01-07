from authorization import Authorization
from recommendations import Recommendations
from vlc import Instance, EventType, Media
import logging
from signal import pause
from threading import Timer
import sys
import termios
import tty

logger = logging.Logger('nprpi')

state = 'PLAYER_STOPPED'
interval = 300

sleep_time = 0
sleep_timer = None
sleep_interval = 60
sleep_timer_set = False


def getch():  # getchar(), getc(stdin)  #PYCHOK flake
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return ch


def sleep_callback(recommendations):
    global sleep_time, sleep_timer
    sleep_time = sleep_time - 1
    print('Sleep time:', sleep_time)
    if sleep_time == 0:
        print('Stopping radio')
        stop(recommendations)
        return
    sleep_timer = Timer(sleep_interval, sleep_callback, args=[recommendations])
    sleep_timer.start()


def rate_interval(recommendations, item, elapsed):
    global t
    logger.debug('rate_interval called, elapsed: {}, playback position: {}'.format(elapsed, (player.get_position() * player.get_length())))
    recommendations.rate_item(item, 'START', elapsed)
    t = Timer(interval, rate_interval, args=[recommendations, item, elapsed + interval])
    t.start()


def on_start(event, recommendations, item):
    logger.debug('Item started playing')
    recommendations.rate_item(item, 'START', 0)


def on_play(event, recommendations, item):
    logger.debug('Playback resumed')
    global state, t
    state = 'PLAYER_PLAYING'
    # Create new timer with interval 300 - (player position % 300)
    position = int(player.get_position() * player.get_length()) // 1000
    remaining = interval - (position % interval)
    t = Timer(remaining, rate_interval, args=[recommendations, item, position + remaining])
    t.start()


def on_end(event, recommendations, item, instance):
    logger.debug('Item finished playing')
    t.cancel()
    recommendations.rate_item(item, 'COMPLETED')
    play_next(recommendations, instance)


def on_pause(event):
    logger.debug('Playback paused')
    global state
    state = 'PLAYER_PAUSED'
    t.cancel()


def on_stop(event):
    logger.debug('Playback stopped')
    global state
    t.cancel()
    state = 'PLAYER_STOPPED'


def play_next(recommendations, instance):
    global player
    item = recommendations.get_next_item()
    logger.debug('Now Playing:', item.data['attributes']['title'])
    player = instance.media_player_new()
    em = player.event_manager()
    em.event_attach(EventType.MediaPlayerEndReached, on_end, recommendations, item, instance)
    em.event_attach(EventType.MediaPlayerOpening, on_start, recommendations, item)
    em.event_attach(EventType.MediaPlayerPlaying, on_play, recommendations, item)
    em.event_attach(EventType.MediaPlayerPaused, on_pause)
    em.event_attach(EventType.MediaPlayerStopped, on_stop)
    player.set_media(Media(item.get_audio_uri()))
    player.play()


def play_pause(recommendations, instance):
    global sleep_timer
    if state == 'PLAYER_STOPPED':
        play_next(recommendations, instance)
    elif state == 'PLAYER_PAUSED':
        player.play()
        if sleep_timer_set:
            sleep_timer = Timer(sleep_interval, sleep_callback, args=[recommendations])
            sleep_timer.start()
    elif state == 'PLAYER_PLAYING':
        if sleep_timer is not None:
            sleep_timer.cancel()
        player.pause()


def stop(recommendations):
    global sleep_timer_set
    sleep_timer_set = False
    if sleep_timer is not None:
        sleep_timer.cancel()

    if state == 'PLAYER_PLAYING' or state == 'PLAYER_PAUSED':
        player.stop()
        if state == 'PLAYER_PLAYING':
            t.cancel()

    recommendations.reset()


def set_sleep_timer(recommendations, instance):
    global sleep_timer, sleep_time, sleep_timer_set
    if sleep_timer is not None:
        sleep_timer.cancel()

    if sleep_time < 10:
        sleep_time = 10
    elif sleep_time < 15:
        sleep_time = 15
    elif sleep_time < 30:
        sleep_time = 30
    elif sleep_time < 60:
        sleep_time = 60
    elif sleep_time < 120:
        sleep_time = 120
    else:
        sleep_time = 0

    print('Sleep time:', sleep_time)

    if sleep_time > 0:
        if state == 'PLAYER_STOPPED':
            play_next(recommendations, instance)
        sleep_timer_set = True
        sleep_timer = Timer(sleep_interval, sleep_callback, args=[recommendations])
        sleep_timer.start()
    else:
        sleep_timer_set = False


if __name__ == '__main__':
    with open('credentials') as f:
        client_id = f.readline().strip()
        client_secret = f.readline().strip()
    authorization = Authorization(client_id, client_secret)
    access_token = authorization.get_access_token()
    recommendations = Recommendations(access_token)
    instance = Instance()

    while True:
        k = getch()
        if k == ' ':
            play_pause(recommendations, instance)
        elif k == '.':
            stop(recommendations)
        elif k == 'm':
            set_sleep_timer(recommendations, instance)
        elif k == 'q':
            sleep_timer_set = False
            if sleep_timer is not None:
                sleep_timer.cancel()
            sys.exit(0)
