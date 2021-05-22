# Albert Mac MAC-hwaddr Plugin
resolve and formats ethernet Hardware Address (OUI)

Synopsis: <trigger> {##:##:##[:##:##:##]|##-##-##[-##-##-##]|######[######]}

This plugin fetchs a copy from  http://standards-oui.ieee.org/oui/oui.txt and converts to local json DB. Automatic Update once a month at startup. 

Most distros /var/lib/ieee-data/oui.txt is pretty outdated, but will be used as fallback
Optional, an external API can be used. As default we prefer local/offline data


Default Trigger: `mac [any kind of hw addr]`
  
![image](https://user-images.githubusercontent.com/13567009/119220336-5076ab00-baea-11eb-84a4-b2d0911835b6.png)


# Installation

Simple clone to Albert plugin dir and activate in Albert Python Modules
```
git clone https://github.com/Bierchermuesli/albert-macaddr.git ~/.local/share/albert/org.albert.extension.python/modules/macaddr
```
# Bugs / Feedback
always welcome, its just a random amateur code...
