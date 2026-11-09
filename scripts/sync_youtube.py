name: YouTube to Tumblr Sync

on:
  schedule:
    - cron: '0 */6 * * *'  # Runs every 6 hours
  workflow_dispatch:      # Allows manual trigger

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pytumblr requests yt-dlp

      - name: Run YouTube to Tumblr Sync
        env:
          TUMBLR_CONSUMER_KEY: ${{ secrets.TUMBLR_CONSUMER_KEY }}
          TUMBLR_CONSUMER_SECRET: ${{ secrets.TUMBLR_CONSUMER_SECRET }}
          TUMBLR_OAUTH_TOKEN: ${{ secrets.TUMBLR_OAUTH_TOKEN }}
          TUMBLR_OAUTH_SECRET: ${{ secrets.TUMBLR_OAUTH_SECRET }}
          TUMBLR_BLOG_NAME: ${{ secrets.TUMBLR_BLOG_NAME }}
        run: |
          python scripts/sync_youtube.py

      - name: Save Sync State
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git add synced_videos.txt
          git diff --quiet && git diff --staged --quiet || (git commit -m "Update synced videos state [skip ci]" && git push)
