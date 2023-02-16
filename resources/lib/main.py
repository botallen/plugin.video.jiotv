# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# xbmc imports
from xbmcaddon import Addon
from xbmc import executebuiltin
from xbmcgui import Dialog, DialogProgress

# codequick imports
from codequick import Route, run, Listitem, Resolver, Script
from codequick.utils import keyboard
from codequick.script import Settings
from codequick.storage import PersistentDict

# add-on imports
from resources.lib.utils import getTokenParams, getHeaders, isLoggedIn, refresh_token, login as ULogin, logout as ULogout, check_addon, sendOTP, get_local_ip, no_ssl_verification
from resources.lib.constants import GET_CHANNEL_URL, PLAY_EX_URL, EXTRA_CHANNELS, GENRE_MAP, LANG_MAP, FEATURED_SRC, CONFIG, CHANNELS_SRC, IMG_CATCHUP, PLAY_URL, IMG_CATCHUP_SHOWS, CATCHUP_SRC, M3U_SRC, EPG_SRC, M3U_CHANNEL

# additional imports
import urlquick
import requests
from urllib.parse import urlencode
import inputstreamhelper
import json
import m3u8
from time import time, sleep
from datetime import datetime, timedelta, date


# Root path of plugin
@Route.register
def root(plugin):
    yield Listitem.from_dict(**{
        "label": "Featured",
        "art": {
            "thumb": IMG_CATCHUP_SHOWS + "cms/TKSS_Carousal1.jpg",
            "icon": IMG_CATCHUP_SHOWS + "cms/TKSS_Carousal1.jpg",
            "fanart": IMG_CATCHUP_SHOWS + "cms/TKSS_Carousal1.jpg",
        },
        "callback": Route.ref("/resources/lib/main:show_featured")
    })
    for e in ["Genres", "Languages"]:
        yield Listitem.from_dict(**{
            "label": e,
            "art": {
                "thumb": CONFIG[e][0].get("tvImg"),
                "icon": CONFIG[e][0].get("tvImg"),
                "fanart": CONFIG[e][0].get("promoImg"),
            },
            "callback": Route.ref("/resources/lib/main:show_listby"),
            "params": {"by": e}
        })


