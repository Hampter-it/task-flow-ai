# Development process

- Tasks are GitHub issues, one at a time.
- Read the acceptance criteria before starting and before closing.
- Commit regularly.
- Every lifecycle step is recorded on GitHub. A subagent's final
  response is never a substitute for an issue body edit, an issue
  comment, or closing the issue.

## Roles

- PM - grooms a task before anyone implements it, follows _docs/team/pm.md
- Engineer - implements one groomed task, follows _docs/team/software-engineer.md
- QA - checks the result against the acceptance criteria, follows _docs/team/qa-engineer.md
- Orchestrator - runs the lifecycle and enforces the GitHub gates; it does
  not groom, implement, or test itself

## Lifecycle

1. Pick the next open issue from the backlog.
2. PM grooms it and publishes the groomed body to the GitHub issue using
   `_docs/task-template.md`.
3. Orchestrator verifies the issue body has Goal, Acceptance criteria,
   Out of scope, and Constraints, and that every criterion is checkable.
   Do not start the engineer until this gate passes.
4. Engineer implements the task, commits, and publishes an implementation
   comment on the issue with the commit hash, commands run, and results.
5. QA verifies the result and publishes a `QA: PASS` or `QA: FAIL` comment
   on the issue.
6. On FAIL, return to step 4 with the QA comment as input.
7. On PASS, orchestrator verifies the issue body and both comments exist
   on GitHub, then closes the issue.
8. Repeat until the backlog is empty.

## Rules

- Do not skip step 2.
- The engineer does not close the issue.
- QA does not fix the code, only outputs PASS or FAIL.
- The orchestrator closes the issue only after QA outputs PASS and the
  GitHub record is complete.
- Missing `gh` is not a reason to skip a GitHub step. Use the GitHub REST
  API when the CLI is unavailable.
- Do not report lifecycle work as done until it is visible on GitHub.
