# How to Add Database Logging to an AI Agent

This guide documents the process of adding database logging to an AI agent running in a Docker container, with logs stored in a Supabase table.

## 1. Create the Database Table

First, create a table in Supabase to store the logs:

```sql
CREATE TABLE agent_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    level TEXT,
    source TEXT,
    message TEXT,
    details JSONB
);

-- Add indexes for better query performance
CREATE INDEX idx_agent_logs_timestamp ON agent_logs (timestamp DESC);
CREATE INDEX idx_agent_logs_level ON agent_logs (level);
```

## 2. Implement the Custom Log Handler

Add a custom logging handler to your agent's main Python file:

```python
class SupabaseLogHandler(logging.Handler):
    """
    Custom logging handler that sends logs to a Supabase table.
    """
    def __init__(self, supabase_client):
        super().__init__()
        self.supabase = supabase_client
        
    def emit(self, record):
        try:
            # Extract exception info if present
            exc_info = None
            if record.exc_info:
                exc_info = self.formatter.formatException(record.exc_info)
            
            # Format the log message
            log_entry = {
                "level": record.levelname,
                "source": record.name,
                "message": self.format(record),
                "details": {
                    "lineno": record.lineno,
                    "funcName": record.funcName,
                    "pathname": record.pathname,
                    "exc_info": exc_info
                }
            }
            
            # Insert into Supabase
            self.supabase.client.table("agent_logs").insert(log_entry).execute()
        except Exception:
            # Don't let logging errors crash the application
            self.handleError(record)
```

## 3. Initialize the Log Handler

In your agent's initialization method, add the Supabase log handler:

```python
def __init__(self):
    """
    Initialize the agent.
    """
    # Initialize clients
    self.supabase = SupabaseClient()
    
    # Add Supabase log handler
    try:
        supabase_handler = SupabaseLogHandler(self.supabase)
        supabase_handler.setLevel(logging.INFO)  # Only log INFO and above
        supabase_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(supabase_handler)
        logger.info("Supabase log handler initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase log handler: {str(e)}")
    
    logger.info("Agent initialized")
```

## 4. Add Log Cleanup Functionality

Add a method to clean up old logs to prevent the table from growing too large:

```python
def cleanup_old_logs(self, days_to_keep=7):
    """
    Remove logs older than the specified number of days.
    
    Args:
        days_to_keep: Number of days of logs to keep
        
    Returns:
        Number of logs deleted
    """
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_to_keep)
    
    try:
        # Delete logs older than cutoff_date
        response = self.supabase.client.table("agent_logs").delete().lt("timestamp", cutoff_date.isoformat()).execute()
        deleted_count = len(response.data) if response.data else 0
        logger.info(f"Cleaned up {deleted_count} logs older than {days_to_keep} days")
        return deleted_count
    except Exception as e:
        logger.error(f"Error cleaning up old logs: {str(e)}")
        return 0
```

## 5. Schedule Log Cleanup

Add the log cleanup task to your agent's scheduled tasks:

```python
# Define the log cleanup task
def log_cleanup_task():
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"[{current_time}] Running scheduled log cleanup")
    try:
        deleted = self.cleanup_old_logs(days_to_keep=7)  # Keep logs for 7 days
        logger.info(f"[{current_time}] Scheduled log cleanup complete - deleted {deleted} old logs")
    except Exception as e:
        logger.error(f"[{current_time}] Error in scheduled log cleanup: {str(e)}")

# Schedule the task to run once per day
schedule.every(1).day.at("00:00").do(log_cleanup_task)
```

## 6. Commit Changes and Update the Docker Container

After implementing the changes:

1. Commit the changes to your Git repository:
   ```bash
   git add .
   git commit -m "Add database logging to Supabase"
   git push
   ```

2. SSH into your server:
   ```bash
   ssh user@your-server
   ```

3. Navigate to your agent's directory:
   ```bash
   cd /path/to/agent
   ```

4. Pull the latest changes:
   ```bash
   git pull
   ```

5. Rebuild and restart the Docker container:
   ```bash
   # Remove existing containers and volumes
   docker-compose down -v
   
   # Build the container with no cache
   docker-compose build --no-cache
   
   # Start the container
   docker-compose up -d
   ```

## 7. Verify Logging is Working

Check if logs are being stored in the database:

```bash
# Run a command that generates logs
docker-compose exec agent python -c "from agent import Agent; agent = Agent(); agent.run_some_task()"

# Check if logs appear in the database
docker-compose exec agent python -c "from supabase_client import SupabaseClient; client = SupabaseClient(); print(client.client.table('agent_logs').select('*').execute())"
```

## 8. Integrate with Dashboard

To display logs in your dashboard:

```javascript
// Example in JavaScript
const { data, error } = await supabase
  .from('agent_logs')
  .select('*')
  .order('timestamp', { ascending: false })
  .limit(100);

if (error) console.error('Error fetching logs:', error);
else {
  // Display logs in your dashboard
  displayLogs(data);
}
```

## Troubleshooting

If logs aren't appearing in the database:

1. Check if the SupabaseLogHandler class is available in the container:
   ```bash
   docker-compose exec agent python -c "import agent; print('SupabaseLogHandler exists:', 'SupabaseLogHandler' in dir(agent))"
   ```

2. Check if the logger has the SupabaseLogHandler:
   ```bash
   docker-compose exec agent python -c "from agent import Agent; import logging; agent = Agent(); logger = logging.getLogger('agent'); print('Logger handlers:', [h.__class__.__name__ for h in logger.handlers])"
   ```

3. Check for errors in the Docker logs:
   ```bash
   docker-compose logs --tail=100 agent | grep -i error
   ```

4. Ensure the Supabase client is properly initialized and has the correct credentials.

This process can be adapted for any AI agent that uses Python and Supabase, with appropriate modifications for your specific agent's structure and requirements.
