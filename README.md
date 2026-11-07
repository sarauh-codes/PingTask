# PingTask

**A Telegram-Based Group Task Management and Automated Reminder System**

## About

PingTask is a Python-based Telegram bot designed to help student groups and small teams manage tasks, assign responsibilities, track deadlines, and receive automated reminders.

The bot provides a simple way to coordinate group work directly within Telegram without requiring a separate task management application.

## Features

- Create and assign tasks.
- View all pending group tasks.
- View your own pending tasks.
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
# Optional: where the SQLite database is stored (default: pingtask.db)
# DATABASE_PATH=pingtask.db
```

`BOT_TOKEN` is required. `TIMEZONE` defaults to `Asia/Kuala_Lumpur`.

Never upload your actual `.env` file or Telegram bot token to GitHub.

### 5. Run the Bot

```bash
python src/bot.py
```

The bot must keep running for reminders to be sent. Stop it with `Ctrl+C`.

## Available Commands

| Command | Description |
|---|---|
| `/start` | Start the bot |
| `/help` | Show available commands |
| `/todo @username Task description by Date/Time` | Create a task, for example `/todo @sarah Finish schema db by tomorrow 5pm` |
| `/tasks` | View all pending tasks in this group |
| `/mytasks` | View your pending tasks in this group |
| `/done <task ID>` | Mark a task as completed, for example `/done 3` |

Only the task's assignee or creator can mark it as completed.

## Reminders

Every 10 minutes, the bot checks for pending tasks due within the next 24 hours. It sends one reminder per task to the group and does not repeat it. Completed and overdue tasks are skipped.

## Running Tests

```bash
python -m unittest discover -s tests
```

The tests use mocks and in-memory databases, so they do not contact Telegram.

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

All planned features are implemented and tested. See `docs/06_TESTING_PLAN.md` for the test results.

## Contributors

@sarauh-codes

## License

For academic and educational purposes.
