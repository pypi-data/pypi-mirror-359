"""
XenTokeniser - Core Tokenizer Implementation

This module provides the XenTokenizerFast class, a high-performance tokenizer
built on top of Hugging Face's PreTrainedTokenizerFast, with additional
optimizations and features for XenArcAI's NLP pipelines.
"""

import os
import json
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple, overload

import torch
from transformers import PreTrainedTokenizerFast, BatchEncoding
from filelock import FileLock

from .config import TokenizerConfig
from .exceptions import TokenizerError, TokenizerWarning


class XenTokenizerFast(PreTrainedTokenizerFast):
    """
    A high-performance tokenizer optimized for XenArcAI's NLP pipelines.
    
    This tokenizer extends Hugging Face's PreTrainedTokenizerFast with additional
    optimizations, better error handling, and integration with XenArcAI's infrastructure.
    
    Args:
        tokenizer_file: Path to the tokenizer.json file or directory containing tokenizer files
        config: Optional TokenizerConfig instance for custom configuration
        **kwargs: Additional arguments for PreTrainedTokenizerFast
    """
    
    def __init__(
        self,
        tokenizer_file: Union[str, os.PathLike],
        config: Optional[TokenizerConfig] = None,
        **kwargs
    ) -> None:
        # Convert string paths to Path objects
        tokenizer_path = Path(tokenizer_file)
        
        # Handle directory input (look for tokenizer.json)
        if tokenizer_path.is_dir():
            tokenizer_file = str(tokenizer_path / "tokenizer.json")
            if not os.path.exists(tokenizer_file):
                raise FileNotFoundError(
                    f"tokenizer.json not found in directory: {tokenizer_path}"
                )
        
        # Set default config if not provided
        self.config = config or TokenizerConfig()
        
        try:
            # Initialize the parent class with file lock to prevent race conditions
            with FileLock(f"{tokenizer_file}.lock"):
                super().__init__(
                    tokenizer_file=tokenizer_file,
                    model_max_length=self.config.max_length,
                    **kwargs
                )
                
                # Add special tokens if not already present
                self._add_special_tokens()
                
                # Initialize device for tensor operations
                self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                
        except Exception as e:
            raise TokenizerError(
                f"Failed to initialize tokenizer from {tokenizer_file}"
            ) from e
    
    def _add_special_tokens(self) -> None:
        """Add special tokens to the tokenizer if they don't exist."""
        special_tokens_dict = {}
        
        # Define required special tokens
        special_tokens = {
            "pad_token": self.config.pad_token,
            "eos_token": self.config.eos_token,
            "bos_token": self.config.bos_token,
            "unk_token": self.config.unk_token,
        }
        
        # Add tokens that aren't already present
        for key, token in special_tokens.items():
            if getattr(self, key, None) is None and token is not None:
                special_tokens_dict[key] = token
        
        # Update tokenizer with special tokens
        if special_tokens_dict:
            self.add_special_tokens(special_tokens_dict)
            
            # Verify all special tokens are set
            for key, token in special_tokens.items():
                if getattr(self, key, None) is None:
                    warnings.warn(
                        f"Failed to set {key} token",
                        TokenizerWarning,
                        stacklevel=2
                    )
        if self.eos_token is None:
            special_tokens_dict["eos_token"] = self.config.eos_token
    
    def save_pretrained(self, save_directory: Union[str, os.PathLike], **kwargs) -> None:
        """
        Save the tokenizer to the specified directory.
        
        Args:
            save_directory: Directory to save the tokenizer files
            **kwargs: Additional arguments for PreTrainedTokenizerFast.save_pretrained
            
        Raises:
            TokenizerError: If saving fails
        """
        save_path = Path(save_directory)
        save_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # Save tokenizer files with file lock
            with FileLock(str(save_path / ".lock")):
                super().save_pretrained(str(save_path), **kwargs)
                
                # Save the config
                config_path = save_path / "tokenizer_config.json"
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(self.config.to_dict(), f, indent=2, ensure_ascii=False)
                    
        except Exception as e:
            raise TokenizerError(f"Failed to save tokenizer to {save_path}") from e
    
    @classmethod
    def from_pretrained(
        cls,
        pretrained_model_name_or_path: Union[str, os.PathLike],
        *args,
        **kwargs
    ) -> 'XenTokenizerFast':
        """
        Load a tokenizer from a pretrained model or path.
        
        Args:
            pretrained_model_name_or_path: Path to the tokenizer directory or model name
            *args: Additional arguments for PreTrainedTokenizerFast.from_pretrained
            **kwargs: Additional keyword arguments
            
        Returns:
            XenTokenizerFast: Loaded tokenizer instance
            
        Raises:
            TokenizerError: If loading fails
        """
        try:
            path = Path(pretrained_model_name_or_path)
            
            # Handle directory input
            if path.is_dir():
                tokenizer_file = path / "tokenizer.json"
                if not tokenizer_file.exists():
                    raise FileNotFoundError(
                        f"tokenizer.json not found in {path}"
                    )
                
                # Load config if exists
                config_path = path / "tokenizer_config.json"
                if config_path.exists():
                    with open(config_path, "r", encoding="utf-8") as f:
                        config_dict = json.load(f)
                        kwargs["config"] = TokenizerConfig(**config_dict)
            
            # Initialize with file lock
            with FileLock(f"{pretrained_model_name_or_path}.lock"):
                return super().from_pretrained(
                    str(pretrained_model_name_or_path),
                    *args,
                    **kwargs
                )
                
        except Exception as e:
            raise TokenizerError(
                f"Failed to load tokenizer from {pretrained_model_name_or_path}"
            ) from e
    
    def encode_batch(
        self,
        texts: List[str],
        max_length: Optional[int] = None,
        padding: Union[bool, str] = True,
        truncation: Union[bool, str] = True,
        return_tensors: Optional[str] = None,
        **kwargs
    ) -> BatchEncoding:
        """
        Encode a batch of texts with optimized batching.
        
        Args:
            texts: List of texts to encode
            max_length: Maximum length of the returned sequence
            padding: Padding strategy
            truncation: Truncation strategy
            return_tensors: Type of tensors to return ('pt', 'tf', 'np')
            **kwargs: Additional arguments for batch_encode_plus
            
        Returns:
            BatchEncoding: Encoded batch
        """
        if max_length is None:
            max_length = self.model_max_length
            
        return self.batch_encode_plus(
            texts,
            max_length=max_length,
            padding=padding,
            truncation=truncation,
            return_tensors=return_tensors or "pt",
            **kwargs
        )
    
    def parallelize(self) -> None:
        """Enable multi-GPU processing if available."""
        if torch.cuda.device_count() > 1:
            self.model_parallel = True
            self.device_map = {
                i: f"cuda:{i}" for i in range(torch.cuda.device_count())
            }
            self.device = torch.device("cuda:0")
