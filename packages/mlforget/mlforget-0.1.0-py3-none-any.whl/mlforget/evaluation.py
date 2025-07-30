from sklearn.metrics import r2_score
import torch
from torch import nn

def evaluate_predictions(preds: torch.Tensor, targets: torch.Tensor) -> dict:
    """
    Evaluates model predictions using RMSE, MAE, and R².

    Parameters:
    - preds: Predicted values (Tensor)
    - targets: Ground truth values (Tensor)

    Returns:
    - Dictionary with RMSE, MAE, R²
    """
    rmse = torch.sqrt(nn.functional.mse_loss(preds, targets)).item()
    mae = nn.functional.l1_loss(preds, targets).item()
    r2 = r2_score(targets.detach().cpu().numpy(), preds.detach().cpu().numpy())

    return {"RMSE": rmse, "MAE": mae, "R2": r2}

def compare_models(preds1, preds2):
    """
    Compares two models on the same dataset using RMSE and MAE.

    Parameters:
    - model_a: First PyTorch model.
    - model_b: Second PyTorch model.
    - data_loader: DataLoader with test/val data.
    - device: "cpu" or "cuda".

    Returns:
    - Dictionary with RMSE and MAE between model predictions.
    """
    delta = torch.norm(preds1 - preds2).item()
    return {"L2_Delta": delta}

