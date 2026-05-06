from pathlib import Path

import pytest

from app.controllers.app_controller import AppController
from app.services.config_loader import AppConfig


@pytest.fixture
def tmp_app_config(tmp_path: Path) -> AppConfig:
    """Create a temporary config pointing to test data directories."""
    data_dir = tmp_path / "data"
    participants_dir = data_dir / "participants"
    sessions_dir = data_dir / "sessions"

    participants_dir.mkdir(parents=True)
    sessions_dir.mkdir(parents=True)

    # Create test participants Excel
    try:
        from openpyxl import Workbook
    except ImportError:
        pytest.skip("openpyxl not installed")

    participants_file = participants_dir / "participants.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["email", "first_name", "last_name"])
    sheet.append(["alice@example.com", "Alice", "Alpha"])
    sheet.append(["bob@example.com", "Bob", "Beta"])
    workbook.save(participants_file)

    # Create test image files and prizes Excel in session folder
    session_dir = sessions_dir / "2026-05-06"
    session_dir.mkdir(parents=True)

    image1 = session_dir / "prize1.png"
    image1.write_text("fake image 1")
    image2 = session_dir / "prize2.png"
    image2.write_text("fake image 2")

    prizes_file = session_dir / "prizes.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["prize_id", "title", "description", "image_path"])
    sheet.append(["p1", "Prize One", "First prize", str(image1)])
    sheet.append(["p2", "Prize Two", "Second prize", str(image2)])
    workbook.save(prizes_file)

    return AppConfig(
        title="Test Lottery",
        autosave=True,
        participants_excel=participants_file,
        sessions_root=sessions_dir,
        resume_same_day=True,
        snapshot_inputs=True,
        export_excel_after_each_action=True,
        previous_winners_excluded_until_confirmed_winners=3,
        max_wins_per_participant_per_session=1,
    )


def test_app_controller_creates_new_session(tmp_app_config: AppConfig) -> None:
    """Test that AppController creates a new session when none exists."""
    app = AppController(tmp_app_config)
    session, controller = app.initialize_session()

    assert session.session_date == app.today
    assert len(session.participants) == 2
    assert len(session.prizes) == 2
    assert session.status == "ready_to_draw"


def test_app_controller_resumes_existing_session(tmp_app_config: AppConfig) -> None:
    """Test that AppController resumes an existing session."""
    app = AppController(tmp_app_config)

    # Create initial session
    session1, _ = app.initialize_session()
    session1.winners = []  # Simulate no winners yet

    # Create a second controller pointing to same config
    app2 = AppController(tmp_app_config)
    session2, _ = app2.initialize_session()

    # Should have same session date
    assert session2.session_date == session1.session_date
    assert len(session2.participants) == 2


def test_app_controller_snapshots_inputs_when_configured(tmp_app_config: AppConfig) -> None:
    """Test that input files are snapshotted when configured."""
    app = AppController(tmp_app_config)
    session, _ = app.initialize_session()

    session_dir = tmp_app_config.sessions_root / app.today
    assert (session_dir / "participants_snapshot.xlsx").exists()
    assert (session_dir / "prizes_snapshot.xlsx").exists()
