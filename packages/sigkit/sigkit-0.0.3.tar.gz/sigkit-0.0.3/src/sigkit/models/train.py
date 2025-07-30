"""Training Module for the SigKitClassifier."""

from typing import Dict, List

import click
import lightning as pl
import numpy as np
import torch
from lightning.pytorch.callbacks import EarlyStopping, ModelCheckpoint
from lightning.pytorch.loggers import WandbLogger
from torchvision.transforms import Compose

from sigkit.datasets.procedural import ProceduralDataset
from sigkit.models.DataModule import SigKitDataModule
from sigkit.models.Module import SigKitClassifier
from sigkit.modem.base import Modem
from sigkit.modem.fsk import FSK
from sigkit.modem.psk import PSK
from sigkit.transforms.awgn import ApplyAWGN
from sigkit.transforms.frequency_shift import ApplyFrequencyShift
from sigkit.transforms.phase_shift import ApplyPhaseShift
from sigkit.transforms.utils import ComplexTo2D, Normalize, RandomApplyProb

torch.set_float32_matmul_precision("medium")

SAMPLE_RATE = 1024


@click.command()
@click.option(
    "--batch-size",
    default=128,
    type=int,
    show_default=True,
)
@click.option("--lr", default=1e-3, type=float, show_default=True, help="Learning rate")
@click.option(
    "--max-epochs",
    default=10000,
    type=int,
    show_default=True,
    help="Maximum number of epochs, arbitrarily large for early stop",
)
def train(batch_size: int, lr: float, max_epochs: int):
    """Train the SigKitClassifier on SigKit datasets."""
    train_transform = Compose(
        [
            RandomApplyProb(
                [
                    (ApplyAWGN((-2, 30)), 1.0),
                    (ApplyPhaseShift((-np.pi, np.pi)), 0.9),
                    (
                        ApplyFrequencyShift((-164, 164), sample_rate=SAMPLE_RATE),
                        0.7,
                    ),  # 164 is 16% of sample rate  # noqa: E501
                ]
            ),
            Normalize(norm=np.inf),
            ComplexTo2D(),
        ]
    )
    val_transform = train_transform

    mapping_list: List[Dict[Modem, List[int]]] = [
        {PSK: [2, 4, 8, 16]},
        {FSK: [2, 4, 8, 16]},
    ]
    train_ds = ProceduralDataset(mapping_list, transform=train_transform)
    val_ds = ProceduralDataset(mapping_list, transform=val_transform, val=True, seed=42)

    dm = SigKitDataModule(
        train_dataset=train_ds, val_dataset=val_ds, batch_size=batch_size
    )

    model = SigKitClassifier(num_classes=dm.num_classes, lr=lr)

    logger = WandbLogger(project="SigKit")
    trainer = pl.Trainer(
        max_epochs=max_epochs,
        logger=logger,
        callbacks=[
            ModelCheckpoint(
                monitor="val_acc",
                save_top_k=1,
                mode="max",
                dirpath="data/checkpoints",
                filename="best",
            ),
            EarlyStopping(monitor="val_loss", patience=10, mode="min", verbose=True),
        ],
    )
    trainer.fit(model, datamodule=dm)


if __name__ == "__main__":
    train()