# Shows Featured Content
@Route.register
def show_featured(plugin, id=None):
    resp = urlquick.get(FEATURED_SRC, headers={
        "usergroup": "tvYR7NSNn7rymo3F",
        "os": "android",
        "devicetype": "phone",
        "versionCode": "226"
    }, max_age=-1).json()
    for each in resp.get("featuredNewData", []):
        if id:
            if int(each.get("id", 0)) == int(id):
                data = each.get("data", [])
                for child in data:
                    info_dict = {
                        "art": {
                            "thumb": IMG_CATCHUP_SHOWS + child.get("episodePoster", ""),
                            "icon": IMG_CATCHUP_SHOWS + child.get("episodePoster", ""),
                            "fanart": IMG_CATCHUP_SHOWS + child.get("episodePoster", ""),
                            "clearart": IMG_CATCHUP + child.get("logoUrl", ""),
                            "clearlogo": IMG_CATCHUP + child.get("logoUrl", ""),
                        },
                        "info": {
                            'originaltitle': child.get("showname"),
                            "tvshowtitle": child.get("showname"),
                            "genre": child.get("showGenre"),
                            "plot": child.get("description"),
                            "episodeguide": child.get("episode_desc"),
                            "episode": 0 if child.get("episode_num") == -1 else child.get("episode_num"),
                            "cast": child.get("starCast", "").split(', '),
                            "director": child.get("director"),
                            "duration": child.get("duration")*60,
                            "tag": child.get("keywords"),
                            "mediatype": "movie" if child.get("channel_category_name") == "Movies" else "episode",
                        }
                    }
                    if child.get("showStatus") == "Now":
                        info_dict["label"] = info_dict["info"]["title"] = child.get(
                            "showname", "") + " [COLOR red] [ LIVE ] [/COLOR]"
                        info_dict["callback"] = play
                        info_dict["params"] = {
                            "channel_id": child.get("channel_id")}
                        yield Listitem.from_dict(**info_dict)
                    elif child.get("showStatus") == "future":
                        timetext = datetime.fromtimestamp(int(child.get("startEpoch", 0)*.001)).strftime(
                            '    [ %I:%M %p -') + datetime.fromtimestamp(int(child.get("endEpoch", 0)*.001)).strftime(' %I:%M %p ]   %a')
                        info_dict["label"] = info_dict["info"]["title"] = child.get(
                            "showname", "") + (" [COLOR green]%s[/COLOR]" % timetext)
                        info_dict["callback"] = ""
                        yield Listitem.from_dict(**info_dict)
                    elif child.get("showStatus") == "catchup":
                        timetext = datetime.fromtimestamp(int(child.get("startEpoch", 0)*.001)).strftime(
                            '    [ %I:%M %p -') + datetime.fromtimestamp(int(child.get("endEpoch", 0)*.001)).strftime(' %I:%M %p ]   %a')
                        info_dict["label"] = info_dict["info"]["title"] = child.get(
                            "showname", "") + (" [COLOR yellow]%s[/COLOR]" % timetext)
                        info_dict["callback"] = play
                        info_dict["params"] = {
                            "channel_id": child.get("channel_id"),
                            "showtime": child.get("showtime", "").replace(":", ""),
                            "srno": datetime.fromtimestamp(int(child.get("startEpoch", 0)*.001)).strftime('%Y%m%d')
                        }
                        yield Listitem.from_dict(**info_dict)
        else:
            yield Listitem.from_dict(**{
                "label": each.get("name"),
                "art": {
                    "thumb": IMG_CATCHUP_SHOWS + each.get("data", [{}])[0].get("episodePoster"),
                    "icon": IMG_CATCHUP_SHOWS + each.get("data", [{}])[0].get("episodePoster"),
                    "fanart": IMG_CATCHUP_SHOWS + each.get("data", [{}])[0].get("episodePoster"),
                },
                "callback": Route.ref("/resources/lib/main:show_featured"),
                "params": {"id": each.get("id")}
            })


# Shows Filter options
@Route.register
def show_listby(plugin, by):
    for each in CONFIG[by]:
        yield Listitem.from_dict(**{
            "label": each.get("name"),
            "art": {
                "thumb": each.get("tvImg"),
                "icon": each.get("tvImg"),
                "fanart": each.get("promoImg")
            },
            "callback": Route.ref("/resources/lib/main:show_category"),
            "params": {"category_id": each.get("name").replace(" ", ""), "by": by}
        })


# Shows channels by selected filter/category
@Route.register
def show_category(plugin, category_id, by):
    resp = urlquick.get(CHANNELS_SRC).json().get("result")

    def fltr(x):
        fby = by.lower()[:-1]
        if fby == "genre":
            return GENRE_MAP[x.get("channelCategoryId")] == category_id and Settings.get_boolean(LANG_MAP[x.get("channelLanguageId")])
        else:
            return LANG_MAP[x.get("channelLanguageId")] == category_id

    for each in filter(fltr, resp):
        if each.get("channelIdForRedirect") and not Settings.get_boolean("extra"):
            continue
        litm = Listitem.from_dict(**{
            "label": each.get("channel_name"),
            "art": {
                "thumb": IMG_CATCHUP + each.get("logoUrl"),
                "icon": IMG_CATCHUP + each.get("logoUrl"),
                "fanart": IMG_CATCHUP + each.get("logoUrl"),
                "clearlogo": IMG_CATCHUP + each.get("logoUrl"),
                "clearart": IMG_CATCHUP + each.get("logoUrl"),
            },
            "callback": play,
            "params": {
                "channel_id": each.get("channel_id")
            }
        })
        if each.get("isCatchupAvailable"):
            litm.context.container(show_epg, "Catchup",
                                   0, each.get("channel_id"))
        yield litm


