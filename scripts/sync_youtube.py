import os
import xml.etree.ElementTree as ET
import urllib.request
import pytumblr

# Retrieve environment variables
CONSUMER_KEY = os.environ['TUMBLR_CONSUMER_KEY']
CONSUMER_SECRET = os.environ['TUMBLR_CONSUMER_SECRET']
OAUTH_TOKEN = os.environ['TUMBLR_OAUTH_TOKEN']
OAUTH_SECRET = os.environ['TUMBLR_OAUTH_SECRET']
BLOG_NAME = os.environ['TUMBLR_BLOG_NAME']

# Initialize Tumblr client
client = pytumblr.TumblrRestClient(
    CONSUMER_KEY,
    CONSUMER_SECRET,
    OAUTH_TOKEN,
    OAUTH_SECRET
)

# File to keep track of posted videos
STATE_FILE = "synced_videos.txt"
synced_ids = set()

if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        synced_ids = set(line.strip() for line in f if line.strip())

# Fetch RSS feed using explicit channel_id
rss_url = os.environ.get('YOUTUBE_RSS_URL')
if not rss_url:
    rss_url = "https://www.youtube.com/feeds/videos.xml?channel_id=UCGRizY96gsfts3lWXLWbYLg"

print(f"Fetching RSS feed: {rss_url}")
req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
xml_data = urllib.request.urlopen(req).read()

root = ET.fromstring(xml_data)
ns = {'atom': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}

entries = root.findall('atom:entry', ns)
entries.reverse() # Process oldest to newest

new_synced = False

for entry in entries:
    video_id = entry.find('yt:videoId', ns).text
    title = entry.find('atom:title', ns).text
    link = entry.find('atom:link', ns).attrib['href']
    
    if video_id in synced_ids:
        continue
        
    print(f"Posting video to Tumblr: {title}")
    client.create_video(
        BLOG_NAME,
        embed=f"https://www.youtube.com/watch?v={video_id}",
        caption=f"<h3>{title}</h3><p><a href=\"{link}\">Watch on YouTube</a></p>"
    )
    
    synced_ids.add(video_id)
    new_synced = True

# Save updated state
if new_synced:
    with open(STATE_FILE, "w") as f:
        for vid in synced_ids:
            f.write(f"{vid}\n")
    print("Updated state file with new videos.")
else:
    print("No new videos to post.")
