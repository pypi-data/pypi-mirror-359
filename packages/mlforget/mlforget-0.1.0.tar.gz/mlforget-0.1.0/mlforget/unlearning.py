from . import training, model_utils, data_utils as data_utils

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from torch.utils.data import random_split
from typing import Callable, Tuple, List


###################################
# Exact Unlearning and Retraining #
###################################

def retrain_model(model_fn: Callable,
                  train_loader: DataLoader,
                  val_loader: DataLoader,
                  loss_fn: Callable,
                  optimizer_fn: Callable,
                  num_epochs: int = 10,
                  device: str = "cpu") -> Tuple[nn.Module, list]:
    """
    Fully retrains a model from scratch on a new training set (used for exact unlearning).

    Parameters:
    - model_fn: Callable that returns a fresh, untrained model
    - train_loader: New training DataLoader (with data to forget removed)
    - val_loader: Validation DataLoader
    - loss_fn: Loss function
    - optimizer_fn: Function that returns a new optimizer given a model
    - num_epochs: Number of epochs
    - device: "cpu" or "cuda"

    Returns:
    - Trained model and validation loss history
    """
    model = model_fn()
    optimizer = optimizer_fn(model)
    return training.train_model(model, train_loader, val_loader, loss_fn, optimizer, num_epochs, device)

##################################
# SISA Partitioning and Training #
##################################

def split_into_shards_and_slices(data, targets, num_shards=5, num_slices=3, seed=42):
    """
    Splits the dataset into shards and slices for SISA training.
    Supports both NumPy arrays and PyTorch tensors.
    """
    import torch

    np.random.seed(seed)
    indices = np.random.permutation(len(data))

    if isinstance(data, torch.Tensor):
        data = data[indices]
        targets = targets[indices]
    else:
        data = data[indices, :]
        targets = targets[indices]

    shard_size = len(data) // num_shards
    shards = []

    for i in range(num_shards):
        start_idx = i * shard_size
        end_idx = (i + 1) * shard_size if i < num_shards - 1 else len(data)
        shard_data = data[start_idx:end_idx]
        shard_targets = targets[start_idx:end_idx]
        slice_size = len(shard_data) // num_slices
        slices = []
        for j in range(num_slices):
            s_start = j * slice_size
            s_end = (j + 1) * slice_size if j < num_slices - 1 else len(shard_data)
            slices.append((shard_data[s_start:s_end], shard_targets[s_start:s_end]))

        shards.append(slices)

    return shards

def train_sisa_models(shards, input_size, hidden_size=64, num_epochs=10, batch_size=128, learning_rate=1e-3, device="cpu"):
    """
    Trains one model per slice per shard and returns a dictionary of trained models.
    """
    sisa_models = {}

    for shard_idx, shard in enumerate(shards):
        for slice_idx, (slice_data, slice_targets) in enumerate(shard):
            print(f"Training model for Shard {shard_idx}, Slice {slice_idx}")

            model = model_utils.MyLSTM(input_size=input_size, hidden_size=hidden_size).to(device)

            dataset = torch.utils.data.TensorDataset(slice_data, slice_targets)

            loss_fn = nn.MSELoss()
            optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

            train_size = int(0.8 * len(dataset))
            val_size = len(dataset) - train_size
            train_data, val_data = random_split(dataset, [train_size, val_size])

            train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True)
            val_loader = DataLoader(val_data, batch_size=batch_size)

            training.train_model(model, train_loader, num_epochs=num_epochs, lr=learning_rate, device=device, loss_fn=loss_fn, optimizer=optimizer, val_loader=val_loader)

            sisa_models[(shard_idx, slice_idx)] = model

    return sisa_models

