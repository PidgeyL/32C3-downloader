import argparse
import os
import re
import sys
import urllib.request as req
import zipfile
from bs4 import BeautifulSoup
from io import BytesIO

_DownloadPath='32C3-downloads'
_Slides='https://lab.dsst.io/32c3-slides/'
_Recordings='http://mirror-1.server.selfnet.de/CCC/congress/32C3/%s'

def fetchImages(language, translations):
  # Build list of audio links
  soup = BeautifulSoup(req.urlopen(_Recordings%"mp3"), "lxml")
  links=soup.findAll('a', attrs={'href': re.compile("^32c3-[0-9]{4}-%s-.*"%language)})
  for a in links: a["orig"]=_Recordings%"mp3/"
  if translations:
    soup = BeautifulSoup(req.urlopen(_Recordings%"mp3-translated"), "lxml")
    links.extend(soup.findAll('a', attrs={'href': re.compile("^32c3-[0-9]{4}-%s-.*"%language)}))
    for a in links: a["orig"]=_Recordings%"mp3-translated/"
  # Loop over presentations
  for i, a in enumerate(links):
    pres_id=a.get('href')[5:9]
    title  =a.get('href')[13:-4]
    path   ="%s/%s/"%(_DownloadPath, title)
    try:
      # Status
      sys.stdout.write('%i/%i - "%s"\r' % (i, len(links), title[0:50]))
      sys.stdout.flush()
      # Download & extract pictures
      data = req.urlopen("%sslides/%s.zip"%(_Slides, pres_id)).read()
      pictureZip = zipfile.ZipFile(BytesIO(data), 'r')
      os.makedirs(path)
      for info in pictureZip.infolist():
        if info.file_size != 0: # not a folder
          name = info.filename
          with open(path+name.split("/")[-1], "wb") as f:
            f.write(pictureZip.read(name))
      # Fetch mp3
      with open("%s%s.mp3"%(path, title), "wb") as f:
        f.write(req.urlopen(a.get('orig') + a.get('href')).read())
    except Exception as e:
      print('Failed to download presentation: "%s"'%title)

def prepare():
  if not os.path.exists(_DownloadPath):
    os.makedirs(_DownloadPath)
  else:
    sys.exit("Path already exists: %s"%_DownloadPath)


if __name__ == '__main__':
  # arguments
  parser = argparse.ArgumentParser(description='''Downloads 32C3 content''')
  parser.add_argument('-v', action='store_true',                        help='Download video (default: pictures+mp3)')
  parser.add_argument('-l', metavar='language', type=str, default="en", help='Language: [en/de] (default: en)')
  parser.add_argument('-t', action='store_true',                        help='Include translations (default: false)')
  args = parser.parse_args()

  prepare()
  if not args.l.lower() in ["en", "de"]: sys.exit("Language needs to be en or de")
  try:
    if args.v: print("fetch video")
    else:  fetchImages(args.l, args.t)
  except KeyboardInterrupt:
    print("\nInterrupted by user")
