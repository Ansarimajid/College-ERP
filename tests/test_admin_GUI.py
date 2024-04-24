from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from django.test import TestCase
import os

class AdminGUITest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = webdriver.Chrome()  # Use the appropriate WebDriver for your browser
        # self.browser.implicitly_wait(10)  # Set an implicit wait for elements to be present
        cls.live_server_url = 'http://127.0.0.1:8000/'

    def setUp(self):
        # Log in as the admin before each test
        self.browser.get(self.live_server_url)
        email_input = self.browser.find_element(By.NAME, 'email')
        password_input = self.browser.find_element(By.NAME, 'password')
        login_button = self.browser.find_element(By.XPATH, '//button[text()="Log In"]')
        email_input.send_keys('superuser@gmail.com')
        password_input.send_keys('superuser')
        login_button.click()

    def test_admin_login(self):
        # Assert that the admin user is redirected to the admin home page
        admin_home_url = 'admin/home/'
        self.assertEqual(self.browser.current_url, self.live_server_url + admin_home_url)

        # Check for the presence of page heading
        page_heading = self.browser.find_element(By.TAG_NAME, 'h1')
        self.assertEqual(page_heading.text, 'Administrative Dashboard')

    def test_admin_update_profile(self):
        # Navigate to the admin home page
        admin_home_url = self.live_server_url + 'admin/home/'
        self.browser.get(admin_home_url)

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

        success_message = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'alert-success'))
        )

        # Submit the form again to revert the changes
        submit_button = self.browser.find_element(By.XPATH, '//button[contains(text(), "Update Profile")]')
        self.browser.execute_script("arguments[0].click();", submit_button)

    def test_admin_add_manage_course(self):
        # Navigate to the admin home page
        admin_home_url = self.live_server_url + 'admin/home/'
        self.browser.get(admin_home_url)

        # Click on Course Expandable
        course_menu = self.browser.find_element(By.XPATH, "//a[@class='nav-link']//p[contains(text(), 'Course')]")
        course_menu.click()

        # Click on the "Add Course" link
        add_course_link = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/course/add']"))
        )
        add_course_link.click()

        # Fill in name of course
        name_input = self.browser.find_element(By.NAME, 'name')
        name_input.send_keys('Mechanical Engineering (ME)')

        # Submit the form to add the course
        submit_button = self.browser.find_element(By.XPATH, '//button[contains(text(), "Add Course")]')
        self.browser.execute_script("arguments[0].click();", submit_button)

        # Click on Course Expandable
        course_menu = self.browser.find_element(By.XPATH, "//a[@class='nav-link']//p[contains(text(), 'Course')]")
        course_menu.click()

        # Click on the "Manage Course" link
        manage_course_link = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/course/manage/']"))
        )
        manage_course_link.click()

        # Get the last row of the table
        courses_table = self.browser.find_element(By.CLASS_NAME, 'table')
        last_row = courses_table.find_elements(By.CSS_SELECTOR, 'tr')[-1]
        cells = last_row.find_elements(By.TAG_NAME, 'td')
        
        # Check the contents of each cell in the last row
        self.assertEqual(cells[1].text, 'Mechanical Engineering (ME)')

        # Click on the Edit button for the last course
        edit_link = last_row.find_element(By.CSS_SELECTOR, 'a.btn-info')
        self.browser.execute_script("arguments[0].click();", edit_link)

        # Update the course name
        new_name_input = self.browser.find_element(By.NAME, 'name')
        new_name_input.clear()
        new_name_input.send_keys('Aerospace Engineering (AE)')

        # Submit the form to update the course
        update_button = self.browser.find_element(By.XPATH, '//button[contains(text(), "Edit Course")]')
        update_button.click()

        # Click on Course Expandable
        course_menu = self.browser.find_element(By.XPATH, "//a[@class='nav-link']//p[contains(text(), 'Course')]")
        course_menu.click()

        # Click on the "Manage Course" link again
        manage_course_link = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/course/manage/']"))
        )
        manage_course_link.click()

        # Get the updated last row of the table
        courses_table = self.browser.find_element(By.CLASS_NAME, 'table')
        last_row = courses_table.find_elements(By.CSS_SELECTOR, 'tr')[-1]
        cells = last_row.find_elements(By.TAG_NAME, 'td')

        # Check the updated course name
        self.assertEqual(cells[1].text, 'Aerospace Engineering (AE)')

        # Click on the Delete button for the last course
        delete_link = last_row.find_element(By.CSS_SELECTOR, 'a.btn-danger')
        self.browser.execute_script("arguments[0].click();", delete_link)

        # Handle the confirm dialog
        alert = self.browser.switch_to.alert
        alert.accept()

    def add_test_subject(self):
        # Navigate to the admin home page
        admin_home_url = self.live_server_url + 'admin/home/'
        self.browser.get(admin_home_url)

        # Click on Subject Expandable
        subject_menu = self.browser.find_element(By.XPATH, "//a[@class='nav-link']//p[contains(text(), 'Subject')]")
        subject_menu.click()

        # Click on the "Add Subject" link
        add_subject_link = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/subject/add/']"))
        )
        add_subject_link.click()

        # Fill in name of subject
        name_input = self.browser.find_element(By.NAME, 'name')
        name_input.send_keys('Test Subject')

        # Select "John Doe" as the staff
        staff_select = Select(self.browser.find_element(By.ID, 'id_staff'))
        staff_select.select_by_visible_text('John Doe')

        # Select "Mechanical Engineering (ME)" as the course
        course_select = Select(self.browser.find_element(By.ID, 'id_course'))
        course_select.select_by_visible_text('Mechanical Engineering (ME)')

        # Submit the form to add the subject
        submit_button = self.browser.find_element(By.XPATH, '//button[contains(text(), "Add Subject")]')
        self.browser.execute_script("arguments[0].click();", submit_button)

    def test_admin_add_manage_subject(self):
        # Navigate to the admin home page
        admin_home_url = self.live_server_url + 'admin/home/'
        self.browser.get(admin_home_url)

        # Click on Subject Expandable
        subject_menu = self.browser.find_element(By.XPATH, "//a[@class='nav-link']//p[contains(text(), 'Subject')]")
        subject_menu.click()

        # Click on the "Add Subject" link
        add_subject_link = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/subject/add/']"))
        )
        add_subject_link.click()

        # Fill in name of subject
        name_input = self.browser.find_element(By.NAME, 'name')
        name_input.send_keys('Test Subject')

        # Select "John Doe" as the staff
        staff_select = Select(self.browser.find_element(By.ID, 'id_staff'))
        staff_select.select_by_visible_text('John Doe')

        # Select "Mechanical Engineering (ME)" as the course
        course_select = Select(self.browser.find_element(By.ID, 'id_course'))
        course_select.select_by_visible_text('Mechanical Engineering (ME)')

        # Submit the form to add the subject
        submit_button = self.browser.find_element(By.XPATH, '//button[contains(text(), "Add Subject")]')
        self.browser.execute_script("arguments[0].click();", submit_button)

        # Click on Subject Expandable
        subject_menu = self.browser.find_element(By.XPATH, "//a[@class='nav-link']//p[contains(text(), 'Subject')]")
        subject_menu.click()

        # Click on the "Manage Subject" link
        manage_subject_link = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/subject/manage/']"))
        )
        manage_subject_link.click()

        # Get the last row of the table
        subjects_table = self.browser.find_element(By.CLASS_NAME, 'table')
        last_row = subjects_table.find_elements(By.CSS_SELECTOR, 'tr')[-1]
        cells = last_row.find_elements(By.TAG_NAME, 'td')
        
        # Check the contents of each cell in the last row
        self.assertEqual(cells[1].text, 'Test Subject')

        # Click on the Edit button for the last subject
        edit_link = last_row.find_element(By.CSS_SELECTOR, 'a.btn-info')
        self.browser.execute_script("arguments[0].click();", edit_link)

        # Update the subject name
        new_name_input = self.browser.find_element(By.NAME, 'name')
        new_name_input.clear()
        new_name_input.send_keys('Test Subject 2')

        # Submit the form to update the subject
        update_button = self.browser.find_element(By.XPATH, '//button[contains(text(), "Edit Subject")]')
        update_button.click()

        # Click on subject Expandable
        subject_menu = self.browser.find_element(By.XPATH, "//a[@class='nav-link']//p[contains(text(), 'Subject')]")
        subject_menu.click()

        # Click on the "Manage subject" link again
        manage_subject_link = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/subject/manage/']"))
        )
        manage_subject_link.click()

        # Get the updated last row of the table
        subjects_table = self.browser.find_element(By.CLASS_NAME, 'table')
        last_row = subjects_table.find_elements(By.CSS_SELECTOR, 'tr')[-1]
        cells = last_row.find_elements(By.TAG_NAME, 'td')

        # Check the updated subject name
        self.assertEqual(cells[1].text, 'Test Subject 2')

        # Click on the Delete button for the last subject
        delete_link = last_row.find_element(By.CSS_SELECTOR, 'a.btn-danger')
        self.browser.execute_script("arguments[0].click();", delete_link)

        # Handle the confirm dialog
        alert = self.browser.switch_to.alert
        alert.accept()

    def test_admin_add_manage_session(self):
        # Navigate to the admin home page
        admin_home_url = self.live_server_url + 'admin/home/'
        self.browser.get(admin_home_url)

        # Click on Session Expandable
        session_menu = self.browser.find_element(By.XPATH, "//a[@class='nav-link']//p[contains(text(), 'Session')]")
        session_menu.click()

        # Click on the "Add Session" link
        add_session_link = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/add_session/']"))
        )
        add_session_link.click()

        # Fill in start and end year
        start_year_input = self.browser.find_element(By.ID, 'id_start_year')
        self.browser.execute_script("arguments[0].value = '2023-06-01';", start_year_input)

        end_year_input = self.browser.find_element(By.ID, 'id_end_year')
        self.browser.execute_script("arguments[0].value = '2024-05-31';", end_year_input)

        # Submit the form to add the session
        submit_button = self.browser.find_element(By.XPATH, '//button[contains(text(), "Add Session")]')
        self.browser.execute_script("arguments[0].click();", submit_button)

        # Click on Session Expandable
        session_menu = self.browser.find_element(By.XPATH, "//a[@class='nav-link']//p[contains(text(), 'Session')]")
        session_menu.click()

        # Click on the "Manage Session" link
        manage_session_link = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/session/manage/']"))
        )
        manage_session_link.click()

        # Get the last row of the table
        sessions_table = self.browser.find_element(By.CLASS_NAME, 'table')
        last_row = sessions_table.find_elements(By.CSS_SELECTOR, 'tr')[-1]
        cells = last_row.find_elements(By.TAG_NAME, 'td')

        # Check the contents of each cell in the last row
        self.assertEqual(cells[1].text, 'June 1, 2023')
        self.assertEqual(cells[2].text, 'May 31, 2024')

        # Click on the Edit button for the last session
        edit_link = last_row.find_element(By.CSS_SELECTOR, 'a.btn-info')
        self.browser.execute_script("arguments[0].click();", edit_link)

        # Update the start and end year
        start_year_input = self.browser.find_element(By.ID, 'id_start_year')
        self.browser.execute_script("arguments[0].value = '2023-07-01';", start_year_input)

        end_year_input = self.browser.find_element(By.ID, 'id_end_year')
        self.browser.execute_script("arguments[0].value = '2024-06-30';", end_year_input)

        # Submit the form to update the session
        update_button = self.browser.find_element(By.XPATH, '//button[contains(text(), "Update Session")]')
        update_button.click()

        # Click on Session Expandable
        session_menu = self.browser.find_element(By.XPATH, "//a[@class='nav-link']//p[contains(text(), 'Session')]")
        session_menu.click()

        # Click on the "Manage Session" link again
        manage_session_link = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/session/manage/']"))
        )
        manage_session_link.click()

        # Get the updated last row of the table
        sessions_table = self.browser.find_element(By.CLASS_NAME, 'table')
        last_row = sessions_table.find_elements(By.CSS_SELECTOR, 'tr')[-1]
        cells = last_row.find_elements(By.TAG_NAME, 'td')

        # Check the updated start and end year
        self.assertEqual(cells[1].text, 'July 1, 2023')
        self.assertEqual(cells[2].text, 'June 30, 2024')

        # Click on the Delete button for the last session
        delete_link = last_row.find_element(By.CSS_SELECTOR, 'a.btn-danger')
        self.browser.execute_script("arguments[0].click();", delete_link)

        # Handle the confirm dialog
        alert = self.browser.switch_to.alert
        alert.accept()

    def test_admin_add_manage_staff(self):
        # Navigate to the admin home page
        admin_home_url = self.live_server_url + 'admin/home/'
        self.browser.get(admin_home_url)

        # Click on the "Add Staff" link
        add_staff_link = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/staff/add']"))
        )
        add_staff_link.click()

        # Fill in the staff details
        first_name_input = self.browser.find_element(By.ID, 'id_first_name')
        first_name_input.send_keys('John')

        last_name_input = self.browser.find_element(By.ID, 'id_last_name')
        last_name_input.send_keys('Doe')

        email_input = self.browser.find_element(By.ID, 'id_email')
        email_input.send_keys('staffuser@example.com')

        gender_select = Select(self.browser.find_element(By.ID, 'id_gender'))
        gender_select.select_by_value('M')

        password_input = self.browser.find_element(By.ID, 'id_password')
        password_input.send_keys('testpassword')

        # Upload a test profile picture (replace with your file path)
        profile_pic_input = self.browser.find_element(By.ID, 'id_profile_pic')
        profile_pic_input.send_keys(os.path.join(os.getcwd(), 'main_app', 'static', 'image', 'favicon1.ico'))

        address_input = self.browser.find_element(By.ID, 'id_address')
        address_input.send_keys('123 Main St, Anytown USA')

        course_select = Select(self.browser.find_element(By.ID, 'id_course'))
        course_select.select_by_visible_text('Mechanical Engineering (ME)')

        # Submit the form to add the staff
        submit_button = self.browser.find_element(By.XPATH, '//button[contains(text(), "Add Staff")]')
        self.browser.execute_script("arguments[0].click();", submit_button)

        # Click on the "Manage Staff" link
        manage_staff_link = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/staff/manage/']"))
        )
        manage_staff_link.click()

        # Get the last row of the staff table
        staff_table = self.browser.find_element(By.CLASS_NAME, 'table')
        last_row = staff_table.find_elements(By.CSS_SELECTOR, 'tr')[-1]
        cells = last_row.find_elements(By.TAG_NAME, 'td')

        # Check the staff details in the last row
        self.assertEqual(cells[1].text, 'Doe, John')
        self.assertEqual(cells[2].text, 'staffuser@example.com')

        # Click on the Edit button for the last staff member
        edit_link = last_row.find_element(By.CSS_SELECTOR, 'a.btn-info')
        self.browser.execute_script("arguments[0].click();", edit_link)

        # Update the staff details
        first_name_input = self.browser.find_element(By.ID, 'id_first_name')
        first_name_input.clear()
        first_name_input.send_keys('Jane')

        # Submit the form to update the staff
        update_button = self.browser.find_element(By.XPATH, '//button[contains(text(), "Update Staff")]')
        self.browser.execute_script("arguments[0].click();", update_button)

        # Click on the "Manage Staff" link again
        manage_staff_link = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/staff/manage/']"))
        )
        manage_staff_link.click()

        # Get the updated last row of the staff table
        staff_table = self.browser.find_element(By.CLASS_NAME, 'table')
        last_row = staff_table.find_elements(By.CSS_SELECTOR, 'tr')[-1]
        cells = last_row.find_elements(By.TAG_NAME, 'td')

        # Check the updated staff details
        self.assertEqual(cells[1].text, 'Doe, Jane')
        self.assertEqual(cells[2].text, 'staffuser@example.com')

        # Click on the Delete button for the last staff member
        delete_link = last_row.find_element(By.CSS_SELECTOR, 'a.btn-danger')
        self.browser.execute_script("arguments[0].click();", delete_link)

        # Handle the confirm dialog
        alert = self.browser.switch_to.alert
        alert.accept()

    def test_admin_add_manage_student(self):
        # Navigate to the admin home page
        admin_home_url = self.live_server_url + 'admin/home/'
        self.browser.get(admin_home_url)

        # Click on the "Add Student" link
        add_student_link = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/student/add/']"))
        )
        add_student_link.click()

        # Fill in the student details
        first_name_input = self.browser.find_element(By.ID, 'id_first_name')
        first_name_input.send_keys('Test')

        last_name_input = self.browser.find_element(By.ID, 'id_last_name')
        last_name_input.send_keys('Student')

        email_input = self.browser.find_element(By.ID, 'id_email')
        email_input.send_keys('student@example.com')

        gender_select = Select(self.browser.find_element(By.ID, 'id_gender'))
        gender_select.select_by_value('M')

        password_input = self.browser.find_element(By.ID, 'id_password')
        password_input.send_keys('testpassword')

        # Upload a test profile picture (replace with your file path)
        profile_pic_input = self.browser.find_element(By.ID, 'id_profile_pic')
        profile_pic_input.send_keys(os.path.join(os.getcwd(), 'main_app', 'static', 'image', 'favicon1.ico'))

        address_input = self.browser.find_element(By.ID, 'id_address')
        address_input.send_keys('123 Test Address')

        course_select = Select(self.browser.find_element(By.ID, 'id_course'))
        course_select.select_by_visible_text('Mechanical Engineering (ME)')

        session_select = Select(self.browser.find_element(By.ID, 'id_session'))
        session_select.select_by_value('1')

        # Submit the form to add the student
        submit_button = self.browser.find_element(By.XPATH, '//button[contains(text(), "Add Student")]')
        self.browser.execute_script("arguments[0].click();", submit_button)

        # Click on the "Manage Student" link
        manage_student_link = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/student/manage/']"))
        )
        manage_student_link.click()

        # Get the last row of the student table
        student_table = self.browser.find_element(By.CLASS_NAME, 'table')
        last_row = student_table.find_elements(By.CSS_SELECTOR, 'tr')[-1]
        cells = last_row.find_elements(By.TAG_NAME, 'td')

        # Check the student details in the last row
        self.assertEqual(cells[1].text, 'Student, Test')
        self.assertEqual(cells[2].text, 'student@example.com')

        # Click on the Edit button for the last student
        edit_link = last_row.find_element(By.CSS_SELECTOR, 'a.btn-info')
        self.browser.execute_script("arguments[0].click();", edit_link)

        # Update the student details
        first_name_input = self.browser.find_element(By.ID, 'id_first_name')
        first_name_input.clear()
        first_name_input.send_keys('Testy')

        # Submit the form to update the student
        update_button = self.browser.find_element(By.XPATH, '//button[contains(text(), "Update Student")]')
        self.browser.execute_script("arguments[0].click();", update_button)

        # Click on the "Manage Student" link again
        manage_student_link = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/student/manage/']"))
        )
        manage_student_link.click()

        # Get the updated last row of the student table
        student_table = self.browser.find_element(By.CLASS_NAME, 'table')
        last_row = student_table.find_elements(By.CSS_SELECTOR, 'tr')[-1]
        cells = last_row.find_elements(By.TAG_NAME, 'td')

        # Check the updated student details
        self.assertEqual(cells[1].text, 'Student, Testy')
        self.assertEqual(cells[2].text, 'student@example.com')

        # Click on the Delete button for the last student
        delete_link = last_row.find_element(By.CSS_SELECTOR, 'a.btn-danger')
        self.browser.execute_script("arguments[0].click();", delete_link)

        # Handle the confirm dialog
        alert = self.browser.switch_to.alert
        alert.accept()

    def test_admin_send_notification_to_staff(self):
        # Navigate to the admin home page
        admin_home_url = self.live_server_url + 'admin/home/'
        self.browser.get(admin_home_url)

        # Click on the "Notify Staff" link
        notify_staff_link = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/admin_notify_staff']"))
        )
        notify_staff_link.click()

        # Get the row for John Doe
        staff_table = self.browser.find_element(By.CLASS_NAME, 'table')
        staff_rows = staff_table.find_elements(By.CSS_SELECTOR, 'tbody > tr')
        john_doe_row = None
        for row in staff_rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if cells[1].text == 'Doe, John':
                john_doe_row = row
                break

        self.assertIsNotNone(john_doe_row, "John Doe row not found in the staff table")

        # Click on the "Send Notification" button for John Doe
        send_notification_button = john_doe_row.find_element(By.CSS_SELECTOR, 'button.show_notification')
        self.browser.execute_script("arguments[0].click();", send_notification_button)

        modal_dialog = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'myModal'))
        )

        # Enter the notification message
        notification_message_input = modal_dialog.find_element(By.ID, 'message')
        notification_message_input.send_keys('Test Notification')

        # Click the "Send Notification" button
        send_notification_button = modal_dialog.find_element(By.ID, 'send')
        send_notification_button.click()

        # Wait for and accept alert
        alert = WebDriverWait(self.browser, 10).until(EC.alert_is_present())
        alert_text = alert.text
        alert.accept()

        # Check if the alert text contains "Notification Sent"
        self.assertIn('Notification Sent', alert_text)

    def test_admin_send_notification_to_student(self):
        # Navigate to the admin home page
        admin_home_url = self.live_server_url + 'admin/home/'
        self.browser.get(admin_home_url)

        # Click on the "Notify Student" link
        notify_student_link = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/admin_notify_student']"))
        )
        notify_student_link.click()

        # Get the row for the first student
        student_table = self.browser.find_element(By.CLASS_NAME, 'table')
        student_rows = student_table.find_elements(By.CSS_SELECTOR, 'tbody > tr')
        test_student_row = None
        for row in student_rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if cells[1].text == 'Student, Test':
                test_student_row = row
                break

        self.assertIsNotNone(test_student_row, "Test Student row not found in the student table")

        # Click on the "Send Notification" button for the student
        send_notification_button = test_student_row.find_element(By.CSS_SELECTOR, 'button.show_notification')
        self.browser.execute_script("arguments[0].click();", send_notification_button)

        # Wait for the modal dialog to be visible
        modal_dialog = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'myModal'))
        )

        # Enter the notification message
        notification_message_input = modal_dialog.find_element(By.ID, 'message')
        notification_message_input.send_keys('Test Notification')

        # Click the "Send Notification" button
        send_notification_button = modal_dialog.find_element(By.ID, 'send')
        send_notification_button.click()

        # Wait for and accept alert
        alert = WebDriverWait(self.browser, 10).until(EC.alert_is_present())
        alert_text = alert.text
        alert.accept()

        # Check if the alert text contains "Notification Sent"
        self.assertIn('Notification Sent', alert_text)

    def test_admin_view_attendance(self):
        # Navigate to the admin home page
        admin_home_url = self.live_server_url + 'admin/home/'
        self.browser.get(admin_home_url)

        # Click on the "View Attendance" link
        view_attendance_link = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/attendance/view/']"))
        )
        view_attendance_link.click()

        # Select "Test Subject" from the subject dropdown
        subject_select = Select(self.browser.find_element(By.ID, 'subject'))
        subject_select.select_by_visible_text('Test Subject')

        # Select the first session from the session dropdown
        session_select = Select(self.browser.find_element(By.ID, 'session'))
        session_select.select_by_index(1)  # Assuming the first session has index 1

        # Click the "Fetch Attendance" button
        fetch_attendance_button = self.browser.find_element(By.ID, 'fetch_attendance')
        fetch_attendance_button.click()

        # Wait for the attendance dates to appear
        attendance_date_select = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, 'attendance_date'))
        )

        # Check if the attendance dates are present
        self.assertTrue(attendance_date_select.is_displayed())

        # Select the first attendance date
        attendance_date_options = attendance_date_select.find_elements(By.TAG_NAME, 'option')
        if attendance_date_options:
            first_attendance_date = attendance_date_options[1].get_attribute('value')
            attendance_date_select = Select(self.browser.find_element(By.ID, 'attendance_date'))
            attendance_date_select.select_by_value(first_attendance_date)

        # Click the "Fetch Students" button
        fetch_students_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.ID, 'fetch_student'))
        )
        fetch_students_button.click()

        # Check if the student data is displayed
        student_data_container = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, 'student_data'))
        )
        self.assertTrue(student_data_container.is_displayed())

    def test_admin_student_feedback(self):
        # Navigate to the admin home page
        admin_home_url = self.live_server_url + 'admin/home/'
        self.browser.get(admin_home_url)

        # Click on the "Student Feedback" link
        student_feedback_link = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/student/view/feedback/']"))
        )
        student_feedback_link.click()

        # Wait for the feedback table to be present
        feedback_table = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'table.table-bordered'))
        )

        # Get all feedback rows
        feedback_rows = feedback_table.find_elements(By.CSS_SELECTOR, 'tbody > tr')

        # Check if there are at least 1 feedback row
        self.assertGreaterEqual(len(feedback_rows), 1)

        # Check the contents of the nth feedback row
        n = 2
        first_row_cells = feedback_rows[n].find_elements(By.TAG_NAME, 'td')
        self.assertEqual(first_row_cells[1].text, 'Student, Test')
        self.assertEqual(first_row_cells[2].text, 'From 2022-08-19 to 2022-08-27')
        self.assertEqual(first_row_cells[3].text, 'This is a test feedback')
        # self.assertEqual(first_row_cells[4].text, 'April 24, 2024, 6:39 a.m.')
        self.assertEqual(first_row_cells[5].text, 'Pending Response')

        # Click on the "Reply" button for the first feedback
        reply_button = first_row_cells[6].find_element(By.CSS_SELECTOR, 'button.reply_open_modal')
        reply_button.click()

        # Wait for the reply modal to be visible
        reply_modal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'reply_modal'))
        )

        # Enter a reply message
        reply_message_input = reply_modal.find_element(By.ID, 'reply_message')
        reply_message_input.send_keys('This is a test reply')

        # Click the "Reply" button in the modal
        reply_button = reply_modal.find_element(By.ID, 'reply_btn')
        reply_button.click()

        # Wait for the success message
        alert = WebDriverWait(self.browser, 10).until(EC.alert_is_present())
        alert_text = alert.text
        alert.accept()

        # Check if the alert text contains "Reply Sent"
        self.assertIn('Reply Sent', alert_text)

    def test_admin_staff_feedback(self):
        # Navigate to the admin home page
        admin_home_url = self.live_server_url + 'admin/home/'
        self.browser.get(admin_home_url)

        # Click on the "Staff Feedback" link
        staff_feedback_link = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/staff/view/feedback/']"))
        )
        staff_feedback_link.click()

        # Wait for the feedback table to be present
        feedback_table = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'table.table-bordered'))
        )

        # Get all feedback rows
        feedback_rows = feedback_table.find_elements(By.CSS_SELECTOR, 'tbody > tr')

        # Check if there are at least 1 feedback row
        self.assertGreaterEqual(len(feedback_rows), 1)

        # Check the contents of the nth feedback row
        n = 1
        first_row_cells = feedback_rows[n].find_elements(By.TAG_NAME, 'td')
        self.assertEqual(first_row_cells[1].text, 'John Doe')
        self.assertEqual(first_row_cells[2].text, 'Mechanical Engineering (ME)')
        self.assertEqual(first_row_cells[3].text, 'This is a test feedback')
        # self.assertEqual(first_row_cells[4].text, 'April 24, 2024, 3:22 a.m.')
        self.assertEqual(first_row_cells[5].text, 'Pending Response')

        # Click on the "Reply" button for the first feedback
        reply_button = first_row_cells[6].find_element(By.CSS_SELECTOR, 'button.reply_open_modal')
        reply_button.click()

        # Wait for the reply modal to be visible
        reply_modal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'reply_modal'))
        )

        # Enter a reply message
        reply_message_input = reply_modal.find_element(By.ID, 'reply_message')
        reply_message_input.send_keys('This is a test reply')

        # Click the "Reply" button in the modal
        reply_button = reply_modal.find_element(By.ID, 'reply_btn')
        reply_button.click()

        # Wait for the success message
        alert = WebDriverWait(self.browser, 10).until(EC.alert_is_present())
        alert_text = alert.text
        alert.accept()

        # Check if the alert text contains "Reply Sent"
        self.assertIn('Reply Sent', alert_text)

    def test_admin_staff_leave_accept(self):
        # Navigate to the admin home page
        admin_home_url = self.live_server_url + 'admin/home/'
        self.browser.get(admin_home_url)

        # Click on the "Staff Leave" link
        staff_leave_link = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/staff/view/leave/']"))
        )
        staff_leave_link.click()

        # Wait for the leave table to be present
        leave_table = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'table.table-bordered'))
        )

        # Get all leave rows
        leave_rows = leave_table.find_elements(By.CSS_SELECTOR, 'tbody > tr')

        # Check if there are at least 1 leave row
        self.assertGreaterEqual(len(leave_rows), 1)

        # Check the contents of the nth leave row
        john_doe_row = None
        for row in leave_rows[1:]:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if cells[1].text == 'John Doe' and cells[6].text == 'Reply':
                john_doe_row = cells
                break
        self.assertEqual(john_doe_row[1].text, 'John Doe')
        self.assertEqual(john_doe_row[2].text, 'Mechanical Engineering (ME)')
        self.assertEqual(john_doe_row[3].text, 'Applying for leave')

        # Click on the "Reply" button
        reply_button = john_doe_row[6].find_element(By.CSS_SELECTOR, 'button.reply_open_modal')
        self.browser.execute_script("arguments[0].click();", reply_button)

        # Wait for the reply modal to be visible
        reply_modal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'reply_modal'))
        )

        # Enter a reply message
        reply_message_input = Select(reply_modal.find_element(By.ID, 'reply_leave_status'))
        reply_message_input.select_by_visible_text('Accept')

        # Click the "Submit" button in the modal
        reply_button = reply_modal.find_element(By.ID, 'reply_btn')
        reply_button.click()

        # Wait for the success message
        alert = WebDriverWait(self.browser, 10).until(EC.alert_is_present())
        alert_text = alert.text
        alert.accept()

        # Check if the alert text contains "Reply Sent"
        self.assertIn('Leave Response Has Been Saved!', alert_text)

    def test_admin_staff_leave_reject(self):
        # Navigate to the admin home page
        admin_home_url = self.live_server_url + 'admin/home/'
        self.browser.get(admin_home_url)

        # Click on the "Staff Leave" link
        staff_leave_link = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/staff/view/leave/']"))
        )
        staff_leave_link.click()

        # Wait for the leave table to be present
        leave_table = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'table.table-bordered'))
        )

        # Get all leave rows
        leave_rows = leave_table.find_elements(By.CSS_SELECTOR, 'tbody > tr')

        # Check if there are at least 1 leave row
        self.assertGreaterEqual(len(leave_rows), 1)

        # Check the contents of the nth leave row
        john_doe_row = None
        for row in leave_rows[1:]:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if cells[1].text == 'John Doe' and cells[6].text == 'Reply':
                john_doe_row = cells
                break
        self.assertEqual(john_doe_row[1].text, 'John Doe')
        self.assertEqual(john_doe_row[2].text, 'Mechanical Engineering (ME)')
        self.assertEqual(john_doe_row[3].text, 'Applying for leave')

        # Click on the "Reply" button for the first leave
        reply_button = john_doe_row[6].find_element(By.CSS_SELECTOR, 'button.reply_open_modal')
        self.browser.execute_script("arguments[0].click();", reply_button)

        # Wait for the reply modal to be visible
        reply_modal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'reply_modal'))
        )

        # Enter a reply message
        reply_message_input = Select(reply_modal.find_element(By.ID, 'reply_leave_status'))
        reply_message_input.select_by_visible_text('Reject')

        # Click the "Submit" button in the modal
        reply_button = reply_modal.find_element(By.ID, 'reply_btn')
        reply_button.click()

        # Wait for the success message
        alert = WebDriverWait(self.browser, 10).until(EC.alert_is_present())
        alert_text = alert.text
        alert.accept()

        # Check if the alert text contains "Reply Sent"
        self.assertIn('Leave Response Has Been Saved!', alert_text)

    def test_admin_student_leave_approve(self):
        # Navigate to the admin home page
        admin_home_url = self.live_server_url + 'admin/home/'
        self.browser.get(admin_home_url)

        # Click on the "Student Leave" link
        student_leave_link = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/student/view/leave/']"))
        )
        student_leave_link.click()

        # Wait for the leave table to be present
        leave_table = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'table.table-bordered'))
        )

        # Get all leave rows
        leave_rows = leave_table.find_elements(By.CSS_SELECTOR, 'tbody > tr')

        # Check if there are at least 1 leave row
        self.assertGreaterEqual(len(leave_rows), 1)

        # Check the contents of the nth leave row
        john_doe_row = None
        for row in leave_rows[1:]:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if cells[1].text == 'Student, Test' and cells[6].text == 'Reply':
                john_doe_row = cells
                break
        self.assertEqual(john_doe_row[1].text, 'Student, Test')
        self.assertEqual(john_doe_row[2].text, 'Mechanical Engineering (ME)')
        self.assertEqual(john_doe_row[3].text, 'Applying for leave')

        # Click on the "Reply" button
        reply_button = john_doe_row[6].find_element(By.CSS_SELECTOR, 'button.reply_open_modal')
        self.browser.execute_script("arguments[0].click();", reply_button)

        # Wait for the reply modal to be visible
        reply_modal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'reply_modal'))
        )

        # Enter a reply message
        reply_message_input = Select(reply_modal.find_element(By.ID, 'reply_leave_status'))
        reply_message_input.select_by_visible_text('Approve')

        # Click the "Submit" button in the modal
        reply_button = reply_modal.find_element(By.ID, 'reply_btn')
        reply_button.click()

        # Wait for the success message
        alert = WebDriverWait(self.browser, 10).until(EC.alert_is_present())
        alert_text = alert.text
        alert.accept()

        # Check if the alert text contains "Reply Sent"
        self.assertIn('Leave Response Has Been Saved!', alert_text)

    def test_admin_student_leave_reject(self):
        # Navigate to the admin home page
        admin_home_url = self.live_server_url + 'admin/home/'
        self.browser.get(admin_home_url)

        # Click on the "Student Leave" link
        student_leave_link = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/student/view/leave/']"))
        )
        student_leave_link.click()

        # Wait for the leave table to be present
        leave_table = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'table.table-bordered'))
        )

        # Get all leave rows
        leave_rows = leave_table.find_elements(By.CSS_SELECTOR, 'tbody > tr')

        # Check if there are at least 1 leave row
        self.assertGreaterEqual(len(leave_rows), 1)

        # Check the contents of the nth leave row
        john_doe_row = None
        for row in leave_rows[1:]:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if cells[1].text == 'Student, Test' and cells[6].text == 'Reply':
                john_doe_row = cells
                break
        self.assertEqual(john_doe_row[1].text, 'Student, Test')
        self.assertEqual(john_doe_row[2].text, 'Mechanical Engineering (ME)')
        self.assertEqual(john_doe_row[3].text, 'Applying for leave')

        # Click on the "Reply" button
        reply_button = john_doe_row[6].find_element(By.CSS_SELECTOR, 'button.reply_open_modal')
        self.browser.execute_script("arguments[0].click();", reply_button)

        # Wait for the reply modal to be visible
        reply_modal = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'reply_modal'))
        )

        # Enter a reply message
        reply_message_input = Select(reply_modal.find_element(By.ID, 'reply_leave_status'))
        reply_message_input.select_by_visible_text('Reject')

        # Click the "Submit" button in the modal
        reply_button = reply_modal.find_element(By.ID, 'reply_btn')
        reply_button.click()

        # Wait for the success message
        alert = WebDriverWait(self.browser, 10).until(EC.alert_is_present())
        alert_text = alert.text
        alert.accept()

        # Check if the alert text contains "Reply Sent"
        self.assertIn('Leave Response Has Been Saved!', alert_text)

    def tearDown(self):
        logout_url = self.live_server_url + '/logout_user/'
        self.browser.get(logout_url)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()