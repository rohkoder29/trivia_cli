## [2.0.0] - 2025-05-16
### 🎯 Goal
Improve the command-line user experience with a clean and modern UI using the `rich` library.

### ✨ Added
- Integrated `rich` for visually enhanced terminal output.
- Styled question prompts using `Panel` and color-coded answer choices.
- Feedback for correct and incorrect answers shown with consistent, styled messages.
- Question progress indicator during gameplay.
- High scores now rendered with `rich.Table` and sorted with ranks.

### 🛠 Changed
- Replaced raw `print()`/`input()` calls with `rich.console.Console`.
- All file I/O now explicitly uses `encoding="utf-8"` for reliability across platforms.
- Added `.gitignore` to avoid tracking unnecessary files and folders.
- Created `requirements.txt` for easy dependency management (`rich`).

### Notes
- Foundation laid for future enhancements like progress bars and animations

## [2.1.0] - 2025-05-16
### Added
- Username input is now sanitized both on entry and display (e.g., trims spaces).
- High scores are now validated before use (e.g., format, number of fields, score value).
- Scores must now be valid integers and multiple of 3 (matching game logic).
- Malformed high score entries are ignored at load time.

### Changed
- High scores are stored in-memory after playing, avoiding repeated disk reads.
- Improved reliability of score updates and leaderboard display.

### Fixed
- Bug where incorrect high score rows would result in an empty leaderboard.
- Prevented accidental overwrites of valid scores when bad entries are present.
