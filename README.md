[README.md](https://github.com/user-attachments/files/34233285/README.md)
# PingTask

**A Telegram-Based Group Task Management and Automated Reminder System**

## About

PingTask is a Python-based Telegram bot designed to help student groups and small teams manage tasks, assign responsibilities, track deadlines, and receive automated reminders.

The bot provides a simple way to coordinate group work directly within Telegram without requiring a separate task management application.

## Features

- Create and assign tasks.
- View all pending group tasks.
- Mark tasks as completed.
- Automatically remind members about upcoming deadlines.
- Store task information using SQLite.
- Support multiple Telegram groups.

## Technology Stack

- Python
- python-telegram-bot
- SQLite
- APScheduler
- dateparser
- python-dotenv

## Installation

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd PingTask
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment:

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file:

```env
BOT_TOKEN=your_telegram_bot_token
TIMEZONE=Asia/Kuala_Lumpur
```

Never upload your actual `.env` file or Telegram bot token to GitHub.

### 5. Run the Bot

```bash
python src/bot.py
```

## Available Commands

| Command | Description |
|---|---|
| `/start` | Start the bot |
| `/help` | Show available commands |
| `/todo` | Create a task |
| `/tasks` | View pending tasks |
| `/done` | Mark a task as completed |

## Project Structure

```text
PingTask/
├── docs/
├── src/
├── tests/
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Project Status

Currently under development.

## Contributors

Add your group members' names here.

## License

For academic and educational purposes.
