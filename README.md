# Task Manager Application

A full-stack task management application with a Flask backend API, SQLite database, and Streamlit frontend UI.

## Overview

This application provides a simple but complete task management system with the following features:

- Create, read, update, and delete tasks
- Filter tasks by status and priority
- Dashboard with task statistics
- Database backup functionality
- Configuration management

## Tech Stack

- **Backend**: Flask RESTful API
- **Database**: SQLite
- **Frontend**: Streamlit
- **Testing**: Unittest with Selenium for frontend testing

## Project Structure

```
task-manager/
├── app.py                  # Flask API entry point
├── config_utils.py         # Configuration management utilities
├── frontend.py             # Streamlit UI
├── task_service.py         # Business logic for task management
├── database/
│   └── database_manager.py # Database operations
├── config.json             # Application configuration
├── test_api.py             # Backend API tests
└── test_frontend.py        # Frontend integration tests
```

## Installation

1. Clone the repository:
   ```
   git clone [repository-url]
   cd task-manager
   ```

2. Install dependencies:
   ```
   pip install flask flask-cors streamlit selenium webdriver-manager
   ```

3. Set up the database:
   ```
   python -c "from database.database_manager import DatabaseManager; DatabaseManager().setup_database()"
   ```

## Running the Application

1. Start the backend API:
   ```
   python app.py
   ```

2. Start the frontend UI (in a separate terminal):
   ```
   streamlit run frontend.py
   ```

3. Access the application at `http://localhost:8501`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tasks` | GET | Get all tasks with optional filtering and sorting |
| `/api/tasks/<task_id>` | GET | Get a specific task by ID |
| `/api/tasks` | POST | Create a new task |
| `/api/tasks/<task_id>` | PUT | Update an existing task |
| `/api/tasks/<task_id>` | DELETE | Delete a task |
| `/api/stats` | GET | Get task statistics |
| `/api/system/info` | GET | Get system information |
| `/api/system/backup` | POST | Create a database backup |

## Task Data Structure

```json
{
  "id": "uuid-string",
  "title": "Task title",
  "description": "Task description",
  "status": "pending|in_progress|completed|cancelled",
  "priority": 1-5,
  "created_at": "ISO date string",
  "updated_at": "ISO date string"
}
```

## Configuration

The application uses a JSON configuration file (`config.json`) that controls various aspects of the application, including:

- Database path and backup settings
- API host and port settings
- Logging configuration

Default configuration is automatically created if no config file exists.

## Known Issues

There is a bug in the task update functionality where the `updated_at` timestamp is not being updated when a task is modified. This is marked in the code with a comment in the `task_service.py` file.

## Testing

### Backend API Tests

Run the backend tests with:
```
python test_api.py
```

### Frontend Integration Tests

Run the frontend tests with:
```
python test_frontend.py
```

Note: Frontend tests require Chrome and ChromeDriver to be installed. The tests will automatically download the appropriate ChromeDriver version if needed.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.