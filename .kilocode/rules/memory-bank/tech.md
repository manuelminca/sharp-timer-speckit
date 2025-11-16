# Technology Stack: Sharp Timer

## Core Technologies

- **Language**: Python 3.8+
  - **Rationale**: A modern, readable, and widely-supported language with a rich ecosystem of libraries suitable for desktop application development.

- **Framework**: `rumps`
  - **Rationale**: A lightweight and straightforward framework for creating macOS menu bar applications in Python. It provides a simple, event-driven API for managing the application lifecycle and UI elements without the complexity of larger GUI toolkits.

- **System Integration**: `pyobjc-framework-SystemConfiguration`
  - **Rationale**: Provides native access to macOS system configuration and notification APIs, which is essential for reliably detecting sleep and wake events. This avoids inefficient polling and ensures the application integrates seamlessly with the OS.

- **Storage**: JSON (JavaScript Object Notation)
  - **Rationale**: A human-readable and easy-to-parse format for storing user settings and application state. It requires no external dependencies and is well-supported by Python's standard library.

## Development & Testing

- **Testing Framework**: `pytest`
  - **Rationale**: The de facto standard for testing in the Python ecosystem. It offers a powerful and flexible framework for writing unit, integration, and functional tests.
  - **Plugins**:
    - `pytest-mock`: For mocking objects and functions, which is crucial for testing interactions with the `rumps` framework and system APIs in isolation.
    - `pytest-cov`: For measuring test coverage and ensuring a high standard of code quality.

## Dependencies

### Production Dependencies (`requirements.txt`)
- `rumps`: For the core application framework.
- `pyobjc-framework-SystemConfiguration`: For sleep/wake event handling.

### Development Dependencies (`requirements-dev.txt`)
- `pytest`: The core testing framework.
- `pytest-mock`: For mocking dependencies in tests.
- `pytest-cov`: For test coverage analysis.
- `black`: For automated code formatting.
- `ruff`: For linting and code quality checks.
- `mypy`: For static type checking.

## Tool Usage & Patterns

- **State Management**: Application state is explicitly managed in data classes (e.g., `TimerState`) and persisted to JSON files. This ensures a clear and predictable flow of data.
- **Atomic Writes**: To prevent data corruption, a "write-to-temporary-file-then-rename" pattern is used for all file-based persistence.
- **Threading**: The core timer logic runs in a separate thread (`threading.Timer`) to ensure the main UI thread remains responsive at all times.
- **Event-Driven Architecture**: The application is built around an event-driven model, where user interactions and timer completions trigger specific callback functions. This is managed by the `rumps` framework.
