#!/usr/bin/env python
"""Generate mock data for the lottery application."""

import sys
from pathlib import Path

from app.services.mock_data_generator import MockDataGenerator


def main() -> None:
    """Generate mock data in the data/ directory."""
    workspace_root = Path(__file__).parent
    mock_dir = workspace_root / "data"

    print("Generating mock data...")
    try:
        MockDataGenerator.generate_all(mock_dir, participant_count=100, prize_count=20)
        print(f"\nMock data generated successfully in {mock_dir}")
        print("\nYou can now update config/config.yaml to point to this mock data:")
        print(f"  participants_excel: data/participants/participants.xlsx")
        print(f"  prizes_excel: data/prizes/prizes.xlsx")
    except Exception as exc:
        print(f"Error generating mock data: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
