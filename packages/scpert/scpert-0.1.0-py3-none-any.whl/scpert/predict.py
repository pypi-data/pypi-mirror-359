import torch
import pandas as pd
import scanpy as sc
from .scpert import scPert
from .ProcePertdata import PertData

def predict(model_path, data_path, pert_file_path, 
            model_name='norman', device='auto',
            embedding_path=None, output_dir='./results'):
    """
    Perform perturbation prediction using a pre-trained model
    Args:
    model_path (str): Path to the pre-trained model
    data_path (str): Path to the input data directory
    pert_file_path (str): Path to the perturbation gene file
    model_name (str): Model name (default: 'norman')
    device (str): Device to use ('auto', 'cpu', 'cuda', 'cuda:0', etc.)
    embedding_path (str): Path to the gene embedding vector file
    output_dir (str): Output directory for results
    Returns:
    adata: AnnData object containing the prediction results
    """
    if device == 'auto':
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    if 'cuda' in device:
        torch.cuda.set_device(device)
        print(f"Using device: {torch.cuda.get_device_name(torch.cuda.current_device())}")

    pertData = PertData(data_path)
    pertData.load(DataName=model_name)
    pertData.prepare_split(split='no_test', seed=77)
    pertData.get_dataloader(batch_size=128, test_batch_size=128)
    model = scPert(pertData, 
                   device=device, 
                   weight_bias_track=False, 
                   proj_name=model_name, 
                   exp_name=model_name,
                   embedding_path=embedding_path)
    model.load_pretrained(model_path)
    
    pert_file = pd.read_csv(pert_file_path)
    pert_file = pert_file.fillna('ctrl')
    
    pert_list = []
    for _, row in pert_file.iterrows():
        g1, g2 = row['gene1'], row['gene2']
        pert_list.append(f"{g1}+{g2}")
    
    print(f"Predicting for {len(pert_list)} perturbations...")
    
    with torch.cuda.device(device) if 'cuda' in device else nullcontext():
        prediction = model.predict(pert_list)
    if output_dir:
        import os
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{model_name}_predictions.h5ad")
        prediction.write(output_path)
        print(f"Predictions saved to: {output_path}")
    
    return prediction

class nullcontext:
    def __enter__(self):
        return None
    def __exit__(self, *args):
        pass