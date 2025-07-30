"""
Tests for XenTokenizer.
"""

import os
import tempfile
import unittest
from pathlib import Path

from xen_tokenizer import XenTokenizerFast, TokenizerConfig


class TestXenTokenizer(unittest.TestCase):
    """Test cases for XenTokenizer."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        cls.test_dir = tempfile.mkdtemp()
        
        # Create a sample tokenizer config
        cls.config = TokenizerConfig(
            max_length=512,
            pad_token="[PAD]",
            eos_token="</s>",
            unk_token="[UNK]",
            bos_token="<s>"
        )
        
        # Path to a test tokenizer file (you'll need to provide this)
        cls.tokenizer_path = "tokenizer.json"
    
    def test_tokenizer_initialization(self):
        """Test tokenizer initialization."""
        # Test initialization with config
        tokenizer = XenTokenizerFast(
            tokenizer_file=self.tokenizer_path,
            config=self.config
        )
        
        self.assertIsNotNone(tokenizer)
        self.assertEqual(tokenizer.model_max_length, self.config.max_length)
        self.assertEqual(tokenizer.pad_token, self.config.pad_token)
        self.assertEqual(tokenizer.eos_token, self.config.eos_token)
    
    def test_tokenizer_encoding(self):
        """Test tokenizer encoding and decoding."""
        tokenizer = XenTokenizerFast(tokenizer_file=self.tokenizer_path)
        
        # Test basic encoding/decoding
        text = "Hello, world!"
        encoded = tokenizer.encode(text)
        decoded = tokenizer.decode(encoded)
        
        self.assertIsInstance(encoded, list)
        self.assertGreater(len(encoded), 0)
        self.assertEqual(decoded, text)
    
    def test_special_tokens(self):
        """Test special tokens handling."""
        tokenizer = XenTokenizerFast(tokenizer_file=self.tokenizer_path)
        
        # Test special tokens are in the vocabulary
        vocab = tokenizer.get_vocab()
        self.assertIn("<s>", vocab)
        self.assertIn("</s>", vocab)
        self.assertIn("<pad>", vocab)
        self.assertIn("<unk>", vocab)
        
        # Verify the special tokens mapping
        self.assertEqual(tokenizer.pad_token, "<pad>")
        self.assertEqual(tokenizer.unk_token, "<unk>")
        self.assertEqual(tokenizer.eos_token, "</s>")
        self.assertEqual(tokenizer.bos_token, "<s>")
    
    def test_save_and_load(self):
        """Test saving and loading the tokenizer."""
        # Initialize tokenizer
        tokenizer = XenTokenizerFast(
            tokenizer_file=self.tokenizer_path,
            config=self.config
        )
        
        # Save to a temporary directory
        save_dir = os.path.join(self.test_dir, "test_tokenizer")
        tokenizer.save_pretrained(save_dir)
        
        # Check files were saved
        self.assertTrue(os.path.exists(os.path.join(save_dir, "tokenizer.json")))
        self.assertTrue(os.path.exists(os.path.join(save_dir, "config.json")))
        self.assertTrue(os.path.exists(os.path.join(save_dir, "tokenizer_config.json")))
        
        # Load the saved tokenizer
        loaded_tokenizer = XenTokenizerFast.from_pretrained(save_dir)
        
        # Test loaded tokenizer
        text = "Test save and load functionality"
        self.assertEqual(
            tokenizer.encode(text),
            loaded_tokenizer.encode(text)
        )


if __name__ == "__main__":
    unittest.main()
