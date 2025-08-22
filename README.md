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

### Coming Soon
- **Bookmarks**: Search and open bookmarks across all profiles
- **Tabs**: Search and switch to open tabs

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

## Configuration (Optional)

Most users don't need any configuration. The workflow automatically detects Edge and Python installations.

### Custom Installations

If you have Edge or Python in non-standard locations, you can configure paths in Alfred:

1. Select the workflow in Alfred Preferences
2. Click `[x]` button (Configure Workflow)
3. Add environment variables as needed:

| Variable | Description | Default |
|----------|-------------|---------|
| `PYTHON_PATH` | Custom Python path | System Python |
| `EDGE_APP` | Edge application path | `/Applications/Microsoft Edge.app` |
| `EDGE_USER_DATA_DIR` | Edge data directory | `~/Library/Application Support/Microsoft Edge` |

### Common Configurations

**Using Homebrew Python (Apple Silicon):**
```
PYTHON_PATH: /opt/homebrew/bin/python3
```

**Using Edge Beta:**
```
EDGE_APP: /Applications/Microsoft Edge Beta.app
EDGE_USER_DATA_DIR: ~/Library/Application Support/Microsoft Edge Beta
```

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