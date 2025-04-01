# task_service.py - Business logic for task management

import uuid
from datetime import datetime
import logging
from database.database_manager import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tasks.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("task_service")

class TaskService:
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def get_all_tasks(self, filters=None, sort_by='created_at', sort_order='DESC'):
        """
        Get all tasks with optional filtering and sorting
        
        Args:
            filters (dict): Dictionary of filter conditions
            sort_by (str): Field to sort by
            sort_order (str): 'ASC' or 'DESC'
            
        Returns:
            list: List of tasks as dictionaries
        """
        query = "SELECT * FROM tasks"
        params = []
        
        # Apply filters if provided
        if filters:
            filter_conditions = []
            
            if 'status' in filters and filters['status']:
                filter_conditions.append("status = ?")
                params.append(filters['status'])
            
            if 'priority' in filters and filters['priority']:
                filter_conditions.append("priority = ?")
                params.append(filters['priority'])
            
            if 'search' in filters and filters['search']:
                filter_conditions.append("(title LIKE ? OR description LIKE ?)")
                search_term = f"%{filters['search']}%"
                params.append(search_term)
                params.append(search_term)
            
            if filter_conditions:
                query += " WHERE " + " AND ".join(filter_conditions)
        
        # Apply sorting
        query += f" ORDER BY {sort_by} {sort_order}"
        
        try:
            tasks = self.db_manager.execute_query(query, params)
            # Convert Row objects to dictionaries
            return [dict(task) for task in tasks]
        except Exception as e:
            logger.error(f"Error fetching tasks: {e}")
            return []
    
    def get_task_by_id(self, task_id):
        """
        Get a task by its ID
        
        Args:
            task_id (str): The task ID
            
        Returns:
            dict: Task data or None if not found
        """
        query = "SELECT * FROM tasks WHERE id = ?"
        try:
            task = self.db_manager.execute_query(query, (task_id,), fetch_all=False)
            return dict(task) if task else None
        except Exception as e:
            logger.error(f"Error fetching task {task_id}: {e}")
            return None
    
    def create_task(self, task_data):
        """
        Create a new task
        
        Args:
            task_data (dict): Task data
            
        Returns:
            dict: Created task data or None if failed
        """
        if not task_data.get('title'):
            logger.warning("Attempted to create task without title")
            return None
        
        task_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        query = '''
        INSERT INTO tasks (id, title, description, status, priority, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            task_id,
            task_data.get('title'),
            task_data.get('description', ''),
            task_data.get('status', 'pending'),
            task_data.get('priority', 1),
            now,
            now
        )
        
        try:
            self.db_manager.execute_query(query, params, fetch_all=False, commit=True)
            
            # Return the created task
            return {
                "id": task_id,
                "title": task_data.get('title'),
                "description": task_data.get('description', ''),
                "status": task_data.get('status', 'pending'),
                "priority": task_data.get('priority', 1),
                "created_at": now,
                "updated_at": now
            }
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None
    
    def update_task(self, task_id, task_data):
        """
        Update an existing task
        
        Args:
            task_id (str): The task ID
            task_data (dict): Task data to update
            
        Returns:
            dict: Updated task data or None if failed
        """
        # Check if task exists
        existing_task = self.get_task_by_id(task_id)
        if not existing_task:
            logger.warning(f"Attempted to update non-existent task: {task_id}")
            return None
        
        # Build update query
        update_fields = []
        params = []
        
        for field in ['title', 'description', 'status', 'priority']:
            if field in task_data:
                update_fields.append(f"{field} = ?")
                params.append(task_data[field])
        
        if not update_fields:
            logger.warning(f"No valid fields to update for task: {task_id}")
            return existing_task
        
        # THIS IS THE BUG: The updated_at field is missing from the update query!
        # Correct version would include:
        # update_fields.append("updated_at = ?")
        # now = datetime.now().isoformat()
        # params.append(now)
        
        params.append(task_id)  # For the WHERE clause
        
        query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?"
        
        try:
            self.db_manager.execute_query(query, params, fetch_all=False, commit=True)
            
            # Get and return the updated task
            return self.get_task_by_id(task_id)
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {e}")
            return None
    
    def delete_task(self, task_id):
        """
        Delete a task
        
        Args:
            task_id (str): The task ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if task exists
        existing_task = self.get_task_by_id(task_id)
        if not existing_task:
            logger.warning(f"Attempted to delete non-existent task: {task_id}")
            return False
        
        query = "DELETE FROM tasks WHERE id = ?"
        
        try:
            self.db_manager.execute_query(query, (task_id,), fetch_all=False, commit=True)
            logger.info(f"Deleted task: {task_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {e}")
            return False
    
    def get_task_stats(self):
        """
        Get statistics about tasks
        
        Returns:
            dict: Task statistics
        """
        # Get total count
        total_query = "SELECT COUNT(*) as count FROM tasks"
        
        # Get counts by status
        status_query = """
        SELECT status, COUNT(*) as count 
        FROM tasks 
        GROUP BY status
        """
        
        # Get counts by priority
        priority_query = """
        SELECT priority, COUNT(*) as count 
        FROM tasks 
        GROUP BY priority
        ORDER BY priority
        """
        
        try:
            # Execute queries
            total_result = self.db_manager.execute_query(total_query, fetch_all=False)
            status_results = self.db_manager.execute_query(status_query)
            priority_results = self.db_manager.execute_query(priority_query)
            
            # Process results
            total = total_result['count'] if total_result else 0
            status_stats = {row['status']: row['count'] for row in status_results}
            priority_stats = {row['priority']: row['count'] for row in priority_results}
            
            # Calculate average priority
            avg_priority_query = "SELECT AVG(priority) as avg_priority FROM tasks"
            avg_priority_result = self.db_manager.execute_query(avg_priority_query, fetch_all=False)
            avg_priority = avg_priority_result['avg_priority'] if avg_priority_result else 0
            
            return {
                "total": total,
                "by_status": status_stats,
                "by_priority": priority_stats,
                "avg_priority": round(avg_priority, 2)
            }
        except Exception as e:
            logger.error(f"Error getting task stats: {e}")
            return {
                "total": 0,
                "by_status": {},
                "by_priority": {},
                "avg_priority": 0
            }
        
if __name__ == "__main__":
    task_service = TaskService()
    