# Albert Mac MAC-hwaddr Plugin
resolve and formats ethernet Hardware Address (OUI)

Synopsis: <trigger> {##:##:##[:##:##:##]|##-##-##[-##-##-##]|######[######]}

This plugin fetchs a copy from  http://standards-oui.ieee.org/oui/oui.txt and converts to local json DB
oui.txt/oui.json is stored in dataLocation(). Automatic Update once a month at startup. 

Most distros defaults /var/lib/ieee-data/oui.txt is pretty outdated, but can be used as fallback
Optional, an external API can be used. As default we preffer local/offline data


Default Trigger: `mac [any kind of hw addr]`


# Installation

Simple clone to 
`git clone https://github.com/Bierchermuesli/albert-macaddr.git ~/.local/share/albert/org.albert.extension.python/modules/macaddr`and activate in Albert

# Bugs / Feedback
always welcome, the code is not so pretty I guess... 
