# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import warnings
import contextlib
import urlquick
import requests
from uuid import uuid4
import base64
import hashlib
import urllib3
import time
from urllib3.exceptions import InsecureRequestWarning
from functools import wraps
from distutils.version import LooseVersion
from codequick import Script
from codequick.storage import PersistentDict
from xbmc import executebuiltin
from xbmcgui import Dialog
import socket

urllib3.disable_warnings()

old_merge_environment_settings = requests.Session.merge_environment_settings

@contextlib.contextmanager
def no_ssl_verification():
    opened_adapters = set()

    def merge_environment_settings(self, url, proxies, stream, verify, cert):
        # Verification happens only once per connection so we need to close
        # all the opened adapters once we're done. Otherwise, the effects of
        # verify=False persist beyond the end of this context manager.
        opened_adapters.add(self.get_adapter(url))

        settings = old_merge_environment_settings(self, url, proxies, stream, verify, cert)
        settings['verify'] = False

        return settings

    requests.Session.merge_environment_settings = merge_environment_settings

    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', InsecureRequestWarning)
            yield
    finally:
        requests.Session.merge_environment_settings = old_merge_environment_settings

        for adapter in opened_adapters:
            try:
                adapter.close()
            except:
                pass

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(("8.8.8.8", 80))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def isLoggedIn(func):
    """
    Decorator to ensure that a valid login is present when calling a method
    """
    @wraps(func)
    def login_wrapper(*args, **kwargs):
        # Script.log("####################################### CHECKING TOKEN #######################################", lvl=Script.ERROR)
        with PersistentDict("headers") as db:
            username = db.get("username")
            password = db.get("password")
            headers = db.get("headers")
            exp = db.get("exp", 0)
        if headers and exp > time.time():
            return func(*args, **kwargs)
        elif username and password:
            login(username, password)
            return func(*args, **kwargs)
        elif headers and exp < time.time():
            Script.notify(
                "Login Error", "Session expired. Please login again")
            executebuiltin(
                "RunPlugin(plugin://plugin.video.jiotv/resources/lib/main/login/)")
            return False
        else:
            Script.notify(
                "Login Error", "You need to login with Jio Username and password to use this add-on")
            executebuiltin(
                "RunPlugin(plugin://plugin.video.jiotv/resources/lib/main/login/)")
            return False
    return login_wrapper


def refresh_token():
    headers = getHeaders()
    if not headers:
        return
    url = "https://auth.media.jio.com/tokenservice/apis/v1/refreshtoken?langId=6"
    refresh_headers = {
        "accesstoken": headers.get("authToken",""),
        "uniqueid": headers.get("uniqueId",""),
        "devicetype":"phone",
        "os":"android",
        "user-agent":"okhttp/4.2.2",
        "versioncode": "285",
    }
    body = {
        "appName": "RJIL_JioTV",
        "deviceId": headers.get("deviceId",""),
        "refreshToken": headers.get("refreshToken","")
    }
    # Script.log("####################################### TOKEN REFRESH #######################################", lvl=Script.ERROR)
    # Script.log(url, lvl=Script.ERROR)
    # Script.log(refresh_headers, lvl=Script.ERROR)
    # Script.log(body, lvl=Script.ERROR)
    with no_ssl_verification():
        resp = urlquick.post(url, json=body, headers=refresh_headers, max_age=-1, verify=False, raise_for_status=False).json()
        if resp.get("authToken", "") != "":
            # Script.log("Token refreshed", lvl=Script.ERROR)            
            headers["authToken"] = resp.get("authToken")
            with PersistentDict("headers") as db:
                db["headers"] = headers
                db["exp"] = time.time() + 432000
        
    return None


