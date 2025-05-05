# CrewAI Integration for Agent Angus

This document describes how Agent Angus is integrated with CrewAI to create a multi-agent system for YouTube publishing and audience engagement.

## Overview

The integration uses CrewAI to orchestrate specialized agents that handle different aspects of Angus's functionality:

1. **Upload Agent**: Handles uploading videos to YouTube
2. **Engagement Agent**: Manages audience interactions through comments
3. **Analysis Agent**: Analyzes music content for better metadata

## File Structure

- `angus_tools.py`: Wraps Angus functionality as CrewAI tools
- `angus_agents.py`: Defines specialized agents with specific roles
- `angus_tasks.py`: Creates tasks with dependencies
- `angus_crew.py`: Manages the CrewAI workflow
- `run_angus_crew.py`: Command-line interface
- `scheduled_crew.py`: Daemon mode with scheduled tasks
- `test_angus_crew.py`: Unit tests
- `templates/crew.html`: Web UI for the CrewAI control panel

## Installation

To use the CrewAI integration, you need to install the required dependencies:

```bash
pip install crewai openai supabase python-dotenv flask httpx google-api-python-client oauth2client schedule
```

## Usage

### Command Line

You can run the CrewAI integration from the command line using the `run_angus_crew.py` script:

```bash
# Run the full workflow
python run_angus_crew.py --task full

# Run specific tasks
python run_angus_crew.py --task analysis
python run_angus_crew.py --task upload
python run_angus_crew.py --task engagement

# Set a limit for the number of items to process
python run_angus_crew.py --task upload --limit 10

# Enable verbose output
python run_angus_crew.py --task full --verbose

# Use simple tools created with the @tool decorator
python run_angus_crew.py --task full --simple-tools
```

### Web UI

You can access the CrewAI control panel through the web UI:

1. Start the web UI:
   ```bash
   python web_ui.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000/crew
   ```

3. Use the control panel to run different tasks:
   - Music Analysis
   - YouTube Upload
   - Audience Engagement
   - Full Workflow

### Scheduled Operations

You can run the CrewAI integration in daemon mode with scheduled tasks:

```bash
# Run with default settings
python scheduled_crew.py

# Customize the schedule
python scheduled_crew.py --daily-time 08:00 --weekly-day friday --weekly-time 18:00

# Disable specific tasks
python scheduled_crew.py --disable-hourly --disable-weekly

# Use simple tools created with the @tool decorator
python scheduled_crew.py --simple-tools
```

## Architecture

### Tools

The `angus_tools.py` module provides two approaches for creating tools:

#### 1. BaseTool Subclassing

The module defines tool classes that inherit from `BaseTool` and provide input validation through Pydantic models:

```python
class UploadVideosTool(BaseTool):
    name: str = "upload_videos"
    description: str = "Upload pending songs from Supabase to YouTube"
    args_schema: Type[BaseModel] = UploadVideosInput

    def _run(self, limit: int = 5) -> str:
        count = angus_instance.upload_all_pending_songs(limit=limit)
        return f"Successfully uploaded {count} videos to YouTube"
```

#### 2. @tool Decorator

The module also defines simple tools using the `@tool` decorator:

```python
@tool("upload_videos_simple")
def upload_videos_simple(limit: int = 5) -> str:
    """Upload pending songs from Supabase to YouTube."""
    count = angus_instance.upload_all_pending_songs(limit=limit)
    return f"Successfully uploaded {count} videos to YouTube"
```

#### Tool Caching

The module implements caching for tools to improve performance:

```python
def cache_analysis(arguments: dict, result: Dict[str, Any]) -> bool:
    """Cache function for the analyze_music tool."""
    return 'error' not in result

analyze_music_simple.cache_function = cache_analysis
```

### Agents

The `AngusAgents` class defines specialized agents with specific roles:

