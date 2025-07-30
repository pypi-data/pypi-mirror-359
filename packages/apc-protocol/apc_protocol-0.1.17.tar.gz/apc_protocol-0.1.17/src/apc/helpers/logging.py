"""
Enhanced logging configuration for APC with LLM streaming support.
Provides colorized, structured logging that's automatically configured when APC is imported.
"""
import logging
import sys
import time
from typing import Any, Dict, Generator, Iterator
from threading import Lock

class ColorizedFormatter(logging.Formatter):
    """Custom formatter for colorized APC logs"""
    
    COLORS = {
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow  
        'ERROR': '\033[31m',     # Red
        'DEBUG': '\033[36m',     # Cyan
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m',      # Reset
        'BOLD': '\033[1m',       # Bold
        'DIM': '\033[2m',        # Dim
        'PURPLE': '\033[95m',    # Purple/Violet for LLM responses
        'BRIGHT_PURPLE': '\033[1;95m',  # Bright Purple for LLM streaming
        'BRIGHT_MAGENTA': '\033[1;35m', # Bright Magenta for model names
    }
    
    def format(self, record):
        level_color = self.COLORS.get(record.levelname, '')
        reset = self.COLORS['RESET']
        dim = self.COLORS['DIM']
        bold = self.COLORS['BOLD']
        
        # Format timestamp
        timestamp = self.formatTime(record, '%Y-%m-%d %H:%M:%S')
        
        # Format level with padding and color
        colored_level = f"{level_color}{record.levelname.lower():8}{reset}"
        
        # Highlight WARNING and ERROR messages
        if record.levelno == logging.WARNING:
            message = f"{bold}{level_color}{record.getMessage()}{reset}"
        elif record.levelno >= logging.ERROR:
            message = f"{bold}{level_color}{record.getMessage()}{reset}"
        elif record.levelno == logging.DEBUG:
            message = f"{dim}{level_color}{record.getMessage()}{reset}"
        else:
            message = f"{level_color}{record.getMessage()}{reset}"
        
        # Build message
        message_parts = [
            f"{dim}{timestamp}{reset}",
            f"[{colored_level}]",
            message
        ]
        
        return " ".join(message_parts)

def setup_apc_logging(level: str = "INFO") -> None:
    """
    Set up beautiful, colorized logging for APC.
    This gives users the same colorful logs shown in demos.
    """
    
    # Configure root logger
    logger = logging.getLogger('apc')
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers:
        logger.removeHandler(handler)
    
    # Create console handler with our custom formatter
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(ColorizedFormatter())
    logger.addHandler(handler)
    
    # Reduce noise from other libraries
    logging.getLogger("grpc").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """Get a configured APC logger."""
    return logging.getLogger(f'apc.{name}')

class StructuredLogger:
    """A simple structured logger that mimics structlog API but uses standard logging"""
    
    def __init__(self, logger: logging.Logger):
        self._logger = logger
    
    def info(self, message: str, **kwargs):
        """Log info message with key-value pairs"""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with key-value pairs"""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with key-value pairs"""
        self._log(logging.ERROR, message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with key-value pairs"""
        self._log(logging.DEBUG, message, **kwargs)
    
    def _log(self, level: int, message: str, **kwargs):
        """Internal method to format and log messages with key-value pairs"""
        if kwargs:
            # Format key-value pairs
            kv_parts = [f"{k}={v}" for k, v in kwargs.items()]
            full_message = f"{message} {' '.join(kv_parts)}"
        else:
            full_message = message
        
        self._logger.log(level, full_message)

# Global state for streaming output
_stream_lock = Lock()

def stream_llm_response(agent_name: str, model_name: str, response_generator: Iterator[str], logger: logging.Logger = None) -> str:
    """
    Stream LLM response with purple/violet color coding in terminal.
    
    Args:
        agent_name: Name of the agent making the request
        model_name: Name of the LLM model (e.g., 'gpt-4', 'claude-3')
        response_generator: Iterator that yields chunks of the response
        logger: Logger to use (optional)
    
    Returns:
        Complete response text
    """
    if logger is None:
        logger = get_logger('llm_stream')
    
    purple = ColorizedFormatter.COLORS['BRIGHT_PURPLE']
    magenta = ColorizedFormatter.COLORS['BRIGHT_MAGENTA']
    reset = ColorizedFormatter.COLORS['RESET']
    dim = ColorizedFormatter.COLORS['DIM']
    bold = ColorizedFormatter.COLORS['BOLD']
    
    with _stream_lock:
        # Print agent and model header with enhanced styling
        print(f"\n{bold}{magenta}🤖 {agent_name} -> {model_name}{reset}", flush=True)
        print(f"{purple}{'═' * 60}{reset}", flush=True)
        
        # Stream the response with real-time output
        full_response = ""
        start_time = time.time()
        
        try:
            for chunk in response_generator:
                if chunk:
                    print(f"{purple}{chunk}{reset}", end='', flush=True)
                    full_response += chunk
                    time.sleep(0.005)  # Minimal delay for natural streaming effect
        except Exception as e:
            print(f"\n{ColorizedFormatter.COLORS['ERROR']}❌ Streaming error: {e}{reset}")
            logger.error(f"LLM streaming error: {e}")
            return full_response
        
        duration = time.time() - start_time
        
        # Footer with completion stats
        print(f"\n{purple}{'═' * 60}{reset}")
        print(f"{dim}✓ Completed in {duration:.1f}s | {len(full_response)} characters | {len(full_response.split())} words{reset}\n", flush=True)
        
        return full_response

def log_llm_start(agent_name: str, model_name: str, prompt_preview: str = "", logger: logging.Logger = None):
    """Log the start of an LLM request with purple colors."""
    if logger is None:
        logger = get_logger('llm')
    
    purple = ColorizedFormatter.COLORS['PURPLE']
    magenta = ColorizedFormatter.COLORS['BRIGHT_MAGENTA']
    reset = ColorizedFormatter.COLORS['RESET']
    
    preview = f" | Prompt: {prompt_preview[:40]}..." if prompt_preview else ""
    message = f"{purple}🚀 {agent_name} calling {magenta}{model_name}{purple}{preview}{reset}"
    logger.info(message)

def log_llm_complete(agent_name: str, model_name: str, response_length: int, duration: float, logger: logging.Logger = None):
    """Log the completion of an LLM request."""
    if logger is None:
        logger = get_logger('llm')
    
    purple = ColorizedFormatter.COLORS['PURPLE']
    magenta = ColorizedFormatter.COLORS['BRIGHT_MAGENTA']
    reset = ColorizedFormatter.COLORS['RESET']
    
    message = f"{purple}✅ {agent_name} completed {magenta}{model_name}{purple} ({response_length} chars, {duration:.1f}s){reset}"
    logger.warning(message)  # Use warning level for visibility

# Auto-configure logging when APC helpers are imported
setup_apc_logging()
