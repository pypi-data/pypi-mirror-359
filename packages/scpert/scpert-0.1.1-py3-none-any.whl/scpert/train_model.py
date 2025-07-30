import torch
import os
import sys
import numpy as np
from .scpert import scPert
from .ProcePertdata import PertData

def train(data_path, 
          DataName, 
          model_save_path, 
          embedding_path=None,
          epochs=25,
          learning_rate=0.001,
          batch_size=64,
          test_batch_size=64,
          hidden_size=64,
          device='auto',
          proj_name='pertnet',
          split='simulation',
          seed=77,
          weight_bias_track=False):
    """
    Train the scPert model

    Args:
    data_path (str): Path to the data directory
    DataName (str): Name of the dataset
    model_save_path (str): Path to save the trained model
    embedding_path (str): Path to the gene embedding vector file
    epochs (int): Number of training epochs (default: 25)
    learning_rate (float): Learning rate (default: 0.001)
    batch_size (int): Training batch size (default: 64)
    test_batch_size (int): Test batch size (default: 64)
    hidden_size (int): Hidden layer size (default: 64)
    device (str): Device to use ('auto', 'cpu', 'cuda', 'cuda:0', etc.)
    proj_name (str): Project name (default: 'pertnet')
    split (str): Data split method (default: 'simulation')
    seed (int): Random seed (default: 77)
    weight_bias_track (bool): Whether to track weight and bias (default: False)

    Returns:
    str: Path to the saved trained model
    """
    sys.path.append(os.getcwd())
    
    if device == 'auto':
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    print(f"===== Starting training for dataset: {DataName} =====")
    print(f"Using device: {device}")
    print(f"Epochs: {epochs}, Learning rate: {learning_rate}, Batch size: {batch_size}")
    
    if 'cuda' in device:
        torch.cuda.set_device(device)
        print(f"Using GPU: {torch.cuda.get_device_name(torch.cuda.current_device())}")
    
    print("Loading and preprocessing data...")
    pertData = PertData(data_path)
    pertData.load(DataName=DataName)
    pertData.prepare_split(split=split, seed=seed)
    pertData.get_dataloader(
        batch_size=batch_size, 
        test_batch_size=test_batch_size
    )
    
    print("Initializing model...")
    model = scPert(
        pertData, 
        device=device,
        weight_bias_track=weight_bias_track,
        proj_name=proj_name,
        exp_name=f'{proj_name}_{DataName}',
        embedding_path=embedding_path
    )
    
    model.model_initialize(hidden_size=hidden_size)
    
    print(f"Starting training for {epochs} epochs...")
    model.train(epochs=epochs, lr=learning_rate)
    
    model.save_model(model_save_path)
    print(f"Model saved to: {model_save_path}")
    
    print(f"===== Completed training for dataset: {DataName} =====")
    return model_save_path
