from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.test import TestCase
from django.urls import reverse
import os

class StaffLoginTest(TestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()  # Use the appropriate WebDriver for your browser
        self.browser.implicitly_wait(10)  # Set an implicit wait for elements to be present
        self.live_server_url = 'http://127.0.0.1:8000/'

        # Log in as a superuser to add a temporary staff member
        self.browser.get(self.live_server_url)
        email_input = self.browser.find_element(By.NAME, 'email')
        password_input = self.browser.find_element(By.NAME, 'password')
        login_button = self.browser.find_element(By.XPATH, '//button[text()="Log In"]')
        email_input.send_keys('superuser@gmail.com')
        password_input.send_keys('superuser')
        login_button.click()

        # Navigate to the staff addition page
        add_staff_url = self.live_server_url + '/staff/add'
        self.browser.get(add_staff_url)

        # Fill in the staff details
        first_name_input = self.browser.find_element(By.NAME, 'first_name')
        last_name_input = self.browser.find_element(By.NAME, 'last_name')
        address_input = self.browser.find_element(By.NAME, 'address')
        email_input = self.browser.find_element(By.NAME, 'email')
        gender_select = self.browser.find_element(By.NAME, 'gender')
        password_input = self.browser.find_element(By.NAME, 'password')
        course_select = self.browser.find_element(By.NAME, 'course')
        profile_pic_input = self.browser.find_element(By.NAME, 'profile_pic')

        first_name_input.send_keys('John')
        last_name_input.send_keys('Doe')
        address_input.send_keys('123 Test Address')
        email_input.send_keys('staffuser@gmail.com')
        gender_select.send_keys('Male')
        password_input.send_keys('testpassword')
        course_select.send_keys('Mechanical Engineering (ME)')
        profile_pic_input.send_keys(os.path.join(os.getcwd(), 'main_app', 'static', 'image', 'favicon1.ico'))

        # Submit the staff addition form
        submit_button = self.browser.find_element(By.XPATH, "//button[normalize-space(.)='Add Staff']")
        self.browser.execute_script("arguments[0].click();", submit_button)

        # Log out from the superuser account
        logout_url = self.live_server_url + '/logout_user/'
        self.browser.get(logout_url)

    def test_staff_login(self):
        self.browser.get(self.live_server_url)

        email_input = self.browser.find_element(By.NAME, 'email')
        password_input = self.browser.find_element(By.NAME, 'password')
        login_button = self.browser.find_element(By.XPATH, '//button[text()="Log In"]')

        email_input.send_keys('staffuser@gmail.com')
        password_input.send_keys('testpassword')
        login_button.click()

        # Assert that the staff user is redirected to the staff home page
        staff_home_url = 'staff/home/'
        WebDriverWait(self.browser, 10).until(
            EC.url_to_be(self.live_server_url + staff_home_url)
        )
        self.assertEqual(self.browser.current_url, self.live_server_url + staff_home_url)

        # Check for the presence of page heading
        page_heading = self.browser.find_element(By.TAG_NAME, 'h1')
        self.assertEqual(page_heading.text, 'Staff Panel - John D (Mechanical Engineering (ME))')
        
    def tearDown(self):
        self.browser.quit()
        