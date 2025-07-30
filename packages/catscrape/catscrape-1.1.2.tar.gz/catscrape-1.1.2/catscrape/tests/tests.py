from catscrape import *

# TESTS

def test_scratcher_followers():
    # Get followers
    user = Scratcher("DominoKid11")
    followers = user.get_followers()

    print(followers)

    # Assertions
    assert len(followers) > 50
    assert "sparkbark" in followers

def test_scratcher_following():
    # Get following
    user = Scratcher("DominoKid11")
    following = user.get_following()

    print(following)

    # Assertions
    assert len(following) > 3
    assert "griffpatch" in following
    assert "WazzoTV" in following

def test_is_following():
    # Check is following
    user = Scratcher("DominoKid11")
    is_following = user.is_following("griffpatch")

    # Assertions
    assert is_following

def test_is_followed_by():
    # Check is followed by
    user = Scratcher("DominoKid11")

    # Someone might unfollow DominoKid11, so check two current followers
    is_followed_by = user.is_followed_by("Buckett15") or user.is_followed_by("Goos_kin")

    # Assertions
    assert is_followed_by

def test_studio_curators():
    # Get curators
    studio = Studio(36086387)
    curators = studio.get_curators()

    print(curators)

    # Assertions
    assert "MLTGeniusCoder" in curators or "NathProductions24" in curators

def test_description():
    # Get description
    user = Scratcher("griffpatch")
    description = user.get_about_me()
    description_working_on = user.get_working_on()

    assert "Got hooked on coding" in description
    assert "YouTube Tutorials" in description_working_on