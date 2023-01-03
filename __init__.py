# -*- coding:    utf-8 -*-

"""resolve and formats ethernet hardware address (OUI)

Synopsis: <trigger> {##:##:##[:##:##:##]|##-##-##[-##-##-##]|######[######]}

This plugin fetchs a copy from  http://standards-oui.ieee.org/oui/oui.txt and converts to local json DB.
oui.txt/oui.json is stored in dataLocation(). Automatic update once a month at startup. 

Most distros ships /var/lib/ieee-data/oui.txt but it's pretty outdated. This will be used as fallback.
An external API can be used, but we prefer local/offline data
"""

from albert import *
from datetime import datetime
import requests
import os
import re
import json


md_iid = "0.5"
md_version = "1.2"
md_id = "mac"
md_name = "MAC-HWAddr"
md_description = "resolve and formats ethernet hardware address"
md_license = "BSD-2"
md_url = "https://github.com/Bierchermuesli/albert-macaddr"
md_maintainers = "@Bierchermuesli"
md_authors = "@Bierchermuesli"
md_lib_dependencies = ["requests","datetime","os","re","json"]

# Settings and Defaults
oui_json = os.path.join(dataLocation(), "oui.json")
oui_txt_path = os.path.join(dataLocation(), "oui.txt")
oui_txt_url='http://standards-oui.ieee.org/oui/oui.txt'
oui_txt_path_fallback = '/var/lib/ieee-data/oui.txt'
api_url = 'https://api.macvendors.com/'



iconPath = os.path.dirname(__file__)+"/nic.svg"


class Plugin(QueryHandler):    

    use_macvendors = False

    def id(self):
        return md_id

    def name(self):
        return md_name

    def description(self):
        return md_description

    def initialize(self):
        """ Init checks if a database file exists. 
        if its old or inexistent, it calls a fetch and convert function for a simple key-value database file. 
        """
        age = 30
        global macdb

        if os.path.isfile(oui_json):
            age = self.get_file_age(oui_json)

            debug("HWAddr {} age is {}".format(oui_json,age))

            if age >= 30:
                oui_txt = self.fetch(oui_txt_url,oui_txt_path)
                self.convert(oui_txt,oui_json)
        else:
            oui_txt  = self.fetch(oui_txt_url,oui_txt_path)
            self.convert(oui_txt,oui_json)

        with open(oui_json) as f:
            macdb = json.load(f)
        

        debug("HWAddr initialized with {} entries".format(len(macdb)))


    def fetch(self,url,dst):
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


    def convert(self,src,dst):
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

    def bool2str(self,var):
        """
        Just a stupid function for nicer Bool output"""
        if var:
            return "enable"
        else:
            return "disable"

    def toggle_api(self,newset):
        """ Temporary toggles global variable of use_macvendors"""
        global use_macvendors
        debug('HWAddr API toggled to '+ str(newset))
        self.use_macvendors = newset

    def get_file_age(self,file):
        """ returns a file age"""
        st=os.stat(file)
        age = datetime.fromtimestamp(st.st_mtime) - datetime.today()
        return abs(age.days)

    def handleQuery(self, query):
        """ Main albert function """
        global macdb

        if query.string.startswith("info") or query.string == "":      
            query.add(
                Item(id=md_name,
                text="Database with {} entries".format(len(macdb)),
                subtext="DB is {} days old. API lookups are {}d".format(self.get_file_age(oui_json),self.bool2str(self.use_macvendors)),
                icon=[iconPath],
                actions = [
                            Action("function","{} API Lookups".format(self.bool2str(not self.use_macvendors)),lambda: self.toggle_api(not self.use_macvendors)), 
                            Action("clip","Copy Source {}".format(oui_txt_url),lambda: setClipboardText(text=oui_txt_url)),     
                            Action("clip","Copy Vendor {}".format(oui_json),lambda: setClipboardText(text=oui_json)),            
                            Action("clip","Copy Vendor {}".format(oui_txt_path),lambda: setClipboardText(text=oui_txt_path))
                ]
                ))

        #as this qerry results always only one item, we assamble the ALT actions first, lets start with a default empty response
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
                debug ("Found:" + macdb[mac[0:6]])
                subtext = "found in local db. "
                text = str(macdb[mac[0:6]])
                actions.append(Action("clip","Copy Vendor {}".format(macdb[mac[0:6]]),lambda: setClipboardText(text=str(macdb[mac[0:6]]))))
                actions.append(Action("clip","Copy OUI {}".format(mac[0:6]),lambda: setClipboardText(text=str(mac[0:6]))))
            
            elif mac.startswith("0242"):
                text = "Docker?"

            else:
                #Check API if enabled
                if self.use_macvendors:
                    r = requests.get('https://api.macvendors.com/'+mac[0:6])
                    if r.status_code == 200:
                        text = r.content
                        subtext = "found on macvendors.com. "
                        actions.append(Action("clip","Copy Vendor {}".format(r.content), lambda: setClipboardText(text=r.content)))
                        actions.append(Action("clip","Copy OUI {}".format(rmac[0:6]), lambda: setClipboardText(text=str(mac[0:6]))))
                    else:
                        subtext = "even not on macvendors.com."
                else:
                    subtext = "not found in local db. check macvendors.com? "
                    actions.append(    
                            Action("macvendors", "visit macvendors.com", lambda: openUrl("https://api.macvendors.com/%s" % (mac[0:6]))))
                    actions.append(                                 
                            Action("toggleAPI","Temporary enable API Lookups", lambda: self.toggle_api(True))              
                    )

            #finally, append Additional Format option if it's a valid full lenght MAC
            if re.match('[0-9A-F]{12}', mac):
                subtext += "Valid MAC! press ALT for reformat options."
                format1 = ".".join(["%s" % (mac[i:i+4]) for i in range(0, 12, 4)]).lower()
                format2 = ":".join(["%s" % (mac[i:i+2]) for i in range(0, 12, 2)])
                format3 = "-".join(["%s" % (mac[i:i+2]) for i in range(0, 12, 2)])

                actions.append(Action("clip","Copy {}".format(format1),lambda: setClipboardText(text=str(format1))))
                actions.append(Action("clip","Copy {}".format(format2),lambda: setClipboardText(text=str(format2))))
                actions.append(Action("clip","Copy {}".format(format3),lambda: setClipboardText(text=str(format3))))                                                
                     

        else:
            text="Invalid MAC"
            subtext="Expect first 6 Char or Full MAC: {##:##:##[:##:##:##]|##-##-##[-##-##-##]|######[######]}"

        query.add(Item(
                id = md_name,
                icon = [iconPath],
                text = text,
                subtext = subtext,
                actions=actions
            ))
