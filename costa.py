import asyncio
from playwright.async_api import async_playwright
from openpyxl import Workbook, load_workbook
import os
from datetime import datetime

# Function to scrape cruise listings
async def scrape_cruise_listings():
    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(headless=True)  # Set to True for headless
        page = await browser.new_page()
        
        print("Navigating to the page...")
        # Navigate to the Costa Cruises page
        await page.goto('https://www.costacruises.co.uk/cruises.html?page=1#{!tag=destinationTag}destinationIds=PE&occupancy_GBP_anonymous=A&guestAges=30&guestBirthdates=1995-01-25&group.sort=departDate%20asc')
        
        # Wait for the cruise tiles to load
        print("Waiting for the cruise tiles...")
        await page.wait_for_selector('.costa-itinerary-tile', timeout=10000)
        
        # Find all cruise tiles
        cruise_tiles = await page.query_selector_all('.costa-itinerary-tile')
        print(f"Found {len(cruise_tiles)} cruise tiles.")
        
        cruise_data = []
        for tile in cruise_tiles:
            # Extract cruise title
            title = await tile.query_selector('.costa-itinerary-tile__title')
            title_text = await title.inner_text() if title else 'N/A'
            
            # Extract ship name
            ship = await tile.query_selector('.costa-itinerary-tile__ship')
            ship_text = await ship.inner_text() if ship else 'N/A'
            
            # Extract price
            price_element = await tile.query_selector('.currency-GBP')
            price_text = await price_element.inner_text() if price_element else 'N/A'
            
            # Extract cruise dates
            dates_element = await tile.query_selector('.costa-itinerary-tile__dates')
            dates_text = await dates_element.inner_text() if dates_element else 'N/A'
            
            # Extract cruise duration
            duration_element = await tile.query_selector('.costa-itinerary-tile__days')
            duration_text = await duration_element.inner_text() if duration_element else 'N/A'
            
            cruise_data.append({
                'title': title_text,
                'ship': ship_text,
                'price': price_text,
                'dates': dates_text,
                'duration': duration_text
            })
        
        print(f"Scraped {len(cruise_data)} cruises.")
        # Close the browser
        await browser.close()
        return cruise_data

# Function to save data into an Excel file
def save_to_excel(data, filename="cruise_data.xlsx"):
    # Get the current date for the sheet name
    sheet_name = datetime.now().strftime("%Y-%m-%d")
    
    # Check if the file already exists
    if os.path.exists(filename):
        workbook = load_workbook(filename)
    else:
        workbook = Workbook()
    
    # Create a new sheet for the current date
    if sheet_name not in workbook.sheetnames:
        sheet = workbook.create_sheet(sheet_name)
    else:
        sheet = workbook[sheet_name]
    
    # Add headers
    headers = ['Title', 'Ship', 'Price', 'Dates', 'Duration']
    sheet.append(headers)

    # Add data rows
    for cruise in data:
        sheet.append([cruise['title'], cruise['ship'], cruise['price'], cruise['dates'], cruise['duration']])

    # Save the workbook
    workbook.save(filename)
    print(f"Data saved to {filename}.")

async def main():
    cruises = await scrape_cruise_listings()
    if cruises:
        save_to_excel(cruises)
    else:
        print("No cruise data found.")

if __name__ == '__main__':
    asyncio.run(main())
