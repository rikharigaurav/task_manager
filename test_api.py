# test_api.py - Backend API Tests

import unittest
import requests
import json
import os
import sys
import subprocess
import time
import signal
from multiprocessing import Process

API_URL = "http://localhost:5000"

class TestTaskAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start the Flask server in a separate process
        cls.server_process = subprocess.Popen(
            ["python", "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give the server some time to start
        time.sleep(2)
        
        # Clean database for testing
        if os.path.exists('database/tasks.db'):
            os.remove('database/tasks.db')
    
    @classmethod
    def tearDownClass(cls):
        # Terminate the server process
        cls.server_process.terminate()
        cls.server_process.wait()
    
    def test_1_create_task(self):
        """Test creating a new task"""
        task_data = {
            "title": "Test Task",
            "description": "This is a test task",
            "status": "pending",
            "priority": 3
        }
        
        response = requests.post(f"{API_URL}/api/tasks", json=task_data)
        self.assertEqual(response.status_code, 201)
        
        # Verify response data
        data = response.json()
        self.assertEqual(data["title"], task_data["title"])
        self.assertEqual(data["description"], task_data["description"])
        self.assertEqual(data["status"], task_data["status"])
        self.assertEqual(data["priority"], task_data["priority"])
        self.assertIn("id", data)
        
        # Save task ID for later tests
        self.__class__.task_id = data["id"]
    
    def test_2_get_all_tasks(self):
        """Test retrieving all tasks"""
        response = requests.get(f"{API_URL}/api/tasks")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
    
    def test_3_get_task_by_id(self):
        """Test retrieving a single task by ID"""
        response = requests.get(f"{API_URL}/api/tasks/{self.__class__.task_id}")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["id"], self.__class__.task_id)
        self.assertEqual(data["title"], "Test Task")
    
    def test_4_update_task(self):
        """Test updating a task"""
        update_data = {
            "title": "Updated Test Task",
            "status": "in_progress"
        }
        
        response = requests.put(f"{API_URL}/api/tasks/{self.__class__.task_id}", json=update_data)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["title"], update_data["title"])
        self.assertEqual(data["status"], update_data["status"])
        self.assertEqual(data["description"], "This is a test task")  # Unchanged field
    
    def test_5_get_stats(self):
        """Test getting task statistics"""
        response = requests.get(f"{API_URL}/api/stats")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("total", data)
        self.assertIn("by_status", data)
        self.assertIn("by_priority", data)
        
        # After our update, there should be 1 task with status 'in_progress'
        self.assertIn("in_progress", data["by_status"])
        self.assertEqual(data["by_status"]["in_progress"], 1)
    
    def test_6_delete_task(self):
        """Test deleting a task"""
        response = requests.delete(f"{API_URL}/api/tasks/{self.__class__.task_id}")
        self.assertEqual(response.status_code, 200)
        
        # Verify the task is actually deleted
        response = requests.get(f"{API_URL}/api/tasks/{self.__class__.task_id}")
        self.assertEqual(response.status_code, 404)
    
    def test_7_get_nonexistent_task(self):
        """Test retrieving a non-existent task"""
        response = requests.get(f"{API_URL}/api/tasks/nonexistent-id")
        self.assertEqual(response.status_code, 404)
    
    def test_8_create_task_missing_title(self):
        """Test creating a task without a title (should fail)"""
        task_data = {
            "description": "This task has no title",
            "status": "pending"
        }
        
        response = requests.post(f"{API_URL}/api/tasks", json=task_data)
        self.assertEqual(response.status_code, 400)

if __name__ == "__main__":
    unittest.main()