# Lottery Application Architecture And Implementation Plan

## 1. Scope

This document refines the requirements in `system_description.md` into a concrete technical design for a Qt-based desktop application that runs a recurring lottery.

The application must:

- load eligible participants from Excel
- load a fixed prize list for the current lottery occasion
- draw winners according to the lottery rules
- support live operator decisions for presence and prize selection
- autosave after every operator action
- restart safely after interruption
- export official results to Excel

## 2. Clarified Business Rules

### 2.1 Participant identity

- The unique identifier for a participant is `email`.
- Participant input columns are:
  - `email`
  - `first_name`
  - `last_name`

### 2.2 Prize list

- Each lottery occasion starts with a prepared prize list.
- The prize list is fixed before the event and is not edited during the lottery.
- Each prize has an image and text metadata.

### 2.3 Winner eligibility

- A participant can win at most once in the current lottery occasion.
- Winners from the previous lottery occasion are temporarily excluded.
- The temporary exclusion lasts until the current lottery has produced 3 confirmed winners.
- "Confirmed winners" means winners whose presence has been confirmed by the operator.
- A draw marked as `not_present` does not count toward the first 3 winners.
- After 3 confirmed winners, previous-lottery winners return to the eligible pool.

### 2.4 Presence and redraws

- After each draw, the operator decides whether the candidate is present.
- If the candidate is not present, the draw is logged and no prize is consumed.
- The operator then draws again.

### 2.5 Prize assignment

- If the candidate is confirmed present, the operator confirms the candidate.
- Prize selection is manual and done by clicking an available prize in the UI.
- Once selected, that prize becomes unavailable for future winners.

### 2.6 Completion condition

- The lottery ends when there are no prizes left.

### 2.7 Persistence and recovery

- The application must be restartable.
- Every button click and state-changing action must be saved immediately.
- The application must be able to resume an interrupted lottery session.

### 2.8 Official output

- The official winner export is an Excel file with columns:
  - `email`
  - `first_name`
  - `last_name`
  - `chosen_prize`

## 3. Architectural Decisions

### 3.1 Technology stack

- Language: Python 3.12+
- GUI: PySide6
- Spreadsheet I/O: `pandas` with `openpyxl`
- Configuration: YAML
- Runtime persistence: JSON and JSON Lines
- Tests: `pytest`

### 3.2 Architectural style

The application should use MVC at the UI level, plus a service layer for business logic and persistence.

- Model: domain entities and session state
- View: Qt widgets and dialogs
- Controller: user actions and workflow orchestration
- Services: draw logic, Excel import/export, state persistence, config handling

This separation keeps draw logic testable without Qt and keeps file I/O out of UI code.

### 3.3 Source of truth

The runtime source of truth must not be Excel.

Instead:

- `session_state.json` is the authoritative current session state
- `event_log.jsonl` is the append-only audit log of actions
- Excel files are import and export artifacts

This is necessary for recovery, auditing, and safe undo.

## 4. High-Level Architecture

## 4.1 Main components

1. `ConfigLoader`
   Loads and validates application configuration.

2. `ParticipantRepository`
   Loads participant data from Excel.

3. `PrizeRepository`
   Loads prize definitions from Excel.

4. `PreviousWinnersRepository`
   Loads the previous lottery winners from the latest earlier session folder.

5. `DrawEngine`
   Computes the eligible pool and selects the next candidate.

6. `SessionStore`
   Creates today's folder, saves state, appends audit events, and restores sessions.

7. `ExcelExporter`
   Writes winners and action logs to Excel.

8. `LotteryController`
   Handles draw, confirm, not present, prize assignment, undo, and completion.

9. `MainWindow`
   Coordinates the visible UI and binds widgets to controller actions.

## 4.2 Data flow

1. App starts.
2. Config is loaded.
3. Participants and prepared prizes are loaded.
4. Previous winners are loaded from the latest earlier session.
5. A new session is created or an unfinished session for today is resumed.
6. Operator interacts through the UI.
7. Every state-changing action is persisted immediately.
8. Winners and logs are continuously exportable and final outputs remain in today's folder.

## 5. Domain Model

## 5.1 Participant

Fields:

- `email: str`
- `first_name: str`
- `last_name: str`

## 5.2 Prize

Fields:

- `prize_id: str`
- `title: str`
- `description: str`
- `image_path: str`
- `is_available: bool`

## 5.3 DrawAttempt

Represents each draw whether successful or not.

Fields:

- `attempt_id: str`
- `timestamp: str`
- `email: str`
- `first_name: str`
- `last_name: str`
- `result: str`
- `details: str`

Allowed results:

- `drawn`
- `not_present`
- `confirmed`
- `finalized`
- `undone`

## 5.4 WinnerRecord

Fields:

- `email: str`
- `first_name: str`
- `last_name: str`
- `chosen_prize: str`
- `confirmed_at: str`

## 5.5 PendingWinner

Needed for restart safety between `Confirm` and prize selection.

Fields:

