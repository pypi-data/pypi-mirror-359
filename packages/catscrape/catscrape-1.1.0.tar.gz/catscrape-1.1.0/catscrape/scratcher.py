from .data import *
from .web import *

# SCRATCHER CLASS

class Scratcher(object):
    def __init__(self, username):
        self.username = username

    def _generate_followers_following_urls(self,
                                           n_pages: int,
                                           page_type: str=FOLLOWING
                                           ):
        # Generate the base url for the username page
        if page_type == FOLLOWERS:
            base_url = 'https://scratch.mit.edu/users/{}/followers/?page='.format(self.username)
        elif page_type == FOLLOWING:
            base_url = 'https://scratch.mit.edu/users/{}/following/?page='.format(self.username)
        else:
            raise Exception("Invalid page type: {}".format(page_type))
        
        # Initalize a list of urls
        urls = []

        # Iterate through all the pages of followers
        for i in range(n_pages):
            # Add the url to the list
            urls.append(base_url + str(i + 1))

        # Return the result
        return urls

    GET_FOLLOWERS_PAGES_TEXT = "page-links"
    GET_FOLLOWERS_PAGES_STOP_TEXT = "</div>"
    GET_FOLLOWERS_PAGES_SPAN = "span"
    GET_FOLLOWERS_PAGES_FIRST_SKIP = 42

    def _get_followers_pages(self,
                            page_type: str
                            ) -> int:
        """
        Returns the number of followers/following pages that the user has

        Parameters:
            page_type (str): Should be 'FOLLOWERS' or 'FOLLOWING'

        Returns:
            int: The number of followers/following pages
        
        """
        # Check if the data was previously saved
        if getattr(self, "followers_pages", None):
            return self.followers_pages
        
        # Generate the url for the first follower page
        url = self._generate_followers_following_urls(1, page_type)[0]

        # Get the HTML from the url
        html = get_website_html(url)

        # Find the location of the parent span tag of the list of links to other pages
        start_location = html.find(Scratcher.GET_FOLLOWERS_PAGES_TEXT)

        # Add the skip amount to the start location
        start_location += Scratcher.GET_FOLLOWERS_PAGES_FIRST_SKIP

        # Cut off the html text from the start position so it is easier to work with
        html = html[start_location:]

        # Now, keep going till we find the stop text
        # The fomula is, count the "span"s, sub 2, and div 2
        span_count = 0

        while True:
            # Get the location of the next span
            span_location = html.find(Scratcher.GET_FOLLOWERS_PAGES_SPAN)

            # Make sure we have not passed a div, if so, the pages section of the code has ended
            # After finding the div location, compare it to the location of the next span
            # If the div location is lower, the div is sooner than the next span and we break the loop
            div_location = html.find(Scratcher.GET_FOLLOWERS_PAGES_STOP_TEXT)
            if div_location < span_location:
                break

            # Otherwise, add one to the span count, and cut off the html
            span_count += 1
            html = html[span_location + len(Scratcher.GET_FOLLOWERS_PAGES_SPAN):]

        # Calculate the number of pages, based on the number of spans
        pages = int((span_count - 2) / 2)

        # 1 page will show up as 0, so set it
        if pages == 0:
            pages = 1

        # Save the data for later use
        self.followers_pages = pages

        # Return the number of pages
        return pages

    GET_FOLLOWERS_SKIP_CHAR = "/"
    GET_FOLLOWERS_CHARS_TO_SKIP = 20
    GET_FOLLOWERS_PER_PAGE = 59 # Doesn't include first username, the real number is 60
    GET_FOLLOWERS_AFTER_THUMB = 39
    GET_FOLLOWERS_THUMB_TEXT = "user thumb item"

    def _get_followers_following(self, page_type, search_for=None, verbose=True) -> list[str] | bool:
        # Check if the data was previously saved
        if search_for:
            if getattr(self, "followers", None) and page_type == FOLLOWERS:
                return search_for in self.followers
            if getattr(self, "following", None) and page_type == FOLLOWERS:
                return search_for in self.following
        else:
            if getattr(self, "followers", None) and page_type == FOLLOWERS:
                return self.followers
            if getattr(self, "following", None) and page_type == FOLLOWERS:
                return self.following
        
        # Generate the urls for the followers pages
        urls = self._generate_followers_following_urls(self._get_followers_pages(page_type), page_type)

        usernames = []

        for url in urls:
            # Print a progress message
            if verbose:
                print("Reading pages: {}/{}".format(urls.index(url) + 1, len(urls)))

            # Get the text
            html = get_website_html(url)

            # Return the existing usernames if the page failed to load
            if not html:
                return usernames

            # Get start location
            start_location = html.find(Scratcher.GET_FOLLOWERS_THUMB_TEXT) + Scratcher.GET_FOLLOWERS_AFTER_THUMB

            # Shorten url
            html = html[start_location - 1:]

            # Get first username
            usernames.append(html[:html.find(Scratcher.GET_FOLLOWERS_SKIP_CHAR)])

            # First username needed one more char, so add it back
            html = html[1:]

            # Iterate through all the code
            for i in range(Scratcher.GET_FOLLOWERS_PER_PAGE):
                # Skip the number of triangles
                for i in range(Scratcher.GET_FOLLOWERS_CHARS_TO_SKIP):
                    start_location = html.find(Scratcher.GET_FOLLOWERS_SKIP_CHAR)

                    # Cut off the html, but add delete one more char, this is the triangle
                    html = html[start_location + 1:]

                usernames.append(html[:html.find(Scratcher.GET_FOLLOWERS_SKIP_CHAR)])

            # Check if the username being searched for is in the list
            if search_for in usernames:
                return True
        
        # Each of the methods introduce some incorrect random text, delete that
        if page_type == FOLLOWERS:
            del usernames[-9:]
        elif page_type == FOLLOWING:
            del usernames[-14:]

        # Save the data for later
        if not search_for:
            if page_type == FOLLOWERS:
                self.followers = usernames
            elif page_type == FOLLOWING:
                self.following = usernames

        # Return the usernames. If searching for a username, return if the username was found
        if search_for:
            return search_for in usernames
        return usernames
    
    # Wrapper functions

    def get_followers(self, verbose: bool=True) -> list[str]:
        """
        Return a list of the followers of the users.

        Parameters:
            verbose (bool): Whether to be verbose.

        Returns:
            list[str]: The list of followers.
        """
        followers = self._get_followers_following(page_type=FOLLOWERS, verbose=verbose)
        assert isinstance(followers, list)
        return followers
    
    def get_following(self, verbose: bool=True) -> list[str]:
        """
        Return a list of the users that the user is following.

        Parameters:
            verbose (bool): Whether to be verbose.

        Returns:
            list[str]: The list of users that the user follows.
        """
        following = self._get_followers_following(page_type=FOLLOWING, verbose=verbose)
        assert isinstance(following, list)
        return following
    
    def is_following(self, username, verbose: bool=True):
        """
        Returns whether the user is following the given username.

        Parameters:
            verbose (bool): Whether to be verbose.

        Returns:
            bool: Whether the user is following the given username.
        """
        return self._get_followers_following(page_type=FOLLOWING, search_for=username, verbose=verbose)
    
    def is_followed_by(self, username, verbose: bool=True):
        """
        Returns whether the user is followed by the given username.

        Parameters:
            verbose (bool): Whether to be verbose.

        Returns:
            bool: Whether the user is followed by the given username.
        """
        return self._get_followers_following(page_type=FOLLOWERS, search_for=username, verbose=verbose)
    
    
    def follower_count(self, verbose: bool=True):
        """
        Returns the number of followers of the user.

        Parameters:
            verbose (bool): Whether to be verbose.

        Returns:
            int: The number of followers.
        """
        return len(self.get_followers(verbose=verbose))
    
    def following_count(self, verbose: bool=True):
        """
        Returns the number of users the user is following.

        Parameters:
            verbose (bool): Whether to be verbose.

        Returns:
            int: The following amount.
        """
        return len(self.get_following(verbose=verbose))