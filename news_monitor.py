#!/usr/bin/env python3
"""
Daily News Monitor with Brevo Email Integration
Monitors news for specific keywords and sends email notifications.

Deploy on Render as a Cron Job - runs daily to check news and send alerts.
"""

import requests
import os
from datetime import datetime
from typing import Optional
import json
import re
from urllib.parse import quote

# Load .env file if it exists (for local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ============ CONFIGURATION ============
# Set these as environment variables in Render Dashboard

BREVO_API_KEY = os.getenv("BREVO_API_KEY", "your-brevo-api-key-here")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "news@yourdomain.com")
SENDER_NAME = os.getenv("SENDER_NAME", "News Monitor")

# Daily news recipient
DAILY_NEWS_RECIPIENT = os.getenv("DAILY_NEWS_RECIPIENT", "your-email@example.com")

# Special recipient for "ilkyar" keyword alerts
ILKYAR_ALERT_RECIPIENT = os.getenv("ILKYAR_ALERT_RECIPIENT", "special-recipient@example.com")

# Keywords to monitor (add more as needed)
MONITORED_KEYWORDS = ["ilkyar"]

# =======================================


class NewsMonitor:
    def __init__(self):
        self.brevo_api_url = "https://api.brevo.com/v3/smtp/email"
        self.headers = {
            "accept": "application/json",
            "api-key": BREVO_API_KEY,
            "content-type": "application/json"
        }

    def fetch_google_news(self, query: Optional[str] = None, language: str = "en") -> list:
        """
        Fetch news from Google News RSS feed.
        """
        news_items = []
        
        if query:
            # Search for specific query
            rss_url = f"https://news.google.com/rss/search?q={quote(query)}&hl={language}"
        else:
            # Get top news
            rss_url = f"https://news.google.com/rss?hl={language}"
        
        try:
            response = requests.get(rss_url, timeout=30)
            response.raise_for_status()
            
            # Parse RSS (simple regex parsing to avoid dependencies)
            items = re.findall(r'<item>(.*?)</item>', response.text, re.DOTALL)
            
            for item in items[:20]:  # Limit to 20 items
                title_match = re.search(r'<title>(.*?)</title>', item)
                link_match = re.search(r'<link>(.*?)</link>', item)
                pubdate_match = re.search(r'<pubDate>(.*?)</pubDate>', item)
                source_match = re.search(r'<source[^>]*>(.*?)</source>', item)
                
                if title_match and link_match:
                    news_items.append({
                        'title': self._clean_html(title_match.group(1)),
                        'link': link_match.group(1),
                        'pubDate': pubdate_match.group(1) if pubdate_match else '',
                        'source': source_match.group(1) if source_match else 'Unknown'
                    })
        
        except Exception as e:
            print(f"Error fetching news: {e}")
        
        return news_items

    def _clean_html(self, text: str) -> str:
        """Remove HTML entities and tags."""
        text = re.sub(r'<[^>]+>', '', text)
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        return text.strip()

    def check_keyword_in_news(self, news_items: list, keyword: str) -> list:
        """Check if keyword appears in any news items."""
        matching_items = []
        keyword_lower = keyword.lower()
        
        for item in news_items:
            if keyword_lower in item['title'].lower():
                matching_items.append(item)
        
        return matching_items

    def create_daily_digest_html(self, news_items: list) -> str:
        """Create HTML content for daily news digest."""
        today = datetime.now().strftime("%B %d, %Y")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .news-item {{ background: white; padding: 15px; margin-bottom: 15px; border-radius: 8px; border-left: 4px solid #667eea; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .news-title {{ font-size: 16px; font-weight: bold; color: #333; text-decoration: none; }}
                .news-title:hover {{ color: #667eea; }}
                .news-meta {{ font-size: 12px; color: #888; margin-top: 8px; }}
                .footer {{ text-align: center; padding: 20px; color: #888; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📰 Daily News Digest</h1>
                <p>{today}</p>
            </div>
            <div class="content">
        """
        
        if news_items:
            for item in news_items:
                html += f"""
                <div class="news-item">
                    <a href="{item['link']}" class="news-title">{item['title']}</a>
                    <div class="news-meta">
                        📌 {item['source']} | 🕐 {item['pubDate']}
                    </div>
                </div>
                """
        else:
            html += "<p>No news items found for today.</p>"
        
        html += """
            </div>
            <div class="footer">
                <p>This email was automatically generated by News Monitor</p>
            </div>
        </body>
        </html>
        """
        
        return html

    def create_keyword_alert_html(self, keyword: str, matching_items: list) -> str:
        """Create HTML content for keyword alert."""
        today = datetime.now().strftime("%B %d, %Y %H:%M")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }}
                .header {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .alert-badge {{ background: #ff4757; padding: 5px 15px; border-radius: 20px; display: inline-block; margin-bottom: 10px; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .news-item {{ background: white; padding: 15px; margin-bottom: 15px; border-radius: 8px; border-left: 4px solid #f5576c; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .news-title {{ font-size: 16px; font-weight: bold; color: #333; text-decoration: none; }}
                .news-meta {{ font-size: 12px; color: #888; margin-top: 8px; }}
                .keyword {{ background: #fff3cd; padding: 2px 6px; border-radius: 3px; font-weight: bold; }}
                .footer {{ text-align: center; padding: 20px; color: #888; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="alert-badge">🚨 KEYWORD ALERT</div>
                <h1>News Alert: "{keyword}"</h1>
                <p>{today}</p>
            </div>
            <div class="content">
                <p>We found <strong>{len(matching_items)}</strong> news item(s) containing the keyword <span class="keyword">{keyword}</span>:</p>
        """
        
        for item in matching_items:
            html += f"""
            <div class="news-item">
                <a href="{item['link']}" class="news-title">{item['title']}</a>
                <div class="news-meta">
                    📌 {item['source']} | 🕐 {item['pubDate']}
                </div>
            </div>
            """
        
        html += """
            </div>
            <div class="footer">
                <p>This is an automated keyword alert from News Monitor</p>
            </div>
        </body>
        </html>
        """
        
        return html

    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email via Brevo API."""
        payload = {
            "sender": {
                "name": SENDER_NAME,
                "email": SENDER_EMAIL
            },
            "to": [
                {
                    "email": to_email
                }
            ],
            "subject": subject,
            "htmlContent": html_content
        }
        
        try:
            response = requests.post(
                self.brevo_api_url,
                headers=self.headers,
                json=payload
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Email sent successfully to {to_email}")
                return True
            else:
                print(f"❌ Failed to send email: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False

    def run_daily_digest(self):
        """Run daily news digest and send to recipient."""
        print(f"\n{'='*50}")
        print(f"🗞️  Running Daily News Digest - {datetime.now()}")
        print(f"{'='*50}\n")
        
        # Fetch top news
        news_items = self.fetch_google_news()
        print(f"📰 Fetched {len(news_items)} news items")
        
        # Create and send daily digest
        html_content = self.create_daily_digest_html(news_items)
        today = datetime.now().strftime("%B %d, %Y")
        subject = f"📰 Daily News Digest - {today}"
        
        self.send_email(DAILY_NEWS_RECIPIENT, subject, html_content)
        
        return news_items

    def run_keyword_monitor(self, news_items: list = None):
        """Check for keyword mentions and send alerts."""
        print(f"\n{'='*50}")
        print(f"🔍 Running Keyword Monitor - {datetime.now()}")
        print(f"{'='*50}\n")
        
        # If no news items provided, fetch them
        if news_items is None:
            news_items = self.fetch_google_news()
        
        # Also search specifically for the keywords
        for keyword in MONITORED_KEYWORDS:
            print(f"\n🔎 Searching for keyword: '{keyword}'")
            
            # Search specifically for the keyword
            keyword_news = self.fetch_google_news(query=keyword)
            
            # Combine with general news
            all_news = news_items + keyword_news
            
            # Remove duplicates based on title
            seen_titles = set()
            unique_news = []
            for item in all_news:
                if item['title'] not in seen_titles:
                    seen_titles.add(item['title'])
                    unique_news.append(item)
            
            # Check for keyword matches
            matching_items = self.check_keyword_in_news(unique_news, keyword)
            
            if matching_items:
                print(f"🚨 Found {len(matching_items)} news items about '{keyword}'!")
                
                # Send alert email
                html_content = self.create_keyword_alert_html(keyword, matching_items)
                subject = f"🚨 News Alert: '{keyword}' mentioned in {len(matching_items)} article(s)"
                
                # Send to special recipient for ilkyar keyword
                if keyword.lower() == "ilkyar":
                    self.send_email(ILKYAR_ALERT_RECIPIENT, subject, html_content)
                else:
                    self.send_email(DAILY_NEWS_RECIPIENT, subject, html_content)
            else:
                print(f"✨ No news found for keyword: '{keyword}'")

    def run(self):
        """Run the complete news monitoring routine."""
        # Run daily digest
        news_items = self.run_daily_digest()
        
        # Run keyword monitor
        self.run_keyword_monitor(news_items)
        
        print(f"\n{'='*50}")
        print("✅ News monitoring complete!")
        print(f"{'='*50}\n")


if __name__ == "__main__":
    monitor = NewsMonitor()
    monitor.run()
