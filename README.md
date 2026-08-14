# Infinite Image v1.3.0

A local Windows image conversion and resizing app.

## Changes in v1.3.0
- Renamed UI to **Infinite Image**.
- Added the supplied Infinite Image logo to the sidebar.
- Improved preview rendering for large, transparent and portrait/landscape images.
- Improved dark-mode list readability with strong selected/unselected contrast.
- Single-image Convert now opens **Save As** so you can choose the exact output filename and location.
- Single-image Resize now opens **Save As** so you can choose the exact output filename and location.
- Batch jobs continue to use the selected output folder and automatic source-based names.
- Updated executable, spec and Inno Setup installer names.

## Build
1. Run `build.bat`.
2. Test `dist\InfiniteImage.exe`.
3. Open `installer.iss` in Inno Setup and compile it.
4. Share `installer_output\InfiniteImage_Setup_v1.3.0.exe`.


## v1.3.0 UI fix
- Primary Convert & Save / Resize & Save actions are pinned to the bottom of the workspace and are always visible.
- Settings are vertically scrollable on smaller screens.
- Single-image jobs use Save As for the exact output filename.
- Batch jobs keep automatic output naming.
- Preview remains visible while settings are scrolled.


## v1.3.0 layout
- Preview panel has its own independent scrollbar.
- Conversion/resize settings have their own independent scrollbar.
- The primary action is pinned to the bottom of the right panel.
- With one image selected, the primary button is explicitly **Save As…**.
- With multiple images selected, the primary button becomes **Convert & Save All** or **Resize & Save All**.
