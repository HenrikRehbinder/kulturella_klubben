from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class AppConfig:
    title: str
    autosave: bool
    participants_excel: Path
    prizes_excel: Path
    sessions_root: Path
    resume_same_day: bool
    snapshot_inputs: bool
    export_excel_after_each_action: bool
    previous_winners_excluded_until_confirmed_winners: int
    max_wins_per_participant_per_session: int


def load_config(config_path: Path) -> AppConfig:
    try:
        import yaml
    except ModuleNotFoundError as exc:
        raise RuntimeError("PyYAML is required to load the config file.") from exc

    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    app = raw["app"]
    paths = raw["paths"]
    session = raw["session"]
    rules = raw["rules"]
    base_dir = config_path.parent.parent
    return AppConfig(
        title=app["title"],
        autosave=bool(app["autosave"]),
        participants_excel=(base_dir / paths["participants_excel"]).resolve(),
        prizes_excel=(base_dir / paths["prizes_excel"]).resolve(),
        sessions_root=(base_dir / paths["sessions_root"]).resolve(),
        resume_same_day=bool(session["resume_same_day"]),
        snapshot_inputs=bool(session["snapshot_inputs"]),
        export_excel_after_each_action=bool(session["export_excel_after_each_action"]),
        previous_winners_excluded_until_confirmed_winners=int(
            rules["previous_winners_excluded_until_confirmed_winners"]
        ),
        max_wins_per_participant_per_session=int(rules["max_wins_per_participant_per_session"]),
    )