- `email: str`
- `first_name: str`
- `last_name: str`
- `confirmed_at: str`

## 5.6 LotterySession

Fields:

- `session_date: str`
- `participants: list[Participant]`
- `prizes: list[Prize]`
- `winners: list[WinnerRecord]`
- `draw_attempts: list[DrawAttempt]`
- `previous_winner_emails: set[str]`
- `pending_winner: PendingWinner | None`
- `status: str`

Allowed statuses:

- `ready_to_draw`
- `candidate_drawn`
- `awaiting_prize_selection`
- `completed`

## 6. Session State Machine

The session should behave like a small state machine.

### 6.1 `ready_to_draw`

- `DRAW` is enabled
- `Confirm` is disabled
- `Not present` is disabled
- available prizes are visible

Transition:

- `DRAW` -> `candidate_drawn`

### 6.2 `candidate_drawn`

- a candidate is visible in the UI
- `DRAW` is disabled
- `Confirm` is enabled
- `Not present` is enabled

Transitions:

- `Not present` -> `ready_to_draw`
- `Confirm` -> `awaiting_prize_selection`

### 6.3 `awaiting_prize_selection`

- confirmed winner is visible
- prize grid is active for remaining prizes
- operator must select a prize

Transition:

- `Prize selected` -> `ready_to_draw` or `completed`

### 6.4 `completed`

- all prizes assigned
- drawing actions disabled
- final exports remain available

## 7. Eligibility Algorithm

## 7.1 Candidate pool calculation

To compute the current eligible pool:

1. Start with all participants.
2. Remove all participants who have already won in the current session.
3. If the number of confirmed winners in the current session is less than 3, remove all participants who won in the previous session.
4. Draw uniformly at random from the remaining participants.

## 7.2 Important rule interpretation

The "first three drawings" rule is interpreted as "first three confirmed winners".

That means:

- confirmed winners count toward the threshold
- absent participants do not count toward the threshold
- previous winners remain excluded until 3 confirmed winners exist

## 8. Persistence Design

## 8.1 Folder structure

Recommended structure:

```text
data/
  participants/
    participants.xlsx
  sessions/
    2026-05-06/
      prizes.xlsx
      prize_images/ (optional, referenced by prizes.xlsx)
      participants_snapshot.xlsx
      winners.xlsx
      event_log.xlsx
      event_log.jsonl
      session_state.json
      assets/
    2026-05-13/
      prizes.xlsx
      ...
```

## 8.2 Why snapshots matter

At session start, the app should copy the current participant and prize inputs into the session folder as snapshots.

This makes the session reproducible even if the source files later change.

## 8.3 `session_state.json`

This file should contain:

- session metadata
- current UI state
- current candidate if one is drawn
- pending winner if one is confirmed but no prize has been chosen yet
- remaining prizes
- finalized winners
- previous-winner exclusion data
- undo metadata

## 8.4 `event_log.jsonl`

Append one event per action. Example event types:

- `session_created`
- `session_resumed`
- `draw_performed`
- `candidate_marked_not_present`
- `candidate_confirmed`
- `prize_assigned`
- `undo_last_action`
- `session_completed`

## 8.5 Excel outputs

Maintain these Excel outputs in the session folder:

- `winners.xlsx`
- `event_log.xlsx`

These can be refreshed after every state change to keep operator-visible artifacts current.

## 9. File Contracts

## 9.1 Participant input Excel

Required columns:

- `email`
- `first_name`
- `last_name`

Validation rules:

- email must be unique
- email must not be empty
- first and last names must not be empty

## 9.2 Prize input Excel (per lottery)

Location: `data/sessions/YYYY-MM-DD/prizes.xlsx`

Required columns:

- `prize_id`
- `title`
- `description`
- `image_path`

Notes:

- This file must be prepared manually before each lottery
- Image paths can be absolute or relative to the session folder
- Prizes are stored per-session, not globally, so they can vary between lottery occasions
- If using local images, store them in `data/sessions/YYYY-MM-DD/prize_images/`

Validation rules:

- `prize_id` must be unique within the lottery
- `image_path` must point to an existing image file

## 9.3 Winners output Excel

Required columns:

- `email`
- `first_name`
- `last_name`
- `chosen_prize`

## 9.4 Event log Excel

Recommended columns:

- `timestamp`
- `action_type`
- `email`
- `first_name`
- `last_name`
- `prize_id`
- `prize_title`
- `details`

## 10. Configuration Design

Recommended file: `config/config.yaml`

Example structure:

```yaml
app:
  title: Kulturella Klubben Lottery
  autosave: true
  random_seed: null

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

ui:
  prize_grid_columns: 4
  image_thumbnail_width: 180
  image_thumbnail_height: 180
```

Notes:

- `participants_excel` points to the global participant file used for all lotteries
- Prizes are no longer configured globally; they must be placed in `sessions_root/YYYY-MM-DD/prizes.xlsx`
- The app expects `prizes.xlsx` to exist in the current session folder before starting

## 11. Module Layout

Recommended project structure:

