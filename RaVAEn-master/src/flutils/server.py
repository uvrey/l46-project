from omegaconf import DictConfig
from collections import OrderedDict
from src.flutils.client import SimpleVAEModel
import pytorch_lightning as pl
import torch

def get_on_fit_config(cfg: DictConfig):
    def fit_config_fn(server_round: int):
        return {'lr': cfg.lr, 
                'momentum': cfg.momentum, 
                'local_epochs': cfg.local_epochs}
    return fit_config_fn

def get_evaluate_fn(input_shape, testloader):
    def evaluate_fn(server_round: int, parameters, config):
        # TODO CHANGE
        model = SimpleVAEModel(input_shape=input_shape, latent_dim = 128, vis_channels = [2,1,0])
        
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        
        params_dict = zip(model.state_dict().keys(), parameters)
        state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
        model.load_state_dict(state_dict, strict=True)
        
        trainer = pl.Trainer()
        results = trainer.test(model, testloader)
        
        loss = results[0]["test_loss"]
        accuracy = results[0]["accuracy"]
        
        return loss, {'accuracy': accuracy}
    
    return evaluate_fn