# MediumBot 🧠

MediumBot is a Telegram bot that automatically fetches and posts Medium articles based on a specific hashtag to a designated channel or chat. It supports admin-only commands, logs events, and is easily configurable through environment variables.

## 📦 Features

- Fetches latest Medium posts with a given hashtag
- Posts articles to a specified Telegram chat/channel
- Admin-only command control (based on a private admin group or user IDs)
- Error and startup logs sent to a logging channel
- Configurable via `.env` file

## ⚙️ Setup

> **Prerequisite:** Python 3.11 must be installed.
> You can check your version using:
> ```bash
> python3 --version
> ```

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Dineshv52/mediumbot.git
   cd mediumbot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file**:
   ```
   bot_token=YOUR_TELEGRAM_BOT_TOKEN
   ADMIN_CHANNEL=-100xxxxxxxxxx        # Chat ID of the private admin group
   LOGS_CHANNEL=-100yyyyyyyyyy         # Chat ID of the logs channel
   ```

4. **Run the bot**:
   ```bash
   python3 bot.py
   ```

## 🔐 Admin Access

Only users who are part of the private `ADMIN_CHANNEL` can run sensitive commands like:

- `/startfeed` — starts the Medium scraping loop
- `/stopfeed` — stops the scraping
- `/settag <tag>` — sets the Medium tag to monitor
- `/setchat <chat_id>` — sets the target posting chat/channel

## 📤 Logging

- Bot sends startup success messages and error logs to the `LOGS_CHANNEL`.

## 📚 Commands

| Command        | Description                                |
|----------------|--------------------------------------------|
| `/start`       | Check if the bot is online                 |
| `/settag`      | Update the Medium tag to follow            |
| `/setchat`     | Set the Telegram chat ID to post articles  |
| `/startfeed`   | Begin scheduled scraping and posting       |
| `/stopfeed`    | Stop the feed                              |

## 🤖 Notes

- The bot checks Medium every hour (`CHECK_INTERVAL` can be changed in code).
- Articles are deduplicated using a local file.

## 🛠 License

MIT License
