# PingTask – Project Overview

**Project Title:** PingTask: A Telegram-Based Group Task Management and Automated Reminder System

## 1. Introduction

PingTask is a Telegram-based group task management and automated reminder bot developed using Python.

The system aims to help student groups and small teams manage their tasks, assign responsibilities, monitor deadlines, and receive automated reminders directly through Telegram.

Group projects often involve multiple members working on different tasks with individual deadlines. However, managing these responsibilities through ordinary messaging applications can become difficult, especially when important messages get buried in conversations.

PingTask addresses this problem by providing a simple task management solution within an existing Telegram group.

Users can create tasks, assign them to group members, view outstanding tasks, mark tasks as completed, and receive automated notifications when deadlines are approaching.

## 2. Problem Statement

Group project members frequently encounter difficulties when coordinating tasks and responsibilities.

Common problems include:

- Forgetting assigned tasks and upcoming deadlines.
- Difficulty identifying which member is responsible for a particular task.
- Losing track of pending and completed tasks.
- Having to manually remind other members about approaching deadlines.
- Difficulty monitoring the overall progress of group assignments.
- Important task information getting buried in group conversations.

Although messaging applications allow members to communicate, they do not necessarily provide dedicated task tracking and automated deadline management.

Therefore, PingTask is proposed as a lightweight Telegram bot that simplifies task coordination and improves accountability among group members.

## 3. Project Objectives

The objectives of PingTask are:

1. To develop a Telegram bot that allows group members to create and assign tasks.
2. To provide a centralized list of pending tasks within a Telegram group.
3. To implement automated deadline reminders.
4. To allow users to update task statuses when tasks are completed.
5. To store task information persistently using an SQLite database.
6. To demonstrate the practical application of Python asynchronous programming, database management, and background scheduling.
7. To improve task visibility and accountability among group members.

## 4. Project Scope

### 4.1 Included Features

The initial version of PingTask will include:

- Telegram bot integration.
- Task creation and assignment.
- Task deadline management.
- Viewing pending group tasks.
- Viewing tasks assigned to the current user.
- Marking tasks as completed.
- Automated reminders before deadlines.
- SQLite database integration.
- Group-based task management.
- Basic input validation and error handling.

### 4.2 Excluded Features

The following features are excluded from the initial development scope:

- Web-based dashboard.
- Dedicated mobile application.
- File and document sharing.
- Advanced project analytics.
- Integration with external project management platforms.
- Recurring tasks.
- Advanced role and permission management.
- Customizable notification schedules.

These features may be considered for future improvements.

## 5. Target Users

PingTask is designed for:

- University students working on group assignments.
- Small project teams.
- Club and society committees.
- Small organizations coordinating tasks.
- Teams that use Telegram for communication.

## 6. Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Bot Framework | python-telegram-bot |
| Database | SQLite |
| Background Scheduler | APScheduler |
| Date and Time Parsing | dateparser |
| Environment Configuration | python-dotenv |
| Version Control | Git and GitHub |
| Development Environment | Visual Studio Code |

## 7. Expected Outcome

At the end of development, PingTask should function as a Telegram group bot that enables users to:

- Assign tasks to group members.
- Specify task descriptions and deadlines.
- View pending tasks.
- View their own assigned tasks.
- Mark tasks as completed.
- Receive automatic deadline reminders.

The project will demonstrate the integration of Telegram Bot API, Python programming, asynchronous operations, database management, and scheduled background processing.

## 8. Project Deliverables

The expected project deliverables include:

1. Functional PingTask Telegram bot.
2. SQLite database.
3. Automated reminder system.
4. Python source code.
5. Software requirements documentation.
6. System design documentation.
7. Database design documentation.
8. Testing documentation.
9. Final project demonstration and presentation.