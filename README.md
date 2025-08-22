# Edge Alfred Workflow

Control the Microsoft Edge browser directly from Alfred. Search and switch between profiles and workspaces, with more features coming soon.

## Features

### Profile Management

- **Search Edge profiles** by name, email, or profile directory
- **Quickly open** windows with different Edge profiles

### Workspace Management

- **Search Edge workspaces** across all profiles
- **View workspace details** including tab count and last active time
- **Quickly open** any workspace with its associated profile
- **Active workspace indicator** shows which workspace is currently in use

### Tab Search & Switching

- **Search all open tabs** across windows and profiles
- **Quick switch** to any tab with a single keystroke
- **Copy URLs** or close tabs with modifier keys
- **See tab associations** with profiles and workspaces

### Coming Soon
- **Bookmarks**: Search and open bookmarks across all profiles

## Known Limitations

Due to macOS system design, there are some limitations with window activation:

### Window Activation Behavior

| Feature | Behavior | Note |
|---------|----------|------|
| **Profile Opening** | ✅ Only activates the new window | Opens with configurable URL (default: `edge://newtab`) |
| **Workspace Opening** | ⚠️ Activates all Edge windows | macOS limitation - brings all windows forward |
| **Tab Switching** | ⚠️ Activates all Edge windows | macOS limitation - brings all windows forward |

**Why this happens:** 
- macOS is designed to bring all application windows to the front when an app is activated. This is standard behavior across most Mac applications.
- The Profile feature can avoid this by using a special activation method. You can configure which URL to open via the `EDGE_PROFILE_START_URL` setting.
- Workspace and Tab features must use standard activation, which brings all windows forward.

## Installation

### Quick Setup

1. Download Edge Control.alfredworkflow from the [releases page](https://github.com/jiywww/edge-alfred-workflow/releases)
2. Double-click the `.alfredworkflow` file to install

## Usage

### Search Profiles

1. Open Alfred
2. Type `ep` followed by your profile name set in Edge.
3. Press `↩` to open Edge with the selected profile
4. Press `⌥` + `↩` to copy the profile directory name

Example searches:
- `ep work` - Find your work profile
- `ep john@` - Find profile by email
- `ep` - List all profiles

### Search Workspaces

1. Open Alfred
2. Type `ew` followed by your workspace name
3. Press `↩` to open the workspace in Edge
4. Press `⌥` + `↩` to copy the workspace ID
5. Press `⌘` + `↩` to view workspace details

Example searches:
- `ew project` - Find workspace named "project"
- `ew test` - Find workspaces containing "test"
- `ew` - List all workspaces sorted by recent activity

Workspace indicators:
- 📂 Active workspace currently in use
- 👥 Shared workspace (if using Edge for Business)

### Search Tabs

1. Open Alfred
2. Type `et` followed by your search query
3. Press `↩` to switch to the selected tab
4. Press `⌘` + `↩` to copy the tab's URL
5. Press `⌥` + `↩` to close the tab

Example searches:
- `et github` - Find tabs with "github" in title or URL
- `et youtube` - Find YouTube tabs
- `et` - List all open tabs

Tab indicators:
- ⭐ Currently active tab
- 📂 Tab belongs to a workspace
- Profile and email shown for each tab

## Configuration (Optional)

Most users don't need any configuration. The workflow automatically detects Edge and Python installations.

### User Configuration

To customize the workflow:

1. Right-click the workflow in Alfred Preferences
2. Select "Configure..." 
3. Adjust any of the following settings:

| Setting | Description | Default |
|---------|-------------|---------|
| **Profile Start URL** | URL to open when launching a new profile window | `edge://newtab` |
| **Python Path** | Custom Python 3 path (leave empty for system default) | System Python |
| **Edge Application Path** | Path to Microsoft Edge app | `/Applications/Microsoft Edge.app` |
| **Edge User Data Directory** | Custom data directory (leave empty for default) | `~/Library/Application Support/Microsoft Edge` |

### Example Configurations

**Profile Start URL Options:**
- `edge://newtab` - Edge's new tab page (default)
- `about:blank` - Blank page
- `https://google.com` - Any website URL

**Using Homebrew Python (Apple Silicon):**
- Python Path: `/opt/homebrew/bin/python3`

**Using Edge Beta:**
- Edge Application Path: `/Applications/Microsoft Edge Beta.app`
- Edge User Data Directory: `~/Library/Application Support/Microsoft Edge Beta`


## Requirements

- macOS 11+ (Big Sur or later)
- Python 3.9+
- Microsoft Edge browser
- Alfred 4+ with Powerpack

## Troubleshooting

### Profiles not showing up?

- Fully quit Edge and try again (Edge needs to save profile data)
- Check if Edge is installed in the standard location

### Workflow not working?
- Verify Python 3 is installed: `python3 --version`
- Check Edge installation: `ls -la "/Applications/Microsoft Edge.app"`

## License

MIT License - See LICENSE file for details