def unlearn_with_sisa(shards, sisa_models, forget_data, input_size, hidden_size=64, num_epochs=10, batch_size=128, learning_rate=1e-3, device="cpu", rtol=1e-3, atol=1e-3):
    """
    Retrains only the slices containing any rows from forget_data using fuzzy matching.
    Logs forgotten rows and prediction deltas.
    """
    updated_models = sisa_models.copy()

    for shard_idx, shard in enumerate(shards):
        for slice_idx, (slice_data, slice_targets) in enumerate(shard):
            if len(slice_data) == 0:
                continue

            if (shard_idx, slice_idx) not in sisa_models:
                print(f"Skipping Shard {shard_idx}, Slice {slice_idx} - no model found")
                continue

            if len(slice_data) < 2:
                print(f"Skipping tiny slice ({shard_idx}, {slice_idx})")
                continue

            forget_mask = torch.zeros(len(slice_data), dtype=torch.bool)

            # Precompute forget row set
            forget_row_set = {tuple(row.squeeze().tolist()) for row in forget_data}
            for i, row in enumerate(slice_data):
                if tuple(row.squeeze().tolist()) in forget_row_set:
                    forget_mask[i] = True

            if forget_mask.any():
                matched_indices = torch.nonzero(forget_mask).flatten().tolist()
                print(f"\n Retraining Shard {shard_idx}, Slice {slice_idx}")
                print(f" Matched {len(matched_indices)} forgotten datapoint(s)")

                forget_slice_data = slice_data[forget_mask]
                model_before = sisa_models[(shard_idx, slice_idx)]
                model_before.eval()
                with torch.no_grad():
                    preds_before = model_before(forget_slice_data.to(device)).cpu()

                # Filter to kept data
                kept_data = slice_data[~forget_mask]
                kept_targets = slice_targets[~forget_mask]

                dataset = TensorDataset(kept_data, kept_targets)
                train_size = int(0.8 * len(dataset))
                val_size = len(dataset) - train_size
                train_set, val_set = random_split(dataset, [train_size, val_size])

                train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True)
                val_loader = DataLoader(val_set, batch_size=batch_size)

                model = model_utils.MyLSTM(input_size=input_size, hidden_size=hidden_size).to(device)
                optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
                loss_fn = nn.MSELoss()

                trained_model, _ = training.train_model(
                    model, train_loader, val_loader,
                    loss_fn=loss_fn,
                    optimizer=optimizer,
                    num_epochs=num_epochs,
                    device=device
                )

                updated_models[(shard_idx, slice_idx)] = trained_model

                trained_model.eval()
                with torch.no_grad():
                    preds_after = trained_model(forget_slice_data.to(device)).cpu()

                delta = torch.norm(preds_before - preds_after).item()
                print(f" Prediction change on forgotten data: {delta:.4f}")

    return updated_models

def predict_with_sisa(sisa_models, X, device="cpu"):
    """Aggregate predictions from all SISA slice models."""
    model_preds = []
    for model in sisa_models.values():
        model.eval()
        with torch.no_grad():
            preds = model(X.to(device)).cpu()
            model_preds.append(preds)
    # Average predictions from all models
    ensemble_preds = torch.stack(model_preds).mean(dim=0)
    return ensemble_preds

##########################
# Knowledge Distillation #
##########################

def train_teacher_model(model, train_loader, val_loader, num_epochs, lr, device):
    """Trains the teacher model on the full dataset using standard training."""
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()
    return training.train_model(model, train_loader, val_loader, loss_fn, optimizer, num_epochs=num_epochs, device=device)

def train_student_model(student_model, teacher_model, train_loader, val_loader, num_epochs, lr, device, alpha=0.5):
    """
    Trains a student model using knowledge distillation.
    Combines soft labels from the teacher and hard labels from the true data.
    """
    optimizer = torch.optim.Adam(student_model.parameters(), lr=lr)
    student_model.train()
    teacher_model.eval()

    loss_fn_true = nn.MSELoss()
    loss_fn_soft = nn.MSELoss()  # Could also use KLDivLoss if using log-probabilities

    for epoch in range(num_epochs):
        for x_batch, y_batch in train_loader:
            x_batch, y_batch = x_batch.to(device), y_batch.to(device)

            with torch.no_grad():
                teacher_preds = teacher_model(x_batch)

            student_preds = student_model(x_batch)

            loss_true = loss_fn_true(student_preds, y_batch)
            loss_soft = loss_fn_soft(student_preds, teacher_preds)

            loss = alpha * loss_soft + (1 - alpha) * loss_true

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        student_model.eval()
        val_losses = []
        with torch.no_grad():
            for x_val, y_val in val_loader:
                x_val, y_val = x_val.to(device), y_val.to(device)
                val_preds = student_model(x_val)
                val_loss = loss_fn_true(val_preds, y_val)
                val_losses.append(val_loss.item())
        student_model.train()

        avg_val_loss = sum(val_losses) / len(val_losses)
        print(f"Epoch {epoch+1}/{num_epochs}, Val Loss: {avg_val_loss:.4f}")

    return student_model