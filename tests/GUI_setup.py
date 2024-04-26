from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from django.test import TestCase
import os

# Be sure to set up superuser before hand with
# email: superuser@gmail.com
# password: superuser

browser = webdriver.Chrome()
live_server_url = 'http://127.0.0.1:8000/'

def login_as_admin():
    browser.get(live_server_url)
    email_input = browser.find_element(By.NAME, 'email')
    password_input = browser.find_element(By.NAME, 'password')
    login_button = browser.find_element(By.XPATH, '//button[text()="Log In"]')
    email_input.send_keys('superuser@gmail.com')
    password_input.send_keys('superuser')
    login_button.click()

def login_as_staff():
    browser.get(live_server_url)
    email_input = browser.find_element(By.NAME, 'email')
    password_input = browser.find_element(By.NAME, 'password')
    login_button = browser.find_element(By.XPATH, '//button[text()="Log In"]')
    email_input.send_keys('staffuser@gmail.com')
    password_input.send_keys('testpassword')
    login_button.click()

def login_as_student():
    browser.get(live_server_url)
    email_input = browser.find_element(By.NAME, 'email')
    password_input = browser.find_element(By.NAME, 'password')
    login_button = browser.find_element(By.XPATH, '//button[text()="Log In"]')
    email_input.send_keys('student@gmail.com')
    password_input.send_keys('testpassword')
    login_button.click()

def admin_update_profile():
    # Navigate to the admin home page
    admin_home_url = live_server_url + 'admin/home/'
    browser.get(admin_home_url)

    # Click on the "Update Profile" link
    update_profile_link = browser.find_element(By.PARTIAL_LINK_TEXT, 'Update Profile')
    update_profile_link.click()

    # Fill in the form fields
    first_name_input = browser.find_element(By.NAME, 'first_name')
    first_name_input.clear()
    first_name_input.send_keys('Admin')

    last_name_input = browser.find_element(By.NAME, 'last_name')
    last_name_input.clear()
    last_name_input.send_keys('User')

    profile_pic_input = browser.find_element(By.NAME, 'profile_pic')
    profile_pic_input.send_keys(os.path.join(os.getcwd(), 'main_app', 'static', 'image', 'favicon1.ico'))

    address_input = browser.find_element(By.NAME, 'address')
    address_input.clear()
    address_input.send_keys('123 Test Address')

    gender_select = Select(browser.find_element(By.NAME, 'gender'))
    gender_select.select_by_value('M')

    # Submit the form
    submit_button = browser.find_element(By.XPATH, '//button[contains(text(), "Update Profile")]')
    browser.execute_script("arguments[0].click();", submit_button)

    # Wait for the success message to be present (up to 10 seconds)
    success_message = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'alert-success'))
    )

def admin_add_staff():
    # Navigate to the staff addition page
    add_staff_url = live_server_url + 'staff/add'
    browser.get(add_staff_url)

    # Fill in the staff details
    first_name_input = browser.find_element(By.NAME, 'first_name')
    last_name_input = browser.find_element(By.NAME, 'last_name')
    address_input = browser.find_element(By.NAME, 'address')
    email_input = browser.find_element(By.NAME, 'email')
    gender_select = browser.find_element(By.NAME, 'gender')
    password_input = browser.find_element(By.NAME, 'password')
    course_select = browser.find_element(By.NAME, 'course')
    profile_pic_input = browser.find_element(By.NAME, 'profile_pic')

    first_name_input.send_keys('John')
    last_name_input.send_keys('Doe')
    address_input.send_keys('123 Test Address')
    email_input.send_keys('staffuser@gmail.com')
    gender_select.send_keys('Male')
    password_input.send_keys('testpassword')
    course_select.send_keys('Mechanical Engineering (ME)')
    profile_pic_input.send_keys(os.path.join(os.getcwd(), 'main_app', 'static', 'image', 'favicon1.ico'))

    # Submit the staff addition form
    submit_button = browser.find_element(By.XPATH, "//button[normalize-space(.)='Add Staff']")
    browser.execute_script("arguments[0].click();", submit_button)

def admin_add_student():
    # Navigate to the student addition page
    add_student_url = live_server_url + 'student/add'
    browser.get(add_student_url)

    # Fill in the student details
    first_name_input = browser.find_element(By.NAME, 'first_name')
    last_name_input = browser.find_element(By.NAME, 'last_name')
    address_input = browser.find_element(By.NAME, 'address')
    email_input = browser.find_element(By.NAME, 'email')
    gender_select = browser.find_element(By.NAME, 'gender')
    password_input = browser.find_element(By.NAME, 'password')
    course_select = browser.find_element(By.NAME, 'course')
    profile_pic_input = browser.find_element(By.NAME, 'profile_pic')
    session_select = Select(browser.find_element(By.ID, 'id_session'))
    
    first_name_input.send_keys('Test')
    last_name_input.send_keys('Student')
    address_input.send_keys('123 Test Address')
    email_input.send_keys('student@gmail.com')
    gender_select.send_keys('Male')
    password_input.send_keys('testpassword')
    course_select.send_keys('Mechanical Engineering (ME)')
    profile_pic_input.send_keys(os.path.join(os.getcwd(), 'main_app', 'static', 'image', 'favicon1.ico'))
    session_select.select_by_index(1)

    # Submit the student addition form
    submit_button = browser.find_element(By.XPATH, "//button[normalize-space(.)='Add Student']")
    browser.execute_script("arguments[0].click();", submit_button)

