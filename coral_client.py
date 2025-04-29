import requests
import json
import sseclient
import threading
import time
import logging
import uuid
import re
import queue

class CoralClient:
    def __init__(self, session_id=None, app_id="default-app", privacy_key="public", server_url="https://coral.pushcollective.club", use_devmode=True):
        """
        Initialize the Coral Protocol client.
        
        Args:
            session_id (str, optional): Unique session identifier. Defaults to a generated ID.
            app_id (str, optional): Application ID. Defaults to "default-app".
            privacy_key (str, optional): Privacy key. Defaults to "public".
            server_url (str, optional): Base URL of the Coral server. Defaults to "https://coral.pushcollective.club".
            use_devmode (bool, optional): Whether to use DevMode endpoints. Defaults to True.
        """
        self.session_id = session_id or f"yona-agent-{uuid.uuid4().hex[:8]}"
        self.app_id = app_id
        self.privacy_key = privacy_key
        self.server_url = server_url
        self.use_devmode = use_devmode
        self.devmode_prefix = "/devmode" if use_devmode else ""
        
        # Construct the base URL
        self.base_url = f"{self.server_url}{self.devmode_prefix}/{self.app_id}/{self.privacy_key}/{self.session_id}"
        self.sse_url = f"{self.base_url}/sse"
        
        # Will be set after connecting to SSE
        self.message_url = None
        self.transport_session_id = None
        
        self.agent_id = None
        self.event_handlers = {}
        self.logger = logging.getLogger("coral_client")
        
        # Set up logging
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        self.logger.info(f"Initialized Coral client with session ID: {self.session_id}")
        self.logger.info(f"Base URL: {self.base_url}")
        self.logger.info(f"SSE URL: {self.sse_url}")
        
        # Connect to SSE and get transport session ID
        self._connect_to_sse()
    
    def _connect_to_sse(self):
        """
        Connect to the SSE endpoint and extract the transport session ID.
        """
        # Queue to pass the transport session ID between threads
        session_id_queue = queue.Queue()
        
        # Function to capture the transport session ID from SSE events
        def capture_session_id():
            try:
                # Use requests to establish SSE connection
                headers = {"Accept": "text/event-stream"}
                sse_url_with_agent = f"{self.sse_url}?agentId=yona-agent"
                
                self.logger.info(f"Connecting to SSE endpoint: {sse_url_with_agent}")
                response = requests.get(sse_url_with_agent, headers=headers, stream=True)
                
                if response.status_code != 200:
                    self.logger.error(f"Error connecting to SSE endpoint: {response.status_code} {response.reason}")
                    session_id_queue.put(None)
                    return
                    
                self.logger.info("SSE connection established successfully")
                
                # Read the response line by line
                for line in response.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                        
                    self.logger.debug(f"SSE: {line}")
                    
                    # Look for the endpoint event
                    if line.strip() == "event: endpoint":
                        # The next line should contain the data with the session ID
                        data_line = next(response.iter_lines(decode_unicode=True), "").decode() if hasattr(next(response.iter_lines(decode_unicode=True), ""), 'decode') else next(response.iter_lines(decode_unicode=True), "")
                        self.logger.debug(f"SSE data: {data_line}")
                        
                        # Extract the session ID using regex
                        if data_line.startswith("data: "):
                            data_content = data_line[6:]  # Remove "data: " prefix
                            match = re.search(r'sessionId=([a-zA-Z0-9-]+)', data_content)
                            if match:
                                transport_session_id = match.group(1)
                                self.logger.info(f"Found transport session ID: {transport_session_id}")
                                session_id_queue.put(transport_session_id)
                                return
                    
                    # Direct pattern match for sessionId in the line
                    match = re.search(r'sessionId=([a-zA-Z0-9-]+)', line)
                    if match:
                        transport_session_id = match.group(1)
                        self.logger.info(f"Found transport session ID directly: {transport_session_id}")
                        session_id_queue.put(transport_session_id)
                        return
                
                self.logger.error("Could not find transport session ID in SSE events")
                session_id_queue.put(None)
            except Exception as e:
                self.logger.error(f"Error in capture_session_id: {str(e)}")
                session_id_queue.put(None)
        
        # Start the SSE connection in a separate thread
        self.logger.info("Starting SSE connection thread...")
        sse_thread = threading.Thread(target=capture_session_id)
        sse_thread.daemon = True
        sse_thread.start()
        
        # Wait for the transport session ID
        try:
            self.logger.info("Waiting for transport session ID...")
            self.transport_session_id = session_id_queue.get(timeout=10)
            
            if self.transport_session_id is None:
                self.logger.error("Failed to get transport session ID")
                raise Exception("Failed to get transport session ID")
                
            # Construct the message URL with the correct session ID
            self.message_url = f"{self.base_url}/message?sessionId={self.transport_session_id}"
            self.logger.info(f"Message URL: {self.message_url}")
            
            return True
        except queue.Empty:
            self.logger.error("Timeout waiting for transport session ID")
            raise Exception("Timeout waiting for transport session ID")
        except Exception as e:
            self.logger.error(f"Error connecting to SSE: {str(e)}")
            raise
    
    def _send_tool_call(self, tool, args):
        """
        Send a tool call to the Coral server using JSON-RPC format.
        
        Args:
            tool (str): The tool name to call.
            args (dict): The arguments for the tool.
            
        Returns:
            dict: The response from the server, or None if the request failed.
        """
        if not self.message_url or not self.transport_session_id:
            self.logger.error("No message URL or transport session ID available. Reconnecting...")
            self._connect_to_sse()
            
        request_id = str(uuid.uuid4())
        message = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "tool_call",
            "params": {
                "tool": tool,
                "args": args
            }
        }
        
        self.logger.info(f"Sending tool call: {tool}")
        self.logger.debug(f"Tool call details: {json.dumps(message, indent=2)}")
        
        try:
            response = requests.post(
                self.message_url, 
                headers={"Content-Type": "application/json"},
                json=message,
                timeout=10
            )
            
            self.logger.info(f"Response status code: {response.status_code}")
            
            if response.status_code == 200 or response.status_code == 202:
                try:
                    result = response.json()
                    self.logger.debug(f"Tool call response: {json.dumps(result, indent=2)}")
                    return result
                except json.JSONDecodeError:
                    self.logger.info(f"Response is not JSON: {response.text}")
                    # For 202 Accepted responses, this is normal
                    if response.status_code == 202 and response.text.strip() == "Accepted":
                        return {"status": "accepted"}
                    return None
            else:
                self.logger.error(f"Error sending tool call: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Exception sending tool call: {str(e)}")
            return None
    
    def register_agent(self, name, description):
        """
        Register an agent with the Coral server.
        
        Args:
            name (str): The name of the agent.
            description (str): A description of the agent.
            
        Returns:
            str: The agent ID assigned by the server, or None if registration failed.
        """
        self.logger.info(f"Registering agent: {name}")
        
        response = self._send_tool_call("register_agent", {
            "name": name,
            "description": description
        })
        
        if response:
            if response.get("status") == "accepted":
                self.logger.info(f"Agent registration request accepted")
                # We don't have an agent ID yet, but the request was accepted
                return "pending"
            elif response.get("result") and response.get("result").get("agent_id"):
                self.agent_id = response["result"]["agent_id"]
                self.logger.info(f"Agent registered with ID: {self.agent_id}")
                return self.agent_id
        
        self.logger.error(f"Failed to register agent: {response}")
        return None
    
    def list_agents(self):
        """
        List all registered agents.
        
        Returns:
            list: A list of agent information dictionaries, or None if the request failed.
        """
        self.logger.info("Listing agents")
        
        response = self._send_tool_call("list_agents", {})
        
        if response and response.get("result") and "agents" in response.get("result", {}):
            agents = response["result"]["agents"]
            self.logger.info(f"Retrieved {len(agents)} agents")
            return agents
        else:
            self.logger.error(f"Failed to list agents: {response}")
            return None
    
    def create_thread(self, participants, metadata=None):
        """
        Create a new thread.
        
        Args:
            participants (list): List of agent IDs to include in the thread.
            metadata (dict, optional): Additional metadata for the thread.
            
        Returns:
            str: The thread ID assigned by the server, or None if the request failed.
        """
        self.logger.info(f"Creating thread with {len(participants)} participants")
        
        response = self._send_tool_call("create_thread", {
            "participants": participants,
            "metadata": metadata or {}
        })
        
        if response:
            if response.get("status") == "accepted":
                self.logger.info(f"Thread creation request accepted")
                return "pending"
            elif response.get("result") and response.get("result").get("thread_id"):
                thread_id = response["result"]["thread_id"]
                self.logger.info(f"Thread created with ID: {thread_id}")
                return thread_id
        
        self.logger.error(f"Failed to create thread: {response}")
        return None
    
    def send_message(self, thread_id, content, mentions=None):
        """
        Send a message to a thread.
        
        Args:
            thread_id (str): The ID of the thread to send the message to.
            content (str): The content of the message.
            mentions (list, optional): List of agent IDs to mention.
            
        Returns:
            str: The message ID assigned by the server, or None if the request failed.
        """
        self.logger.info(f"Sending message to thread: {thread_id}")
        
        response = self._send_tool_call("send_message", {
            "thread_id": thread_id,
            "content": content,
            "mentions": mentions or []
        })
        
        if response:
            if response.get("status") == "accepted":
                self.logger.info(f"Message send request accepted")
                return "pending"
            elif response.get("result") and response.get("result").get("message_id"):
                message_id = response["result"]["message_id"]
                self.logger.info(f"Message sent with ID: {message_id}")
                return message_id
        
        self.logger.error(f"Failed to send message: {response}")
        return None
    
    def wait_for_mentions(self, agent_id, timeout_seconds=60):
        """
        Wait for mentions of the specified agent.
        
        Args:
            agent_id (str): The ID of the agent to wait for mentions of.
            timeout_seconds (int, optional): Maximum time to wait in seconds.
            
        Returns:
            list: A list of messages mentioning the agent, or None if the request failed.
        """
        self.logger.info(f"Waiting for mentions of agent: {agent_id}")
        
        response = self._send_tool_call("wait_for_mentions", {
            "agent_id": agent_id,
            "timeout_seconds": timeout_seconds
        })
        
        if response and response.get("result") and "messages" in response.get("result", {}):
            messages = response["result"]["messages"]
            self.logger.info(f"Received {len(messages)} mentions")
            return messages
        else:
            self.logger.error(f"Failed to wait for mentions: {response}")
            return None
    
    def start_listening(self, event_handlers=None):
        """
        Start listening for events from the Coral server.
        
        Args:
            event_handlers (dict, optional): Dictionary mapping event types to handler functions.
            
        Returns:
            threading.Thread: The thread that is listening for events.
        """
        if event_handlers:
            self.event_handlers.update(event_handlers)
        
        def _listen():
            self.logger.info(f"Starting event listener for session: {self.session_id}")
            headers = {"Accept": "text/event-stream"}
            sse_url_with_agent = f"{self.sse_url}?agentId=yona-agent"
            
            while True:
                try:
                    self.logger.info(f"Connecting to SSE endpoint: {sse_url_with_agent}")
                    response = requests.get(sse_url_with_agent, headers=headers, stream=True)
                    
                    if response.status_code == 200:
                        self.logger.info("SSE connection established successfully")
                        client = sseclient.SSEClient(response)
                        
                        for event in client.events():
                            try:
                                self.logger.debug(f"Received event: {event.data}")
                                
                                # Check if this is an endpoint event
                                if event.event == "endpoint":
                                    self.logger.info(f"Received endpoint event: {event.data}")
                                    match = re.search(r'sessionId=([a-zA-Z0-9-]+)', event.data)
                                    if match:
                                        self.transport_session_id = match.group(1)
                                        self.message_url = f"{self.base_url}/message?sessionId={self.transport_session_id}"
                                        self.logger.info(f"Updated transport session ID: {self.transport_session_id}")
                                        self.logger.info(f"Updated message URL: {self.message_url}")
                                    continue
                                
                                # Process regular events
                                try:
                                    data = json.loads(event.data)
                                    event_type = data.get("type")
                                    
                                    if event_type in self.event_handlers:
                                        self.logger.info(f"Processing event of type: {event_type}")
                                        self.event_handlers[event_type](data)
                                    else:
                                        self.logger.debug(f"No handler for event type: {event_type}")
                                except json.JSONDecodeError:
                                    self.logger.error(f"Error parsing event data as JSON: {event.data}")
                            except Exception as e:
                                self.logger.error(f"Error processing event: {str(e)}")
                    else:
                        self.logger.error(f"Failed to connect to SSE endpoint: {response.status_code} - {response.text}")
                        time.sleep(5)  # Wait before retrying
                except Exception as e:
                    self.logger.error(f"Error in event listener: {str(e)}")
                    time.sleep(5)  # Wait before retrying
        
        thread = threading.Thread(target=_listen, daemon=True)
        thread.start()
        self.logger.info("Event listener thread started")
        return thread

# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create a client
    client = CoralClient(use_devmode=True)
    
    # Define event handlers
    def handle_tool_response(data):
        print(f"Received tool response: {json.dumps(data, indent=2)}")
    
    def handle_message(data):
        print(f"Received message: {json.dumps(data, indent=2)}")
    
    # Start listening for events
    client.start_listening({
        "tool_response": handle_tool_response,
        "message": handle_message
    })
    
    # Register an agent
    agent_id = client.register_agent(
        name="YonaAgent",
        description="An AI music agent that creates songs based on prompts and feedback"
    )
    print(f"Registered agent with ID: {agent_id}")
    
    # Keep the script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
