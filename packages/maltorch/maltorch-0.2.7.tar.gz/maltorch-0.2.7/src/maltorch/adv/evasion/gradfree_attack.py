import nevergrad
import torch
from nevergrad.optimization import Optimizer
from secmlt.models.base_model import BaseModel
from torch.utils.data import DataLoader, TensorDataset

from maltorch.adv.evasion.backend_attack import BackendAttack


class GradientFreeBackendAttack(BackendAttack):
    def _optimizer_step(
        self, delta: nevergrad.p.Array, loss: torch.Tensor
    ) -> nevergrad.p.Array:
        if isinstance(delta, torch.Tensor):
            delta = self.optimizer.parametrization.spawn_child(new_value=delta.cpu().numpy())
        self.optimizer.tell(delta, loss.item())
        return self.optimizer.ask()


    def _apply_manipulation(
        self, x: torch.Tensor, delta: nevergrad.p.Array
    ) -> (torch.Tensor, torch.Tensor):
        p_delta = torch.from_numpy(delta.value)
        p_delta = p_delta.float()
        p_delta = p_delta.to(x.device)
        return self.manipulation_function(x.data, p_delta)

    def _consumed_budget(self):
        return 1

    def _init_attack_manipulation(
        self, samples: torch.Tensor
    ) -> (torch.Tensor, nevergrad.p.Array):
        x_adv, delta = super()._init_attack_manipulation(samples)
        optim_delta = nevergrad.p.Array(shape=delta.shape, lower=0.0, upper=255.0)
        optim_delta.value = delta.cpu().numpy()
        return x_adv, optim_delta

    def _init_optimizer(self, model: BaseModel, delta: nevergrad.p.Array) -> Optimizer:
        self.optimizer = self.optimizer_cls(
            parametrization=nevergrad.p.Array(
                shape=delta.value.shape, lower=0.0, upper=255.0
            )
        )
        return self.optimizer

    def __call__(self, model: BaseModel, data_loader: DataLoader) -> DataLoader:
        adversarials = []
        original_labels = []
        for samples, labels in data_loader:
            for sample, label in zip(samples, labels):
                sample = sample.unsqueeze(0)
                label = label.unsqueeze(0)
                x_adv, _ = self._run(model, sample, label)
                adversarials.append(x_adv.transpose(0,1))
                original_labels.append(label)
        adversarials = (
            torch.nn.utils.rnn.pad_sequence(adversarials, padding_value=256)
            .transpose(0,1)
            .squeeze()
            .long()
        )
        adversarials = torch.atleast_2d(adversarials)
        original_labels = torch.vstack(original_labels)
        adversarial_dataset = TensorDataset(adversarials, original_labels)
        return DataLoader(
            adversarial_dataset,
            batch_size=data_loader.batch_size,
        )

    def _init_best_tracking(self, delta: torch.Tensor): ...

    def _track_best(self, loss: torch.Tensor, delta: torch.Tensor): ...

    def _get_best_delta(self):
        return self.optimizer.provide_recommendation()
