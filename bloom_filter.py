"""Compact Bloom filter with deterministic SHA-256 double hashing."""
from __future__ import annotations

import hashlib
import math
from typing import Any


def normalize_email(email: str) -> str:
    """Normalize consistently for this educational demo: trim and lowercase."""
    return email.strip().lower()


class BloomFilter:
    """Space-efficient probabilistic membership screen backed by a bytearray."""

    def __init__(self, capacity: int = 10_000, hash_count: int = 7) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be greater than zero")
        if hash_count <= 0:
            raise ValueError("hash_count must be greater than zero")
        self.capacity = capacity
        self.hash_count = hash_count
        self._bits = bytearray((capacity + 7) // 8)
        self.inserted_count = 0

    def positions(self, value: str) -> list[int]:
        normalized = normalize_email(value).encode("utf-8")
        digest1 = hashlib.sha256(b"bloomcheck:h1:" + normalized).digest()
        digest2 = hashlib.sha256(b"bloomcheck:h2:" + normalized).digest()
        h1 = int.from_bytes(digest1[:8], "big")
        h2 = int.from_bytes(digest2[:8], "big") or 1
        return [(h1 + i * h2) % self.capacity for i in range(self.hash_count)]

    def _get_bit(self, position: int) -> int:
        if not 0 <= position < self.capacity:
            raise IndexError("bit position is outside the filter")
        return (self._bits[position // 8] >> (position % 8)) & 1

    def _set_bit(self, position: int) -> bool:
        """Set a bit; return True only when it changed from 0 to 1."""
        if not 0 <= position < self.capacity:
            raise IndexError("bit position is outside the filter")
        byte_index, bit_index = divmod(position, 8)
        mask = 1 << bit_index
        changed = not (self._bits[byte_index] & mask)
        self._bits[byte_index] |= mask
        return bool(changed)

    def add(self, value: str) -> dict[str, Any]:
        positions = self.positions(value)
        before = [self._get_bit(p) for p in positions]
        changed: list[int] = []
        for position in positions:
            if self._set_bit(position):
                changed.append(position)
        self.inserted_count += 1
        return {
            "positions": positions,
            "before": before,
            "after": [self._get_bit(p) for p in positions],
            "changed_positions": changed,
            "already_set_positions": [p for p, was_set in zip(positions, before) if was_set],
        }

    def check(self, value: str) -> dict[str, Any]:
        positions = self.positions(value)
        values = [self._get_bit(p) for p in positions]
        return {
            "positions": positions,
            "bit_values": values,
            "possibly_present": all(values),
            "zero_positions": [p for p, bit in zip(positions, values) if bit == 0],
        }

    @property
    def set_bits(self) -> int:
        return sum(byte.bit_count() for byte in self._bits)

    @property
    def unset_bits(self) -> int:
        return self.capacity - self.set_bits

    @property
    def occupancy(self) -> float:
        return self.set_bits / self.capacity * 100

    def estimated_false_positive_rate(self, inserted_count: int | None = None) -> float:
        n = self.inserted_count if inserted_count is None else max(0, inserted_count)
        return (1 - math.exp(-self.hash_count * n / self.capacity)) ** self.hash_count

    def bit_array(self) -> list[int]:
        return [self._get_bit(i) for i in range(self.capacity)]

    def stats(self) -> dict[str, Any]:
        return {
            "capacity": self.capacity,
            "hash_count": self.hash_count,
            "inserted_count": self.inserted_count,
            "set_bits": self.set_bits,
            "unset_bits": self.unset_bits,
            "occupancy_percent": round(self.occupancy, 3),
            "estimated_false_positive_rate": self.estimated_false_positive_rate(),
            "estimated_false_positive_percent": round(self.estimated_false_positive_rate() * 100, 4),
        }