# Shows EPG container from Context menu
@Route.register
def show_epg(plugin, day, channel_id):
    resp = urlquick.get(CATCHUP_SRC.format(day, channel_id), max_age=-1).json()
    epg = sorted(
        resp['epg'], key=lambda show: show['startEpoch'], reverse=True)
    livetext = '[COLOR red] [ LIVE ] [/COLOR]'
    for each in epg:
        current_epoch = int(time()*1000)
        if not each['stbCatchupAvailable'] or each['startEpoch'] > current_epoch:
            continue
        islive = each['startEpoch'] < current_epoch and each['endEpoch'] > current_epoch
        showtime = '   '+livetext if islive else datetime.fromtimestamp(
            int(each['startEpoch']*.001)).strftime('    [ %I:%M %p -') + datetime.fromtimestamp(int(each['endEpoch']*.001)).strftime(' %I:%M %p ]   %a')
        yield Listitem.from_dict(**{
            "label": each['showname'] + showtime,
            "art": {
                'thumb': IMG_CATCHUP_SHOWS+each['episodePoster'],
                'icon': IMG_CATCHUP_SHOWS+each['episodePoster'],
                'fanart': IMG_CATCHUP_SHOWS+each['episodePoster'],
            },
            "callback": play,
            "info": {
                'title': each['showname'] + showtime,
                'originaltitle': each['showname'],
                "tvshowtitle": each['showname'],
                'genre': each['showGenre'],
                'plot': each['description'],
                "episodeguide": each.get("episode_desc"),
                'episode': 0 if each['episode_num'] == -1 else each['episode_num'],
                'cast': each['starCast'].split(', '),
                'director': each['director'],
                'duration': each['duration']*60,
                'tag': each['keywords'],
                'mediatype': 'episode',
            },
            "params": {
                "channel_id": each.get("channel_id"),
                "showtime": None if islive else each.get("showtime", "").replace(":", ""),
                "srno": None if islive else datetime.fromtimestamp(int(each.get("startEpoch", 0)*.001)).strftime('%Y%m%d')
            }
        })
    if int(day) == 0:
        for i in range(-1, -7, -1):
            label = 'Yesterday' if i == - \
                1 else (date.today() + timedelta(days=i)).strftime('%A %d %B')
            yield Listitem.from_dict(**{
                "label": label,
                "callback": Route.ref("/resources/lib/main:show_epg"),
                "params": {
                    "day": i,
                    "channel_id": channel_id
                }
            })


@Resolver.register
@isLoggedIn
def play_ex(plugin, dt=None):
    is_helper = inputstreamhelper.Helper(
        dt.get("proto", "mpd"), drm=dt.get("drm"))
    if is_helper.check_inputstream():
        licenseUrl = dt.get("lUrl") and dt.get("lUrl").replace("{HEADERS}", urlencode(
            getHeaders())).replace("{TOKEN}", urlencode(getTokenParams()))
        art = {}
        if dt.get("default_logo"):
            art['thumb'] = art['icon'] = IMG_CATCHUP + \
                dt.get("default_logo")
        return Listitem().from_dict(**{
            "label": dt.get("label") or plugin._title,
            "art": art or None,
            "callback": dt.get("pUrl"),
            "properties": {
                "IsPlayable": True,
                "inputstream": is_helper.inputstream_addon,
                "inputstream.adaptive.stream_headers": dt.get("hdrs"),
                "inputstream.adaptive.manifest_type": dt.get("proto", "mpd"),
                "inputstream.adaptive.license_type": dt.get("drm"),
                "inputstream.adaptive.license_key": licenseUrl,
            }
        })


