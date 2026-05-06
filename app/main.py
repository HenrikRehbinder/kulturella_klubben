from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.controllers.app_controller import AppController
from app.services.config_loader import load_config
from app.views.main_window import MainWindow
from app.views.resume_dialog import ResumeDialog


def main() -> None:
    config = load_config(Path("config/config.yaml"))
    print(f"Loaded configuration for {config.title}.")

    app_controller = AppController(config)
    
    # Check for unfinished session
    force_new = False
    if app_controller.has_unfinished_session():
        # Create Qt app temporarily to show dialog
        qt_app = QApplication(sys.argv)
        dialog = ResumeDialog(app_controller.session_dir)
        dialog.exec()
        if dialog.get_action() == ResumeDialog.NEW_SESSION:
            force_new = True
    else:
        qt_app = QApplication(sys.argv)

    session, controller = app_controller.initialize_session(force_new=force_new)

    print(f"Session initialized for {session.session_date}")
    print(f"Participants: {len(session.participants)}")
    print(f"Prizes: {len(session.prizes)}")

    # Launch Qt application
    if 'qt_app' not in locals():
        qt_app = QApplication(sys.argv)
    window = MainWindow(session, controller)
    window.show()
    sys.exit(qt_app.exec())


if __name__ == "__main__":
    main()