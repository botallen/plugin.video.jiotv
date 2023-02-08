# -*- coding: utf-8 -*-
import os
from xbmcvfs import translatePath
import xbmcaddon

ADDON = xbmcaddon.Addon()

# Urls
IMG_PUBLIC = "https://jioimages.cdn.jio.com/imagespublic/"
IMG_CATCHUP = "http://jiotv.catchup.cdn.jio.com/dare_images/images/"
IMG_CATCHUP_SHOWS = "http://jiotv.catchup.cdn.jio.com/dare_images/shows/"
PLAY_URL = "plugin://plugin.video.jiotv/resources/lib/main/play/?"
PLAY_EX_URL = "plugin://plugin.video.jiotv/resources/lib/main/play_ex/?_pickle_="
FEATURED_SRC = "https://tv.media.jio.com/apis/v1.6/getdata/featurednew?start=0&limit=30&langId=6"
EXTRA_CHANNELS = os.path.join(translatePath(
    ADDON.getAddonInfo("path")), "resources", "extra", "channels.json")
CHANNELS_SRC = "https://jiotv.data.cdn.jio.com/apis/v3.0/getMobileChannelList/get/?langId=6&os=android&devicetype=phone&usertype=tvYR7NSNn7rymo3F&version=285&langId=6"
GET_CHANNEL_URL = "https://jiotvapi.media.jio.com/playback/apis/v1/geturl?langId=6"
CATCHUP_SRC = "http://jiotv.data.cdn.jio.com/apis/v1.3/getepg/get?offset={0}&channel_id={1}&langId=6"
M3U_SRC = os.path.join(translatePath(
    ADDON.getAddonInfo("profile")), "playlist.m3u")
M3U_CHANNEL = "\n#EXTINF:0 tvg-id=\"{tvg_id}\" tvg-name=\"{channel_name}\" group-title=\"{group_title}\" tvg-chno=\"{tvg_chno}\" tvg-logo=\"{tvg_logo}\"{catchup},{channel_name}\n{play_url}"
EPG_SRC = "https://kodi.botallen.com/tv/epg.xml.gz"

# Configs
GENRE_CONFIG = [
    {
        "name": "News",
        "tvImg":  IMG_PUBLIC + "logos/langGen/news_1579517470920.jpg",
        "promoImg": IMG_PUBLIC + "logos/langGen/news_1579517470920.jpg",
    },
    {
        "name": "Music",
        "tvImg":  IMG_PUBLIC + "logos/langGen/Music_1579245819981.jpg",
        "promoImg": IMG_PUBLIC + "logos/langGen/Music_1579245819981.jpg",
    },
    {

        "name": "Sports",
        "tvImg":  IMG_PUBLIC + "logos/langGen/Sports_1579245819981.jpg",
        "promoImg": IMG_PUBLIC + "logos/langGen/Sports_1579245819981.jpg",

    },
    {

        "name": "Entertainment",
        "tvImg":  IMG_PUBLIC + "38/52/Entertainment_1584620980069_tv.jpg",
        "promoImg": IMG_PUBLIC + "logos/langGen/Entertainment_1579245819981.jpg",

    },
    {

        "name": "Devotional",
        "tvImg":  IMG_PUBLIC + "logos/langGen/devotional_1579517470920.jpg",
        "promoImg": IMG_PUBLIC + "logos/langGen/devotional_1579517470920.jpg",

    },
    {
        "name": "Movies",
        "tvImg":  IMG_PUBLIC + "logos/langGen/movies_1579517470920.jpg",
        "promoImg": IMG_PUBLIC + "logos/langGen/movies_1579517470920.jpg",

    },
    {
        "name": "Infotainment",
        "tvImg":  IMG_PUBLIC + "logos/langGen/infotainment_1579517470920.jpg",
        "promoImg": IMG_PUBLIC + "logos/langGen/infotainment_1579517470920.jpg",

    },
    {
        "name": "Business",
        "tvImg":  IMG_PUBLIC + "logos/langGen/business_1579517470920.jpg",
        "promoImg": IMG_PUBLIC + "logos/langGen/business_1579517470920.jpg",
    },
    {
        "name": "Kids",
        "tvImg":  IMG_PUBLIC + "logos/langGen/kids_1579517470920.jpg",
        "promoImg": IMG_PUBLIC + "logos/langGen/kids_1579517470920.jpg",
    },
    {
        "name": "Lifestyle",
        "tvImg":  IMG_PUBLIC + "logos/langGen/lifestyle_1579517470920.jpg",
        "promoImg": IMG_PUBLIC + "logos/langGen/lifestyle_1579517470920.jpg",
    },
    {
        "name": "Jio Darshan",
        "tvImg":  IMG_PUBLIC + "logos/langGen/jiodarshan_1579517470920.jpg",
        "promoImg": IMG_PUBLIC + "logos/langGen/jiodarshan_1579517470920.jpg",
    },
    {
        "name": "Shopping",
        "tvImg":  IMG_PUBLIC + "logos/langGen/shopping_1579517470920.jpg",
        "promoImg": IMG_PUBLIC + "logos/langGen/shopping_1579517470920.jpg",
    },
    {
        "name": "Educational",
        "tvImg":  IMG_PUBLIC + "logos/langGen/educational_1579517470920.jpg",
        "promoImg": IMG_PUBLIC + "logos/langGen/educational_1579517470920.jpg",
    }
]
LANGUAGE_CONFIG = [
    {
        "name": "Hindi",
        "tvImg": IMG_PUBLIC + "logos/langGen/Hindi_1579245819981.jpg",
        "promoImg": IMG_PUBLIC+"98/98/Hindi_1580458058289_promo.jpg",
    },
    {
        "name": "English",
        "tvImg": IMG_PUBLIC + "logos/langGen/English_1579245819981.jpg",
        "promoImg": IMG_PUBLIC+"52/8/English_1580458071796_promo.jpg",
    },    
    {
        "name": "Punjabi",
        "tvImg": IMG_PUBLIC + "logos/langGen/Punjabi_1579245819981.jpg",
        "promoImg": IMG_PUBLIC+"79/58/Punjabi_1580458722849_promo.jpg",
    }
]
LANG_MAP = {6: "English", 1: "Hindi", 2: "Marathi", 3: "Punjabi", 4: "Urdu", 5: "Bengali", 7: "Malayalam", 8: "Tamil",
            9: "Gujarati", 10: "Odia", 11: "Telugu", 12: "Bhojpuri", 13: "Kannada", 14: "Assamese", 15: "Nepali", 16: "French", 18: "Unknown"}
GENRE_MAP = {8: "Sports", 5: "Entertainment", 6: "Movies", 12: "News", 13: "Music", 7: "Kids", 9: "Lifestyle",
             10: "Infotainment", 15: "Devotional", 16: "Business", 17: "Educational", 18: "Shopping", 19: "JioDarshan"}
CONFIG = {"Genres": GENRE_CONFIG, "Languages": LANGUAGE_CONFIG}