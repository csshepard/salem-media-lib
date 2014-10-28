__author__ = 'chris.shepard'
from bs4 import BeautifulSoup
from flask import Flask, make_response, render_template, request
import urllib.request
import urllib.parse

app = Flask(__name__)


@app.route('/')
def mrss_gen():
    url = request.args.get('url', "https://sites.google.com/a/salem.edu/media-wall/home/media-library")
    if url[0].lower() != 'h' and url[0] != '/':
        url = '//' + url
    url_parsed = urllib.parse.urlparse(url, 'https')
    print(url_parsed)
    try:
        page = urllib.request.urlopen(url_parsed.geturl())
    except urllib.error.URLError:
        return make_response(url_parsed.geturl()+' not found', 404)
    links = get_links(page.read(), url_parsed.netloc)
    res = make_response(render_template('mrss_template.xml', items=links), 200)
    res.headers['Content-Type'] = 'application/rss+xml; charset=UTF-8'
    return res


def get_links(page, netloc):
    links = []
    supported_formats = {'jpg': 'jpeg',
                         'jpeg': 'jpeg',
                         'bmp': 'bmp',
                         'gif': 'gif',
                         'tiff': 'tiff',
                         'tif': 'tiff'}
    soup = BeautifulSoup(page)
    for atag in soup.find_all('a'):
        link = atag.get('href')
        if link is not None:
            link_list = list(urllib.parse.urlparse(link, 'https'))
            link_list[3] = link_list[4] = link_list[5] = ''
            if link_list[1] == '':
                link_list[1] = netloc
            link_split = link_list[2].split('.')
            if link_split[-1] in supported_formats.keys():
                extension = supported_formats[link_split[-1]]
                desc = link_list[2].split('/')[-1]
                link = urllib.parse.urlunparse(link_list)
                if (link, extension, desc) not in links:
                    links.append((link, extension, desc))
    return links

if __name__ == '__main__':
    app.run()