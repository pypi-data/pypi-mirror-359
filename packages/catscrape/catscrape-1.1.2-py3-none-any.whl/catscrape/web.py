from .data import *

# FUNCTIONS

def new_driver(headless: bool=True):
    """ Creates a new selenium driver """
    # Initalize the Chrome options object to change settings for the driver
    chrome_options = Options()

    # Add the headless tag if requested
    if headless:
        chrome_options.add_argument("--headless=new")
    
    # Initialize the Chrome driver
    driver = webdriver.Chrome(options=chrome_options)

    return driver

def get_website_html(url):
    """ Return the HTML of the URL"""
    # Get the HTML
    response = requests.get(url)

    # Make sure the scrape was successful
    response.raise_for_status()
    
    return response.text

def login():
    """ Login to Scratch """
    # Create the driver
    driver = new_driver()

    # Open the login page
    driver.get(LOGIN_URL)

    # Wait until the username input is interactable
    wait = WebDriverWait(driver, 10)
    username_input = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="id_username" and @name="username"]')))
    password_input = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="id_password" and @name="password"]')))

    # Get the login data
    login_data = get_login_data()

    # Enter username and password
    username_input.send_keys(login_data[0])
    password_input.send_keys(login_data[1])

    # Click "Sign in" button
    sign_in_button = driver.find_element(By.XPATH, '//button[contains(text(), "Login")]')
    sign_in_button.click()

    # Wait for login to complete
    time.sleep(5)