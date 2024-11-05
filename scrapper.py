import youtube_dl
import pandas as pd
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def get_channel_name(url):
    """
    Get channel name using Selenium with the specific selector
    """
    try:
        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Initialize the driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        
        # Wait for and find the channel name element
        selector = "#page-header > yt-page-header-renderer > yt-page-header-view-model > div > div.page-header-view-model-wiz__page-header-headline > div > yt-dynamic-text-view-model > h1 > span"
        channel_name_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        
        channel_name = channel_name_element.text.strip()
        driver.quit()
        
        return channel_name
    except Exception as e:
        print(f"Error getting channel name: {str(e)}")
        return "Unknown Channel"
    finally:
        try:
            driver.quit()
        except:
            pass

def scrape_channel(channel_url):
    """
    Scrapes YouTube channel data and saves it to a CSV file.
    
    Args:
        channel_url (str): URL of the YouTube channel
    """
    # Get channel name first
    channel_name = get_channel_name(channel_url)
    print(f"\nScraping channel: {channel_name}")
    
    # Configure youtube-dl options
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
        'ignoreerrors': True
    }
    
    # Initialize lists to store video data
    videos_data = []
    
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            # Extract video info
            channel_info = ydl.extract_info(channel_url, download=False)
            
            # Iterate through videos
            for entry in channel_info['entries']:
                if entry:
                    video_data = {
                        'channel_name': channel_name,
                        'video_name': entry.get('title', 'Unknown Title'),
                        'views_count': entry.get('view_count', 0)
                    }
                    videos_data.append(video_data)
    
    except Exception as e:
        print(f"Error scraping channel: {str(e)}")
        return None
    
    # Create DataFrame and save to CSV
    if videos_data:
        df = pd.DataFrame(videos_data)
        
        # Calculate total views
        total_views = df['views_count'].sum()
        
        # Generate filename using channel name
        safe_channel_name = "".join(x for x in channel_name if x.isalnum())
        filename = f"{safe_channel_name}_videos_{datetime.now().strftime('%Y%m%d')}.csv"
        
        # Save to CSV
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Data saved to {filename}")
        
        # Print summary
        print(f"\nChannel Summary:")
        print(f"{channel_name} = {total_views:,} views")
        
        return filename
    
    return None

def main():
    # Get channel URL from user
    channel_url = input("Enter YouTube channel URL: ")
    
    # Run scraper
    output_file = scrape_channel(channel_url)
    
    if output_file:
        print("\nScraping completed successfully!")
    else:
        print("\nFailed to scrape channel data.")

if __name__ == "__main__":
    main()