# PingTask – Software Requirements Specification

## 1. Introduction

This document describes the functional and non-functional requirements of PingTask.

It defines the expected system behaviour, available commands, task management operations, and reminder functionality.

## 2. Functional Requirements

Functional requirements describe the operations that the system must perform.

### FR-01: Start the Bot

The system shall allow users to start interacting with PingTask using the `/start` command.

Expected behaviour:
1. Receive the `/start` command.
2. Display a welcome message.
3. Briefly introduce the bot's purpose.
4. Provide basic instructions.

### FR-02: Display Help Information

The system shall provide a `/help` command to display available commands and their descriptions.

### FR-03: Create a Task

The system shall allow users to create a task using the `/todo` command.

Command format:

`/todo @username [Task description] by [Date/Time]`

Example:

`/todo @adam Finish database schema by tomorrow 5pm`

Expected behaviour:
1. Receive the command.
2. Extract the assignee, task description, and deadline.
3. Validate the provided information.
4. Convert the deadline into a Python datetime object.
5. Store the task in the SQLite database.
6. Send a confirmation message.

Each task shall contain:
- Unique task ID.
- Telegram group chat ID.
- Assignee username.
- Assignee Telegram user ID, if available.
- Task description.
- Due date and time.
- Task status.
- Reminder status.
- Creation timestamp.

### FR-04: View Pending Tasks

The system shall allow users to display all pending tasks in the current Telegram group using `/tasks`.

Expected behaviour:
- Retrieve pending tasks from the database.
- Display task IDs.
- Display assigned users.
- Display task descriptions.
- Display deadlines.
- Display task statuses.

Tasks should be displayed in ascending order of their deadlines.

### FR-05: View Personal Tasks

The system shall allow users to view tasks assigned to themselves using `/mytasks`.

Expected behaviour:
1. Identify the Telegram user.
2. Retrieve pending tasks assigned to that user.
3. Restrict the results to the current group.
4. Display the task information.

### FR-06: Complete a Task

The system shall allow users to mark a task as completed using `/done`.

Example:

`/done 3`

Expected behaviour:
1. Receive the task ID.
2. Check whether the task exists.
3. Verify that the task belongs to the current Telegram group.
4. Verify that the user is authorized to complete it.
5. Update the task status to completed.
6. Record the completion timestamp.
7. Send a confirmation message.

### FR-07: Automated Deadline Reminder

The system shall periodically check pending tasks using a background scheduler.

Expected behaviour:
1. The scheduler executes the reminder checking function at a configured interval.
2. The system retrieves eligible pending tasks.
3. The system checks whether a task has entered the reminder window.
4. The bot sends a reminder message to the relevant Telegram group.
5. The system updates the reminder status after successful delivery.
6. The same reminder must not be sent repeatedly.

### FR-08: Task Validation

The system shall validate task information before storing it.

Validation requirements:
- Assignee must be provided.
- Task description must not be empty.
- Due date must be valid.
- Due date must be in the future.
- The task must be associated with a valid Telegram group.
- The assignee should be identifiable as a member of the group.

### FR-09: Error Handling

The system shall provide understandable error messages when:

- A command is entered incorrectly.
- Required information is missing.
- A deadline cannot be interpreted.
- A task ID does not exist.
- A task is already completed.
- A user attempts an unauthorized operation.
- A database operation fails.
- A Telegram message cannot be delivered.

## 3. Non-Functional Requirements

### NFR-01: Usability

The bot shall provide simple commands that users can understand without technical knowledge.

### NFR-02: Performance

Normal task operations should return responses within a reasonable time.

### NFR-03: Reliability

Task information shall remain stored in the database even after the bot is restarted.

### NFR-04: Maintainability

The source code shall be separated into modules based on their responsibilities.

### NFR-05: Security

- The Telegram bot token must not be hardcoded into the source code.
- Sensitive configuration shall be stored in environment variables.
- SQL queries shall use parameterized statements.
- Users must not be able to modify tasks belonging to unrelated groups.
- Task modification operations shall verify user permissions.

### NFR-06: Compatibility

The bot shall operate through Telegram and be developed using Python-compatible libraries.

### NFR-07: Time Accuracy

The system shall use consistent date and time handling to ensure reminder notifications are delivered at the correct time.

## 4. User Commands

| Command | Description |
|---|---|
| `/start` | Start interacting with the bot |
| `/help` | Display available commands |
| `/todo` | Create a new task |
| `/tasks` | Display pending group tasks |
| `/mytasks` | Display tasks assigned to the current user |
| `/done` | Mark a task as completed |

## 5. Task Status

The initial version supports two task statuses.

| Status | Description |
|---|---|
| pending | Task has not been completed |
| completed | Task has been completed |

## 6. Reminder Requirements

The initial reminder configuration is:

- Reminder interval: Every 10 minutes.
- Reminder window: 24 hours before the deadline.
- Reminder destination: Telegram group.
- Reminder target: Assigned group member.
- Duplicate reminders: Not allowed for the same reminder event.
- Completed tasks: Excluded from reminder processing.
- Overdue tasks: Excluded from the 24-hour reminder process.

If a task is created less than 24 hours before its deadline, the system shall send its reminder during the next eligible scheduler check.

## 7. Assumptions and Constraints

- Users must have access to a Telegram group containing the bot.
- The bot must have permission to send messages in the group.
- Users should have Telegram accounts.
- The bot must be running for scheduled reminders to be delivered.
- SQLite will be used for the initial implementation.
- The system is intended for small groups and academic projects.
- The default timezone for the initial implementation is Asia/Kuala_Lumpur.

## 8. Acceptance Criteria

PingTask will satisfy its initial requirements when:

1. Users can create tasks successfully.
2. Users can view pending tasks.
3. Users can view their assigned tasks.
4. Users can mark tasks as completed.
5. Task information is stored persistently.
6. The scheduler identifies tasks approaching their deadlines.
7. The bot sends automated reminders.
8. Duplicate reminders are prevented.
9. Tasks are isolated between Telegram groups.
10. Invalid operations produce appropriate error messages.