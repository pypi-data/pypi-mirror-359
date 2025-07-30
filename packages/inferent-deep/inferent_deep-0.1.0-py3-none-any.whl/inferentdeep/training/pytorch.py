from contextlib import contextmanager
import copy
import logging
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, TensorDataset
from torch.utils.tensorboard import SummaryWriter

def get_pytorch_trainloader(datamgr, batch_size=64, shuffle=True):
    """Get TrainLoader"""
    # TODO: dtypes
    # TODO: Dataset must fit in memory; if not, must use Streaming Data
    # Loader
    trainset = TensorDataset(
        torch.tensor(datamgr.X_train, dtype=torch.float32),
        torch.tensor(datamgr.y_train, dtype=torch.int),
    )
    return DataLoader(trainset, batch_size=batch_size, shuffle=shuffle)

@contextmanager
def evaluating(net):
    """Temporarily switch to evaluation mode.

    Affects modules such as batchnorm and dropout.
    """
    istrain = net.training
    try:
        net.eval()
        yield net
    finally:
        if istrain:
            net.train()

class TorchModule(torch.nn.Module):
    """Pytorch module"""

    def __init__(self):
        super().__init__()
        # TODO: make this configurable by children
        self.install_hooks()

    def install_hooks(self, output=True):
        """Install hooks (configurable)"""
        if output:
            _ = torch.nn.modules.module.register_module_forward_hook(
                self.save_output_hook
            )

    def save_output_hook(self, module, _, output):
        """save any modules output in an attribute"""
        module.forward_output = output

    def forward(self):
        """forward"""
        raise NotImplementedError("forward not implemented")

class PytorchTrainer:
    """Model trainer class"""

    logger = logging.getLogger("Trainer")
    epoch = 0

    def __init__(
        self,
        name,
        datamgr,
        model,
        loss_fn,
        metrics,
        optimizer="adam",
        batch_size=64,
        max_epochs=50,
        lr=0.001,
    ):
        self.datamgr = datamgr
        self.model = model
        self.loss_fn = loss_fn
        self.metrics = metrics
        self.batch_size = batch_size
        self.max_epochs = max_epochs
        self.writer = SummaryWriter(name)
        if optimizer == "adam":
            self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        else:
            raise ValueError(f"Invalid optimizer {optimizer}")

    def write(self, name, x):
        """Write to summarywriter"""
        if x is None:
            self.logger.info("x is None. Not writing.")
            return
        if isinstance(x, torch.Tensor) and x.numel() > 1:
            self.writer.add_histogram(name, x, self.epoch)
        else:
            self.writer.add_scalar(
                name,
                x.item() if isinstance(x, torch.Tensor) else x,
                self.epoch,
            )

    def write_stdratio(self, name, x, y):
        """Write ratio of std to summarywriter"""
        if x is None or y is None:
            self.logger.info("x (%s) or y(%s) is None. Not writing.", x, y)
            return
        if isinstance(x, torch.Tensor) and x.numel() > 1:
            self.writer.add_histogram(name, x.std() / y.std(), self.epoch)
        else:
            self.writer.add_scalar(name, x.std() / y.std(), self.epoch)

    def train(self):
        """train"""
        self.logger.info(
            "Model has %s parameters",
            sum(x.reshape(-1).shape[0] for x in self.model.parameters()),
        )
        batch_idx = 0

        trainloader = get_pytorch_trainloader(
                self.datamgr, batch_size=self.batch_size, shuffle=True
        )

        best_acc = np.inf  # init to negative infinity
        best_weights = None
        best_epoch = -1
        self.epoch = 0
        trn_metrics = copy.deepcopy(self.metrics)
        vld_metrics = copy.deepcopy(self.metrics)

        self.logger.info("Starting to train")
        for _ in range(self.max_epochs):
            trn_metrics.reset()
            vld_metrics.reset()
            for batch in trainloader:
                batch_idx += 1
                X, y = batch
                preds = self.model(X)
                with evaluating(self.model), torch.inference_mode():
                    metrics_output = trn_metrics.update(
                        preds.squeeze(), y.squeeze()
                    )
                    vld_preds = self.model(
                        torch.tensor(self.datamgr.X_vld, dtype=torch.float32)
                    )
                    vld_metrics_output = vld_metrics.update(
                        vld_preds.squeeze(),
                        torch.tensor(
                            self.datamgr.y_vld, dtype=torch.int
                        ).squeeze(),
                    )

                loss_val = self.loss_fn(preds, y.type(torch.float32))
                self.optimizer.zero_grad()
                loss_val.backward()
                self.optimizer.step()

            for metric, metric_output in metrics_output.items():
                self.write(f"metrics/{metric}", metric_output[1])
            for metric, metric_output in vld_metrics_output.items():
                self.write(f"vld_metrics/{metric}", metric_output[1])
            # TODO: optimizer
            # self.model.write("learning_rate", optimizer.lr, scal=True)
            # logger.info(f"state_dict {optimizer.state_dict()}")

            moduledict = {}
            for name, module in self.model.named_modules():
                instancenum = moduledict.get(name, 0) + 1
                moduledict[name] = instancenum
                if isinstance(module, torch.nn.Linear):
                    self.write(f"linear{instancenum}/weights", module.weight)
                    self.write(
                        f"linear{instancenum}/weights/grad", module.weight.grad
                    )
                    self.write_stdratio(
                        f"linear{instancenum}/grad-data-ratio",
                        module.weight.grad,
                        module.weight,
                    )
                    self.write(f"linear{instancenum}/bias", module.bias)
                    self.write(
                        f"linear{instancenum}/bias/grad", module.bias.grad
                    )
                    self.write(
                        f"linear{instancenum}/output", module.forward_output
                    )
                elif isinstance(module, torch.nn.LayerNorm):
                    self.write(
                        f"layernorm{instancenum}/weights", module.weight
                    )
                    self.write(
                        f"layernorm{instancenum}/weights/grad",
                        module.weight.grad,
                    )
                    self.write(f"layernorm{instancenum}/bias", module.bias)
                    self.write(
                        f"layernorm{instancenum}/bias/grad", module.bias.grad
                    )
                    # TODO: check if output exists
                    self.write(
                        f"layernorm{instancenum}/output", module.forward_output
                    )

            def _get_metrics_str(metrics_output):
                return " | ".join(
                    [
                        metric + f" {metric_output[1]:,.2f}"
                        for metric, metric_output in metrics_output.items()
                    ]
                )

            self.logger.info(
                "\033[33mEpoch %s, trn: %s \033[0m",
                self.epoch,
                _get_metrics_str(metrics_output),
            )
            self.logger.info(
                "\033[32mEpoch %s, vld: %s \033[0m",
                self.epoch,
                _get_metrics_str(vld_metrics_output),
            )
            if vld_metrics_output["Binary Cross Entropy"][1] < best_acc:
                best_acc = vld_metrics_output["Binary Cross Entropy"][1]
                best_weights = copy.deepcopy(self.model.state_dict())
                best_epoch = self.epoch
            self.epoch += 1

        self.logger.info(
            "Best model found in epoch %s with BCE %s.", best_epoch, best_acc
        )
        self.model.load_state_dict(best_weights)
