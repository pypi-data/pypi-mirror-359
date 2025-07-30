import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from typing import Tuple, Callable

from . import data_utils as data
from .evaluation import evaluate_predictions

def train_model(model: nn.Module,
                train_loader: DataLoader,
                val_loader: DataLoader,
                loss_fn: Callable,
                optimizer: optim.Optimizer,
                lr: float = 0.001,
                num_epochs: int = 10,
                device: str = "cpu") -> Tuple[nn.Module, list]:
    """
    Trains a PyTorch model using training and optional validation data.

    Parameters:
    - model: PyTorch model instance.
    - train_loader: DataLoader for training data.
    - val_loader: Optional DataLoader for validation.
    - epochs: Number of training epochs.
    - device: Device to use ("cpu" or "cuda").
    - lr: Learning rate.
    - verbose: If True, prints loss per epoch.

    Returns:
    - (model, train_losses, val_losses)
    """
    model = model.to(device)
    val_losses = []

    if loss_fn is None:
        loss_fn = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    for epoch in range(int(num_epochs)):
        model.train()
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)

            optimizer.zero_grad()
            output = model(X_batch)
            loss = loss_fn(output, y_batch)
            loss.backward()
            optimizer.step()

        # Evaluation
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for X_val, y_val in val_loader:
                X_val, y_val = X_val.to(device), y_val.to(device)
                val_output = model(X_val)
                val_loss += loss_fn(val_output, y_val).item()

        val_loss /= len(val_loader)
        val_losses.append(val_loss)
        print(f"Epoch {epoch+1}/{num_epochs}, Val Loss: {val_loss:.4f}")

    return model, val_losses

def evaluate_on_loader(model: nn.Module,
                        data_loader: DataLoader,
                        device: str = "cpu") -> dict:
    """
    Evaluates a model using a DataLoader and loss function.

    Parameters:
    - model: Trained PyTorch model.
    - loader: DataLoader with evaluation data.
    - loss_fn: Loss function used for evaluation.
    - device: Device to run on.

    Returns:
    - Dictionary with RMSE, MAE, R².
    """
    model.eval()
    all_preds, all_targets = [], []
    with torch.no_grad():
        for X_batch, y_batch in data_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            preds = model(X_batch)
            all_preds.append(preds.cpu())
            all_targets.append(y_batch.cpu())

    all_preds = torch.cat(all_preds)
    all_targets = torch.cat(all_targets)
    return evaluate_predictions(all_preds, all_targets)