# Play live stream/ catchup according to params.
# Also insures that user is logged in.
@Resolver.register
@isLoggedIn
def play(plugin, channel_id, showtime=None, srno=None):
    is_helper = inputstreamhelper.Helper("mpd", drm="com.widevine.alpha")
    hasIs = is_helper.check_inputstream()
    if not hasIs:
        return
    if showtime is None and Settings.get_boolean("extra"):
        with open(EXTRA_CHANNELS, "r") as f:
            extra = json.load(f)
        if extra.get(str(channel_id)):
            if extra.get(str(channel_id)).get("ext"):
                return extra.get(str(channel_id)).get("ext")
            return PLAY_EX_URL + extra.get(str(channel_id)).get("data")
    db = getHeaders()
    srno = datetime.now().strftime('%y%m%d%H%M%S')
    # Script.log("###################################### PLAY CHANNEL #######################################", lvl=Script.ERROR)
    headers = {
        "accesstoken":  db.get("authToken",""),
        "appkey":db.get("appkey",""),
        "camid": "",
        "channel_id":str(channel_id),
        "content-type":"application/x-www-form-urlencoded",
        "crmid":db.get("crmid",""),
        "deviceid":db.get("deviceId",""),
        "devicetype":"phone",
        "dm":"OnePlus ONEPLUS A5000",
        "isott":"false",
        "langid":"",
        "languageid":"6",
        "lbcookie":"1",
        "os":"android",
        "osversion":"10",
        "sid":db.get("uniqueId",""),
        "subscriberid":db.get("crmid",""),
        "uniqueid":db.get("uniqueId",""),
        "user-agent":"okhttp/4.2.2",
        "usergroup":db.get("usergroup",""),
        "userid":db.get("userId",""),
        "versioncode":"285",
    }

    body = {
        "channel_id": str(channel_id),
        "stream_type": "Seek"
    }
    if showtime and srno:
        body["begin"] = showtime
        body["srno"] = srno

    # Script.log(GET_CHANNEL_URL, lvl=Script.ERROR)
    # Script.log(headers, lvl=Script.ERROR)
    # Script.log(body, lvl=Script.ERROR)
    refresh_token()
    with no_ssl_verification():
        resp = urlquick.post(GET_CHANNEL_URL, data=body, headers=headers, max_age=-1, verify=False, raise_for_status=False)
        if resp.status_code == 419 or resp.status_code == 403:
            # Login Again or Refresh
            refresh_token()
            executebuiltin("RunPlugin(plugin://plugin.video.jiotv/resources/lib/main/play/?channel_id={0})".format(str(channel_id)))
            return

    resp = resp.json()        
    # Script.log(resp, lvl=Script.ERROR)

    art = {}
    art["thumb"] = art["icon"] = IMG_CATCHUP + \
        resp.get("result", "").split("/")[-1].replace(".m3u8", ".png")
    params = getTokenParams()
    playback_url = resp.get("result","")

    playback_headers = {
        "accept-encoding":"gzip, deflate",
        "accesstoken": db.get("authToken",""),
        "channelid":str(channel_id),
        "crmid": db.get("crmid",""),
        "deviceid":db.get("deviceId",""),
        "devicetype":"phone",
        "os":"android",
        "osversion":"10",
        "srno": srno,
        "ssotoken": db.get("ssotoken",""),
        "subscriberid":db.get("crmid",""),
        "uniqueid":db.get("uniqueId",""),
        "user-agent":"plaYtv/7.0.8 (Linux;Android 10) ExoPlayerLib/2.11.7",
        "usergroup":db.get("usergroup",""),
        "userid":db.get("userId",""),
        "versioncode":"285",
    }

    #master playlist cookies
    mresp = urlquick.get(playback_url, headers=playback_headers, max_age=-1, verify=False, raise_for_status=False)
    playback_headers["Cookie"] = mresp.headers.get("set-cookie","")
    # Script.log("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$", lvl=Script.ERROR)
    # Script.log(mresp.headers.get("set-cookie",""), lvl=Script.ERROR)

    # variant_m3u8 = m3u8.load(playback_url,headers=playback_headers)
    # if variant_m3u8.is_variant:
    #     playback_url = variant_m3u8.playlists[-1].absolute_uri

    return Listitem().from_dict(**{
        "label": plugin._title,
        "art": art,
        "callback": playback_url,
        "properties": {
            "IsPlayable": True,
            "inputstream": "inputstream.adaptive",
            "inputstream.adaptive.stream_headers": urlencode(playback_headers),
            "inputstream.adaptive.manifest_type": "hls",
            "inputstream.adaptive.license_key": "|" + urlencode(playback_headers) + "|R{SSM}|",
        }
    })


