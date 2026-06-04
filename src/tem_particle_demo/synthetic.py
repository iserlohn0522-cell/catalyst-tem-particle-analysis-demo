from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

from .manifest import ManifestRow, sha256_file, write_manifest


@dataclass(frozen=True)
class SyntheticParticle:
    particle_id: str
    center_x: float
    center_y: float
    radius_px: float

    @property
    def bbox(self) -> list[float]:
        return [
            self.center_x - self.radius_px,
            self.center_y - self.radius_px,
            self.center_x + self.radius_px,
            self.center_y + self.radius_px,
        ]

    def as_label(self) -> dict[str, object]:
        return {
            "particle_id": self.particle_id,
            "center": [round(self.center_x, 3), round(self.center_y, 3)],
            "radius_px": round(self.radius_px, 3),
            "bbox": [round(value, 3) for value in self.bbox],
        }


def _support_texture(rng: np.random.Generator, size: int) -> np.ndarray:
    yy, xx = np.mgrid[0:size, 0:size]
    low_frequency = 12.0 * np.sin(xx / 19.0) + 9.0 * np.cos(yy / 23.0)
    gradient = 18.0 * (xx / max(1, size - 1)) + 8.0 * (yy / max(1, size - 1))
    noise = rng.normal(0.0, 8.0, size=(size, size))
    return 188.0 + low_frequency + gradient + noise


def _draw_soft_particle(image: np.ndarray, particle: SyntheticParticle, intensity: float) -> None:
    yy, xx = np.mgrid[0:image.shape[0], 0:image.shape[1]]
    distance = np.sqrt((xx - particle.center_x) ** 2 + (yy - particle.center_y) ** 2)
    core = distance <= particle.radius_px
    rim = (distance > particle.radius_px) & (distance <= particle.radius_px + 1.5)
    image[core] = np.minimum(image[core], intensity)
    image[rim] = np.minimum(image[rim], intensity + 25.0)


def generate_synthetic_image(index: int, seed: int, size: int = 256) -> tuple[np.ndarray, list[SyntheticParticle], float]:
    rng = np.random.default_rng(seed + index * 1009)
    image = _support_texture(rng, size)
    particle_count = int(rng.integers(18, 30))
    particles: list[SyntheticParticle] = []
    attempts = 0
    while len(particles) < particle_count and attempts < particle_count * 80:
        attempts += 1
        radius = float(rng.uniform(4.0, 8.5))
        cx = float(rng.uniform(16.0 + radius, size - 16.0 - radius))
        cy = float(rng.uniform(16.0 + radius, size - 16.0 - radius))
        if any(math.hypot(cx - p.center_x, cy - p.center_y) < (radius + p.radius_px + 2.0) for p in particles):
            continue
        particle = SyntheticParticle(
            particle_id=f"p{len(particles):03d}",
            center_x=cx,
            center_y=cy,
            radius_px=radius,
        )
        particles.append(particle)
        _draw_soft_particle(image, particle, intensity=float(rng.uniform(35.0, 70.0)))
    nm_per_px = float(rng.uniform(0.115, 0.155))
    return np.clip(image, 0, 255).astype(np.uint8), particles, nm_per_px


def write_synthetic_example(output_dir: Path, index: int, seed: int, size: int = 256) -> ManifestRow:
    output_dir = Path(output_dir)
    image_dir = output_dir / "images"
    label_dir = output_dir / "labels"
    image_dir.mkdir(parents=True, exist_ok=True)
    label_dir.mkdir(parents=True, exist_ok=True)

    image, particles, nm_per_px = generate_synthetic_image(index=index, seed=seed, size=size)
    image_id = f"synthetic_tem_{index:03d}"
    image_path = image_dir / f"{image_id}.png"
    label_path = label_dir / f"{image_id}.json"
    Image.fromarray(image, mode="L").save(image_path)
    label_path.write_text(
        json.dumps(
            {
                "image_id": image_id,
                "description": "Synthetic TEM-like image generated for public demo use only.",
                "image_width": int(size),
                "image_height": int(size),
                "nm_per_px": nm_per_px,
                "particles": [particle.as_label() for particle in particles],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    split = "demo" if index == 0 else "validation"
    return ManifestRow(
        image_id=image_id,
        split=split,
        image_path=str(image_path.relative_to(output_dir)).replace("\\", "/"),
        label_path=str(label_path.relative_to(output_dir)).replace("\\", "/"),
        nm_per_px=nm_per_px,
        source="synthetic_generated",
        allowed_use="public_demo_only",
        sha256_image=sha256_file(image_path),
    )


def generate_dataset(output_dir: Path, count: int = 4, seed: int = 7, size: int = 256) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = [write_synthetic_example(output_dir, index=index, seed=seed, size=size) for index in range(count)]
    return write_manifest(output_dir / "manifest.csv", rows)
