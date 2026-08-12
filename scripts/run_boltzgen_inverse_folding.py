#!/usr/bin/env python3
"""Run only BoltzGen inverse folding with the study's exact custom settings.

This wrapper derives its configuration from the installed BoltzGen package.
It is intended to run inside the official BoltzGen environment on a GPU server.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--design-dir", type=Path, required=True,
                        help="Directory containing paired design CIF and NPZ files")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--moldir", type=Path, required=True)
    parser.add_argument("--checkpoint", required=True,
                        help="Local checkpoint or huggingface:repo:file")
    parser.add_argument("--sequences-per-backbone", type=int, default=4)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--avoid", default="C")
    parser.add_argument("--devices", type=int, default=4)
    parser.add_argument("--num-workers", type=int, default=4)
    parser.add_argument("--reuse", action="store_true")
    parser.add_argument("--use-kernels", choices=["auto", "true", "false"], default="auto")
    parser.add_argument("--print-config", action="store_true")
    args = parser.parse_args()

    import torch
    from huggingface_hub import hf_hub_download
    from omegaconf import OmegaConf
    import boltzgen
    from boltzgen.data import const

    package_dir = Path(boltzgen.__file__).resolve().parent
    template = package_dir / "resources" / "config" / "inverse_fold.yaml"
    main_script = package_dir / "resources" / "main.py"
    for path in [template, main_script, args.design_dir, args.moldir]:
        if not path.exists():
            raise FileNotFoundError(path)

    cifs = sorted(path for path in args.design_dir.glob("*.cif")
                  if not path.name.endswith("_native.cif"))
    if not cifs:
        raise RuntimeError(f"No design CIF files in {args.design_dir}")
    missing_npz = [path.with_suffix(".npz") for path in cifs
                   if not path.with_suffix(".npz").is_file()]
    if missing_npz:
        raise RuntimeError(f"Missing {len(missing_npz)} paired NPZ files; first: {missing_npz[0]}")

    if args.checkpoint.startswith("huggingface:"):
        _, repo_id, filename = args.checkpoint.split(":", 2)
        checkpoint = Path(hf_hub_download(repo_id=repo_id, filename=filename,
                                          library_name="boltzgen"))
    else:
        checkpoint = Path(args.checkpoint).expanduser().resolve()
        if not checkpoint.is_file():
            raise FileNotFoundError(checkpoint)

    restriction = []
    for aa in args.avoid.replace(",", "").replace(" ", "").upper():
        if aa not in const.prot_letter_to_token:
            raise ValueError(f"Unknown amino acid: {aa}")
        restriction.append(const.prot_letter_to_token[aa])

    if args.use_kernels == "auto":
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA GPU not detected")
        kernels = torch.cuda.get_device_capability()[0] >= 8
    else:
        kernels = args.use_kernels == "true"

    result_dir = args.output_dir / "intermediate_designs_inverse_folded"
    if result_dir.exists() and any(result_dir.iterdir()) and not args.reuse:
        raise RuntimeError(f"Non-empty output exists: {result_dir}; use --reuse or a new path")
    result_dir.mkdir(parents=True, exist_ok=True)
    config_dir = args.output_dir / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    generated = config_dir / "inverse_folding.yaml"

    cfg = OmegaConf.load(template)
    updates = {
        "output": str(result_dir),
        "checkpoint": str(checkpoint),
        "data.design_dir": str(args.design_dir.resolve()),
        "data.output_dir": str(result_dir),
        "writer.output_dir": str(result_dir),
        "data.cfg.moldir": str(args.moldir.resolve()),
        "data.cfg.multiplicity": args.sequences_per_backbone,
        "data.cfg.num_workers": args.num_workers,
        "trainer.devices": args.devices,
        "data.skip_existing": args.reuse,
        "data.skip_existing_kind": "inverse_fold",
        "override.use_kernels": kernels,
        "override.inverse_fold_args.sampling_temperature": args.temperature,
        "override.inverse_fold_args.inverse_fold_restriction": restriction,
    }
    for key, value in updates.items():
        OmegaConf.update(cfg, key, value, merge=False, force_add=True)
    OmegaConf.save(cfg, generated)

    print(f"Backbones: {len(cifs)}")
    print(f"Expected samples: {len(cifs) * args.sequences_per_backbone}")
    print(f"Generated config: {generated}")
    if args.print_config:
        print(OmegaConf.to_yaml(cfg))
    subprocess.run([sys.executable, str(main_script), str(generated)], check=True)


if __name__ == "__main__":
    main()

