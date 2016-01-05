from bs4 import BeautifulSoup
import urllib.request as req
import zipfile
import re
import os
import sys
from io import BytesIO

_DownloadPath='32C3-downloads'
_Slides='https://lab.dsst.io/32c3-slides/'

def progressbar(it, prefix="Preparing ", size=50):
  count = len(it)
  def _show(_i):
    if count != 0 and sys.stdout.isatty():
      x = int(size * _i / count)
      sys.stdout.write("%s[%s%s] %i/%i\r" % (prefix, "#" * x, " " * (size - x), _i, count))
      sys.stdout.flush()

  _show(0)
  for i, item in enumerate(it):
    yield item
    _show(i + 1)
  sys.stdout.write("\n")

def fetchAll():
  slide_page = req.urlopen(_Slides)
  soup = BeautifulSoup(slide_page, "lxml")
  links=soup.findAll('a', attrs={'href': re.compile("^7")})
  for i, a in enumerate(links):
    link  = a.get('href')
    div   = a.findChild("div")
    title = div.contents[0].strip()
    path  = "%s/%s/"%(_DownloadPath, title)
    try:
      # Status
      sys.stdout.write('%i/%i - "%s"\r' % (i, len(links), title[0:50]))
      sys.stdout.flush()
      # Download & extract pictures
      data = req.urlopen("%sslides/%s.zip"%(_Slides, link.split(".")[0])).read()
      pictureZip = zipfile.ZipFile(BytesIO(data), 'r')
      os.makedirs(path)
      for name in pictureZip.namelist():
        if os.path.isfile(name):
          with open(path+name.split("/")[-1], "wb") as f:
            f.write(pictureZip.read(name))
    except Exception as e:
      print(e)
      print('Failed to download presentation: "%s"'%title)

def prepare():
  if not os.path.exists(_DownloadPath):
    os.makedirs(_DownloadPath)
  else:
    sys.exit("Path already exists: %s"%_DownloadPath)

prepare()
fetchAll()
