# -*- coding: utf-8 -*-

from libs.utils import *

CHANNEL_NAME = 'CanalSur'
url_base = 'https://www.canalsur.es'

def get_channel():
    return CHANNEL_NAME

@LimitResults()
def mainmenu(item):
    itemlist = list()

    if not item.page:
        item.page = 1

    data = remove_white_spaces(httptools.downloadpage(url_base + '/programas_tv.html?pagina=%s' % item.page).data)

    patron = """<div class="col-xs-6"><a href="([^"]+).*?title="([^"]+)"><img src='([^']+).*?<div class="programs_list_az_item_description">([^<]+)</div>"""

    for url, title, icon, plot in re.findall(patron, data):
        itemlist.append(item.clone(
            label=title,
            action="index",
            url= urllib_parse.urljoin(url_base, url),
            icon=url_base + icon,
            plot=plot
        ))

    # Paginacion
    next_page = re.findall(r'class="enlace">%s</a>' % (item.page + 1), data)
    if next_page:
        itemlist.append(item.clone(type='next', page=item.page + 1))

    return itemlist


@LimitResults()
def index(item):
    itemlist = list()

    data = remove_white_spaces(httptools.downloadpage(item.url).data)
    #logger(data)

    patron = 'div class="relative"> <img src="([^"]+).*?<span class="titulo">([^<]+)(.*?)<div class="videos"[^>]+>([^<]+)'
    for icon, title, info, videos in re.findall(patron, data):
        plot = re.findall(r'<div class="descripcion hidden"[^>]+>([^<]+)', info)

        itemlist.append(item.clone(
            label=title,
            action="play",
            url=videos.split('::'),
            icon=url_base + icon,
            plot=plot[0] if plot else item.plot
        ))

    return itemlist


def play(item):
    video_list = list()

    video = Video(plot=item.plot,
                  titulo=item.label)

    for url in item.url:
        if url:
            video_list.append(video.clone(url=url))

    return video_list