# Kulturella Klubben Lottery

A Qt-based desktop application for running recurring art lotteries. Participants are drawn randomly, confirm their presence, and manually select from available art prizes. The application automatically handles winner eligibility rules, session persistence, and official result exports.

## Features

- **Random Drawing**: Weighted selection respecting eligibility rules
- **Previous Winner Exclusion**: Winners from the previous lottery are temporarily excluded
- **Live Attendance Tracking**: Operator confirms or marks candidates as absent during the event
- **Manual Prize Selection**: Winners click to choose their prize from available artwork
- **Persistent Sessions**: Automatically saves state after every action; resume interrupted lotteries
- **Official Exports**: Generate Excel files with winners and complete audit trail
- **Per-Lottery Configuration**: Prizes can vary between lottery occasions
- **Mock Data**: Reproducible test data with 100 participants and 20 artwork pieces

## Quick Test (5 minutes)

### Prerequisites

- Python 3.12 or later
- micromamba (or conda/mamba)

### 1. Clone and Navigate
```bash
git clone <repo-url>
cd kulturella_klubben
```

### 2. Create Environment
```bash
# If using micromamba (recommended)
micromamba create -n kultur python=3.12 -y
micromamba activate kultur

# Or with conda
conda create -n kultur python=3.12 -y
conda activate kultur
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Generate Mock Data
```bash
python generate_mock_data.py
```

This creates:
- 100 test participants in `data/participants/participants.xlsx`
- 20 test artwork prizes in `data/sessions/2026-05-06/prizes.xlsx`
- Generated placeholder images in `data/sessions/2026-05-06/prize_images/`

### 5. Run Tests
```bash
pytest tests -v
```

Expected: **18 tests pass** covering draw rules, persistence, Excel I/O, and UI logic.

### 6. Launch the App
```bash
python -m app.main
```

A Qt window opens showing:
- Prize grid on the left
- Draw/Confirm/Not Present controls in the center
- Winners table and status panel on the right

### 7. Test Workflow

1. Click **DRAW** – a random participant is selected
2. Click **Confirm** or **Not Present** depending on their presence
3. If confirmed, click a prize in the grid to assign it
4. Repeat until all prizes are assigned or you quit
5. Check `data/sessions/2026-05-06/` for output files:
   - `winners.xlsx` – final winners and prize choices
   - `event_log.xlsx` – audit trail of all actions
   - `session_state.json` – resumable session state

## Project Structure

```
kulturella_klubben/
  app/
    controllers/         # AppController, LotteryController
    models/             # Domain entities (Participant, Prize, SessionState, etc.)
    services/           # DrawEngine, repositories, persistence, Excel export
    views/              # Qt widgets (MainWindow, prize grid, candidates, winners table)
    utils/              # Helper functions
    main.py             # Application entry point

  tests/                # 18 pytest tests (all passing)
    test_*.py           # Unit and integration tests

  config/
    config.yaml         # Configuration: paths, rules, UI settings

  data/
    participants/
      participants.xlsx # Global participant list (used for all lotteries)
    sessions/
      2026-05-06/      # Per-lottery folder (created per date)
        prizes.xlsx    # Prize list for this lottery (must be prepared manually)
        prize_images/  # Images referenced by prizes.xlsx
        winners.xlsx   # Generated: final winners
        event_log.xlsx # Generated: action audit trail
        session_state.json # Generated: resumable state
        event_log.jsonl    # Generated: raw event log

  QUICKSTART.md         # Operational guide for running lotteries
  requirements.txt      # Python dependencies
  generate_mock_data.py # Script to create reproducible test data
  pyproject.toml        # Poetry/setuptools configuration
```

## Architecture Highlights

### Domain-Driven Design
- Pure business logic in `DrawEngine` and `LotteryController` (no Qt dependencies)
- Easily testable; 18 tests with 100% pass rate

### MVC + Service Layer
- **Views**: Qt widgets (MainWindow, PrizeGridWidget, etc.)
- **Controllers**: AppController (initialization), LotteryController (draw workflow)
- **Models**: Immutable domain entities with JSON serialization
- **Services**: DrawEngine, repositories, persistence, Excel export

### Guaranteed Persistence
- `session_state.json` is the authoritative live state
- `event_log.jsonl` records every action for auditing
- State saved immediately after each button click
- Resume dialog on startup if session interrupted

### Business Rules (All Tested)
1. Previous lottery winners are excluded until 3 confirmed winners exist in current lottery
2. A participant can win at most once per lottery
3. Absent candidates do not consume prizes and don't count toward the winner threshold
4. Lottery ends when all prizes are assigned

## Configuration

Edit `config/config.yaml` to customize:

```yaml
app:
  title: Kulturella Klubben Lottery
  autosave: true

paths:
  participants_excel: data/participants/participants.xlsx
  sessions_root: data/sessions

session:
  resume_same_day: true
  snapshot_inputs: true
  export_excel_after_each_action: true

rules:
  previous_winners_excluded_until_confirmed_winners: 3
  max_wins_per_participant_per_session: 1
```

## Development

### Run Tests
```bash
pytest tests -v          # All tests
pytest tests/test_draw_engine.py -v  # Specific test file
pytest -k "previous_winners" -v       # Tests matching a name
```

### Generate Mock Data for a Custom Date
```python
from app.services.mock_data_generator import MockDataGenerator
from pathlib import Path

MockDataGenerator.generate_all(
    Path("data"),
    session_date="2026-05-20",
    participant_count=100,
    prize_count=20
)
```

### Extend the Application

**Add a new feature**:
1. Define domain logic in `models/` or `services/`
2. Write tests in `tests/`
3. Wire into `controllers/` and `views/`

**Example**: Add "undo last action" button
1. Add `undo()` method to `LotteryController`
2. Test in `test_lottery_controller.py`
3. Add button to `MainWindow` and wire `clicked` signal

## Operational Workflow

For each lottery occasion:

1. **Create session folder**: `data/sessions/YYYY-MM-DD/`
2. **Prepare prizes**: Place `prizes.xlsx` in that folder
3. **Launch app**: `python -m app.main`
4. **Run drawing**: Use UI to draw, confirm presence, assign prizes
5. **Export results**: Close app; winners and audit logs are in the session folder

See [QUICKSTART.md](QUICKSTART.md) for detailed operational guide.

## Technical Stack

- **Language**: Python 3.12+
- **GUI**: PySide6 (Qt 6 for Python)
- **Spreadsheet I/O**: openpyxl
- **Configuration**: PyYAML
- **Testing**: pytest
- **Images**: Pillow

## Troubleshooting

### Error: "Prizes file not found"
Ensure `data/sessions/YYYY-MM-DD/prizes.xlsx` exists before launching the app.

### Error: "No eligible participants"
All participants have already won this lottery. Confirm you have enough participants for the number of prizes.

### App won't start
Confirm Python 3.12+ is active: `python --version`

### Tests fail
Ensure all dependencies installed: `pip install -r requirements.txt`

## Next Steps

- Use `QUICKSTART.md` to run your first real lottery
- Customize prizes, participants, and rules in config
- Extend with new features (see Development section)
- Deploy to a lottery machine or share with the committee

## Architecture & Design Doc

See [architecture_plan.md](architecture_plan.md) for complete technical specification including:
- State machine diagram
- Eligibility algorithm
- Persistence model
- File contracts
- Phased implementation plan

## License

[Add your license here]

## Contact

[Add contact information]