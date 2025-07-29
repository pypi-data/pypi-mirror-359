"""PyTorch model trainers with early stopping."""

import torch.nn
from torch.optim.lr_scheduler import _LRScheduler
from torch.utils.data import DataLoader
from tqdm import tqdm
import copy


class EarlyStoppingPyTorchTrainer:
    """Trainer for PyTorch models with early stopping."""

    def __init__(self, optimizer: torch.optim.Optimizer, epochs: int = 5,
                 loss: torch.nn.Module = None, scheduler: _LRScheduler = None) -> None:
        """
        Create PyTorch trainer.
        Parameters
        ----------
        optimizer : torch.optim.Optimizer
            Optimizer to use for training the model.
        epochs : int, optional
            Number of epochs, by default 5.
        loss : torch.nn.Module, optional
            Loss to minimize, by default None.
        scheduler : _LRScheduler, optional
            Scheduler for the optimizer, by default None.
        """
        self._epochs = epochs
        self._optimizer = optimizer
        self._loss = loss if loss is not None else torch.nn.BCEWithLogitsLoss()
        self._scheduler = scheduler

        self.training_losses = []
        self.training_accuracies = []
        self.validation_losses = []
        self.validation_accuracies = []

    def train(self, model: torch.nn.Module,
            train_loader: DataLoader,
            val_loader: DataLoader,
            patience: int) -> torch.nn.Module:
        """
        Train model with given loaders and early stopping.
        Parameters
        ----------
        model : torch.nn.Module
            Pytorch model to be trained.
        train_loader : DataLoader
            Train data loader.
        val_loader : DataLoader
            Validation data loader.
        patience : int
            Number of epochs to wait before early stopping.
        Returns
        -------
        torch.nn.Module
            Trained model.
        """
        # Check model has .threshold
        if not hasattr(model, 'threshold'):
            raise AttributeError("Model must have a 'threshold' attribute for binary classification.")

        best_loss = float("inf")
        best_model = None
        patience_counter = 0
        for epoch in range(self._epochs):
            model = self.fit(model, train_loader)
            val_loss = self.validate(model, val_loader)
            if val_loss <= best_loss:
                best_loss = val_loss
                best_model = copy.deepcopy(model)
                best_model = best_model.to(next(model.parameters()).device)
                patience_counter = 0
            else:
                patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping triggered. The validation losss hasn't improved for {patience_counter} epochs")
                break
            print(
                f"Epoch {epoch}: val_loss = {val_loss}, best_loss = {best_loss}, patience_counter = {patience_counter}")
        return best_model

    def fit(self,
              model: torch.nn.Module,
              dataloader: DataLoader) -> torch.nn.Module:
        """
        Train model for one epoch with given loader.
        Parameters
        ----------
        model : torch.nn.Module
            Pytorch model to be trained.
        dataloader : DataLoader
            Train data loader.
        Returns
        -------
        torch.nn.Module
            Trained model.
        """
        device = next(model.parameters()).device
        model = model.train()
        running_loss = 0.0
        train_total = 0
        train_correct = 0
        num_batches = 0
        for x, y in tqdm(dataloader):
            x, y = x.to(device), y.to(device)
            self._optimizer.zero_grad()
            outputs = model(x)
            outputs = outputs.view(-1)
            loss = self._loss(outputs, y.float())
            loss.backward()
            self._optimizer.step()

            running_loss += loss.item()
            probs = torch.sigmoid(outputs)
            y_preds = (probs >= model.threshold).int()

            train_total += y.size(0)
            train_correct += (y_preds == y).sum().item()
            num_batches += 1
        self.training_losses.append(running_loss / num_batches)
        self.training_accuracies.append(train_correct / train_total)

        if self._scheduler is not None:
            self._scheduler.step()
        return model

    def validate(self,
                 model: torch.nn.Module,
                 dataloader: DataLoader) -> float:
        """
        Validate model with given loader.
        Parameters
        ----------
        model : torch.nn.Module
            Pytorch model to be validated.
        dataloader : DataLoader
            Validation data loader.
        Returns
        -------
        float
            Validation loss of the model.
        """
        running_loss = 0
        val_total = 0
        val_correct = 0
        device = next(model.parameters()).device
        model = model.eval()
        num_batches = 0
        with torch.no_grad():
            for x, y in tqdm(dataloader):
                x, y = x.to(device), y.to(device)
                outputs = model(x)
                outputs = outputs.view(-1)
                loss = self._loss(outputs, y.float())
                running_loss += loss.item()
                probs = torch.sigmoid(outputs)
                y_preds = (probs >= model.threshold).int()
                val_total += y.size(0)
                val_correct += (y_preds == y).sum().item()
                num_batches += 1

            val_loss = running_loss / num_batches
            self.validation_losses.append(running_loss / num_batches)
            self.validation_accuracies.append(val_correct / val_total)
        return val_loss
