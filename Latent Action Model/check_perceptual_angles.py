"""Per-patch DINO angles between the LAM's predicted frame t+gap and the real one.

No training: loads an existing checkpoint, runs a few eval batches, and reports the
angle distribution behind the perceptual loss (loss = 2 * (1 - mean cos) / 768).

Put this file in the repo's ``script/`` folder (it imports ``script/_common.py``) and
run from the repo root on the cluster:

    uv run python script/check_perceptual_angles.py \
        --checkpoint /path/to/run/checkpoint-65000 \
        --data-config lam.configs.data.lam_mixture_1_data \
        --num-batches 4

Outputs: a printed summary and ``perceptual_angles.png``.
"""

from __future__ import annotations

import argparse
import importlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
from torch.utils.data import DataLoader

from _common import build_from_data_config
from lam import LatentActionModel
from lam.encoders import get_visual_encoder


def load_dotted(path: str):
    module_name, _, attr = path.rpartition(".")
    return getattr(importlib.import_module(module_name), attr)


def summarize(name: str, angles_deg: torch.Tensor, cos: torch.Tensor) -> None:
    mean_cos = cos.mean().item()
    q = torch.quantile(angles_deg, torch.tensor([0.1, 0.5, 0.9, 0.99]))
    print(f"\n{name}  ({angles_deg.numel()} patches)")
    print(f"  mean cos                 : {mean_cos:.4f}")
    print(f"  implied raw L_perc       : {2 * (1 - mean_cos) / 768:.6f}   (x250 = {250 * 2 * (1 - mean_cos) / 768:.4f})")
    print(f"  angle of the mean cos    : {torch.rad2deg(torch.arccos(torch.tensor(mean_cos))).item():.1f} deg")
    print(f"  mean of the angles       : {angles_deg.mean().item():.1f} deg   (differs from the line above: Jensen)")
    print(f"  angle p10 / p50 / p90 / p99: {q[0]:.1f} / {q[1]:.1f} / {q[2]:.1f} / {q[3]:.1f} deg")
    print(f"  share above 60 deg       : {(angles_deg > 60).float().mean().item():.2%}   (loss no longer ~ theta^2)")
    print(f"  share above 90 deg       : {(angles_deg > 90).float().mean().item():.2%}   (gradient shrinks as error grows)")


@torch.no_grad()
def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--checkpoint", required=True, help="HF checkpoint-N directory of a trained LAM")
    parser.add_argument("--data-config", default="lam.configs.data.lam_mixture_1_data")
    parser.add_argument("--encoder", default="dinov3_b", help="dinov3_b (needs HF_TOKEN) or dinov2_b")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--num-batches", type=int, default=4)
    parser.add_argument("--num-workers", type=int, default=4)
    parser.add_argument("--out", default="perceptual_angles.png")
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"

    lam = LatentActionModel.from_pretrained(args.checkpoint).to(device).eval()
    encoder = get_visual_encoder(args.encoder).to(device).eval()

    train_set, eval_set = build_from_data_config(
        load_dotted(args.data_config), tuple(lam.config.image_size), seed=0
    )
    loader = DataLoader(
        eval_set if eval_set is not None else train_set,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        shuffle=False,
    )

    results: dict[str, dict[str, list[torch.Tensor]]] = {
        "prediction vs real t+gap": {"angle": [], "cos": []},
        "copy (frame t) vs real t+gap": {"angle": [], "cos": []},
    }

    for i, batch in enumerate(loader):
        if i >= args.num_batches:
            break
        video = batch["video"].to(device)                      # [B, 3, 2, H, W] in [0, 1]
        r = batch["relative_offset"].to(device)                # [B]
        output = lam(video=video, relative_offset=r)           # eval mode: hard codes

        first = video[:, :, 0].float()                         # [B, 3, H, W]
        real = video[:, :, 1].float()
        pred = output.reconstruction[:, :, 0].float()          # [B, 3, H, W], not clamped (as in training)

        target_feat = encoder.encode(real)                     # [B, N, D], unit vectors
        for name, image in (("prediction vs real t+gap", pred), ("copy (frame t) vs real t+gap", first)):
            cos = (encoder.encode(image) * target_feat).sum(-1).clamp(-1.0, 1.0)   # [B, N]
            results[name]["cos"].append(cos.flatten().cpu())
            results[name]["angle"].append(torch.rad2deg(torch.arccos(cos)).flatten().cpu())

    plt.figure(figsize=(8, 4.5))
    for name, vals in results.items():
        angles = torch.cat(vals["angle"])
        cos = torch.cat(vals["cos"])
        summarize(name, angles, cos)
        plt.hist(angles.numpy(), bins=90, range=(0, 180), alpha=0.55, label=name)
    for x, label in ((60, "60 deg: loss ~ theta^2 up to here"), (90, "90 deg: max gradient")):
        plt.axvline(x, linestyle="--", linewidth=1)
        plt.text(x + 1, plt.ylim()[1] * 0.92, label, fontsize=8)
    plt.xlabel("angle between DINO patch features (degrees)")
    plt.ylabel("number of patches")
    plt.title(f"Per-patch DINO angle, {args.checkpoint.rstrip('/').split('/')[-1]}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(args.out, dpi=150)
    print(f"\nSaved histogram to {args.out}")


if __name__ == "__main__":
    main()
