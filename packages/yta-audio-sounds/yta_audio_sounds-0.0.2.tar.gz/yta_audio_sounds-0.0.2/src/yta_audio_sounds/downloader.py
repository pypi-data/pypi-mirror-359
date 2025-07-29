"""
TODO: This module needs a bit more work
and also to be tested.
"""
from yta_web_scraper.chrome import ChromeScraper, By
from yta_validation.parameter import ParameterValidator
from yta_file_downloader import Downloader as FileDownloader
from typing import Union


MYINSTANTS_SEARCH_URL = 'https://www.myinstants.com/es/search/'
"""
The url in which you append the query
to look for an specific sound.
"""

class Downloader:
    """
    Class to download sounds from external
    platforms.
    """

    def download_from_myinstants(
        query: str,
        output_filename: Union[str, None] = None
    ) -> Union['FileReturned', None]:
        """
        Look for the sounds with the provided
        'query' in the myinstants web platform
        and download one if existing.
        """
        ParameterValidator.validate_mandatory_string('query', query, do_accept_empty = True)

        """
        Explanation, if needed:

        You search for a query within this url:
        https://www.myinstants.com/es/search/?name=bob+esponja
        and then you find a lot of 
        '<div class="instant">' that are the
        different sounds. Inside, you have a
        button that includes an 'onclick' like
        this:
        "play('/media/sounds/bob-esponja-fail-sound.mp3', 'loader-288665', 'bob-esponja-fail-sound-80147')"
        and that is the last part of the web
        platform url you need to access to the
        audio file to download it.

        This is an example of an url that goes
        to the specific page of a sound:
        https://www.myinstants.com/es/instant/a-calamardo-le-gusta-mi-p1t0-26839/

        And this is the url to download one
        specific sound from the button:
        https://www.myinstants.com/media/sounds/a-calamardo-le-gusta-mi-p1t0.mp3
        """
        scraper = ChromeScraper(do_use_gui = True)
        # TODO: I would like to do format the query
        # with one of my libs, but they don't do
        # this exactly...
        scraper.go_to_web_and_wait_until_loaded(f'{MYINSTANTS_SEARCH_URL}?{query.replace(' ', '+')}')

        # We wait until they appear and obtain them
        scraper.find_element_by_class_waiting('div', 'instant')
        divs = scraper.find_elements_by_class('div', 'instant')

        sound_urls = [
            f'https://www.myinstants.com{div.find_element(By.TAG_NAME, 'button').get_attribute('onclick').split(',')[0].replace('play(', '').replace('\'', '')}'
            for div in divs
        ]

        return (
            # TODO: Maybe force the extension that the
            # remote file has...
            FileDownloader.download_audio(sound_urls[0], output_filename)
            if len(sound_urls) > 0 else
            None
        )