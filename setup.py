import os

# Environment variables expected to be set in Render.com dashboard
GIMME = os.getenv("TELEGRAM_API_TOKEN")         # gimmequotes_bot token
TEST = os.getenv("TEST_TELEGRAM_API_TOKEN")     # nawzaysfinah bot token (optional/test)
NOTION_TOKEN = os.getenv("NOTION_TOKEN")        # Notion integration token
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")   # Notion database ID
