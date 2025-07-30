from .model_utils import MyLSTM
from .training import train_model
from .unlearning import split_into_shards_and_slices, train_sisa_models, unlearn_with_sisa, predict_with_sisa, train_teacher_model, train_student_model
from .data_utils import select_forget_set
from .evaluation import evaluate_predictions

import torch
from torch.utils.data import DataLoader, TensorDataset, random_split
import torch.nn as nn
import torch.optim as optim


def run_sisa_unlearning(X, y, df, input_cols, target_col, id_column, id_values, device, num_shards=3, num_slices=2, num_epochs=5):
    """
    Runs SISA unlearning (sharded, sliced retraining on retained data).

    Parameters:
    - X: Feature tensor.
    - y: Target tensor.
    - df: Original DataFrame.
    - input_cols: List of input feature column names.
    - target_col: Name of the target column.
    - id_column: Column used to identify forget data.
    - forget_ids: List of IDs to forget.
    - config: Training configuration.
    - device: Device for training.

    Returns:
    - Dictionary with models and evaluation metrics.
    """
    print("\n Running SISA Unlearning")
    forget_df, retain_df = select_forget_set(df, id_column, id_values)

    if forget_df.empty:
        raise ValueError(f"No matching rows found for ids {id_values} in column '{id_column}' after preprocessing.")

    print(f" Forget set size: {len(forget_df)}")
    print(f" Retain set size: {len(retain_df)}")

    forget_data = torch.tensor(forget_df[input_cols].values, dtype=torch.float32).unsqueeze(1)
    forget_targets = torch.tensor(forget_df[target_col].values, dtype=torch.float32).view(-1, 1)

    print(" Splitting data into shards and slices...")
    shards = split_into_shards_and_slices(X, y,num_shards=num_shards, num_slices=num_slices)

    print(" Training initial SISA models on full data...")
    assert X.dim() == 3, f"Expected 3D input (batch, seq_len, features), got {X.shape}"
    assert y.dim() == 2, f"Expected 2D target tensor (batch, 1), got {y.shape}"

    sisa_models = train_sisa_models(
        shards=shards,
        input_size=X.shape[2],
        hidden_size=64,
        num_epochs=num_epochs,
        batch_size=64,
        device=device
    )

    pre_preds = predict_with_sisa(sisa_models, X, device)
    pre_metrics = evaluate_predictions(pre_preds.cpu(), y)

    print(" Performing unlearning...")
    updated_models = unlearn_with_sisa(
        shards=shards,
        sisa_models=sisa_models,
        forget_data=forget_data,
        input_size=X.shape[2],
        hidden_size=64,
        num_epochs=num_epochs,
        batch_size=64,
        learning_rate=0.001,
        device=device
    )

    post_preds = predict_with_sisa(updated_models, X, device)
    post_metrics = evaluate_predictions(post_preds.cpu(), y)

    return {
        "pre_metrics": pre_metrics,
        "post_metrics": post_metrics,
        "models": updated_models
    }

