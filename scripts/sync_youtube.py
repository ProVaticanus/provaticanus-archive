import os
import feedparser
import pytumblr

# Load credentials from environment variables
client = pytumblr.TumblrRestClient(
    os.environ['TUMBLR_CONSUMER_KEY'],
    os.environ['TUMBLR_CONSUMER_SECRET'],
    os.environ['TUMBLR_OAUTH_TOKEN'],
    os.environ['TUMBLR_OAUTH_SECRET']
)

blog_name = os.environ['TUMBLR_BLOG_NAME']
rss_url = os.environ['YOUTUBE_RSS_URL']

print(f"Fetching feed from {rss_url}...")
feed = feedparser.parse(rss_url)

# Track posted IDs to avoid duplication across runs
posted_ids_file = 'posted_videos.txt'
if os.path.exists(posted_ids_file):
    with open(posted_ids_file, 'r') as f:
        posted_ids = set(f.read().splitlines())
else:
    posted_ids = set()

new_posts_count = 0

# Loop through all historical entries found in the RSS feed
for entry in reversed(feed.entries):
    video_id = entry.get('yt_videoid', entry.link)
    
    if video_id in posted_ids:
        continue
        
    title = entry.title
    link = entry.link
    published = entry.published
    
    print(f"Backfilling to Tumblr: {title}")
    
    # Create a link post on Tumblr containing the YouTube video link
    response = client.create_link(
        blog_name,
        title=title,
        url=link,
        description=f"<p>{title}</p><p><a href='{link}'>Watch on YouTube</a></p>",
        state="published",
        date=published
    )
    
    if 'id' in response:
        posted_ids.add(video_id)
        new_posts_count += 1
    else:
        print(f"Error posting: {response}")

# Save state tracker back to repository
with open(posted_ids_file, 'w') as f:
    f.write('\n'.join(posted_ids))

print(f"Retroactive sync complete. Successfully backfilled {new_posts_count} videos.")
