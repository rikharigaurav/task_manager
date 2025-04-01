from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from task_service import task_service
from database.database_manager import db_manager
from config_utils import app_settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler("api.log"), logging.StreamHandler()])
logger = logging.getLogger("api")

# Initialize app and services
app = Flask(__name__)
CORS(app)
api_config = app_settings.get_api_settings()

@app.get('/api/tasks')
def get_tasks():
    try:
        filters = {
            "status": request.args.get("status"),
            "priority": int(request.args.get("priority")) if request.args.get("priority") else None,
            "search": request.args.get("search")
        }
        
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'DESC')
        
        valid_sort_fields = ['created_at', 'updated_at', 'title', 'priority', 'status']
        if sort_by not in valid_sort_fields:
            sort_by = 'created_at'
        if sort_order not in ['ASC', 'DESC']:
            sort_order = 'DESC'
        
        tasks = task_service.get_all_tasks(filters, sort_by, sort_order)
        return jsonify(tasks)
    except Exception as e:
        logger.error(f"Error in get_tasks: {e}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.get('/api/tasks/<task_id>')
def get_task(task_id):
    try:
        task = task_service.get_task_by_id(task_id)
        return jsonify(task) if task else (jsonify({"error": "Task not found"}), 404)
    except Exception as e:
        logger.error(f"Error in get_task: {e}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.post('/api/tasks')
def create_task():
    try:
        task_data = request.json
        if not task_data or not task_data.get('title'):
            return jsonify({"error": "Title is required"}), 400
        
        created_task = task_service.create_task(task_data)
        return jsonify(created_task), 201 if created_task else (jsonify({"error": "Failed to create task"}), 500)
    except Exception as e:
        logger.error(f"Error in create_task: {e}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.put('/api/tasks/<task_id>')
def update_task(task_id):
    try:
        task_data = request.json
        if not task_data:
            return jsonify({"error": "No data provided"}), 400
        
        updated_task = task_service.update_task(task_id, task_data)
        return jsonify(updated_task) if updated_task else (jsonify({"error": "Task not found"}), 404)
    except Exception as e:
        logger.error(f"Error in update_task: {e}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.delete('/api/tasks/<task_id>')
def delete_task(task_id):
    try:
        return jsonify({"message": "Task deleted successfully"}) if task_service.delete_task(task_id) else (jsonify({"error": "Task not found"}), 404)
    except Exception as e:
        logger.error(f"Error in delete_task: {e}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.get('/api/stats')
def get_stats():
    try:
        return jsonify(task_service.get_task_stats())
    except Exception as e:
        logger.error(f"Error in get_stats: {e}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.get('/api/system/info')
def get_system_info():
    try:
        safe_config = {key: api_config[key] for key in ("host", "port", "cors_enabled") if key in api_config}
        return jsonify({
            "database": db_manager.get_table_info(),
            "config": safe_config,
            "api_version": "1.0.0"
        })
    except Exception as e:
        logger.error(f"Error in get_system_info: {e}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.post('/api/system/backup')
def create_backup():
    try:
        if db_manager.backup_database():
            app_settings.update_last_backup_time()
            return jsonify({"message": "Database backup created successfully"})
        return jsonify({"error": "Failed to create database backup"}), 500
    except Exception as e:
        logger.error(f"Error in create_backup: {e}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    if app_settings.should_backup_database():
        logger.info("Performing scheduled database backup")
        if db_manager.backup_database():
            app_settings.update_last_backup_time()
    
    logger.info(f"Starting API server on {api_config.get('host', 'localhost')}:{api_config.get('port', 5000)}")
    app.run(debug=api_config.get("debug", False), host=api_config.get("host", "localhost"), port=api_config.get("port", 5000))