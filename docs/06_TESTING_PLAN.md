# PingTask – Testing Plan

## 1. Testing Objectives

The purpose of testing is to ensure that PingTask operates correctly, handles invalid inputs, stores task information reliably, and sends deadline reminders as expected.

Testing will be performed throughout development to identify and resolve issues before the final project demonstration.

## 2. Testing Types

### 2.1 Unit Testing

Individual functions and modules will be tested separately.

Examples:
- Database insertion.
- Database retrieval.
- Task status updates.
- Date and time parsing.
- Task validation.
- Reminder eligibility checking.

### 2.2 Integration Testing

Tests will verify that different system components work together correctly.

Examples:
- Telegram command handler with task manager.
- Task manager with SQLite.
- Scheduler with database.
- Scheduler with Telegram bot notifications.

### 2.3 Functional Testing

Tests will verify that the system behaves according to its functional requirements.

Examples:
- Creating tasks.
- Viewing tasks.
- Viewing personal tasks.
- Completing tasks.
- Sending reminders.

### 2.4 Error Handling Testing

Tests will verify that the system handles invalid commands and unexpected situations.

Examples:
- Invalid task IDs.
- Missing command arguments.
- Invalid deadlines.
- Unauthorized task modifications.
- Database errors.
- Telegram delivery failures.

## 3. Functional Test Cases

| Test ID | Test Scenario | Expected Result |
|---|---|---|
| TC-01 | Start the bot using `/start` | Bot displays a welcome message |
| TC-02 | Use `/help` | Bot displays available commands |
| TC-03 | Create a valid task using `/todo` | Task is saved successfully |
| TC-04 | Create a task without an assignee | Bot displays an error |
| TC-05 | Create a task without a description | Bot displays an error |
| TC-06 | Enter an invalid deadline | Bot requests a valid date and time |
| TC-07 | Enter a deadline in the past | Bot rejects the task |
| TC-08 | Display tasks using `/tasks` | Pending tasks are displayed |
| TC-09 | Display personal tasks using `/mytasks` | Only the current user's tasks are displayed |
| TC-10 | Complete an existing task | Task status changes to completed |
| TC-11 | Complete a non-existing task | Bot displays an error |
| TC-12 | Complete a task from another group | Operation is rejected |
| TC-13 | Unauthorized user attempts task completion | Operation is rejected |
| TC-14 | Task enters the reminder window | Reminder is sent |
| TC-15 | Scheduler checks an already-reminded task | No duplicate reminder is sent |
| TC-16 | Complete a task before its deadline | No subsequent reminder is sent |
| TC-17 | Task deadline has passed | No 24-hour reminder is sent |
| TC-18 | Restart the bot | Previously stored tasks remain available |
| TC-19 | View tasks in another group | Only that group's tasks are displayed |
| TC-20 | Telegram message delivery fails | Reminder remains eligible for retry |

## 4. Reminder System Testing

The reminder system requires special attention because it involves time-based background processing.

### Scenario A: Task More Than 24 Hours Away

Input:
- Due date: 48 hours from now.
- Status: pending.
- Reminder sent: false.

Expected result:

No reminder is sent yet.

### Scenario B: Task Within 24 Hours

Input:
- Due date: 12 hours from now.
- Status: pending.
- Reminder sent: false.

Expected result:

The bot sends a reminder during the next eligible scheduler check.

### Scenario C: Reminder Already Sent

Input:
- Due date: 12 hours from now.
- Status: pending.
- Reminder sent: true.

Expected result:

No duplicate reminder is sent.

### Scenario D: Task Completed

Input:
- Due date: 12 hours from now.
- Status: completed.

Expected result:

No reminder is sent.

### Scenario E: Deadline Has Passed

Input:
- Due date: 1 hour ago.
- Status: pending.

Expected result:

No 24-hour reminder is sent.

### Scenario F: Task Created Within 24 Hours of Deadline

Input:
- Due date: 6 hours from now.
- Status: pending.
- Reminder sent: false.

Expected result:

The bot sends a reminder during the next eligible scheduler check.

### Scenario G: Telegram Delivery Failure

Input:
- Task is eligible for a reminder.
- Telegram API returns a delivery error.

Expected result:

The reminder status remains unchanged so the system can attempt delivery again.

## 5. Testing Tools

- Python `unittest` or `pytest`.
- SQLite.
- Telegram test group.
- Manual command testing.
- Python logging.

## 6. Acceptance Criteria

PingTask will be considered ready for demonstration when:

1. Users can successfully create tasks.
2. Users can view pending tasks.
3. Users can view their assigned tasks.
4. Users can mark tasks as completed.
5. Task information persists in SQLite.
6. The scheduler correctly identifies eligible tasks.
7. The bot sends automated deadline reminders.
8. Duplicate reminders are prevented.
9. Tasks are isolated between Telegram groups.
10. Unauthorized operations are rejected.
11. Invalid commands produce understandable error messages.

## 7. Testing Results

Automated tests are run with:

```bash
python -m unittest discover -s tests
```

The suite has 64 tests and all pass. Some results were also checked by hand in Telegram. Status meanings:

- **Passed (automated):** covered by a unit test in `tests/`.
- **Passed (live):** checked by sending a command to the bot in Telegram.
- **Pending live test:** covered by an automated test, but not yet checked in Telegram.

| Test ID | Actual Result | Status | Remarks |
|---|---|---|---|
| TC-01 | Bot replies with the welcome message | Passed (live) | |
| TC-02 | Bot lists the available commands | Passed (live) | |
| TC-03 | Task is saved and confirmed | Passed (live) | `test_task_handlers.py` |
| TC-04 | Error: assignee is missing | Passed (automated) | `test_task_manager.py` |
| TC-05 | Error: task description is empty | Passed (automated) | `test_task_manager.py` |
| TC-06 | Error: deadline could not be understood | Passed (automated) | `test_task_manager.py` |
| TC-07 | Error: deadline must be in the future | Passed (automated) | `test_task_manager.py` |
| TC-08 | Pending tasks are listed | Passed (live) | `test_task_handlers.py` |
| TC-09 | Only the sender's tasks are listed | Passed (live) | `test_task_handlers.py` |
| TC-10 | Task status changes to completed | Passed (live) | Checked in `pingtask.db` |
| TC-11 | Error: task does not exist in this group | Passed (automated) | `test_task_manager.py` |
| TC-12 | Error: task belongs to another group | Passed (automated) | `test_task_manager.py`, `test_database.py` |
| TC-13 | Error: only assignee or creator can complete | Passed (automated) | `test_task_manager.py`, `test_task_handlers.py` |
| TC-14 | Reminder is sent for a task due within 24 hours | Pending live test | `test_scheduler.py` |
| TC-15 | Already-reminded task is not sent again | Passed (automated) | `test_scheduler.py` |
| TC-16 | Completed task gets no reminder | Passed (automated) | `test_scheduler.py` |
| TC-17 | Overdue task gets no reminder | Passed (automated) | `test_scheduler.py` |
| TC-18 | Tasks are still listed after restart | Pending live test | Automated: `test_database.py` (persistence test) |
| TC-19 | Only this group's tasks are listed | Passed (automated) | `test_database.py`; live check pending |
| TC-20 | Failed delivery leaves reminder eligible for retry | Passed (automated) | `test_scheduler.py` |

The testing records shall be updated after each test has been performed.