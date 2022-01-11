import os
from pathlib import Path
import datetime

import requests as r
from bs4 import BeautifulSoup


# Constants

API_KEY = os.environ['PUSHOVER_TOKEN']

REFERENCE = """VTL1
1 Feb - 6 Feb Start Selling From  10 Jan 2022, 10am
The designated Vaccination Travel Lane (VTL) bus between Singapore and Malaysia via land transport.
LEARN MORE
"""

# Convenience wrapper

class VTLMonitor:
  def __init__(self):
    self.url = "https://www.causewaylink.com.my/"

  def send_notification(self):
    r.post(
      "https://api.pushover.net/1/messages.json",
      data = {
        "token": API_KEY,
        "user": "ukcppm8wzmu58ideby57h26td6czw2",
        "message": "VTL change detected!\nhttps://www.causewaylink.com.my/"
      }
    )

  def is_different(self):
    result = r.get("https://www.causewaylink.com.my/")
    soup = BeautifulSoup(result.text, 'html.parser')

    scraped_text = ""

    for x in soup.find_all(id="slider-7-slide-15-layer-7"):
      scraped_text += x.get_text()

    return REFERENCE != scraped_text, scraped_text

  def run(self):
    different, scraped_text = self.is_different()

    if different:
      print("Difference detected at", datetime.datetime.now())
      print("Original:", REFERENCE)
      print("New text:", scraped_text)
      self.send_notification()
    else:
      print("No difference detected at", datetime.datetime.now())

    print("=" * 10)
