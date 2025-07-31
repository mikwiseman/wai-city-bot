# CLAUDE.md - Project Information for AI Assistants

## Project Overview
This is a Python project named "wai-city" located at `/Users/mikwiseman/Documents/Code/Py/wai-city/`.

## Project Structure
- `main.py` - Main entry point of the application

## Development Commands
<!-- Add commonly used commands here as you discover them -->
### Linting
<!-- Add linting command when discovered -->

### Type Checking
<!-- Add type checking command when discovered -->

### Testing
<!-- Add testing command when discovered -->

### Running the Application
<!-- Add run command when discovered -->

## Dependencies
<!-- List main dependencies and their purposes -->

## Important Notes
<!-- Add any project-specific conventions, patterns, or important information -->

## Recent Context
- Project initialized with first commit
- Currently on main branch
- Added address geocoding functionality:
  - Users can now send text addresses instead of just sharing location
  - OpenAI o3 model converts addresses to coordinates
  - Integrated with existing photo finding flow
- Enhanced location handling:
  - Location sharing now works from any state (not just waiting_for_location)
  - Added options menu when location is shared (use as-is or change)
  - Locations are now displayed as Telegram venues (native map view)
  - Users can tap venues to open in their preferred maps app
  - Smooth flow for changing locations during photo browsing
- Map picker functionality:
  - Updated UI to guide users on using Telegram's map picker
  - Added help button explaining how to drop pins anywhere on map
  - Users can navigate map and select any location, not just current
  - Clear instructions throughout the flow
- Enhanced location selection guidance:
  - Added explicit instructions to use "Send Selected Location" option
  - Created attachment menu guide as alternative method
  - Multiple help options to ensure users understand how to pick any location
  - Visual step-by-step guides for both methods

---
*This file helps AI assistants understand the project structure and common tasks. Update it as you learn more about the project.*