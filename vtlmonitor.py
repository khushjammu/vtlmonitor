import os
import abc
from pathlib import Path
import datetime

import requests as r
from bs4 import BeautifulSoup

API_TOKEN = os.environ['PUSHOVER_TOKEN']

REFERENCE_TRANSFER = """<table border="1" style="border-collapse:collapse">\n<tr style="background-color:yellow"><th style="padding:3px">Departure Date</th><th style="padding:3px">Singapore to Johor Bahru</th><th style="padding:3px">Johor Bahru to Singapore</th></tr>\n<tr><td style="font-weight:bold">07/02/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr><tr><td style="font-weight:bold">08/02/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr><tr><td style="font-weight:bold">09/02/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr><tr><td style="font-weight:bold">10/02/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr><tr><td style="font-weight:bold">11/02/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr><tr><td style="font-weight:bold">12/02/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr><tr><td style="font-weight:bold">13/02/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr><tr><td style="font-weight:bold">14/02/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr><tr><td style="font-weight:bold">15/02/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr><tr><td style="font-weight:bold">16/02/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr><tr><td style="font-weight:bold">17/02/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr><tr><td style="font-weight:bold">18/02/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr><tr><td style="font-weight:bold">19/02/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr><tr><td style="font-weight:bold">20/02/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr><tr><td style="font-weight:bold">21/02/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr><tr><td style="font-weight:bold">22/02/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr><tr><td style="font-weight:bold">23/02/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr><tr><td style="font-weight:bold">24/02/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr><tr><td style="font-weight:bold">25/02/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr><tr><td style="font-weight:bold">26/02/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr><tr><td style="font-weight:bold">27/02/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr><tr><td style="font-weight:bold">28/02/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr><tr><td style="font-weight:bold">01/03/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr><tr><td style="font-weight:bold">02/03/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr><tr><td style="font-weight:bold">03/03/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr><tr><td style="font-weight:bold">04/03/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr><tr><td style="font-weight:bold">05/03/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr><tr><td style="font-weight:bold">06/03/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr><tr><td style="font-weight:bold">07/03/2022</td><td style="color:red">Full</td><td style="color:red">Full</td></tr>\n</table>"""

REFERENCE_CAUSEWAYLINK = """VTL1
14 Feb - 28 Feb Start Selling From  14 Jan 2022, 9am
The designated Vaccination Travel Lane (VTL) bus between Singapore and Malaysia via land transport.
LEARN MORE
"""

# Convenience wrapper

class BaseMonitor:
  @abc.abstractmethod
  def check_if_different(self):
    raise NotImplementedError

  def log(self, text):
    print(text)

  def send_notification(self):
    r.post(
      "https://api.pushover.net/1/messages.json",
      data = {
        "token": API_TOKEN,
        "user": "ukcppm8wzmu58ideby57h26td6czw2",
        "message": f"VTL change detected!\n{self.url}"
      }
    )

  def run(self):
    is_different, reference, scraped_text = self.check_if_different()

    s = ""

    if is_different:
      s += f"Difference detected at {datetime.datetime.now()}\n"
      s += f"URL: {self.url}\n"
      s += f"Orignal: {reference}\n"
      s += f"New text: {scraped_text}\n"

      self.send_notification()
    else:
      s += f"No difference detected at {datetime.datetime.now()}\n"
      s += f"URL: {self.url}\n"

    s += "=" * 10

    self.log(s)


class TranstarMonitor(BaseMonitor):
  def __init__(self):
    self.url = "https://mybooking.transtar.travel/transtar-schedule"

  def check_if_different(self):
    result = r.get(self.url)
    soup = BeautifulSoup(result.text, 'html.parser')

    scraped_text = str(soup.table)

    return REFERENCE_TRANSFER != scraped_text, REFERENCE_TRANSFER, scraped_text


class CausewayLinkMonitor(BaseMonitor):
  def __init__(self):
    self.url = "https://www.causewaylink.com.my/"

  def check_if_different(self):
    result = r.get(self.url)
    soup = BeautifulSoup(result.text, 'html.parser')

    scraped_text = ""

    for x in soup.find_all(id="slider-7-slide-15-layer-7"):
      scraped_text += x.get_text()

    return REFERENCE_CAUSEWAYLINK != scraped_text, REFERENCE_CAUSEWAYLINK, scraped_text

if __name__ == "__main__":
  t = TranstarMonitor()
  t.run()

  # c = CausewayLinkMonitor()
  # c.run()
