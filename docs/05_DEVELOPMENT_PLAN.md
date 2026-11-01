# PingTask – Development Plan

## 1. Development Approach

PingTask will be developed using an incremental development approach.

The project will be divided into smaller modules. Each module will be implemented and tested before integration into the complete system.

This approach allows team members to work on separate components while reducing integration difficulties.

## 2. Development Phases

### Phase 1: Project Setup

Tasks:
- Create the GitHub repository.
- Set up the Python virtual environment.
- Install the required libraries.
- Create the project folder structure.
- Configure the Telegram bot through BotFather.
- Configure environment variables.
- Implement basic `/start` and `/help` commands.

Deliverable:

A working Telegram bot that can receive and respond to basic commands.

### Phase 2: Database Development

Tasks:
- Create the SQLite database.
- Implement database connection functions.
- Create the tasks table.
- Implement task insertion.
- Implement task retrieval.
- Implement task status updates.
- Test database operations.

Deliverable:

A functioning database module.

### Phase 3: Task Management Development

Tasks:
- Implement `/todo`.
- Implement `/tasks`.
- Implement `/mytasks`.
- Implement `/done`.
- Implement date and time parsing.
- Implement input validation.
- Implement error handling.

Deliverable:

Users can create, view, and complete tasks through Telegram.

### Phase 4: Reminder System Development

Tasks:
- Integrate APScheduler.
- Configure periodic scheduler execution.
- Implement the reminder checking function.
- Retrieve eligible tasks.
- Compare deadlines with the reminder window.
- Send reminder messages to Telegram groups.
- Prevent duplicate reminders.
- Handle failed notification delivery.

Deliverable:

A functioning automated deadline reminder system.

### Phase 5: Integration and Testing

Tasks:
- Integrate all Python modules.
- Test Telegram command handling.
- Test database operations.
- Test scheduler execution.
- Test multiple Telegram groups.
- Test invalid inputs.
- Fix bugs and improve error handling.

Deliverable:

A fully integrated and tested PingTask bot.

### Phase 6: Documentation and Presentation

Tasks:
- Complete project documentation.
- Prepare system architecture diagrams.
- Prepare database diagrams if required.
- Capture screenshots.
- Prepare a project demonstration.
- Prepare the final presentation.

Deliverable:

Final project submission.

## 3. Suggested Team Responsibilities

The following division assumes a group of four members.

| Member | Responsibility | Main Tasks |
|---|---|---|
| Member 1 | Telegram Bot Development | Bot setup, commands, handlers |
| Member 2 | Database Development | SQLite, database queries, data validation |
| Member 3 | Reminder System Development | APScheduler, deadline checking, notifications |
| Member 4 | Integration and Testing | Integration, test cases, documentation |

All members should participate in code reviews, integration, and final testing.

The responsibilities can be adjusted depending on the actual number of group members.

## 4. Suggested Timeline

| Week | Activities |
|---|---|
| Week 1 | Requirements gathering and project setup |
| Week 2 | Database design and implementation |
| Week 3 | Telegram command development |
| Week 4 | Reminder system development |
| Week 5 | Integration and testing |
| Week 6 | Documentation and final presentation |

## 5. Development Tools

- Python
- Visual Studio Code
- Git
- GitHub
- Telegram
- SQLite
- python-telegram-bot
- APScheduler
- dateparser
- python-dotenv

## 6. Version Control Strategy

GitHub will be used for source code management and collaboration.

Suggested branches:

- `main`: Stable and tested code.
- `development`: Combined development work.
- `feature/bot`: Telegram bot implementation.
- `feature/database`: Database implementation.
- `feature/reminder`: Reminder functionality.
- `feature/task-management`: Task management functionality.

Team members should commit changes regularly and use pull requests when merging features.

## 7. Definition of Done

A feature is considered complete when:

- Its functionality has been implemented.
- Relevant test cases pass.
- Errors are handled appropriately.
- The feature works with the integrated system.
- Relevant documentation has been updated.
- Changes have been committed to GitHub.