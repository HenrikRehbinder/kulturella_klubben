# Kulturella Klubben Lottery - Quick Start Guide

## Setup (First Time)

### 1. Install Dependencies
```powershell
& 'C:\Users\hrehe10977\micromamba\envs\kultur\python.exe' -m pip install -r requirements.txt
```

### 2. Generate Mock Data (Optional, for testing)
```powershell
& 'C:\Users\hrehe10977\micromamba\envs\kultur\python.exe' generate_mock_data.py
```

This creates:
- `data/participants/participants.xlsx` – 100 mock participants
- `data/sessions/2026-05-06/prizes.xlsx` – 20 mock prizes for today's date
- `data/sessions/2026-05-06/prize_images/` – Generated placeholder images

## Before Each Lottery

### Step 1: Create Session Folder
Create today's session folder with the date as folder name:
```
data/sessions/YYYY-MM-DD/
```

### Step 2: Prepare Prizes
Place a `prizes.xlsx` file in the session folder with columns:
- `prize_id`: Unique identifier (e.g., "p1", "p2")
- `title`: Prize name (e.g., "Abstract Painting")
- `description`: Short description
- `image_path`: Path to the prize image file (can be absolute or relative to the session folder)

Example:
```
data/sessions/2026-05-06/
  prizes.xlsx
  prize_images/
    painting_1.png
    sculpture_2.png
    ...
```

### Step 3: Prepare Participants (Shared)
Place `participants.xlsx` in `data/participants/` with columns:
- `email`: Unique participant email
- `first_name`: First name
- `last_name`: Last name

This file is used for all lotteries unless you need lottery-specific participants.

## Running the Lottery

### Launch the Application
```powershell
& 'C:\Users\hrehe10977\micromamba\envs\kultur\python.exe' -m app.main
```

### Workflow
1. **DRAW** button: Randomly selects a candidate
2. **Confirm** or **Not Present**: Decide if the winner is present
   - If not present, the draw is logged and you draw again
   - If present, move to prize selection
3. **Select Prize**: Click a prize in the grid to assign it to the winner
4. **Repeat** until all prizes are assigned

### Output Files
After the lottery, check the session folder:
- `winners.xlsx` – Final list of winners and their chosen prizes
- `event_log.xlsx` – Complete action history (timestamps, draws, confirmations)
- `session_state.json` – Application state (for resuming if interrupted)
- `event_log.jsonl` – Raw event log (one JSON line per action)

## Resuming an Interrupted Lottery

If the app crashes or closes mid-lottery:
1. Launch the app again
2. A dialog offers to resume or start a new session
3. Select "Resume" to continue from where you left off

## Troubleshooting

### Error: "Prizes file not found"
- Make sure `prizes.xlsx` exists in `data/sessions/YYYY-MM-DD/`
- Check that the date in the folder name matches today's date (ISO format: YYYY-MM-DD)

### Error: "Prize image file not found"
- Check that image paths in `prizes.xlsx` are correct
- Paths can be absolute or relative to the session folder

### Error: "Duplicate email in participant Excel"
- Ensure each participant has a unique email address
- Remove duplicates from `participants.xlsx`

## Configuration

Edit `config/config.yaml` to customize:
- `title`: Application title
- `participants_excel`: Path to participants file
- `sessions_root`: Root folder for lottery sessions
- `previous_winners_excluded_until_confirmed_winners`: How many confirmed winners before previous lottery winners can win again (default: 3)
- UI settings: grid columns, image sizes

## For Developers

Run tests:
```powershell
& 'C:\Users\hrehe10977\micromamba\envs\kultur\python.exe' -m pytest tests -v
```

Generate mock data for a specific date:
```python
from app.services.mock_data_generator import MockDataGenerator
MockDataGenerator.generate_all(
    Path("data"),
    session_date="2026-05-20",
    participant_count=100,
    prize_count=20
)
```
