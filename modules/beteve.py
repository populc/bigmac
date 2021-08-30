# -*- coding: utf-8 -*-

from libs.utils import *

CHANNEL_NAME = 'Betevé'
url_base = 'https://beteve.cat'


def mainmenu(item):
    itemlist = list()

    index_html = remove_white_spaces(httptools.downloadpage(url_base + '/programes/').data)
    patron = r'btv-programes-item-img.*?href="/(.*?)/".*?>.*?>(.*?)<'

    for btv_slug, title in re.findall(patron, index_html, re.S):
        itemlist.append(item.clone(
            label=title,
            action="index",
            btv_slug=btv_slug,
            page=0,
            plot=title
        ))

    return itemlist


@LimitResults()
def index(item):
    itemlist = list()

    url = 'https://beteve.cat/wp-content/ajax-email.php?action=btv_search_posts_by_input_text&btv_search_text=&btv_taxonomy=programa&btv_slug=%s&btv_page_num=%s&btv_date_start=&btv_date_end=' % (
    item.btv_slug, item.page)
    show_html = remove_white_spaces(httptools.downloadpage(url).data)

    patron = r'<div class="d-none d-lg-block card-responsive float-lg-left" style="margin: 0;"><a href="([^"]+).*?src="([^"]+).*?<h3.*?>([^<]+).*?date">([^<]+)'
    for url, img, title, fecha in re.findall(patron, show_html):
        itemlist.append(item.clone(
            label=fecha + ' | ' + title,
            action="play",
            url=url,
            icon=six.moves.urllib.parse.quote(img, safe=':/'),
            plot="[B]" + fecha + " | " + title + "[/B]\n\n" + item.plot,
        ))

    next_page = re.findall(r'page_num="(\d+)"', show_html)
    if next_page:
        itemlist.append(item.clone(type='next', page= item.page + 1))

    return itemlist


def play(item):
    video_list = list()

    video = Video(plot=item.plot, titulo=item.label)

    video_html = remove_white_spaces(httptools.downloadpage(item.url).data)

    es_mp3 = False

    try:
        video_url = 'https://cdnapisec.kaltura.com/p/2346171/sp/234617100/playManifest/entryId/' + \
                    re.findall(r'targetId".*?"(.*?)"', video_html)[
                        0] + '/flavorIds/x/format/applehttp/protocol/https/a.m3u8'

        m3u8 = httptools.downloadpage(video_url)
        if m3u8.code == 200:
            video_list.extend(get_videos_m3u8(video_url, video))
        else:
            es_mp3 = True
    except:
        try:
            video_youtube = re.findall(r'<iframe.*?src=".*?youtube.*?embed/(.*?)"', video_html)[0]
            video_list.append(video.clone(url=video_youtube, res='720', player='youtube'))
        except:
            es_mp3 = True

    if es_mp3:
        try:
            wid = re.findall(r'"wid".*?"(.*?)"', video_html)[0]
            uiconf_id = re.findall(r'"uiconf_id".*?"(.*?)"', video_html)[0]
            entry_id = re.findall(r'"entry_id".*?"(.*?)"', video_html)[0]
            cache_st = re.findall(r'"cache_st".*?"(.*?)"', video_html)[0]
            callback = 'mwi_' + entry_id.replace('_', '') + '0'
            scrap_data = httptools.downloadpage(
                'https://cdnapisec.kaltura.com/html5/html5lib/v2.90/mwEmbedFrame.php?&wid=' + wid + '&uiconf_id=' + uiconf_id + '&entry_id=' + entry_id + '&cache_st=' + cache_st + '&flashvars[streamerType]=auto&flashvars[share.socialShareURL]=parent&playerId=' + entry_id + '&forceMobileHTML5=true&urid=2.90&protocol=https&callback=' + callback).data
            id2 = re.findall(r'"id\\":\\"(.*?)\\"', scrap_data)

        except:
            es_iframe = re.findall(r'<iframe.*?kaltura.*?src="(.*?)"', video_html)
            if len(es_iframe) > 0:
                scrap_data = httptools.downloadpage(es_iframe[0]).data
                id2 = re.findall(r'"id":"(.*?)"', scrap_data)
                #me he dado cuenta que esto puede terminar con / o con &
                #por eso este arreglillo
                entry_id = re.findall(r'entry_id=(.*?)/', es_iframe[0] + '/')[0]
                if '&' in entry_id:
                    entry_id = entry_id.split('&')[0]
            else:
                pass

        try:
            mp3 = 'https://cdnapisec.kaltura.com/p/2346171/sp/234617100/playManifest/entryId/' + entry_id + '/flavorId/' + \
                  id2[-1] + '/format/url/protocol/https/a.mp3'
            video_list.append(video.clone(url==mp3))
        except:
            pass

    return video_list
