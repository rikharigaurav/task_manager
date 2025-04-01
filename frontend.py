# frontend.py - Streamlit UI

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json

# Constants
API_URL = "http://localhost:5000/api"

# Page configuration
st.set_page_config(
    page_title="Task Manager",
    page_icon="✅",
    layout="wide"
)

# Helper functions
def get_all_tasks():
    response = requests.get(f"{API_URL}/tasks")
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch tasks: {response.text}")
        return []

def get_task(task_id):
    response = requests.get(f"{API_URL}/tasks/{task_id}")
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch task: {response.text}")
        return None

def create_task(task_data):
    response = requests.post(f"{API_URL}/tasks", json=task_data)
    if response.status_code == 201:
        st.success("Task created successfully!")
        return response.json()
    else:
        st.error(f"Failed to create task: {response.text}")
        return None

def update_task(task_id, task_data):
    response = requests.put(f"{API_URL}/tasks/{task_id}", json=task_data)
    if response.status_code == 200:
        st.success("Task updated successfully!")
        return response.json()
    else:
        st.error(f"Failed to update task: {response.text}")
        return None

def delete_task(task_id):
    response = requests.delete(f"{API_URL}/tasks/{task_id}")
    if response.status_code == 200:
        st.success("Task deleted successfully!")
        return True
    else:
        st.error(f"Failed to delete task: {response.text}")
        return False

def get_stats():
    response = requests.get(f"{API_URL}/stats")
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch stats: {response.text}")
        return {"total": 0, "by_status": {}, "by_priority": {}}

# UI Components
def display_header():
    st.title("📋 Task Manager Application")
    st.markdown("A simple CRUD application to manage tasks")

def display_dashboard():
    stats = get_stats()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Tasks", stats["total"])
    
    with col2:
        status_data = stats["by_status"]
        st.subheader("Tasks by Status")
        if status_data:
            status_df = pd.DataFrame({
                "Status": list(status_data.keys()),
                "Count": list(status_data.values())
            })
            st.bar_chart(status_df.set_index("Status"))
        else:
            st.info("No status data available")
    
    with col3:
        priority_data = stats["by_priority"]
        st.subheader("Tasks by Priority")
        if priority_data:
            priority_df = pd.DataFrame({
                "Priority": [str(k) for k in priority_data.keys()],
                "Count": list(priority_data.values())
            })
            st.bar_chart(priority_df.set_index("Priority"))
        else:
            st.info("No priority data available")

def create_task_form():
    st.subheader("Create New Task")
    
    with st.form("create_task_form"):
        title = st.text_input("Title")
        description = st.text_area("Description")
        status = st.selectbox("Status", ["pending", "in_progress", "completed", "cancelled"])
        priority = st.slider("Priority", 1, 5, 1)
        
        submitted = st.form_submit_button("Create Task")
        
        if submitted:
            if not title:
                st.error("Title is required!")
            else:
                task_data = {
                    "title": title,
                    "description": description,
                    "status": status,
                    "priority": priority
                }
                create_task(task_data)
                st.experimental_rerun()

def display_tasks():
    st.subheader("Tasks List")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "pending", "in_progress", "completed", "cancelled"])
    with col2:
        priority_filter = st.selectbox("Filter by Priority", ["All", "1", "2", "3", "4", "5"])
    
    # Get tasks
    tasks = get_all_tasks()
    
    # Apply filters
    if status_filter != "All":
        tasks = [task for task in tasks if task["status"] == status_filter]
    if priority_filter != "All":
        tasks = [task for task in tasks if str(task["priority"]) == priority_filter]
    
    # Display tasks
    if not tasks:
        st.info("No tasks found")
    else:
        for task in tasks:
            with st.expander(f"{task['title']} (Priority: {task['priority']}, Status: {task['status']})"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Description:** {task['description'] if task['description'] else 'No description'}")
                    st.markdown(f"**Created:** {task['created_at']}")
                    st.markdown(f"**Last Updated:** {task['updated_at']}")
                
                with col2:
                    # Edit task form
                    with st.form(f"edit_task_{task['id']}"):
                        new_title = st.text_input("Title", value=task['title'])
                        new_desc = st.text_area("Description", value=task['description'])
                        new_status = st.selectbox("Status", 
                                                 ["pending", "in_progress", "completed", "cancelled"], 
                                                 index=["pending", "in_progress", "completed", "cancelled"].index(task['status']))
                        new_priority = st.slider("Priority", 1, 5, int(task['priority']))
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            update_button = st.form_submit_button("Update")
                        with col2:
                            delete_button = st.form_submit_button("Delete", type="primary")
                        
                        if update_button:
                            task_data = {
                                "title": new_title,
                                "description": new_desc,
                                "status": new_status,
                                "priority": new_priority
                            }
                            update_task(task['id'], task_data)
                            st.experimental_rerun()
                        
                        if delete_button:
                            if delete_task(task['id']):
                                st.experimental_rerun()

# Main app
def main():
    display_header()
    
    tab1, tab2 = st.tabs(["Dashboard", "Manage Tasks"])
    
    with tab1:
        display_dashboard()
    
    with tab2:
        col1, col2 = st.columns([1, 3])
        
        with col1:
            create_task_form()
        
        with col2:
            display_tasks()

if __name__ == "__main__":
    main()