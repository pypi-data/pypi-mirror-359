"""
Utility functions for HuggingFace datasets to avoid import conflicts
"""

def load_dataset_builder(dataset_name: str, **kwargs):
    """Load a dataset builder from HuggingFace datasets"""
    from datasets import load_dataset_builder as hf_load_dataset_builder
    return hf_load_dataset_builder(dataset_name, **kwargs)

def load_dataset(dataset_name: str, **kwargs):
    """Load a dataset from HuggingFace datasets"""
    from datasets import load_dataset as hf_load_dataset
    return hf_load_dataset(dataset_name, **kwargs)

def get_dataset_config_names(dataset_name: str, **kwargs):
    """Get config names for a HuggingFace dataset"""
    from datasets import get_dataset_config_names as hf_get_dataset_config_names
    return hf_get_dataset_config_names(dataset_name, **kwargs)

def list_datasets(**kwargs):
    """List available datasets from HuggingFace"""
    from datasets import list_datasets as hf_list_datasets
    return hf_list_datasets(**kwargs)

def Dataset(*args, **kwargs):
    """Create a Dataset from HuggingFace datasets"""
    from datasets import Dataset as HFDataset
    return HFDataset(*args, **kwargs) 