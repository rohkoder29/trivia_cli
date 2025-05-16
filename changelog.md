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
---