__author__ = 'chris.shepard'
from bs4 import BeautifulSoup
from flask import Flask, make_response, render_template, request, url_for
import urllib.parse
import requests

app = Flask(__name__)


@app.route('/')
def mrss_gen():
    url = request.args.get('url',
                           "https://sites.google.com/a/salem.edu/"
                           "media-wall/home/media-library")
    url_parsed = urllib.parse.urlparse(url, 'https')
    if url_parsed.netloc == '':
        url_parsed = urllib.parse.urlparse('//'+url, 'https')
    try:
        page = requests.get(url_parsed.geturl())
        links = get_links(page.text, url_parsed.netloc)
    except requests.exceptions.ConnectionError:
        links = [(url_for('static', filename='mrss_default.jpg',
                      _external=True, _scheme='https'), 'jpeg',
                      'No Media Found')]
    res = make_response(render_template('mrss_template.xml', items=links), 200)
    res.headers['Content-Type'] = 'text/xml; charset=UTF-8'
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
    for a_tag in soup.find_all('a'):
        link = a_tag.get('href')
        if link is not None:
            link_list = list(urllib.parse.urlparse(link, 'https'))
            link_list[3] = link_list[4] = link_list[5] = ''
            if link_list[1] == '':
                link_list[1] = netloc
            link_split = link_list[2].split('.')
            if link_split[-1].lower() in supported_formats.keys():
                extension = supported_formats[link_split[-1].lower()]
                desc = link_list[2].split('/')[-1]
                link = urllib.parse.urlunparse(link_list)
                if (link, extension, desc) not in links:
                    links.append((link, extension, desc))
    if len(links) == 0:
        links.append((url_for('static', filename='mrss_default.jpg',
                      _external=True, _scheme='https'), 'jpeg',
                      'No Media Found'))
    return links

if __name__ == '__main__':
    app.debug = True
    app.run()