# -*- coding: utf-8 -*-

"""resolve and formats ethernet Hardware Address (OUI)

Synopsis: <trigger> {##:##:##[:##:##:##]|##-##-##[-##-##-##]|######[######]}

This plugin fetchs a copy from  http://standards-oui.ieee.org/oui/oui.txt and converts to local json DB
oui.txt/oui.json is stored in dataLocation(). Automatic Update once a month at startup. 

Most distros defaults /var/lib/ieee-data/oui.txt is pretty outdated, but can be used as fallback
Optional, an external API can be used. As default we preffer local/offline data
"""

from albert import *
from datetime import datetime
import requests
import os
import re
import json


__title__ = "MAC-HWAddr"
__version__ = "0.1.1"
__triggers__ = "mac "
__authors__ = ["Stefan Grosser"]
__py_deps__ = ["requests","datetime","os","re","json"]

# Settings and Defaults
oui_json = os.path.join(dataLocation(), "oui.json")
oui_txt_path = os.path.join(dataLocation(), "oui.txt")
oui_txt_url='http://standards-oui.ieee.org/oui/oui.txt'
oui_txt_path_fallback = '/var/lib/ieee-data/oui.txt'
api_url = 'https://api.macvendors.com/'

use_macvendors = False

iconPath = os.path.dirname(__file__)+"/nic.svg"


def initialize():
    """ Init checks if a database file exists. 
    if its old or inexistent, it calls a fetch and convert function for a simple key-value database file. 
    """

    age = 99
    global macdb

    if os.path.isfile(oui_json):
        age = get_file_age(oui_json)

        debug("HWAddr {} age is {}".format(oui_json,age))

        if age >= 30:
            oui_txt = fetch(oui_txt_url,oui_txt_path)
            convert(oui_txt,oui_json)
    else:
        oui_txt  = fetch(oui_txt_url,oui_txt_path)
        convert(oui_txt,oui_json)

    with open(oui_json) as f:
        macdb = json.load(f)
    

    debug("HWAddr initialized with {} entries".format(len(macdb)))

def fetch(url,dst):
    """
    Fetchs a file and returns its path
    """
    try:
        debug("HWAddr fetching  {} and stores to {}".format(url,dst))
        data = requests.get(url)
        with open(dst, 'wb') as f:
            f.write(data.content)
        return dst
    except Exception as e:
        warning("HWAddr fetch failed "+ str(e))
        #return fallback path
        return oui_txt_path_fallback

def convert(src,dst):
    """
    Converts oui.txt and stores as json
    (maybe CSV is smaller/faster than json? or nosql?)
    """

    debug("HWAddr converting "+src)

    macdb = {}

    list = re.findall(r'(\w{6})\s+\(base 16\)\s+(.+)', open(src).read())

    #convert group list to a key-value pair dict. they should be already unique...
    for i in list:
        macdb[i[0]] = i[1]

    debug("HWAddr created with {} entries".format(len(macdb)))

    #store as json
    with open(dst, 'w') as outfile:
        json.dump(macdb, outfile)
    
    debug("HWAddr stored as "+dst)     

def bool2str(var):
    """
    Just a stupid function for nicer Bool output"""
    if var:
        return "enable"
    else:
        return "disable"

def toggle_api(newset):
    """ Temporary toggles global variable of use_macvendors"""
    global use_macvendors
    debug('HWAddr API toggled to '+ str(newset))
    use_macvendors = newset

def get_file_age(file):
    """ returns a file age"""
    st=os.stat(file)
    age = datetime.fromtimestamp(st.st_mtime) - datetime.today()
    return abs(age.days)

def handleQuery(query):
    """ Main albert function """
    global macdb
    if not query.isTriggered:
        return

    if query.isValid and query.isTriggered:
        #return some infos
        if query.string.startswith("info") or query.string == "":           
            return Item(id=__title__,
            icon=iconPath,
            text="Database with {} entries".format(len(macdb)),
            subtext="DB is {} days old. API lookups are {}d".format(get_file_age(oui_json),bool2str(use_macvendors)),
            actions = [
                        FuncAction("{} API Lookups".format(bool2str(not use_macvendors)), lambda: toggle_api(not use_macvendors)),
                        ClipAction("Copy Vendor {}".format(oui_txt_path), oui_txt_path),
                        ClipAction("Copy Vendor {}".format(oui_json), oui_json),
                        ClipAction("Copy Source {}".format(oui_txt_url), oui_txt_url)
                    ])

        #Default an empty response
        actions = []
        text = "no result for "+query.string
        subtext = ""

        #Splits main query string in to generic MAC addr without .:-
        mac = query.string.replace(":","").replace(".","").replace("-","").strip().upper()

        #Only lookup if its valid MAC with atleast 6 charts
        if re.match('^[0-9A-F]{6}|^0242', mac):

            debug ("MAC lookup: " + mac +" strip: "+ mac[0:6] +" len: "+str(len(mac)))
            
            #Check local DB First
            if mac[0:6] in macdb:
                debug ("Found lookup " + mac[0:6])
                subtext = "found in local db. "
                text = str(macdb[mac[0:6]])
                actions.append(ClipAction("Copy Vendor {}".format(macdb[mac[0:6]]), str(macdb[mac[0:6]])))
                actions.append(ClipAction("Copy OUI {}".format(mac[0:6]), str(mac[0:6])))
            
            elif mac.startswith("0242"):
                text = "Docker?"

            else:
                #Check API if enabled
                if use_macvendors:
                    r = requests.get('https://api.macvendors.com/'+mac[0:6])
                    if r.status_code == 200:
                        text = r.content
                        subtext = "found on macvendors.com. "
                        actions.append(ClipAction("Copy Vendor {}".format(r.content), r.content))
                        actions.append(ClipAction("Copy OUI {}".format(mac[0:6]), str(mac[0:6])))
                else:
                    subtext = "not found in local db. check macvendors.com? "
                    actions.append(UrlAction(text="Open macvendors.com", url="https://api.macvendors.com/%s" % (mac[0:6]))),
                    actions.append(FuncAction("Temporary enable API Lookups", lambda: toggle_api(True)))
            

            #finally, append Additional Format option if it's a valid full lenght MAC
            if re.match('[0-9A-F]{12}', mac):
                subtext += "Valid MAC, reformat?"
                format1 = ".".join(["%s" % (mac[i:i+4]) for i in range(0, 12, 4)]).lower()
                format2 = ":".join(["%s" % (mac[i:i+2]) for i in range(0, 12, 2)])
                format3 = "-".join(["%s" % (mac[i:i+2]) for i in range(0, 12, 2)])

                actions.append(ClipAction("Copy {}".format(format1), str(format1)))
                actions.append(ClipAction("Copy {}".format(format2), str(format2)))
                actions.append(ClipAction("Copy {}".format(format3), str(format3)))        

        else:
            subtext = "Expect 6 Char OUI or Full MAC: {##:##:##[:##:##:##]|##-##-##[-##-##-##]|######[######]}"

    return Item(
            id = __title__,
            icon = iconPath,
            text = text,
            subtext = subtext,
            actions=actions
        )