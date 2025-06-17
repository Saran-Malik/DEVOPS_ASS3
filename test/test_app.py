import unittest
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_USERNAME = "testuser_" 
TEST_PASSWORD = "testpass123"

class TodoAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
        cls.driver.implicitly_wait(10)
        cls.wait = WebDriverWait(cls.driver, 15)
        
        # Clean up any existing test data
        with sqlite3.connect('database.db') as conn:
            conn.execute("DELETE FROM users WHERE username LIKE 'testuser_%'")
            conn.commit()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def setUp(self):
        self.driver.get(BASE_URL)
        self.driver.delete_all_cookies()
        self.driver.set_window_size(1200, 1000)

    def _login(self):
        """Helper method to log in the test user"""
        self.driver.get(f"{BASE_URL}/login")
        username_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
        username_field.send_keys(TEST_USERNAME)
        password_field = self.driver.find_element(By.NAME, "password")
        password_field.send_keys(TEST_PASSWORD)
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        self.wait.until(EC.url_contains("/"))
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "form[action='/add']")))

    def _add_task(self, content, category="Work"):
        """Helper to add a new task"""
        self.driver.get(BASE_URL)
        task_input = self.wait.until(EC.presence_of_element_located((By.NAME, "content")))
        task_input.clear()
        task_input.send_keys(content)
        
        category_select = self.driver.find_element(By.NAME, "category")
        category_select.send_keys(category)
        
        add_button = self.driver.find_element(By.CSS_SELECTOR, "form[action='/add'] button[type='submit']")
        add_button.click()
        
        # Confirm task appears
        self.wait.until(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, ".list-group"), 
            content
        ))

    def test_1_register_and_login(self):
        """Test user registration and login flow"""
        self.driver.get(f"{BASE_URL}/register")
        username_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
        username_field.send_keys(TEST_USERNAME)
        password_field = self.driver.find_element(By.NAME, "password")
        password_field.send_keys(TEST_PASSWORD)
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        self.wait.until(EC.url_contains("/login"))
        
        # Login
        self._login()
        welcome_message = self.driver.find_element(By.TAG_NAME, "h2").text
        self.assertIn(TEST_USERNAME, welcome_message)

    def test_2_add_task(self):
        """Test adding a new task"""
        self._login()
        
        task_content = "Test Task " 
        self._add_task(task_content)
        
        # Verify task appears in list
        task_list = self.driver.find_element(By.CSS_SELECTOR, ".list-group").text
        self.assertIn(task_content, task_list)

    def test_3_task_operations(self):
        """Test marking task as done and deleting"""
        self._login()
        
        # Add test task
        task_content = "Task to complete " 
        self._add_task(task_content)
        
        # Mark as done
        done_button = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, f"//li[contains(., '{task_content}')]//a[contains(text(), 'Done')]")
        ))
        done_button.click()
        self.wait.until(EC.url_contains("/"))
        
        # Verify status updated to 'done'
        updated_task = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, f"//li[contains(., '{task_content}')]")
        ))
        self.assertIn("done", updated_task.text)
        
        # Delete task
        delete_button = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, f"//li[contains(., '{task_content}')]//a[contains(text(), 'Delete')]")
        ))
        delete_button.click()
        self.wait.until(EC.url_contains("/"))
        
        # Confirm task is no longer listed
        page_source = self.driver.page_source
        self.assertNotIn(task_content, page_source)

if __name__ == "__main__":
    unittest.main()
