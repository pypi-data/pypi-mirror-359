import os
import json
import logging
import requests
import httpx
import asyncio
from typing import Any, Dict, Optional, Union
from urllib.parse import urlparse
from .session_utils import get_session_id, get_session_name, SessionManager

class TropirStateManager:
    """
    Manager for Tropir state - handles switching between regular state and Tropir rerun state.
    
    In Tropir state:
    - Variables are fetched from Tropir context (rerun inputs)
    - Prompts are fetched from Tropir platform (optimized versions)
    - All requests are tracked to the rerun session
    
    In regular state:
    - Variables come from environment/config
    - Prompts are local/hardcoded versions
    - Normal session tracking
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TropirStateManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self._tropir_variables = {}
        self._tropir_prompts_cache = {}
        self._rerun_session_id = None
        self._original_session_context = None
        
        # Initialize from environment
        self._setup_tropir_state()
        
    def _setup_tropir_state(self):
        """Initialize Tropir state from environment variables."""
        self._is_tropir_state = os.environ.get("TROPIR_RERUN_MODE", "false").lower() == "true"
        self._rerun_session_id = os.environ.get("TROPIR_RERUN_SESSION_ID")
        self._original_session_id = os.environ.get("TROPIR_ORIGINAL_SESSION_ID") 
        
        # Load Tropir variables from environment
        tropir_vars_json = os.environ.get("TROPIR_VARIABLES")
        if tropir_vars_json:
            try:
                self._tropir_variables = json.loads(tropir_vars_json)
                logging.info(f"Tropir State: Loaded {len(self._tropir_variables)} variables")
            except json.JSONDecodeError as e:
                logging.warning(f"Tropir State: Failed to parse TROPIR_VARIABLES: {e}")
                
        # Setup session context for rerun
        if self._is_tropir_state and self._rerun_session_id:
            self._setup_rerun_session()
    
    def _setup_rerun_session(self):
        """Setup session context for Tropir rerun."""
        # Store original session context if exists
        self._original_session_context = {
            'session_id': get_session_id(),
            'session_name': get_session_name()
        }
        
        # Create rerun session manager 
        rerun_session_name = f"tropir_rerun_{self._original_session_id}"
        self._rerun_session_manager = SessionManager(rerun_session_name)
        self._rerun_session_manager.session_id = self._rerun_session_id
        
        # Start the rerun session
        self._rerun_session_manager.__enter__()
        
        logging.info(f"Tropir State: Started rerun session {self._rerun_session_id}")
    
    def is_tropir_state(self) -> bool:
        """Check if currently in Tropir rerun state."""
        return self._is_tropir_state
    
    def get_variable(self, key: str, default: Any = None, source: str = "auto") -> Any:
        """
        Get a variable - from Tropir context if in rerun state, otherwise from regular sources.
        
        Args:
            key: Variable name
            default: Default value if not found
            source: "auto" (detect), "tropir" (force Tropir), "regular" (force regular)
            
        Returns:
            Variable value
        """
        if source == "tropir" or (source == "auto" and self._is_tropir_state):
            # Get from Tropir variables
            if key in self._tropir_variables:
                value = self._tropir_variables[key]
                logging.debug(f"Tropir State: Retrieved variable '{key}' from Tropir context: {value}")
                return value
            else:
                logging.debug(f"Tropir State: Variable '{key}' not found in Tropir context, using default: {default}")
                return default
        else:
            # Get from regular sources (environment, config, etc.)
            value = os.environ.get(key, default)
            logging.debug(f"Tropir State: Retrieved variable '{key}' from environment: {value}")
            return value
    
    def set_variable(self, key: str, value: Any):
        """
        Set a variable in Tropir context.
        
        Args:
            key: Variable name
            value: Variable value
        """
        self._tropir_variables[key] = value
        logging.debug(f"Tropir State: Set variable '{key}' = {value}")
    
    def get_prompt(self, prompt_id: str, context: Optional[Dict] = None, default: str = "") -> str:
        """
        Get a prompt - from Tropir platform if in rerun state, otherwise return default.
        
        Args:
            prompt_id: Unique identifier for the prompt
            context: Optional context for prompt templating
            default: Default prompt to use if not in Tropir state or fetch fails
            
        Returns:
            Prompt text
        """
        if not self._is_tropir_state:
            logging.debug(f"Tropir State: Not in rerun state, using default prompt for '{prompt_id}'")
            return default
            
        # Check cache first
        cache_key = f"{prompt_id}:{hash(str(context))}" if context else prompt_id
        if cache_key in self._tropir_prompts_cache:
            logging.debug(f"Tropir State: Retrieved cached prompt for '{prompt_id}'")
            return self._tropir_prompts_cache[cache_key]
        
        # Fetch from Tropir platform
        try:
            optimized_prompt = self._fetch_tropir_prompt(prompt_id, context)
            if optimized_prompt:
                self._tropir_prompts_cache[cache_key] = optimized_prompt
                logging.info(f"Tropir State: Retrieved optimized prompt for '{prompt_id}' from platform")
                return optimized_prompt
            else:
                logging.warning(f"Tropir State: Failed to fetch prompt '{prompt_id}', using default")
                return default
        except Exception as e:
            logging.warning(f"Tropir State: Error fetching prompt '{prompt_id}': {e}, using default")
            return default
    
    def _fetch_tropir_prompt(self, prompt_id: str, context: Optional[Dict] = None) -> Optional[str]:
        """
        Fetch optimized prompt from Tropir platform.
        
        Args:
            prompt_id: Prompt identifier
            context: Optional context for templating
            
        Returns:
            Optimized prompt text or None if failed
        """
        endpoint = os.environ.get("TROPIR_PROMPTS_ENDPOINT", self._get_default_prompts_endpoint())
        
        payload = {
            "prompt_id": prompt_id,
            "session_id": self._original_session_id,
            "rerun_session_id": self._rerun_session_id
        }
        
        if context:
            payload["context"] = context
            
        headers = {
            "Content-Type": "application/json",
            "X-Session-ID": self._rerun_session_id,
            "X-Original-Session-ID": self._original_session_id
        }
        
        # Add API key if available
        api_key = os.environ.get("TROPIR_API_KEY")
        if api_key:
            headers["X-TROPIR-API-KEY"] = api_key
        
        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("optimized_prompt")
            else:
                logging.warning(f"Tropir Prompts: HTTP {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logging.warning(f"Tropir Prompts: Request failed - {e}")
            return None
    
    def _get_default_prompts_endpoint(self):
        """Get default prompts endpoint based on environment."""
        if os.environ.get("ENVIRONMENT") == "dev":
            return "http://localhost:8080/api/v1/prompts/optimized"
        else:
            return "https://api.tropir.com/api/v1/prompts/optimized"
    
    def add_step(self, data: Dict[str, Any], step_name: Optional[str] = None):
        """
        Add a step to the current session (rerun session if in Tropir state).
        
        Args:
            data: Step data
            step_name: Optional step name
        """
        if self._is_tropir_state and hasattr(self, '_rerun_session_manager'):
            # Add to rerun session
            result = self._rerun_session_manager.add_step(data, step_name)
            # Handle async result if needed
            if asyncio.iscoroutine(result):
                # If we're in an async context, we can await it
                try:
                    loop = asyncio.get_running_loop()
                    # Create a task for the coroutine
                    asyncio.create_task(result)
                except RuntimeError:
                    # Not in async context, run in thread
                    pass
        else:
            # Use regular session manager
            session_manager = SessionManager()
            result = session_manager.add_step(data, step_name)
            if asyncio.iscoroutine(result):
                try:
                    loop = asyncio.get_running_loop()
                    asyncio.create_task(result)
                except RuntimeError:
                    pass
    
    def instrument_variable(self, key: str, value: Any, description: str = ""):
        """
        Instrument a variable for potential rerun usage.
        This marks variables that could be used as rerun inputs.
        
        Args:
            key: Variable name/identifier
            value: Current value
            description: Human-readable description
        """
        instrumentation_data = {
            "type": "variable_instrumentation",
            "key": key,
            "value": value,
            "description": description,
            "location": self._get_caller_location()
        }
        
        self.add_step(instrumentation_data, f"instrument_var_{key}")
        
        # Also store in current context
        if key not in self._tropir_variables and not self._is_tropir_state:
            # Only set if not already in Tropir context (to avoid overriding rerun inputs)
            self._tropir_variables[key] = value
    
    def _get_caller_location(self) -> str:
        """Get the location of the caller for instrumentation."""
        import inspect
        frame = inspect.currentframe()
        try:
            # Go up the stack to find the actual caller
            caller_frame = frame.f_back.f_back
            if caller_frame:
                filename = caller_frame.f_code.co_filename
                lineno = caller_frame.f_lineno
                function = caller_frame.f_code.co_name
                return f"{filename}:{lineno} in {function}"
        finally:
            del frame
        return "unknown"
    
    def cleanup(self):
        """Cleanup Tropir state and restore original session context."""
        if self._is_tropir_state and hasattr(self, '_rerun_session_manager'):
            # End rerun session
            self._rerun_session_manager.__exit__(None, None, None)
            
            # Restore original session context if it existed
            if self._original_session_context:
                # This would need session_utils support for restoring context
                pass
                
        logging.info("Tropir State: Cleaned up rerun state")

# Global state manager instance
_state_manager = None

def get_state_manager() -> TropirStateManager:
    """Get the global Tropir state manager instance."""
    global _state_manager
    if _state_manager is None:
        _state_manager = TropirStateManager()
    return _state_manager

# Convenience functions
def is_tropir_state() -> bool:
    """Check if currently in Tropir rerun state."""
    return get_state_manager().is_tropir_state()

def get_variable(key: str, default: Any = None) -> Any:
    """
    Get a variable - from Tropir context if in rerun state, otherwise from regular sources.
    
    Args:
        key: Variable name
        default: Default value if not found
        
    Returns:
        Variable value
    """
    return get_state_manager().get_variable(key, default)

def get_prompt(prompt_id: str, context: Optional[Dict] = None, default: str = "") -> str:
    """
    Get a prompt - from Tropir platform if in rerun state, otherwise return default.
    
    Args:
        prompt_id: Unique identifier for the prompt
        context: Optional context for prompt templating
        default: Default prompt to use if not in Tropir state or fetch fails
        
    Returns:
        Prompt text
    """
    return get_state_manager().get_prompt(prompt_id, context, default)

def instrument_variable(key: str, value: Any, description: str = ""):
    """
    Instrument a variable for potential rerun usage.
    
    Args:
        key: Variable name/identifier  
        value: Current value
        description: Human-readable description
    """
    return get_state_manager().instrument_variable(key, value, description)

def add_rerun_step(data: Dict[str, Any], step_name: Optional[str] = None):
    """
    Add a step to the current session (rerun session if in Tropir state).
    
    Args:
        data: Step data
        step_name: Optional step name
    """
    return get_state_manager().add_step(data, step_name)

# Cleanup function for graceful shutdown
def cleanup_tropir_state():
    """Cleanup Tropir state on shutdown."""
    global _state_manager
    if _state_manager:
        _state_manager.cleanup()
        _state_manager = None

# Register cleanup on exit
import atexit
atexit.register(cleanup_tropir_state)