def admin_add_test_subject():
    # Navigate to the admin home page
    admin_home_url = live_server_url + 'admin/home/'
    browser.get(admin_home_url)

    # Click on Subject Expandable
    subject_menu = browser.find_element(By.XPATH, "//a[@class='nav-link']//p[contains(text(), 'Subject')]")
    subject_menu.click()

    # Click on the "Add Subject" link
    add_subject_link = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/subject/add/']"))
    )
    add_subject_link.click()

    # Fill in name of subject
    name_input = browser.find_element(By.NAME, 'name')
    name_input.send_keys('Test Subject')

    # Select "John Doe" as the staff
    staff_select = Select(browser.find_element(By.ID, 'id_staff'))
    staff_select.select_by_visible_text('John Doe')

    # Select "Mechanical Engineering (ME)" as the course
    course_select = Select(browser.find_element(By.ID, 'id_course'))
    course_select.select_by_visible_text('Mechanical Engineering (ME)')

    # Submit the form to add the subject
    submit_button = browser.find_element(By.XPATH, '//button[contains(text(), "Add Subject")]')
    browser.execute_script("arguments[0].click();", submit_button)

def admin_send_notification_to_staff():
    # Navigate to the admin home page
    admin_home_url = live_server_url + 'admin/home/'
    browser.get(admin_home_url)

    # Click on the "Notify Staff" link
    notify_staff_link = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@href='/admin_notify_staff']"))
    )
    notify_staff_link.click()

    # Get the row for John Doe
    staff_table = browser.find_element(By.CLASS_NAME, 'table')
    staff_rows = staff_table.find_elements(By.CSS_SELECTOR, 'tbody > tr')
    john_doe_row = None
    for row in staff_rows:
        cells = row.find_elements(By.TAG_NAME, 'td')
        if cells[1].text == 'Doe, John':
            john_doe_row = row
            break

    # Click on the "Send Notification" button for John Doe
    send_notification_button = john_doe_row.find_element(By.CSS_SELECTOR, 'button.show_notification')
    browser.execute_script("arguments[0].click();", send_notification_button)

    modal_dialog = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.ID, 'myModal'))
    )

    # Enter the notification message
    notification_message_input = modal_dialog.find_element(By.ID, 'message')
    notification_message_input.send_keys('Test Notification')

    # Click the "Send Notification" button
    send_notification_button = modal_dialog.find_element(By.ID, 'send')
    send_notification_button.click()

    # Wait for and accept alert
    alert = WebDriverWait(browser, 10).until(EC.alert_is_present())
    alert_text = alert.text
    alert.accept()

def admin_send_notification_to_student():
    # Navigate to the admin home page
    admin_home_url = live_server_url + 'admin/home/'
    browser.get(admin_home_url)

    # Click on the "Notify Student" link
    notify_student_link = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@href='/admin_notify_student']"))
    )
    notify_student_link.click()

    # Get the row for the first student
    student_table = browser.find_element(By.CLASS_NAME, 'table')
    student_rows = student_table.find_elements(By.CSS_SELECTOR, 'tbody > tr')
    test_student_row = None
    for row in student_rows:
        cells = row.find_elements(By.TAG_NAME, 'td')
        if cells[1].text == 'Student, Test':
            test_student_row = row
            break

    # Click on the "Send Notification" button for the student
    send_notification_button = test_student_row.find_element(By.CSS_SELECTOR, 'button.show_notification')
    browser.execute_script("arguments[0].click();", send_notification_button)

    # Wait for the modal dialog to be visible
    modal_dialog = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.ID, 'myModal'))
    )

    # Enter the notification message
    notification_message_input = modal_dialog.find_element(By.ID, 'message')
    notification_message_input.send_keys('Test Notification')

    # Click the "Send Notification" button
    send_notification_button = modal_dialog.find_element(By.ID, 'send')
    send_notification_button.click()

    # Wait for and accept alert
    alert = WebDriverWait(browser, 10).until(EC.alert_is_present())
    alert_text = alert.text
    alert.accept()

def staff_add_books():
    # Navigate to the staff home page
    staff_home_url = live_server_url + 'staff/home/'
    browser.get(staff_home_url)

    # Click on the "Add Books To Lib" link
    add_books_link = browser.find_element(By.PARTIAL_LINK_TEXT, 'Add Books To Lib')
    add_books_link.click()

    # Fill in the form fields
    name_input = browser.find_element(By.NAME, 'name')
    name_input.send_keys('Test Book')

    author_input = browser.find_element(By.NAME, 'author')
    author_input.send_keys('Test Author')

    isbn_input = browser.find_element(By.NAME, 'isbn')
    isbn_input.send_keys('1234567890')

    category_input = browser.find_element(By.NAME, 'category')
    category_input.send_keys('Test Category')

    # Submit the form
    submit_button = browser.find_element(By.XPATH, '//button[contains(text(), "Add Book")]')
    submit_button.click()

