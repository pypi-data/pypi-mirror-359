"""
Configuration module for XenTokeniser.

This module provides configuration classes for the XenTokeniser package,
including tokenizer settings and cloud storage integration configurations.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional, Type, TypeVar, Union

from .exceptions import TokenizerValueError

T = TypeVar('T', bound='BaseConfig')


class BaseConfig:
    """Base configuration class with common serialization methods."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the config to a dictionary, excluding private attributes."""
        return {
            k: v for k, v in vars(self).items()
            if not k.startswith('_') and not callable(getattr(self, k, None))
        }
    
    def to_json_string(self, **kwargs) -> str:
        """
        Serialize this instance to a JSON string.
        
        Args:
            **kwargs: Additional arguments for json.dumps()
            
        Returns:
            JSON string representation of the config
        """
        default_kwargs = {
            'indent': 2,
            'ensure_ascii': False,
            'sort_keys': True
        }
        default_kwargs.update(kwargs)
        return json.dumps(self.to_dict(), **default_kwargs)
    
    def to_json_file(self, json_file: Union[str, os.PathLike], **kwargs) -> None:
        """
        Save this instance to a JSON file.
        
        Args:
            json_file: Path to the output JSON file
            **kwargs: Additional arguments for to_json_string()
        """
        json_file = Path(json_file)
        json_file.parent.mkdir(parents=True, exist_ok=True)
        json_file.write_text(self.to_json_string(**kwargs), encoding='utf-8')
    
    @classmethod
    def from_dict(cls: Type[T], config_dict: Dict[str, Any]) -> T:
        """
        Construct a config from a dictionary.
        
        Args:
            config_dict: Dictionary containing configuration parameters
            
        Returns:
            New instance of the config class
        """
        return cls(**{
            k: v for k, v in config_dict.items()
            if k in cls.__annotations__
        })
    
    @classmethod
    def from_json_file(cls: Type[T], json_file: Union[str, os.PathLike]) -> T:
        """
        Construct a config from a JSON file.
        
        Args:
            json_file: Path to the JSON config file
            
        Returns:
            New instance of the config class
            
        Raises:
            FileNotFoundError: If the JSON file doesn't exist
            json.JSONDecodeError: If the JSON file is invalid
        """
        json_file = Path(json_file)
        if not json_file.exists():
            raise FileNotFoundError(f"Config file not found: {json_file}")
            
        with open(json_file, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
            
        return cls.from_dict(config_dict)


@dataclass
class TokenizerConfig(BaseConfig):
    """
    Configuration for the XenTokeniser tokenizer.
    
    This class holds all configurable parameters for the tokenizer, including
    special tokens and processing options.
    """
    # Tokenization parameters
    max_length: int = 2048
    padding_side: str = "right"
    truncation: Union[bool, str] = True
    
    # Special tokens
    pad_token: str = "<pad>"
    eos_token: str = "</s>"
    unk_token: str = "<unk>"
    bos_token: str = "<s>"
    
    # Additional configuration
    add_prefix_space: bool = False
    clean_up_tokenization_spaces: bool = True
    additional_special_tokens: List[str] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        self._validate()
    
    def _validate(self) -> None:
        """Validate the configuration values."""
        if not isinstance(self.max_length, int) or self.max_length <= 0:
            raise TokenizerValueError(
                f"max_length must be a positive integer, got {self.max_length}"
            )
            
        if self.padding_side not in ["left", "right"]:
            raise TokenizerValueError(
                f"padding_side must be 'left' or 'right', got {self.padding_side}"
            )
            
        if not all(isinstance(t, str) for t in self.additional_special_tokens):
            raise TokenizerValueError(
                "All additional_special_tokens must be strings"
            )
    
    def add_special_tokens(self, tokens: Union[str, List[str]]) -> None:
        """
        Add special tokens to the configuration.
        
        Args:
            tokens: Single token or list of tokens to add
        """
        if isinstance(tokens, str):
            tokens = [tokens]
            
        for token in tokens:
            if token not in self.additional_special_tokens:
                self.additional_special_tokens.append(token)


@dataclass
class AzureConfig(BaseConfig):
    """
    Configuration for Azure Blob Storage integration.
    
    This class holds configuration for connecting to and interacting with
    Azure Blob Storage for data processing tasks.
    """
    # Required Azure settings
    connection_string: str = ""
    container_name: str = ""
    
    # Path prefixes
    input_prefix: str = "raw_data/"
    output_prefix: str = "processed_data/"
    
    # Performance settings
    max_workers: int = 4
    max_concurrent_connections: int = 10
    
    # Timeout settings (in seconds)
    connection_timeout: int = 20
    read_timeout: int = 60
    
    # Retry settings
    max_retries: int = 3
    retry_delay: int = 5  # seconds
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        self._validate()
    
    def _validate(self) -> None:
        """Validate the configuration values."""
        if not self.connection_string:
            raise TokenizerValueError("Azure connection_string is required")
            
        if not self.container_name:
            raise TokenizerValueError("Azure container_name is required")
            
        if self.max_workers <= 0:
            raise TokenizerValueError(
                f"max_workers must be positive, got {self.max_workers}"
            )
    
    @classmethod
    def from_env(cls) -> 'AzureConfig':
        """
        Load configuration from environment variables.
        
        Returns:
            New AzureConfig instance with values from environment variables
            
        Environment Variables:
            AZURE_STORAGE_CONNECTION_STRING: Azure Storage connection string
            AZURE_CONTAINER_NAME: Name of the Azure Storage container
            AZURE_INPUT_PREFIX: Input blob prefix (default: "raw_data/")
            AZURE_OUTPUT_PREFIX: Output blob prefix (default: "processed_data/")
            AZURE_MAX_WORKERS: Maximum number of worker threads (default: 4)
            AZURE_MAX_CONNECTIONS: Maximum concurrent connections (default: 10)
            AZURE_CONNECTION_TIMEOUT: Connection timeout in seconds (default: 20)
            AZURE_READ_TIMEOUT: Read timeout in seconds (default: 60)
            AZURE_MAX_RETRIES: Maximum number of retries (default: 3)
            AZURE_RETRY_DELAY: Delay between retries in seconds (default: 5)
        """
        return cls(
            connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING", ""),
            container_name=os.getenv("AZURE_CONTAINER_NAME", ""),
            input_prefix=os.getenv("AZURE_INPUT_PREFIX", "raw_data/"),
            output_prefix=os.getenv("AZURE_OUTPUT_PREFIX", "processed_data/"),
            max_workers=int(os.getenv("AZURE_MAX_WORKERS", "4")),
            max_concurrent_connections=int(
                os.getenv("AZURE_MAX_CONNECTIONS", "10")
            ),
            connection_timeout=int(os.getenv("AZURE_CONNECTION_TIMEOUT", "20")),
            read_timeout=int(os.getenv("AZURE_READ_TIMEOUT", "60")),
            max_retries=int(os.getenv("AZURE_MAX_RETRIES", "3")),
            retry_delay=int(os.getenv("AZURE_RETRY_DELAY", "5"))
        )
