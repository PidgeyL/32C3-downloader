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
_Recordings='http://mirror-1.server.selfnet.de/CCC/congress/%s/%s'


def prepare():
  if not os.path.exists(_DownloadPath):
    os.makedirs(_DownloadPath)
  else:
    sys.exit("Path already exists: %s"%_DownloadPath)

def getPresentations(con):
  presentations=[]
  soup = BeautifulSoup(req.urlopen(_Recordings%(con, "mp3")), "lxml")
  for a in soup.findAll('a', attrs={'href': re.compile("^%s-[0-9]{4}-.*"%con.lower())}):
    a=a.get('href')
    presentations.append({'id': a[5:9], 'lan': a[10:12], 'title': a[13:-4], 'con': con})
  return presentations

def fetchImages(pres, lan):
  # Fetch mp3
  if pres['lan'] == lan: url=_Recordings%(pres['con'], "mp3")
  else:                  url=_Recordings%(pres['con'], "mp3-translated")
  url+="/%s-%s-%s-%s.mp3"%(pres['con'].lower(), pres['id'], lan, pres['title'])
  with open("%s%s.mp3"%(path, pres['title']), "wb") as f:
    f.write(req.urlopen(url).read())
  # Download & extract pictures
  data = req.urlopen("%sslides/%s.zip"%(_Slides, pres['id'])).read()
  pictureZip = zipfile.ZipFile(BytesIO(data), 'r')
  for info in pictureZip.infolist():
    if info.file_size != 0: # not a folder
      with open(path+info.filename.split("/")[-1], "wb") as f:
        f.write(pictureZip.read(info.filename))

def fetchVideo(pres, lan):
  url=_Recordings%(pres['con'], "h264-hd-web")
  url+="/%s-%s-%s-%s.mp4"%(pres['con'].lower(), pres['id'], lan, pres['title'])
  path="%s/%s/"%(_DownloadPath, pres['title'])
  with open("%s%s.mp4"%(path, pres['title']), "wb") as f:
    f.write(req.urlopen(url).read())

def download(downloadlist, video, language):
  for i, pres in enumerate(downloadlist):
    # Status
    sys.stdout.write('%i/%i - "%s"\r' % (i, len(downloadlist), pres['title'][0:50]))
    sys.stdout.flush()
    try:
      # Make folder
      path="%s/%s/"%(_DownloadPath, pres['title'])
      os.makedirs(path)
      # Fetch content
      if video: fetchVideo(pres, language)
      else:     fetchImages(pres, language)
    except Exception as e:
      print(e)
      print('Failed to download presentation: "%s"'%pres['title'])

if __name__ == '__main__':
  # arguments
  parser = argparse.ArgumentParser(description='''CCConference content downloader''')
  parser.add_argument('-v', action='store_true',                            help='Download video (default: pictures+mp3)')
  parser.add_argument('-l', metavar='language', type=str, default="en",     help='Language: [en/de] (default: en)')
  parser.add_argument('-t', action='store_true',                            help='Include translations (default: false)')
  args = parser.parse_args()

  if not args.l.lower() in ["en", "de"]: sys.exit("Language needs to be en or de")
  try:
    # Prepare download folder
    prepare()
    # Get presentations
    downloadlist=getPresentations("32C3")
    # Filter out translations if needed
    if not args.t: downloadlist=[p for p in downloadlist if p['lan'] == args.l]
    # download
    download(downloadlist, args.v, args.l)
  except KeyboardInterrupt:
    print("\nInterrupted by user")
