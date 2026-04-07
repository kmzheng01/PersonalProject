"""DSL interpreter for executing parsed feature definitions."""

from typing import Dict, Any, Callable, Optional
import time

from utils.logger import get_logger
from .builtins import get_builtin_functions

logger = get_logger(__name__)


class DSLInterpreter:
    """Executes parsed DSL code."""

    def __init__(self):
        """Initialize interpreter."""
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, Dict[str, Any]] = {}
        self.event_handlers: Dict[str, list] = {}
        self.builtin_functions = get_builtin_functions()
        logger.info("DSLInterpreter initialized")

    def register_builtin(self, name: str, func: Callable) -> None:
        """Register a builtin function."""
        self.builtin_functions[name] = func

    def execute(self, ast: list) -> None:
        """
        Execute parsed DSL AST.
        
        Args:
            ast: Abstract syntax tree from parser
        """
        for node in ast:
            self.execute_node(node)

    def execute_node(self, node: Dict[str, Any]) -> Any:
        """Execute a single AST node."""
        node_type = node.get('type')
        
        if node_type == 'define_feature':
            self.define_feature(node)
        elif node_type == 'function':
            self.define_function(node)
        elif node_type == 'import':
            self.execute_import(node)
        elif node_type == 'event_handler':
            self.register_event_handler(node)
        else:
            logger.warning(f"Unknown node type: {node_type}")

    def define_feature(self, node: Dict[str, Any]) -> None:
        """Define a feature."""
        feature_name = node['name']
        body = node['body']
        
        logger.info(f"Defining feature: {feature_name}")
        
        # Register event handlers from feature body
        for statement in body:
            if statement.get('type') == 'event_handler':
                self.register_event_handler(statement)

    def define_function(self, node: Dict[str, Any]) -> None:
        """Define a function."""
        func_name = node['name']
        params = node['params']
        body = node['body']
        
        self.functions[func_name] = {
            'params': params,
            'body': body,
        }
        
        logger.info(f"Defined function: {func_name}")

    def call_function(self, name: str, args: list = None) -> Any:
        """Call a function."""
        args = args or []
        
        # Check builtins first
        if name in self.builtin_functions:
            try:
                return self.builtin_functions[name](*args)
            except Exception as e:
                logger.error(f"Error calling builtin {name}: {e}")
                return None
        
        # Check user-defined functions
        if name in self.functions:
            func = self.functions[name]
            # Create local scope
            old_vars = self.variables.copy()
            
            # Bind parameters
            for param, arg in zip(func['params'], args):
                self.variables[param] = arg
            
            # Execute function body
            result = None
            for stmt in func['body']:
                result = self.execute_node(stmt)
            
            # Restore old scope
            self.variables = old_vars
            return result
        
        logger.warning(f"Function not found: {name}")
        return None

    def register_event_handler(self, node: Dict[str, Any]) -> None:
        """Register an event handler."""
        event = node['event']
        handler = node['body']
        
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        
        self.event_handlers[event].append(handler)
        logger.debug(f"Registered handler for event: {event}")

    def trigger_event(self, event: str, *args, **kwargs) -> None:
        """
        Trigger an event.
        
        Args:
            event: Event name
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
        if event not in self.event_handlers:
            return
        
        for handler in self.event_handlers[event]:
            try:
                # Execute handler body
                for stmt in handler:
                    self.execute_node(stmt)
            except Exception as e:
                logger.error(f"Error executing handler for {event}: {e}")

    def execute_import(self, node: Dict[str, Any]) -> None:
        """Execute import statement."""
        module_name = node['module']
        alias = node.get('alias', module_name)
        
        logger.debug(f"Importing module: {module_name} as {alias}")
        # In a real implementation, would load external modules

    def set_variable(self, name: str, value: Any) -> None:
        """Set a variable."""
        self.variables[name] = value

    def get_variable(self, name: str) -> Any:
        """Get a variable."""
        return self.variables.get(name)

    def get_context(self) -> Dict[str, Any]:
        """Get current execution context."""
        return {
            'variables': self.variables,
            'functions': list(self.functions.keys()),
            'events': list(self.event_handlers.keys()),
        }
