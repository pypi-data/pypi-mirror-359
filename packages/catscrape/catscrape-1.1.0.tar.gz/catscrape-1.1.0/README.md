# Catscrape

*Catscrape* is a library with web scraping functions for the popular beginner programming website Scratch.mit.edu. It can extract data from followers, studios, and *soon* extract hearts, stars, and remix counts for projects.

## Functionality

This library is new, so most features are on the to-do list. Here are the supported and planned features:

|Data to Extract|Support|
|--|--|
|User followers|✅Supported|
|User following|✅Supported|
|Get user "About Me"|🟨Coming Soon|
|Get user shared projects|🟨Coming Soon|
|Studio curators|✅Supported|
|Auto invite to studio|✅Supported|
|Project hearts|🟨Coming Soon|
|Project stars|🟨Coming Soon|
|Project remixes|🟨Coming Soon|
|Project viewes|🟨Coming Soon|
|Anything else|🟥Not Supported|

## Installation

The library can be installed via `pip install`:
```bash
pip install catscrape
```

# Documentation

## Scratcher

The `Scratcher` class has methods to get the number of followers and the number of users the user is following. They are all listed below.
A `Scratcher` object can be initalized as shown below. In the example code, it is assumed a variable named `user` is assigned to a `Scratcher` object.
```python
>>> import catscrape
>>> user = catscrape.Scratcher("CrystalKeeper7")
```
All of the methods can be passed a `verbose` argument, which controls various print statements to assure the user of progress.

All of the methods cache their outputs. For example, if `Scratcher.follower_count` is executed, `Scratcher.get_followers` will return instantly with the already-computed value. The `Scratcher.is_following` and `Scratcher.is_followed_by` methods do not generate a cache because they return as soon as the value is found and do not find all of the followers or following.

### `get_followers`

The `Scratcher.get_followers` method returns a list of the the followers of the user:
```python
>>> followers = user.get_followers()
>>> type(followers)
<class 'list'>
>>> type(followers[0])
<class 'str'>
```

### `get_following`

The `Scratcher.get_following` method returns a list of the users that the user is following:
```python
>>> following = user.get_following()
>>> type(followers)
<class 'list'>
>>> type(followers[0])
<class 'str'>
```

### `is_following`

The `Scratcher.is_following` method has a parameter `username`, and returns whether the user is following that username.
```python
>>> is_following_griffpatch = user.is_following("griffpatch")
>>> type(is_following_griffpatch)
<class 'bool'>
```

### `is_followed_by`

The inverse of the `Scratcher.is_following` method, returning whether the user is followed by the given username.
```python
>>> is_following_griffpatch = user.is_following("griffpatch")
>>> type(is_following_griffpatch)
<class 'bool'>
```

### `follower_count`

Returns the follower count of the user.
```python
>>> num_followers = user.follower_count()
>>> type(num_followers)
<class 'int'>
```

### `following_count`

Returns the number of scratchers the user is following.
```python
>>> num_followers = user.follower_count()
>>> type(num_followers)
<class 'int'>
```

## Providing Login

The `Studio.invite_curators` method requires an account with manager or host authority to invite curators. The `save_login_data` function saves the login data of an account. The data is saved in a pickle file in a folder in the appdata folder of the computer. Example usage is shown below:
```python
>>> from catscrape import save_login_data
>>> save_login_data("<username>", "<password>")
Successfully saved the login data.
```
## Studio

The `Studio` class has methods to get the curators of the studio, and to auto-invite curators. Below is an example of initalizing the studio class. The one parameter is the studio id.
```python
>>> from catscrape import Studio
>>> studio = Studio(45693845)
```

### `get_curators`

The `Studio.get_curators` method returns all of the curators of the studio. Becuase it has to physically scroll through the curators using selenium (headless, of course), this function tends to take longer. The `scroll_wait_time` parameter adjusts the amount of time to wait after pressing the "Load More" button to press it again. Changing this too low causes instability in results, possibly leading to incorrect results, with too few curators.
```python
>>> curators = studio.get_curators(
...     scroll_wait_time=0.25 # More reliable, but slower
... )
>>> type(curators)
<class 'list'>
>>> type(curators[0])
<class 'str'>
```

### `invite_curators`

The `Studio.invite_curators` method invites curators to the studio. Login info is required for this. See "Providing Login" above.
The usernames to invite should be passed to the method. A physical Chrome window will open, and will be controlled by selenium to login and invite the curators.
Warning: I have experienced failure to invite more users after about 100-150 invites in a row. Try to limit the number of usernames to invite in a batch to below this value to avoid partial failure.
```python
>>> invitees = ["griffpatch", "CrystalKeeper7", "DominoKid11", "username4"]
>>> studio.invite_curators(
...     usernames=invitees
... )
<invites curators>
```

# Versions
## 1.1.0
- Initial release