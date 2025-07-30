#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/cli/base.py

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from dataclasses import dataclass
from rich.console import Console
from rich import print as rprint

from logbuch.core.config import get_config, Config
from logbuch.core.logger import get_logger, Logger
from logbuch.core.security import get_security_manager, SecurityManager
from logbuch.core.validators import get_validator, InputValidator
from logbuch.core.exceptions import LogbuchError, format_error_for_user
from logbuch.storage import Storage


@dataclass
class CommandContext:
    config: Config
    logger: Logger
    security_manager: SecurityManager
    validator: InputValidator
    storage: Storage
    console: Console
    
    @classmethod
    def create(cls) -> 'CommandContext':
        config = get_config()
        
        return cls(
            config=config,
            logger=get_logger(),
            security_manager=get_security_manager(),
            validator=get_validator(),
            storage=Storage(config.database.path),
            console=Console()
        )


class BaseCommand(ABC):
    def __init__(self, context: CommandContext):
        self.context = context
        self.config = context.config
        self.logger = context.logger
        self.security = context.security_manager
        self.validator = context.validator
        self.storage = context.storage
        self.console = context.console
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        pass
    
    def validate_inputs(self, **kwargs) -> Dict[str, Any]:
        return kwargs
    
    def check_permissions(self, **kwargs) -> bool:
        return True
    
    def pre_execute(self, **kwargs) -> Dict[str, Any]:
        # Log command execution
        self.logger.log_user_action(
            self.__class__.__name__,
            command_args=list(kwargs.keys())
        )
        
        # Check rate limiting
        if not self.security.check_rate_limit(self.__class__.__name__):
            raise LogbuchError(
                "Rate limit exceeded. Please wait before trying again.",
                error_code="RATE_LIMIT_EXCEEDED"
            )
        
        # Validate inputs
        validated_kwargs = self.validate_inputs(**kwargs)
        
        # Check permissions
        if not self.check_permissions(**validated_kwargs):
            raise LogbuchError(
                "Permission denied for this operation.",
                error_code="PERMISSION_DENIED"
            )
        
        return validated_kwargs
    
    def post_execute(self, result: Any, **kwargs) -> Any:
        # Log successful completion
        self.logger.info(f"Command {self.__class__.__name__} completed successfully")
        return result
    
    def handle_error(self, error: Exception, **kwargs) -> None:
        self.logger.log_error_with_context(error, {
            'command': self.__class__.__name__,
            'kwargs': kwargs
        })
        
        # Display user-friendly error message
        user_message = format_error_for_user(error)
        rprint(f"[red]❌ {user_message}[/red]")
    
    def run(self, **kwargs) -> Any:
        try:
            # Pre-execution
            validated_kwargs = self.pre_execute(**kwargs)
            
            # Execute command
            result = self.execute(**validated_kwargs)
            
            # Post-execution
            return self.post_execute(result, **validated_kwargs)
            
        except Exception as error:
            self.handle_error(error, **kwargs)
            raise
    
    # Utility methods for common operations
    
    def success(self, message: str, **details) -> None:
        rprint(f"[green]✅ {message}[/green]")
        if details:
            for key, value in details.items():
                rprint(f"[blue]{key}:[/blue] {value}")
    
    def warning(self, message: str) -> None:
        rprint(f"[yellow]⚠️ {message}[/yellow]")
    
    def error(self, message: str) -> None:
        rprint(f"[red]❌ {message}[/red]")
    
    def info(self, message: str) -> None:
        rprint(f"[blue]ℹ️ {message}[/blue]")
    
    def confirm(self, message: str, default: bool = False) -> bool:
        from rich.prompt import Confirm
        return Confirm.ask(message, default=default)
    
    def prompt(self, message: str, default: Optional[str] = None) -> str:
        from rich.prompt import Prompt
        return Prompt.ask(message, default=default)
    
    def display_table(self, data: List[Dict], title: Optional[str] = None) -> None:
        from rich.table import Table
        
        if not data:
            self.info("No data to display")
            return
        
        table = Table(title=title)
        
        # Add columns based on first row
        for key in data[0].keys():
            table.add_column(key.replace('_', ' ').title(), style="cyan")
        
        # Add rows
        for row in data:
            table.add_row(*[str(value) for value in row.values()])
        
        self.console.print(table)
    
    def display_progress(self, items: List[Any], description: str = "Processing"):
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console,
        ) as progress:
            task = progress.add_task(description, total=len(items))
            
            for item in items:
                yield item
                progress.advance(task)


class DataCommand(BaseCommand):
    def validate_id(self, item_id: str, item_type: str) -> str:
        return self.validator.validate_string(
            item_id, 
            f"{item_type}_id", 
            min_length=1, 
            max_length=50,
            pattern=r'^[a-zA-Z0-9_-]+$'
        )
    
    def validate_content(self, content: str) -> str:
        return self.validator.validate_string(
            content,
            "content",
            min_length=1,
            max_length=self.config.security.max_input_length,
            allow_empty=False
        )
    
    def validate_tags(self, tags: Any) -> List[str]:
        return self.validator.validate_tags(tags, "tags")
    
    def validate_priority(self, priority: str) -> str:
        return self.validator.validate_priority(priority, "priority")


class FileCommand(BaseCommand):
    def validate_file_path(self, file_path: str, must_exist: bool = False) -> str:
        path = self.validator.validate_file_path(
            file_path, 
            "file_path", 
            must_exist=must_exist
        )
        
        # Additional security validation
        return str(self.security.validate_file_operation(str(path), "access"))
    
    def safe_file_operation(self, operation: str, file_path: str, **kwargs):
        try:
            validated_path = self.validate_file_path(file_path, **kwargs)
            self.logger.info(f"File operation: {operation}", extra={
                'operation': operation,
                'file_path': validated_path
            })
            return validated_path
        except Exception as e:
            self.logger.error(f"File operation failed: {operation}", extra={
                'operation': operation,
                'file_path': file_path,
                'error': str(e)
            })
            raise


class AsyncCommand(BaseCommand):
    async def execute_async(self, **kwargs) -> Any:
        return self.execute(**kwargs)
    
    async def run_async(self, **kwargs) -> Any:
        try:
            validated_kwargs = self.pre_execute(**kwargs)
            result = await self.execute_async(**validated_kwargs)
            return self.post_execute(result, **validated_kwargs)
        except Exception as error:
            self.handle_error(error, **kwargs)
            raise


# Command registry for dynamic loading

class CommandRegistry:
    def __init__(self):
        self._commands: Dict[str, type] = {}
        self._aliases: Dict[str, str] = {}
    
    def register(self, name: str, command_class: type, aliases: Optional[List[str]] = None):
        self._commands[name] = command_class
        
        if aliases:
            for alias in aliases:
                self._aliases[alias] = name
    
    def get_command(self, name: str) -> Optional[type]:
        # Check direct name first
        if name in self._commands:
            return self._commands[name]
        
        # Check aliases
        if name in self._aliases:
            return self._commands[self._aliases[name]]
        
        return None
    
    def list_commands(self) -> List[str]:
        return list(self._commands.keys())
    
    def list_aliases(self) -> Dict[str, str]:
        return self._aliases.copy()


# Global command registry
_command_registry = CommandRegistry()


def register_command(name: str, aliases: Optional[List[str]] = None):
    def decorator(command_class):
        _command_registry.register(name, command_class, aliases)
        return command_class
    return decorator


def get_command_registry() -> CommandRegistry:
    return _command_registry
