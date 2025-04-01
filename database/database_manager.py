# database_manager.py - Database management utilities

import sqlite3
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("database.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("database_manager")

class DatabaseManager:
    def __init__(self, db_path='database/tasks.db'):
        """Initialize the database manager with the specified database path"""
        self.db_path = db_path
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Ensure that the database directory and table exist"""
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
            logger.info(f"Created database directory: {db_dir}")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'pending',
            priority INTEGER DEFAULT 1,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
        ''')
        
        # Create index on commonly filtered fields
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON tasks (status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_priority ON tasks (priority)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON tasks (created_at)')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized with required tables and indexes")
    
    def get_connection(self):
        """Get a database connection with row factory enabled"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def execute_query(self, query, params=(), fetch_all=True, commit=False):
        """Execute a database query and optionally fetch results or commit changes"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            result = None
            if fetch_all:
                result = cursor.fetchall()
            elif not commit:  # If not fetching all and not committing, fetch one
                result = cursor.fetchone()
                
            if commit:
                conn.commit()
                
            return result
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def backup_database(self, backup_path=None):
        """Create a backup of the database"""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"database/backup_{timestamp}.db"
        
        if not os.path.exists(self.db_path):
            logger.warning(f"Cannot backup - source database does not exist: {self.db_path}")
            return False
        
        backup_dir = os.path.dirname(backup_path)
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        try:
            # Open the source database
            source_conn = sqlite3.connect(self.db_path)
            
            # Create a new backup database
            backup_conn = sqlite3.connect(backup_path)
            
            # Copy data from source to backup
            source_conn.backup(backup_conn)
            
            # Close connections
            source_conn.close()
            backup_conn.close()
            
            logger.info(f"Database backed up successfully to {backup_path}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Backup failed: {e}")
            return False
    
    def get_table_info(self):
        """Get information about database tables"""
        tables = {}
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get list of tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            table_names = [row['name'] for row in cursor.fetchall()]
            
            for table_name in table_names:
                # Get column info
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                row_count = cursor.fetchone()['count']
                
                tables[table_name] = {
                    'columns': [dict(col) for col in columns],
                    'row_count': row_count
                }
            
            conn.close()
            return tables
        except sqlite3.Error as e:
            logger.error(f"Error getting table info: {e}")
            return {}
        
if __name__ == "__main__":
    db_manager = DatabaseManager()