def login(username, password, mode="unpw"):
    deviceId = "1e075302d2fb0b64"
    login_headers = {
        "appname":"RJIL_JioTV",
        "devicetype":"phone",
        "os":"android",
        "user-agent":"okhttp/4.2.2",
    }
    if "+91" not in username:
        username = "+91" + username
    body = {
        "number": base64.b64encode(username.encode()).decode(),
        "otp": password,
        "deviceInfo": {
            "consumptionDeviceName": "ONEPLUS A5000",
            "info": {
                "type": "android",
                "platform": {
                    "name": "OnePlus5",
                },
                "androidId": deviceId
            }
        }
    }
    # Script.log(body, lvl=Script.ERROR)
    resp = urlquick.post("https://jiotvapi.media.jio.com/userservice/apis/v1/loginotp/verify", json=body, headers=login_headers, max_age=-1, verify=False, raise_for_status=False).json()
    # Script.log(resp, lvl=Script.INFO)
    if resp.get("ssoToken", "") != "":
        _CREDS = {
            "authToken": resp.get("authToken"),
            "refreshToken": resp.get("refreshToken"),
            "jToken": resp.get("jToken"),
            "ssotoken": resp.get("ssoToken"),
            "userId": resp.get("sessionAttributes", {}).get("user", {}).get("uid"),
            "uniqueId": resp.get("sessionAttributes", {}).get("user", {}).get("unique"),
            "crmid": resp.get("sessionAttributes", {}).get("user", {}).get("subscriberId"),
        }
        headers = {
            "appkey": "NzNiMDhlYzQyNjJm",
            "deviceId": "1e075302d2fb0b64",            
            "User-Agent": "JioTV",
            "os": "Android",
            "deviceId": deviceId,
            "versionCode": "285",
            "devicetype": "phone",
            "srno": "200206173037",            
            "channelid": "100",
            "usergroup": "tvYR7NSNn7rymo3F",
            "lbcookie": "1"
        }
        headers.update(_CREDS)
        with PersistentDict("headers") as db:
            db["headers"] = headers
            db["exp"] = time.time() + 432000
            if mode == "unpw":
                db["username"] = username
                db["password"] = password
        Script.notify("Login Success", "")
        return None
    else:        
        msg = resp.get("message", "Unknow Error")
        Script.notify("Login Failed", msg)
        return msg


def sendOTP(mobile):
    url = "https://jiotvapi.media.jio.com/userservice/apis/v1/loginotp/send"
    login_headers = {
        "appname":"RJIL_JioTV",
        "devicetype":"phone",
        "os":"android",
        "user-agent":"okhttp/4.2.2",
        "Content-Type": "application/json",
    }
    if "+91" not in mobile:
        mobile = "+91" + mobile
    body = {"number": base64.b64encode(mobile.encode()).decode()}
    # Script.log(url, lvl=Script.ERROR)
    # Script.log(login_headers, lvl=Script.ERROR)
    # Script.log(body, lvl=Script.ERROR)
    resp = urlquick.post(url, json=body, headers=login_headers, verify=False, raise_for_status=False)    
    if resp.status_code == 400:
        Script.notify("Otp Send Failed", resp.get("message", ""))
        return resp.json().get("message")
    if resp.status_code == 204:
        Script.notify("Otp Sent", "")
        return None
    return None


def logout():
    with PersistentDict("headers") as db:
        del db["headers"]
    Script.notify("You\'ve been logged out", "")


def getHeaders():
    with PersistentDict("headers") as db:
        return db.get("headers", False)


def getTokenParams():
    def magic(x): return base64.b64encode(hashlib.md5(x.encode()).digest()).decode().replace(
        '=', '').replace('+', '-').replace('/', '_').replace('\r', '').replace('\n', '')
    pxe = str(int(time.time()+(3600*9.2)))
    jct = magic("cutibeau2ic9p-O_v1qIyd6E-rf8_gEOQ"+pxe)
    return {"jct": jct, "pxe": pxe, "st": "9p-O_v1qIyd6E-rf8_gEOQ"}


def check_addon(addonid, minVersion=False):
    """Checks if selected add-on is installed."""
    try:
        curVersion = Script.get_info("version", addonid)
        if minVersion and LooseVersion(curVersion) < LooseVersion(minVersion):
            # Script.log('{addon} {curVersion} doesn\'t setisfy required version {minVersion}.'.format(
                # addon=addonid, curVersion=curVersion, minVersion=minVersion))
            Dialog().ok("Error", "{minVersion} version of {addon} is required to play this content.".format(
                addon=addonid, minVersion=minVersion))
            return False
        return True
    except RuntimeError:
        Script.log('{addon} is not installed.'.format(addon=addonid))
        if not _install_addon(addonid):
            # inputstream is missing on system
            Dialog().ok("Error",
                        "[B]{addon}[/B] is missing on your Kodi install. This add-on is required to play this content.".format(addon=addonid))
            return False
        return True


def _install_addon(addonid):
    """Install addon."""
    try:
        # See if there's an installed repo that has it
        executebuiltin('InstallAddon({})'.format(addonid), wait=True)

        # Check if add-on exists!
        version = Script.get_info("version", addonid)

        Script.log(
            '{addon} {version} add-on installed from repo.'.format(addon=addonid, version=version))
        return True
    except RuntimeError:
        Script.log('{addon} add-on not installed.'.format(addon=addonid))
        return False
