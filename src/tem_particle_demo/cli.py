from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import run_pipeline
from .synthetic import generate_dataset


def generate_main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate a synthetic TEM-like public demo dataset.")
    parser.add_argument("--output", type=Path, default=Path("examples/synthetic_dataset"))
    parser.add_argument("--count", type=int, default=4)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--size", type=int, default=256)
    args = parser.parse_args(argv)
    manifest = generate_dataset(output_dir=args.output, count=args.count, seed=args.seed, size=args.size)
    print(manifest)


def run_main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run the safe synthetic TEM particle-analysis demo.")
    parser.add_argument("--manifest", type=Path, default=Path("examples/synthetic_dataset/manifest.csv"))
    parser.add_argument("--output", type=Path, default=Path("demo_outputs"))
    parser.add_argument("--match-iou", type=float, default=0.3)
    args = parser.parse_args(argv)
    run_pipeline(manifest_path=args.manifest, output_dir=args.output, match_iou=args.match_iou)
    print(args.output / "summary.md")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Synthetic TEM particle-analysis demo commands.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    generate_parser = subparsers.add_parser("generate", help="Generate synthetic public-demo data")
    generate_parser.add_argument("--output", type=Path, default=Path("examples/synthetic_dataset"))
    generate_parser.add_argument("--count", type=int, default=4)
    generate_parser.add_argument("--seed", type=int, default=7)
    generate_parser.add_argument("--size", type=int, default=256)
    run_parser = subparsers.add_parser("run", help="Run the demo pipeline")
    run_parser.add_argument("--manifest", type=Path, default=Path("examples/synthetic_dataset/manifest.csv"))
    run_parser.add_argument("--output", type=Path, default=Path("demo_outputs"))
    run_parser.add_argument("--match-iou", type=float, default=0.3)
    args = parser.parse_args(argv)
    if args.command == "generate":
        manifest = generate_dataset(output_dir=args.output, count=args.count, seed=args.seed, size=args.size)
        print(manifest)
    elif args.command == "run":
        run_pipeline(manifest_path=args.manifest, output_dir=args.output, match_iou=args.match_iou)
        print(args.output / "summary.md")


if __name__ == "__main__":
    main()