- `YouTube Upload Specialist`: Efficiently uploads AI-generated music videos to YouTube
- `Audience Engagement Specialist`: Maximizes audience engagement through thoughtful responses
- `Music Analysis Specialist`: Provides deep insights into music content

The class provides two sets of agents:

1. Regular agents that use tools created by subclassing `BaseTool`
2. Simple agents that use tools created with the `@tool` decorator

### Tasks

The `AngusTasks` class defines tasks with dependencies:

- `analysis_task`: Analyzes new music files that are pending upload
- `upload_task`: Uploads analyzed music to YouTube with optimized metadata
- `engagement_task`: Monitors and responds to comments on uploaded YouTube videos

### Workflow

The `AngusCrew` class manages the CrewAI workflow:

- `run_analysis_only`: Runs only the analysis task
- `run_upload_only`: Runs only the upload task
- `run_engagement_only`: Runs only the engagement task
- `run_full_workflow`: Runs the full workflow with all tasks

The class supports using either regular tools or simple tools:

```python
crew = AngusCrew(use_simple_tools=True)  # Use simple tools created with @tool
```

## Testing

You can run the unit tests for the CrewAI integration:

```bash
python test_angus_crew.py
```

The tests cover:

- Tools: Testing the upload, comment, and analysis tools
- Agents: Testing the upload, engagement, and analysis agents
- Tasks: Testing the analysis, upload, and engagement tasks
- Crew: Testing the full workflow and individual task execution

## Extending the Integration

### Adding New Tools

#### Using BaseTool Subclassing

To add a new tool using BaseTool subclassing:

```python
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class NewToolInput(BaseModel):
    """Input schema for the new tool."""
    param1: str = Field(..., description="Description of param1")
    param2: int = Field(10, description="Description of param2")

class NewTool(BaseTool):
    """Tool for new functionality."""
    name: str = "new_tool"
    description: str = "Description of the new tool"
    args_schema: Type[BaseModel] = NewToolInput

    def _run(self, param1: str, param2: int = 10) -> str:
        # Implement the new functionality
        return f"Result: {param1}, {param2}"
```

#### Using @tool Decorator

To add a new tool using the @tool decorator:

```python
from crewai.tools import tool

@tool("new_tool_simple")
def new_tool_simple(param1: str, param2: int = 10) -> str:
    """Description of the new tool.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        str: Result of the tool
    """
    # Implement the new functionality
    return f"Result: {param1}, {param2}"
```

### Adding New Agents

To add a new agent, update the `AngusAgents` class in `angus_agents.py`:

```python
def get_new_agent(self) -> Agent:
    """Create a new agent."""
    return Agent(
        role='New Agent Role',
        goal='Goal of the new agent',
        backstory="""Detailed backstory of the new agent.""",
        tools=[self.tools.get_new_tool()],
        verbose=True
    )
```

### Adding New Tasks

To add a new task, update the `AngusTasks` class in `angus_tasks.py`:

```python
def get_new_task(self, context_tasks=None) -> Task:
    """Create a new task."""
    return Task(
        description="""Description of the new task.""",
        agent=self.agents.get_new_agent(),
        expected_output="""Expected output of the new task.""",
        context=context_tasks
    )
```

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'crewai'**
   - Make sure you have installed the CrewAI package: `pip install crewai`

2. **AttributeError: 'AngusCrew' object has no attribute 'run_analysis_only'**
   - Make sure you have implemented all the required methods in the `AngusCrew` class

3. **TypeError: __init__() got an unexpected keyword argument 'verbose'**
   - Make sure you are using a compatible version of CrewAI

4. **TypeError: __init__() missing 1 required positional argument: 'args_schema'**
   - Make sure you have defined the `args_schema` attribute for your BaseTool subclass

### Debugging

To enable verbose output, use the `--verbose` flag with the command-line interface:

```bash
python run_angus_crew.py --task full --verbose
```

You can also check the logs in `angus_crew.log` for more information.
