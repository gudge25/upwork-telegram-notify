import requests
import xml.etree.ElementTree as et
import json
import os


def config(loc):
    cfg = filehandle = open(loc, mode="r", encoding="utf-8")
    data = json.loads(cfg.read())
    cfg.close()
    return data


def get_xml(url):
    request = requests.get(url)
    if request.status_code != 200:
        raise BaseException(f"HTTP ERROR: {request.status_code}")
    return request.text


def get_posts(text):
    out = []
    items = et.fromstring(text).find("channel").findall("item")
    for item in items:
        post = {
            "title": item.find('title').text,
            "link": item.find('link').text,
            "description": item.find('description').text,
            "pubDate": item.find('pubDate').text,
            "title": item.find('title').text
        }
        out.append(post)
    return out


def get_processed_posts(db_file):
    file_exists = os.path.exists(db_file)

    if file_exists is False:
         update_db(db_file, [])

    db = filehandle = open(db_file, mode="r", encoding="utf-8")
    processed = json.loads(db.read())['processed']
    db.close()
    return processed


def update_db(db_file, contents):
    data = json.dumps({
        "processed": contents
    })

    db = filehandle = open(db_file, mode="w", encoding="utf-8")
    db.write(data)
    db.close()


def is_processed(items, url):
    for item in items:
        if item == url:
            return True
    return False


def telegram_push(chat_id, item, token):
    text = item['title'] + "\n"
    text += item['link']
    response = requests.post(
        url=f'https://api.telegram.org/bot{token}/sendMessage',
        data={'chat_id': chat_id, 'text': text}
    ).json()
    return response


root = os.path.dirname(os.path.realpath(__file__))
cfg = config(root + '/config.json')
processed = get_processed_posts(root + '/processed.json')
content = get_xml(cfg['upwork_rss_feed'])
items = get_posts(content)
p = 0
p_file = root + '/processed.json'

for item in items:
    if is_processed(processed, item['link']) is False:
        processed.append(item['link'])
        telegram_push(cfg['telegram_chat_id'], item, cfg['telegram_api_token'])
        p = p + 1

if p > 0:
    update_db(p_file, processed)
