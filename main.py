from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import smtplib
import os
from dotenv import load_dotenv
from email.message import EmailMessage

load_dotenv()

# Set up the email parameters
EMAIL_ADDRESS = os.environ.get('EMAIL')
EMAIL_PASSWORD = os.environ.get('PASSWORD')
sender_email = os.environ.get('SENDER_EMAIL')
recipient_email = EMAIL_ADDRESS

# create the email message object
msg = EmailMessage()
msg['From'] = sender_email
msg['To'] = recipient_email

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    print('Logged in successfully')
    try:
        # Set up the Chrome driver
        options = Options()
        # comment out this line to see the process in chrome
        options.add_argument('--headless')

        driver = webdriver.Chrome(
          service=Service(
            ChromeDriverManager()
                          .install()
          ),
          options=options
        )

        # Navigate to the Marriott homepage
        driver.get("https://www.marriott.com/default.mi")

        # Wait for the page to load
        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "m-header__logo-icon")))

        # Find the check-in date input field
        checkin_field = driver.find_element(By.CLASS_NAME, "search__calendar-value")
        checkin_field.click()
        sleep(1)
        
        # Find the desired month
        def find_desired_month(driver, desired_month):
            global furthest_booking_month
            months_in_view = driver.find_elements(By.CLASS_NAME, "DayPicker-Caption")
            for month in months_in_view:
                furthest_booking_month = month.text
                if desired_month in month.text.upper():
                    print("Found the desired month:", desired_month)
                    return True
            else:
                try:
                    # if not correct month, navigate to next month
                    WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CLASS_NAME, "DayPicker-NavButton--next")))
                    month_picker = driver.find_element(By.CLASS_NAME, "DayPicker-NavButton--next")
                    month_picker.click()
                    return False
                except:
                    print("Month picker is not found. Breaking out of the loop.")
                    return True

        desired_month = "APRIL 2024"
        while not find_desired_month(driver, desired_month):
            pass

        # See if desired Date is available (April 8, 2024)
        desired_date = "Mon Apr 02 2024"
        date_elements = driver.find_elements(By.CSS_SELECTOR, 'div[aria-label]')

        # loop through each date element and check if it matches the desired date
        for date_element in date_elements:
            date_string = date_element.get_attribute('aria-label')
            if date_string == desired_date:
                msg['Subject'] = 'Marriott Booking Window IS Open!!!!'
                msg.set_content(f'Booking window is open for {desired_date}')
                print("Booking window is open! ", desired_date)
                server.send_message(msg)
                break
        else:
            msg['Subject'] = 'Marriott Booking Window Not Open'
            msg.set_content(f'Booking month is {furthest_booking_month}. Window has not opened yet for {desired_date}')
            print(f'Booking month is {furthest_booking_month}. Window has not opened yet for {desired_date}')
            server.send_message(msg)

    except Exception as e:
        print(f'Error booking!: {e}')
        server.sendmail(sender_email, recipient_email, f'Error booking: {e}')

    # Close the webdriver and email server
    driver.quit()
    server.quit()
except Exception as e:
    print(f'Error with gmail server: {e}')

