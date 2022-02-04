import os
import requests as r
from vtlmonitor import CausewayLinkMonitor

try:
  t = CausewayLinkMonitor()
  t.run()
except Exception as e:
  # try to send an emergency push notification
  r.post(
    "https://api.pushover.net/1/messages.json",
    data = {
      "token": os.environ['PUSHOVER_TOKEN'],
      "user": "ukcppm8wzmu58ideby57h26td6czw2",
      "message": f"Unknown error encountered by CausewayLinkMonitor!"
    }
  )
  raise e