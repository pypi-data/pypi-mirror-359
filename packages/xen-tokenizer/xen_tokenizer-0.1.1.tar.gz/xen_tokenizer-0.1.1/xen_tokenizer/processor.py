"""
Azure Blob Storage processor for handling parquet files with XenTokenizer.
"""

import os
import logging
import pyarrow.parquet as pq
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from azure.storage.blob import BlobServiceClient, ContainerClient

from .tokenizer import XenTokenizerFast
from .config import AzureConfig, TokenizerConfig

logger = logging.getLogger(__name__)


class AzureParquetProcessor:
    """Process parquet files from Azure Blob Storage using XenTokenizer."""
    
    def __init__(
        self,
        tokenizer: Optional[XenTokenizerFast] = None,
        tokenizer_config: Optional[TokenizerConfig] = None,
        azure_config: Optional[AzureConfig] = None,
        **kwargs
    ):
        """
        Initialize the Azure parquet processor.
        
        Args:
            tokenizer: Optional pre-initialized tokenizer
            tokenizer_config: Configuration for the tokenizer
            azure_config: Configuration for Azure Blob Storage
            **kwargs: Additional arguments for AzureConfig
        """
        # Initialize tokenizer
        if tokenizer is None:
            tokenizer_config = tokenizer_config or TokenizerConfig()
            self.tokenizer = XenTokenizerFast(
                tokenizer_file="tokenizer.json",
                config=tokenizer_config
            )
        else:
            self.tokenizer = tokenizer
        
        # Initialize Azure config
        if azure_config is None:
            self.azure_config = AzureConfig(**kwargs) if kwargs else AzureConfig.from_env()
        else:
            self.azure_config = azure_config
        
        # Initialize Azure clients
        self.blob_service = BlobServiceClient.from_connection_string(
            self.azure_config.connection_string
        )
        self.container_client = self.blob_service.get_container_client(
            self.azure_config.container_name
        )
        
        # Create local directories
        self.local_dir = Path("./data")
        self.input_dir = self.local_dir / "input"
        self.output_dir = self.local_dir / "output"
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def list_parquet_files(self) -> List[Dict[str, Any]]:
        """List all parquet files in the input prefix."""
        try:
            return [
                {
                    "name": blob.name,
                    "size": blob.size,
                    "last_modified": blob.last_modified
                }
                for blob in self.container_client.list_blobs(
                    name_starts_with=self.azure_config.input_prefix
                )
                if blob.name.endswith('.parquet')
            ]
        except Exception as e:
            logger.error(f"Error listing parquet files: {e}")
            return []
    
    def download_file(self, blob_name: str) -> Optional[Path]:
        """Download a file from Azure Blob Storage."""
        try:
            local_path = self.input_dir / Path(blob_name).name
            os.makedirs(local_path.parent, exist_ok=True)
            
            blob_client = self.container_client.get_blob_client(blob_name)
            with open(local_path, "wb") as f:
                f.write(blob_client.download_blob().readall())
            
            return local_path
        except Exception as e:
            logger.error(f"Error downloading {blob_name}: {e}")
            return None
    
    def upload_file(self, local_path: Path, blob_name: str) -> bool:
        """Upload a file to Azure Blob Storage."""
        try:
            output_blob = f"{self.azure_config.output_prefix}{blob_name}"
            with open(local_path, "rb") as data:
                self.container_client.upload_blob(
                    name=output_blob,
                    data=data,
                    overwrite=True
                )
            return True
        except Exception as e:
            logger.error(f"Error uploading {blob_name}: {e}")
            return False
    
    def process_parquet(self, file_path: Path) -> Optional[Path]:
        """Process a single parquet file."""
        try:
            # Read parquet file
            table = pq.read_table(file_path)
            df = table.to_pandas()
            
            # Process text column (adjust column name as needed)
            if 'text' not in df.columns:
                logger.warning(f"No 'text' column found in {file_path}")
                return None
            
            # Tokenize text
            tokenized_data = []
            for text in df['text']:
                if not isinstance(text, str):
                    continue
                
                tokens = self.tokenizer.encode(
                    text,
                    max_length=self.tokenizer.model_max_length,
                    truncation=True,
                    return_attention_mask=True
                )
                tokenized_data.append({
                    'input_ids': tokens['input_ids'],
                    'attention_mask': tokens['attention_mask']
                })
            
            # Save tokenized data
            output_path = self.output_dir / f"tokenized_{file_path.name}"
            pd.DataFrame(tokenized_data).to_parquet(output_path)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return None
    
    def process_all(self) -> None:
        """Process all parquet files in the input prefix."""
        # List all parquet files
        files = self.list_parquet_files()
        if not files:
            logger.warning("No parquet files found to process.")
            return
        
        logger.info(f"Found {len(files)} parquet files to process.")
        
        # Process files in parallel
        with ThreadPoolExecutor(max_workers=self.azure_config.max_workers) as executor:
            futures = []
            
            for file_info in files:
                blob_name = file_info['name']
                futures.append(executor.submit(self._process_single_file, blob_name))
            
            # Track progress
            for future in tqdm(
                as_completed(futures),
                total=len(futures),
                desc="Processing files"
            ):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error in processing: {e}")
    
    def _process_single_file(self, blob_name: str) -> None:
        """Process a single file (helper method for parallel processing)."""
        try:
            # Download file
            local_path = self.download_file(blob_name)
            if not local_path:
                return
            
            # Process file
            output_path = self.process_parquet(local_path)
            if not output_path:
                return
            
            # Upload result
            self.upload_file(output_path, output_path.name)
            
            # Clean up local files
            local_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)
            
        except Exception as e:
            logger.error(f"Error processing {blob_name}: {e}")