def staff_take_attendance():
    # Navigate to the staff home page
    staff_home_url = live_server_url + 'staff/home/'
    browser.get(staff_home_url)

    # Click on the "Take Attendance" link
    take_attendance_link = browser.find_element(By.PARTIAL_LINK_TEXT, 'Take Attendance')
    take_attendance_link.click()

    # Fill in the form to take attendance
    subject_select = Select(browser.find_element(By.ID, 'subject'))
    subject_select.select_by_visible_text('Test Subject')

    session_select = Select(browser.find_element(By.ID, 'session'))
    session_select.select_by_value('1')

    fetch_student_button = browser.find_element(By.ID, 'fetch_student')
    fetch_student_button.click()

    # Wait for the student data to be loaded
    student_data_block = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, 'student_data'))
    )

    attendance_date_input = browser.find_element(By.ID, 'attendance_date')
    browser.execute_script("arguments[0].value = '2023-06-01';", attendance_date_input)

    save_attendance_button = browser.find_element(By.ID, 'save_attendance')
    save_attendance_button.click()

    # Wait for the alert to be present and switch to it
    alert = WebDriverWait(browser, 10).until(EC.alert_is_present())
    alert_text = alert.text
    alert.accept()

def staff_apply_leave():
    # Navigate to the staff home page
    staff_home_url = live_server_url + 'staff/home/'
    browser.get(staff_home_url)

    # Click on the "Apply for Leave" link
    apply_leave_link = browser.find_element(By.PARTIAL_LINK_TEXT, 'Apply For Leave')
    apply_leave_link.click()

    # Fill in the form fields
    date_input = browser.find_element(By.NAME, 'date')
    browser.execute_script("arguments[0].value = '2023-06-01';", date_input)
    message_input = browser.find_element(By.NAME, 'message')
    message_input.send_keys('Applying for leave')

    # Submit the form
    submit_button = browser.find_element(By.XPATH, '//button[contains(text(), "Apply For Leave")]')
    submit_button.click()
    # Wait for the success message to be present (up to 10 seconds)
    success_message = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'alert-success'))
    )

def staff_feedback():
    # Navigate to the staff home page
    staff_home_url = live_server_url + 'staff/home/'
    browser.get(staff_home_url)

    # Click on the "Add Feedback" link
    add_feedback_link = browser.find_element(By.PARTIAL_LINK_TEXT, 'Feedback')
    add_feedback_link.click()

    # Fill in the form field
    feedback_input = browser.find_element(By.NAME, 'feedback')
    feedback_input.send_keys('This is a test feedback')

    # Submit the form
    submit_button = browser.find_element(By.XPATH, '//button[contains(text(), "Submit Feedback")]')
    submit_button.click()

    # Wait for the success message to be present (up to 10 seconds)
    success_message = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'alert-success'))
    )

def student_apply_leave():
    # Navigate to the student home page
    student_home_url = live_server_url + 'student/home/'
    browser.get(student_home_url)

    # Click on the "Apply for Leave" link
    apply_leave_link = browser.find_element(By.PARTIAL_LINK_TEXT, 'Apply For Leave')
    apply_leave_link.click()

    # Fill in the form fields
    date_input = browser.find_element(By.NAME, 'date')
    browser.execute_script("arguments[0].value = '2023-06-01';", date_input)
    message_input = browser.find_element(By.NAME, 'message')
    message_input.send_keys('Applying for leave')

    # Submit the form
    submit_button = browser.find_element(By.XPATH, '//button[contains(text(), "Apply For Leave")]')
    submit_button.click()
    # Wait for the success message to be present (up to 10 seconds)
    success_message = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'alert-success'))
    )

def student_feedback():
    # Navigate to the student home page
    student_home_url = live_server_url + 'student/home/'
    browser.get(student_home_url)

    # Click on the "Add Feedback" link
    add_feedback_link = browser.find_element(By.PARTIAL_LINK_TEXT, 'Feedback')
    add_feedback_link.click()

    # Fill in the form field
    feedback_input = browser.find_element(By.NAME, 'feedback')
    feedback_input.send_keys('This is a test feedback')

    # Submit the form
    submit_button = browser.find_element(By.XPATH, '//button[contains(text(), "Submit Feedback")]')
    submit_button.click()

    # Wait for the success message to be present (up to 10 seconds)
    success_message = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'alert-success'))
    )

def logout():
    logout_url = live_server_url + '/logout_user/'
    browser.get(logout_url)

login_as_admin()
admin_update_profile()
admin_add_staff()
admin_add_student()
admin_add_test_subject()
admin_send_notification_to_staff()
admin_send_notification_to_student()
logout()
login_as_staff()
staff_take_attendance()
staff_add_books()
staff_apply_leave()
staff_apply_leave()
staff_feedback()
logout()
login_as_student()
student_apply_leave()
student_apply_leave()
student_feedback()
logout()

browser.quit()