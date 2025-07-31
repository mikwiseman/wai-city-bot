# WAI City - Historical Photo to Video Telegram Bot

A Telegram bot that finds historical photos from PastVu based on location and generates videos using Runway API.

## Features

- **Location-based photo search**: Send your location to find nearby historical photos
- **AI-powered photo selection**: Uses OpenAI o3 model to select the best historical building/street photos
- **Video generation**: Creates animated videos from historical photos using Runway gen4_turbo
- **Progress tracking**: Real-time updates during video generation
- **Photo history**: Avoids showing the same photos multiple times

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure API keys in `.env`:
```
BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
RUNWAY_API_KEY=your_runway_api_key_here
```

3. Run the bot:
```bash
python main.py
```

## Usage

1. Start the bot with `/start`
2. Share your location using:
   - Telegram's location sharing feature
   - The "📍 Share Location" button
3. The bot will:
   - Search for historical photos near your location (up to year 1928)
   - Use AI to select the best photo for video generation
   - Show you the selected photo with options to:
     - 📍 Send new location
     - 🖼 Another photo (excludes already shown photos)
     - 🎬 Make video
4. If you choose "Make video", the bot will:
   - Generate a 5-second video with camera movement and colorization
   - Show progress updates every 3 seconds
   - Send the completed video

## Technical Details

- **Framework**: aiogram 3.21 (async)
- **APIs**: 
  - PastVu API for historical photos
  - OpenAI o3 model for photo selection
  - Runway gen4_turbo for video generation
- **State Management**: FSM for handling user flow
- **Photo Memory**: Tracks shown photos per session