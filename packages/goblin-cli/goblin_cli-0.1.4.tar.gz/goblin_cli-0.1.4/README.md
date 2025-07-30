# Unit Test Goblin 🧪👹

A CLI tool that analyzes your unit tests and codebase to detect weak test coverage, redundant cases, and untested logic paths. Because your tests _aren’t as good as you think_.

![Goblin CLI Output](./assets/goblin-cli-screenshot.png)

## Why?

Most test suites lie. They pass when they shouldn't, cover when they shouldn't, and leave edge cases to die in the cold. Goblin helps you:

- Spot meaningless tests
- Identify missing assertions
- Catch untested edge cases

## MVP Features

- Parse code and test files
- Detect empty or redundant tests

## Next Steps

- Identify missing logical branches
- Suggest better coverage

## Usage

```bash
$ goblin analyze ./path/to/your/code
```

### 📁 Folder Overview

| Folder    | Purpose                                               |
|-----------|-------------------------------------------------------|
| `goblin/` | Core logic: parsing, detecting, and shaming bad tests |
| `tests/`  | Unit tests _for the Goblin itself_                    |
| `docs/`   | Design plans, roadmap, architecture decisions         |

### 📚 Docs

[Roadmap](./docs/roadmap.md) – See what's coming next in the Goblinverse!
[Virtual Environment](./docs/virtual-environment.md) – Lessons learned about dev environment for Goblin development.

---

👋 Created by [gpapachr](https://github.com/gpapachr) – fueled by sarcasm, caffeine, and a deep hatred for fragile test suites.
