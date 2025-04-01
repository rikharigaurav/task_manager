# test_frontend.py - Frontend Integration Tests
import unittest
import subprocess
import time
import requests
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

API_URL = "http://localhost:5000/api"
FRONTEND_URL = "http://localhost:8501"

class TestStreamlitFrontend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start the Flask server in a separate process
        cls.api_process = subprocess.Popen(
            ["python", "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Start the Streamlit frontend in a separate process
        cls.frontend_process = subprocess.Popen(
            ["streamlit", "run", "frontend.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give the servers some time to start
        time.sleep(5)
        
        # Clean database for testing
        if os.path.exists('database/tasks.db'):
            os.remove('database/tasks.db')
        
        # Setup selenium webdriver
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        cls.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        cls.driver.implicitly_wait(10)
    
    @classmethod
    def tearDownClass(cls):
        # Close the browser
        cls.driver.quit()
        
        # Terminate the server processes
        cls.api_process.terminate()
        cls.api_process.wait()
        
        cls.frontend_process.terminate()
        cls.frontend_process.wait()
    
    def setUp(self):
        # Create a test task via API for testing
        task_data = {
            "title": "Test Frontend Task",
            "description": "This is a test task for frontend testing",
            "status": "pending",
            "priority": 2
        }
        
        response = requests.post(f"{API_URL}/tasks", json=task_data)
        data = response.json()
        self.task_id = data["id"]
        
        # Navigate to the Streamlit app
        self.driver.get(FRONTEND_URL)
        
        # Allow time for the app to load
        time.sleep(3)
    
    def tearDown(self):
        # Clean up the test task
        try:
            requests.delete(f"{API_URL}/tasks/{self.task_id}")
        except:
            pass
    
    def test_1_app_loads(self):
        """Test that the Streamlit app loads successfully"""
        title = self.driver.find_element(By.TAG_NAME, "h1").text
        self.assertIn("Task Manager", title)
    
    def test_2_task_list_displays(self):
        """Test that the tasks list displays the test task"""
        # Navigate to the Manage Tasks tab
        tabs = self.driver.find_elements(By.CSS_SELECTOR, "button[role='tab']")
        tabs[1].click()  # Click the "Manage Tasks" tab
        
        # Wait for the task list to load
        time.sleep(2)
        
        # Find task expanders
        expanders = self.driver.find_elements(By.CSS_SELECTOR, "div[data-testid='stExpander']")
        
        # Check if our test task is displayed
        found = False
        for expander in expanders:
            header_text = expander.find_element(By.CSS_SELECTOR, "span.streamlit-expanderHeader").text
            if "Test Frontend Task" in header_text:
                found = True
                break
        
        self.assertTrue(found, "Test task not found in the tasks list")
    
    def test_3_create_new_task(self):
        """Test creating a new task through the UI"""
        # Navigate to the Manage Tasks tab
        tabs = self.driver.find_elements(By.CSS_SELECTOR, "button[role='tab']")
        tabs[1].click()  # Click the "Manage Tasks" tab
        
        # Fill out the create task form
        title_input = self.driver.find_element(By.CSS_SELECTOR, "input[aria-label='Title']")
        title_input.send_keys("UI Created Task")
        
        desc_input = self.driver.find_element(By.CSS_SELECTOR, "textarea[aria-label='Description']")
        desc_input.send_keys("This task was created through the UI")
        
        # Find form submit button and click it
        create_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[kind='primaryFormSubmit']")
        for button in create_buttons:
            if button.text == "Create Task":
                button.click()
                break
        
        # Wait for success message
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='stSuccessMessage']"))
            )
            success = True
        except TimeoutException:
            success = False
        
        self.assertTrue(success, "Success message not found after creating task")
        
        # Check if the new task appears in the list
        time.sleep(3)  # Wait for page to refresh
        
        expanders = self.driver.find_elements(By.CSS_SELECTOR, "div[data-testid='stExpander']")
        
        found = False
        for expander in expanders:
            header_text = expander.find_element(By.CSS_SELECTOR, "span.streamlit-expanderHeader").text
            if "UI Created Task" in header_text:
                found = True
                break
        
        self.assertTrue(found, "Newly created task not found in the tasks list")
    
    def test_4_dashboard_shows_stats(self):
        """Test that the dashboard shows task statistics"""
        # Create a couple more tasks for better stats
        requests.post(f"{API_URL}/tasks", json={"title": "Dashboard Test 1", "status": "in_progress"})
        requests.post(f"{API_URL}/tasks", json={"title": "Dashboard Test 2", "status": "completed"})
        
        # Navigate to Dashboard tab
        tabs = self.driver.find_elements(By.CSS_SELECTOR, "button[role='tab']")
        tabs[0].click()  # Click the "Dashboard" tab
        
        # Wait for stats to load
        time.sleep(2)
        
        # Check for total tasks metric
        metric_elements = self.driver.find_elements(By.CSS_SELECTOR, "div[data-testid='stMetric']")
        self.assertTrue(len(metric_elements) > 0, "No metrics found on dashboard")
        
        # Check for charts
        chart_elements = self.driver.find_elements(By.CSS_SELECTOR, "div[data-testid='stChart']")
        self.assertTrue(len(chart_elements) > 0, "No charts found on dashboard")

if __name__ == "__main__":
    unittest.main()