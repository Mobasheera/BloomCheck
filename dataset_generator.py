"""Generate a stable collection of synthetic email addresses for BloomCheck."""
from __future__ import annotations


def generate_emails(count: int = 1000) -> list[str]:
    if count < 0:
        raise ValueError("count cannot be negative")
    # Reserved example.com domain; no real accounts or personal email addresses.
    return [f"member{i:04d}@example.com" for i in range(1, count + 1)]


if __name__ == "__main__":
    emails = generate_emails()
    print(f"Generated {len(emails)} deterministic synthetic email addresses.")
    print(f"First: {emails[0]} | Last: {emails[-1]}")