```text
app/
  main.py
  controllers/
    app_controller.py
    lottery_controller.py
  models/
    participant.py
    prize.py
    draw_attempt.py
    winner_record.py
    session_state.py
  services/
    config_loader.py
    participant_repository.py
    prize_repository.py
    previous_winners_repository.py
    draw_engine.py
    session_store.py
    excel_exporter.py
    mock_data_generator.py
  views/
    main_window.py
    prize_grid_widget.py
    current_candidate_widget.py
    winners_table_widget.py
    session_status_widget.py
    resume_dialog.py
  utils/
    paths.py
    time_utils.py
    validation.py

tests/
  test_draw_engine.py
  test_session_store.py
  test_excel_exporter.py
  test_resume_flow.py
  test_undo_flow.py
```

## 12. Controller Responsibilities

## 12.1 `AppController`

- load config
- initialize repositories and services
- open a new session or resume an existing one
- create the main window

## 12.2 `LotteryController`

- compute the next candidate through `DrawEngine`
- apply `Confirm` and `Not present`
- finalize prize assignment
- manage undo actions
- trigger persistence after each action
- expose UI-safe state to the view layer

## 12.3 View layer

The view layer should:

- render current state
- forward user actions to the controller
- avoid business logic decisions
- avoid direct file I/O

## 13. Undo Strategy

At minimum support undo of the latest action.

Supported undo cases:

- undo last `not_present`
- undo latest `confirm`
- undo latest `prize_assigned`

Implementation approach:

- append every action to the event log
- rebuild state from `session_state.json` plus recent metadata, or revert from a saved pre-action snapshot in memory
- persist the corrected state immediately after undo

Simplest safe design:

- support only single-step undo of the most recent action
- disable undo when a new unrelated action has already advanced the session

## 14. Error Handling Requirements

The app should block startup or session creation if:

- participant Excel is missing
- prize Excel is missing
- required columns are missing
- duplicate participant emails exist
- duplicate prize IDs exist
- prize image paths are invalid

The app should show operator-facing errors for:

- empty eligible pool
- corrupted session state on resume
- export failure
- failed autosave

## 15. Test Plan

Critical tests:

1. previous winners are excluded until 3 confirmed winners exist
2. absent participants do not count toward the threshold
3. a participant cannot win twice in one session
4. confirming a winner requires later prize assignment before the next draw
5. resuming after interruption restores the exact state
6. undo restores prizes and winner state correctly
7. outputs match the required Excel columns

## 16. Mock Data Plan

Create reproducible local mock data instead of fetching images from the internet.

Recommended mock assets:

- 100 generated participants with realistic names and unique emails
- 20 local placeholder artwork images
- 20 prize definitions referencing those local images

This avoids external dependencies and avoids copyright issues.

## 17. Phased Implementation Plan

## Phase 1: Project skeleton

- create package structure
- create config loader
- create startup entry point
- add dependency management

Deliverable:

- app starts and validates config

## Phase 2: Data import and validation

- implement participant import
- implement prize import
- implement previous winner lookup
- validate schemas and uniqueness constraints

Deliverable:

- app loads all source data correctly

## Phase 3: Core lottery engine

- implement domain models
- implement eligible pool calculation
- implement draw logic
- implement current-session no-repeat rule

Deliverable:

- draw engine passes rule tests without UI

## Phase 4: Session persistence

- implement session folder creation
- snapshot input files
- write `session_state.json`
- append `event_log.jsonl`
- export `winners.xlsx` and `event_log.xlsx`

Deliverable:

- every action is durably saved

## Phase 5: Main UI workflow

- implement main window
- implement prize grid
- implement candidate panel
- wire `DRAW`, `Confirm`, `Not present`
- wire manual prize selection

Deliverable:

- complete lottery flow works in the GUI

## Phase 6: Resume and undo

- resume same-day unfinished session
- restore pending winner state
- implement single-step undo

Deliverable:

- operator can recover from interruption and simple mistakes

## Phase 7: Mock data and polish

- generate mock participants and prizes
- improve operator messages
- finalize export formatting
- verify full-session behavior with sample data

Deliverable:

- demo-ready application with reproducible local test data

## 18. Recommended First Build Slice

Build this vertical slice first:

1. load config
2. load participants
3. load prizes
4. load previous winners
5. draw candidate
6. mark not present or confirm
7. select prize
8. autosave state and export winners

This is the smallest end-to-end slice that exercises the important rules and persistence behavior.

## 19. Open Decisions

These are no longer blockers, but they should be explicitly decided before implementation starts:

1. Should the app allow resuming only the current date, or any unfinished recent session?
2. Should undo be limited to one step, or support multiple sequential undo operations?
3. Should Excel exports be rewritten after every action, or only on meaningful milestones plus explicit save?
4. Should the event log remain JSON Lines only for runtime and Excel only for reporting, or should both always be maintained?

The recommended answer for the first implementation is:

- resume only today's unfinished session
- support single-step undo only
- export Excel after every action
- maintain both JSON Lines and Excel logs