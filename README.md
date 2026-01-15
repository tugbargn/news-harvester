# 📰 Daily News Monitor with Brevo Email Integration

Automatically monitors news and sends daily digests via email. Includes special alerts for specific keywords like "ilkyar".

## Features

- 🗞️ **Daily News Digest**: Fetches top news from Google News and sends a beautiful HTML email
- 🔍 **Keyword Monitoring**: Monitors for specific keywords (e.g., "ilkyar") and sends instant alerts
- 📧 **Brevo Integration**: Uses Brevo (formerly Sendinblue) API for reliable email delivery
- ⏰ **Scheduled Execution**: Can be set up to run daily via cron job or cloud services

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Your Brevo API Key

1. Go to [Brevo](https://www.brevo.com/) and create an account (if you don't have one)
2. Navigate to: **Settings** → **SMTP & API** → **API Keys**
3. Click **Generate a new API key**
4. Copy your API key

### 3. Configure the Script

Edit `news_monitor.py` and update the configuration section at the top:

```python
# ============ CONFIGURATION ============
BREVO_API_KEY = "your-brevo-api-key-here"
SENDER_EMAIL = "news@yourdomain.com"  # Must be verified in Brevo
SENDER_NAME = "News Monitor"

# Daily news recipient
DAILY_NEWS_RECIPIENT = "your-email@example.com"

# Special recipient for "ilkyar" keyword alerts
ILKYAR_ALERT_RECIPIENT = "special-recipient@example.com"

# Keywords to monitor
MONITORED_KEYWORDS = ["ilkyar"]
```

**Or use environment variables:**

```bash
export BREVO_API_KEY="your-api-key"
export SENDER_EMAIL="news@yourdomain.com"
export SENDER_NAME="News Monitor"
export DAILY_NEWS_RECIPIENT="your-email@example.com"
export ALERT_RECIPIENT="special-recipient@example.com"
```

### 4. Verify Sender Email in Brevo

Before sending emails, you need to verify your sender email in Brevo:

1. Go to **Senders & IP** → **Senders**
2. Add your sender email address
3. Verify it via the confirmation email

### 5. Run the Script

```bash
python news_monitor.py
```

## Setting Up Daily Execution

### Option A: Cron Job (Linux/Mac)

```bash
# Open crontab editor
crontab -e

# Add this line to run daily at 8:00 AM
0 8 * * * /usr/bin/python3 /path/to/news_monitor.py >> /var/log/news_monitor.log 2>&1
```

### Option B: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to "Daily" at your preferred time
4. Action: Start a program → `python.exe` with argument `C:\path\to\news_monitor.py`

### Option C: GitHub Actions (Free Cloud Option)

Create `.github/workflows/news_monitor.yml`:

```yaml
name: Daily News Monitor

on:
  schedule:
    - cron: '0 8 * * *'  # Runs at 8:00 AM UTC daily
  workflow_dispatch:  # Allows manual trigger

jobs:
  run-monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run News Monitor
        env:
          BREVO_API_KEY: ${{ secrets.BREVO_API_KEY }}
          SENDER_EMAIL: ${{ secrets.SENDER_EMAIL }}
          SENDER_NAME: "News Monitor"
          DAILY_NEWS_RECIPIENT: ${{ secrets.DAILY_NEWS_RECIPIENT }}
          ALERT_RECIPIENT: ${{ secrets.ALERT_RECIPIENT }}
        run: python news_monitor.py
```

Then add your secrets in GitHub: Settings → Secrets and variables → Actions → New repository secret

### Option D: Railway / Render / Heroku

Deploy the script to any cloud platform that supports scheduled tasks.

## Customization

### Add More Keywords

```python
MONITORED_KEYWORDS = ["keyword", "another_keyword", "third_keyword"]
```

### Change News Source Language

In `fetch_google_news()`, change the `language` parameter:

```python
news_items = self.fetch_google_news(language="tr")  # Turkish
news_items = self.fetch_google_news(language="de")  # German
```

### Send to Multiple Recipients

Modify the `send_email` function:

```python
"to": [
    {"email": "recipient1@example.com"},
    {"email": "recipient2@example.com"}
]
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Email not sending | Check Brevo API key and sender email verification |
| No news found | Check internet connection and Google News availability |
| Keyword not matching | Keywords are case-insensitive but check spelling |

## Email Preview

The script sends beautifully formatted HTML emails:

- **Daily Digest**: Clean list of top news with sources and timestamps
- **Keyword Alert**: Highlighted alert with all matching articles

---

Made with ❤️ for automated news monitoring
