from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from django.test import TestCase
from django.urls import reverse
import os

class StaffLoginTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = webdriver.Chrome()  # Use the appropriate WebDriver for your browser
        # self.browser.implicitly_wait(10)  # Set an implicit wait for elements to be present
        cls.live_server_url = 'http://127.0.0.1:8000/'

        # Log in as a superuser to add a temporary staff member
        cls.browser.get(cls.live_server_url)
        email_input = cls.browser.find_element(By.NAME, 'email')
        password_input = cls.browser.find_element(By.NAME, 'password')
        login_button = cls.browser.find_element(By.XPATH, '//button[text()="Log In"]')
        email_input.send_keys('superuser@gmail.com')
        password_input.send_keys('superuser')
        login_button.click()

        # Navigate to the staff addition page
        add_staff_url = cls.live_server_url + 'staff/add'
        cls.browser.get(add_staff_url)

        # Fill in the staff details
        first_name_input = cls.browser.find_element(By.NAME, 'first_name')
        last_name_input = cls.browser.find_element(By.NAME, 'last_name')
        address_input = cls.browser.find_element(By.NAME, 'address')
        email_input = cls.browser.find_element(By.NAME, 'email')
        gender_select = cls.browser.find_element(By.NAME, 'gender')
        password_input = cls.browser.find_element(By.NAME, 'password')
        course_select = cls.browser.find_element(By.NAME, 'course')
        profile_pic_input = cls.browser.find_element(By.NAME, 'profile_pic')

        first_name_input.send_keys('John')
        last_name_input.send_keys('Doe')
        address_input.send_keys('123 Test Address')
        email_input.send_keys('staffuser@gmail.com')
        gender_select.send_keys('Male')
        password_input.send_keys('testpassword')
        course_select.send_keys('Mechanical Engineering (ME)')
        profile_pic_input.send_keys(os.path.join(os.getcwd(), 'main_app', 'static', 'image', 'favicon1.ico'))

        # Submit the staff addition form
        submit_button = cls.browser.find_element(By.XPATH, "//button[normalize-space(.)='Add Staff']")
        cls.browser.execute_script("arguments[0].click();", submit_button)

        # Log out from the superuser account
        logout_url = cls.live_server_url + '/logout_user/'
        cls.browser.get(logout_url)

    def setUp(self):
        # Log in as the staff user before each test
        self.browser.get(self.live_server_url)
        email_input = self.browser.find_element(By.NAME, 'email')
        password_input = self.browser.find_element(By.NAME, 'password')
        login_button = self.browser.find_element(By.XPATH, '//button[text()="Log In"]')
        email_input.send_keys('staffuser@gmail.com')
        password_input.send_keys('testpassword')
        login_button.click()

    def test_staff_login(self):
        # Assert that the staff user is redirected to the staff home page
        staff_home_url = 'staff/home/'
        self.assertEqual(self.browser.current_url, self.live_server_url + staff_home_url)

        # Check for the presence of page heading
        page_heading = self.browser.find_element(By.TAG_NAME, 'h1')
        self.assertEqual(page_heading.text, 'Staff Panel - John D (Mechanical Engineering (ME))')

    def test_staff_update_profile(self):
        # Navigate to the staff home page
        staff_home_url = self.live_server_url + 'staff/home/'
        self.browser.get(staff_home_url)

        # Click on the "Update Profile" link
        update_profile_link = self.browser.find_element(By.PARTIAL_LINK_TEXT, 'Update Profile')
        update_profile_link.click()

        # Fill in the form fields
        first_name_input = self.browser.find_element(By.NAME, 'first_name')
        original_first_name = first_name_input.get_attribute('value')
        first_name_input.clear()
        first_name_input.send_keys('Updated First Name')

        last_name_input = self.browser.find_element(By.NAME, 'last_name')
        original_last_name = last_name_input.get_attribute('value')
        last_name_input.clear()
        last_name_input.send_keys('Updated Last Name')

        address_input = self.browser.find_element(By.NAME, 'address')
        original_address = address_input.get_attribute('value')
        address_input.clear()
        address_input.send_keys('Updated Address')

        gender_select = Select(self.browser.find_element(By.NAME, 'gender'))
        original_gender = gender_select.first_selected_option.text
        gender_select.select_by_value('F')

        # Submit the form
        submit_button = self.browser.find_element(By.XPATH, '//button[contains(text(), "Update Profile")]')
        self.browser.execute_script("arguments[0].click();", submit_button)

        # Wait for the success message to be present (up to 10 seconds)
        success_message = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'alert-success'))
        )
        self.assertIn('Profile Updated!', success_message.text)

        # Check if the profile is updated correctly
        updated_first_name = self.browser.find_element(By.NAME, 'first_name').get_attribute('value')
        self.assertEqual(updated_first_name, 'Updated First Name')

        updated_last_name = self.browser.find_element(By.NAME, 'last_name').get_attribute('value')
        self.assertEqual(updated_last_name, 'Updated Last Name')

        updated_address = self.browser.find_element(By.NAME, 'address').get_attribute('value')
        self.assertEqual(updated_address, 'Updated Address')

        updated_gender = Select(self.browser.find_element(By.NAME, 'gender')).first_selected_option.text
        self.assertEqual(updated_gender, 'Female')

        # Revert the profile back to the original values
        first_name_input = self.browser.find_element(By.NAME, 'first_name')
        first_name_input.clear()
        first_name_input.send_keys(original_first_name)

        last_name_input = self.browser.find_element(By.NAME, 'last_name')
        last_name_input.clear()
        last_name_input.send_keys(original_last_name)

        address_input = self.browser.find_element(By.NAME, 'address')
        address_input.clear()
        address_input.send_keys(original_address)

        gender_select = Select(self.browser.find_element(By.NAME, 'gender'))
        gender_select.select_by_visible_text(original_gender)

        # Submit the form again to revert the changes
        submit_button = self.browser.find_element(By.XPATH, '//button[contains(text(), "Update Profile")]')
        self.browser.execute_script("arguments[0].click();", submit_button)

    def test_staff_add_result(self):
        # Navigate to the staff home page
        staff_home_url = self.live_server_url + 'staff/home/'
        self.browser.get(staff_home_url)

        # Click on the "Add Result" link
        add_result_link = self.browser.find_element(By.PARTIAL_LINK_TEXT, 'Add Result')
        add_result_link.click()

        #TODO

    def test_staff_edit_result(self):
        # Navigate to the staff home page
        staff_home_url = self.live_server_url + 'staff/home/'
        self.browser.get(staff_home_url)

        # Click on the "Edit Result" link
        edit_result_link = self.browser.find_element(By.PARTIAL_LINK_TEXT, 'Edit Result')
        edit_result_link.click()

        #TODO

    def test_staff_take_attendance(self):
        # Navigate to the staff home page
        staff_home_url = self.live_server_url + 'staff/home/'
        self.browser.get(staff_home_url)

        # Click on the "Take Attendance" link
        take_attendance_link = self.browser.find_element(By.PARTIAL_LINK_TEXT, 'Take Attendance')
        take_attendance_link.click()

        #TODO

    def test_staff_update_attendance(self):
        # Navigate to the staff home page
        staff_home_url = self.live_server_url + 'staff/home/'
        self.browser.get(staff_home_url)

        # Click on the "View/Update Attendance" link
        update_attendance_link = self.browser.find_element(By.PARTIAL_LINK_TEXT, 'View/Update Attendance')
        update_attendance_link.click()

        #TODO
    
    def test_staff_view_notifications(self):
        # Navigate to the staff home page
        staff_home_url = self.live_server_url + 'staff/home/'
        self.browser.get(staff_home_url)

        # Click on the "View Notifications" link
        view_notifications_link = self.browser.find_element(By.PARTIAL_LINK_TEXT, 'View Notifications')
        view_notifications_link.click()

        #TODO

    def test_staff_add_books(self):
        # Navigate to the staff home page
        staff_home_url = self.live_server_url + 'staff/home/'
        self.browser.get(staff_home_url)

        # Click on the "Add Books To Lib" link
        add_books_link = self.browser.find_element(By.PARTIAL_LINK_TEXT, 'Add Books To Lib')
        add_books_link.click()

        #TODO

    def test_staff_apply_leave(self):
        # Navigate to the staff home page
        staff_home_url = self.live_server_url + 'staff/home/'
        self.browser.get(staff_home_url)

        # Click on the "Apply for Leave" link
        apply_leave_link = self.browser.find_element(By.PARTIAL_LINK_TEXT, 'Apply For Leave')
        apply_leave_link.click()

        # Fill in the form fields
        date_input = self.browser.find_element(By.NAME, 'date')
        self.browser.execute_script("arguments[0].value = '2023-06-01';", date_input)
        message_input = self.browser.find_element(By.NAME, 'message')
        message_input.send_keys('Applying for leave')  # Replace with the desired message

        # Submit the form
        submit_button = self.browser.find_element(By.XPATH, '//button[contains(text(), "Apply For Leave")]')
        submit_button.click()
        # Wait for the success message to be present (up to 10 seconds)
        success_message = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'alert-success'))
        )
        self.assertIn('Application for leave has been submitted for review', success_message.text)

        # Check if the leave request is added to the leave history table
        leave_history_table = self.browser.find_element(By.CLASS_NAME, 'table')
        table_rows = leave_history_table.find_elements(By.TAG_NAME, 'tr')
        self.assertGreater(len(table_rows), 1)  # Assuming there is at least one leave request in the history

    def test_staff_feedback(self):
        # Navigate to the staff home page
        staff_home_url = self.live_server_url + 'staff/home/'
        self.browser.get(staff_home_url)

        # Click on the "Add Feedback" link
        add_feedback_link = self.browser.find_element(By.PARTIAL_LINK_TEXT, 'Feedback')
        add_feedback_link.click()

        # Fill in the form field
        feedback_input = self.browser.find_element(By.NAME, 'feedback')
        feedback_input.send_keys('This is a test feedback')

        # Submit the form
        submit_button = self.browser.find_element(By.XPATH, '//button[contains(text(), "Submit Feedback")]')
        submit_button.click()

        # Wait for the success message to be present (up to 10 seconds)
        success_message = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'alert-success'))
        )
        self.assertIn('Feedback submitted for review', success_message.text)

        # Check if the feedback is added to the feedback table
        feedback_table = self.browser.find_element(By.CLASS_NAME, 'table')
        table_rows = feedback_table.find_elements(By.TAG_NAME, 'tr')
        self.assertGreater(len(table_rows), 1)  # Assuming there is at least one feedback in the table

        # Check if the feedback text is present in the table
        feedback_text = self.browser.find_element(By.XPATH, '//td[contains(text(), "This is a test feedback")]')
        self.assertIsNotNone(feedback_text)

    def tearDown(self):
        logout_url = self.live_server_url + '/logout_user/'
        self.browser.get(logout_url)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()