# Login `route` to access from Settings
@Script.register
def login(plugin):
    headers = getHeaders()
    if headers:
        refresh_token()
        return
    mobile = keyboard("Enter your Jio mobile number")
    error = sendOTP(mobile)
    if error:
        Script.notify("Login Error", error)
        return
    otp = keyboard("Enter OTP", hidden=True)
    ULogin(mobile, otp, mode="otp")


# Logout `route` to access from Settings
@Script.register
def logout(plugin):
    ULogout()


# M3u Generate `route`
@Script.register
@isLoggedIn
def m3ugen(plugin, notify="yes"):
    refresh_token()
    channels = urlquick.get(CHANNELS_SRC).json().get("result")
    m3ustr = "#EXTM3U x-tvg-url=\"%s\"" % EPG_SRC
    for i, channel in enumerate(channels):
        lang = LANG_MAP[channel.get("channelLanguageId")]
        genre = GENRE_MAP[channel.get("channelCategoryId")]
        if not Settings.get_boolean(lang):
            continue
        group = lang + ";" + genre
        _play_url = PLAY_URL + \
            "channel_id={0}".format(channel.get("channel_id"))
        catchup = ""
        if channel.get("isCatchupAvailable"):
            catchup = ' catchup="vod" catchup-source="{0}channel_id={1}&showtime={{H}}{{M}}{{S}}&srno={{Y}}{{m}}{{d}}" catchup-days="7"'.format(
                PLAY_URL, channel.get("channel_id"))
        m3ustr += M3U_CHANNEL.format(
            tvg_id=channel.get("channel_id"),
            channel_name=channel.get("channel_name"),
            group_title=group,
            tvg_chno=int(channel.get("channel_order", i))+1,
            tvg_logo=IMG_CATCHUP + channel.get("logoUrl", ""),
            catchup=catchup,
            play_url=_play_url,
        )
    with open(M3U_SRC, "w+") as f:
        f.write(m3ustr.replace(u'\xa0', ' ').encode('utf-8').decode('utf-8'))
    if notify == "yes":
        Script.notify(
            "JioTV", "Playlist updated. Restart to apply the changes.")


# PVR Setup `route` to access from Settings
@Script.register
def pvrsetup(plugin):
    executebuiltin(
        "RunPlugin(plugin://plugin.video.jiotv/resources/lib/main/m3ugen/)")
    IDdoADDON = 'pvr.iptvsimple'

    def set_setting(id, value):
        if Addon(IDdoADDON).getSetting(id) != value:
            Addon(IDdoADDON).setSetting(id, value)
    if check_addon(IDdoADDON):
        set_setting("m3uPathType", "0")
        set_setting("m3uPath", M3U_SRC)
        set_setting("epgPathType", "1")
        set_setting("epgUrl", EPG_SRC)
        set_setting("catchupEnabled", "true")
        set_setting("catchupWatchEpgBeginBufferMins", "0")
        set_setting("catchupWatchEpgEndBufferMins", "0")


# Cache cleanup
@Script.register
def cleanup(plugin):
    urlquick.cache_cleanup(-1)
    Script.notify("Cache Cleaned", "")