def run_exact_retraining(X, y, df, input_cols, target_col, id_column, id_values, device, num_epochs=5):
    """
    Performs full retraining on retained data to simulate exact unlearning.

    Parameters:
    - X: Full input feature tensor.
    - y: Full target tensor.
    - df: Original DataFrame.
    - input_cols: List of input feature names.
    - target_col: Target column name.
    - id_column: Column to identify forget IDs.
    - forget_ids: List of IDs to remove.
    - device: Training device.

    Returns:
    - Dictionary with retrained model and evaluation metrics.
    """
    print("\n Running Exact Retraining")
    forget_df, retain_df = select_forget_set(df, id_column, id_values)

    print(f" Forget set size: {len(forget_df)}")
    print(f" Retain set size: {len(retain_df)}")

    retain_data = torch.tensor(retain_df[input_cols].values, dtype=torch.float32).unsqueeze(1)
    retain_targets = torch.tensor(retain_df[target_col].values, dtype=torch.float32).view(-1, 1)

    assert X.dim() == 3, f"Expected 3D input (batch, seq_len, features), got {X.shape}"
    assert y.dim() == 2, f"Expected 2D target tensor (batch, 1), got {y.shape}"

    print(" Training full model on all data...")
    full_model = MyLSTM(X.shape[2], 64).to(device)
    full_loader = DataLoader(TensorDataset(X, y), batch_size=64, shuffle=True)
    full_val_loader = DataLoader(TensorDataset(X, y), batch_size=64)
    full_model, _ = train_model(full_model, full_loader, full_val_loader, nn.MSELoss(), optim.Adam(full_model.parameters(), lr=0.001), num_epochs=num_epochs, device=device)
    full_preds = full_model(X.to(device)).cpu()
    full_metrics = evaluate_predictions(full_preds, y)

    print(" Retraining model on retained data only...")
    model = MyLSTM(X.shape[2], 64).to(device)
    dataset = TensorDataset(retain_data, retain_targets)
    train_set, val_set = random_split(dataset, [int(0.8 * len(dataset)), len(dataset) - int(0.8 * len(dataset))])
    train_loader = DataLoader(train_set, batch_size=64, shuffle=True)
    val_loader = DataLoader(val_set, batch_size=64)
    model, _ = train_model(model, train_loader, val_loader, nn.MSELoss(), optim.Adam(model.parameters(), lr=0.001), num_epochs=num_epochs, device=device)
    post_preds = model(X.to(device)).cpu()
    post_metrics = evaluate_predictions(post_preds, y)

    return {
        "pre_metrics": full_metrics,
        "post_metrics": post_metrics,
        "model": model
    }

def run_knowledge_distillation(X, y, df, input_cols, target_col, id_column, id_values, device, num_epochs=5):
    """
    Runs knowledge distillation by training a student model on soft targets.

    Parameters:
    - X: Full input tensor.
    - y: Target tensor.
    - df: Original dataset.
    - input_cols: Features used in training.
    - target_col: Output variable.
    - id_column: Column to identify forget samples.
    - forget_ids: List of values to forget.
    - device: Device to run the distillation on.

    Returns:
    - Dictionary with distilled model and post-unlearning metrics.
    """
    print("\n Running Knowledge Distillation")
    forget_df, retain_df = select_forget_set(df, id_column, id_values)

    print(f" Forget set size: {len(forget_df)}")
    print(f" Retain set size: {len(retain_df)}")

    retain_data = torch.tensor(retain_df[input_cols].values, dtype=torch.float32).unsqueeze(1)
    retain_targets = torch.tensor(retain_df[target_col].values, dtype=torch.float32).view(-1, 1)

    assert X.dim() == 3, f"Expected 3D input (batch, seq_len, features), got {X.shape}"
    assert y.dim() == 2, f"Expected 2D target tensor (batch, 1), got {y.shape}"

    print(" Training teacher model on full data...")
    teacher_model = MyLSTM(X.shape[2], 64).to(device)
    dataset = TensorDataset(X, y)
    train_set, val_set = random_split(dataset, [int(0.8 * len(dataset)), len(dataset) - int(0.8 * len(dataset))])
    train_loader = DataLoader(train_set, batch_size=64, shuffle=True)
    val_loader = DataLoader(val_set, batch_size=64)
    teacher_model, _ = train_teacher_model(teacher_model, train_loader, val_loader, num_epochs=num_epochs, lr=0.001, device=device)

    print(" Training student model on retained data using distillation...")
    student_model = MyLSTM(X.shape[2], 64).to(device)
    retain_dataset = TensorDataset(retain_data, retain_targets)
    retain_train, retain_val = random_split(retain_dataset, [int(0.8 * len(retain_dataset)), len(retain_dataset) - int(0.8 * len(retain_dataset))])
    student_loader = DataLoader(retain_train, batch_size=64, shuffle=True)
    student_val_loader = DataLoader(retain_val, batch_size=64)
    trained_student = train_student_model(student_model, teacher_model, student_loader, student_val_loader, num_epochs=num_epochs, lr=0.001, device=device, alpha=0.5)

    student_model.eval()
    student_preds = trained_student(X.to(device)).cpu()
    student_metrics = evaluate_predictions(student_preds, y)

    return {
        "post_metrics": student_metrics,
        "model": trained_student
    }
