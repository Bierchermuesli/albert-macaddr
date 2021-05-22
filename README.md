# Albert MAC-hwaddr Lookup Module
resolve and formats ethernet Hardware Address (OUI)

Synopsis: `mac {##:##:##[:##:##:##]|##-##-##[-##-##-##]|######[######]}`

This plugin fetchs a copy from  http://standards-oui.ieee.org/oui/oui.txt and converts to local json DB. Automatic Update once a month at startup. 

Most distros ship /var/lib/ieee-data/oui.txt, but it's pretty outdated. This DB will be used as fallback
  
An external API can be used, as default we prefer local/offline data


  
![Default Trigger: `mac [any kind of hw addr]`](https://user-images.githubusercontent.com/13567009/119220474-0b9f4400-baeb-11eb-9e2c-49fca40330cb.gif)


# Installation

Simple clone to Albert plugin dir and activate in Albert Python Modules
```
git clone https://github.com/Bierchermuesli/albert-macaddr.git ~/.local/share/albert/org.albert.extension.python/modules/macaddr
```
# Bugs / Feedback
always welcome, its just a random amateur code...
