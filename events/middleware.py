# your_app/middleware.py

#from events.getdata import run_monthly_script
#from .getdata import run_monthly_script

from datetime import datetime
from django.core.cache import cache

###########################################
import os
import django
import requests
from bs4 import BeautifulSoup
#############################################

class MonthlyScriptMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.check_and_run_script()
        response = self.get_response(request)
        return response

    def check_and_run_script(self):
        today = datetime.today()
        if today.day == 1:
            # Check if the script has already run today
            if not cache.get('monthly_script_ran'):
               print("Updating table")
               self.change_table()
               cache.set('monthly_script_ran', True, timeout=86400)  # Cache for 24 hours SO ONLY 1 PERSON RESETS TABLE

    def change_table(self):
        print("Running monthly script")
        # Add your script logic here
        # Set up Django environment
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djbox.settings')
        django.setup()

        # Import the Event model
        from events.models import Event

        Event.objects.all().delete() #empty current table

        # URL of the BBC boxing calendar page
        url = 'https://www.bbc.co.uk/sport/boxing/calendar'  # Can change URL to each month

        # Fetch the HTML content
        response = requests.get(url)
        html_content = response.content
        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all event cards containing the word 'Title' in any of their details
        event_cards = soup.find_all('div', class_='ssrcss-3ivill-Card exhoryp0')
        # Loop through each event card
        for event_card in event_cards:
            # Find all event details within the event card
            event_details = event_card.find_all('li', class_='ssrcss-1qjnrre-Secondary e10sdt6w2')
    
            # Initialize time as an empty string initially
            time = 'CANCELLED'

            # Check if any event detail contains the word 'Title'
            for detail in event_details:
                if 'Title' in detail.text:
                    # Extract the required data
                    date = event_card.find('span', class_='visually-hidden').text.strip()
                    venue = event_card.find('li', class_='ssrcss-1w2a1rr-VenueName e10sdt6w0').text.strip()
                    title_detail = event_card.find('li', class_='ssrcss-1qjnrre-Secondary e10sdt6w2', string=lambda text: 'Title' in text).text.strip()
                    event_name = event_card.find('li', class_='ssrcss-y82q52-EventName e10sdt6w1').text.strip()

                # Check if time is available
                    time_element = event_card.find('li', class_='ssrcss-1qjnrre-Secondary e10sdt6w2', string=lambda text: 'Title' not in text)
                    if time_element:
                        time = time_element.text.strip()

                    # Create and save the Event object
                    event = Event(
                        date=date,
                        time=time,
                        event=title_detail,
                        title=event_name,
                        location=venue
                    )
                    event.save()
                    break  # Stop checking other event details if 'Title' is found
