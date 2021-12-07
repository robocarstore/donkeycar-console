



sudo nmcli conn down id Hotspot; sleep 5; sudo nmcli device wifi connect Proactive_JBB_Guest password 74298342

sudo nmcli conn down id Hotspot-1; sleep 5; sudo nmcli device wifi connect PROACTIVE_JBB_5G password 83018231

sudo nmcli conn down id Proactive_JBB_Guest; sleep 5; sudo nmcli device wifi connect Proactive_JBB_5G password 83018231



f
saudo nmcli conn down id Proactive_JBB_5G; sleep 5; sudo nmcli conn up id Hotspot

 sudo nmcli conn down id PROACTIVE_JBB_5G; sleep 5; sudo nmcli device wifi connect JPhone password abcd1234

 sudo nmcli conn down id Hotspot-1; sleep 5; sudo nmcli device wifi connect JPhone password abcd1234



 sudo nmcli conn down id Hotspot-1; sleep 5; sudo nmcli conn up id JPhone