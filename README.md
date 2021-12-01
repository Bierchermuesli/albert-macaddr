# Albert MAC-hwaddr Lookup Module
This is a sipmle query modul for awsome [Albert Launcher](https://albertlauncher.github.io/). It resolves and re-formats any kind of ethernet Hardware Address (OUI)

Synopsis: `mac {##:##:##[:##:##:##]|##-##-##[-##-##-##]|######[######]}`

![Default Trigger: `mac [any kind of hw addr]`](https://user-images.githubusercontent.com/13567009/119220474-0b9f4400-baeb-11eb-9e2c-49fca40330cb.gif)

Background details: This plugin fetchs a copy from  http://standards-oui.ieee.org/oui/oui.txt and converts to local json DB. Automatic Updates once a month at startup. Most distros ships /var/lib/ieee-data/oui.txt, but it's pretty outdated but will be used as fallback. 
  
An external API ca be used if no local db found or no local result is returned. In general we prefer local db for offline working and privacy purposes.

# Installation

Simple clone to Albert plugin directory and activate in Albert Python Modules Settings. Python3 and only default modules are required.
```
git clone https://github.com/Bierchermuesli/albert-macaddr.git ~/.local/share/albert/org.albert.extension.python/modules/macaddr
```

# Bugs / Feedback
always welcome, just some ad hoc coding
