import requests
import xml.etree.ElementTree as et
import json
import os

# Function to read configuration from a JSON file
def config(loc):
    cfg = filehandle = open(loc, mode="r", encoding="utf-8")
    data = json.loads(cfg.read())
    cfg.close()
    return data

# Function to fetch XML data from a URL
def get_xml(url):
    request = requests.get(url)
    if request.status_code != 200:
        raise BaseException(f"HTTP ERROR: {request.status_code}")
    return request.text

# Function to parse XML data and extract relevant post information
def get_posts(text):
    out = []
    items = et.fromstring(text).find("channel").findall("item")
    for item in items:
        post = {
            "title": item.find('title').text,
            "link": item.find('link').text,
            "description": item.find('description').text,
            "pubDate": item.find('pubDate').text,
        }
        out.append(post)
    return out

# Function to retrieve processed posts from a database file
def get_processed_posts(db_file):
    file_exists = os.path.exists(db_file)

    if not file_exists:
         update_db(db_file, [])

    db = filehandle = open(db_file, mode="r", encoding="utf-8")
    processed = json.loads(db.read())['processed']
    db.close()
    return processed

# Function to update the database file with processed posts
def update_db(db_file, contents):
    data = json.dumps({
        "processed": contents
    })

    db = filehandle = open(db_file, mode="w", encoding="utf-8")
    db.write(data)
    db.close()

# Function to check if a post has been processed
def is_processed(items, url):
    for item in items:
        if item == url:
            return True
    return False

# Function to send a notification to a Telegram chat
def telegram_push(chat_id, item, token):
    text = item['title'] + "\n"
    text += item['link']
    response = requests.post(
        url=f'https://api.telegram.org/bot{token}/sendMessage',
        data={'chat_id': chat_id, 'text': text}
    ).json()

# Main part of the script
if __name__ == "__main__":
    # Get the directory path of the script
    root = os.path.dirname(os.path.realpath(__file__))
    # Load configuration from config.json
    cfg = config(root + '/config.json')
    # Load processed posts from processed.json
    processed = get_processed_posts(root + '/processed.json')
    # Initialize a counter for new posts
    p = 0

    # Iterate over each RSS feed in the configuration
    for feed in cfg['upwork_rss_feeds']:
        # Fetch XML data from the RSS feed
        content = get_xml(feed)
        # Extract posts from the XML data
        items = get_posts(content)
        # Path to the processed posts database file
        p_file = root + '/processed.json'

        # Iterate over each post
        for item in items:
            # Check if the post has been processed before
            if not is_processed(processed, item['link']):
                # If not processed, add it to the processed list
                processed.append(item['link'])
                # Send a notification to the Telegram chat
                telegram_push(cfg['telegram_chat_id'], item, cfg['telegram_api_token'])
                # Increment the counter for new posts
                p += 1

    # If there are new posts, update the processed database file
    if p > 0:
        update_db(p_file, processed)
