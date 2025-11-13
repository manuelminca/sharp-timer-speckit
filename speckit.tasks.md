---

description: "Task list for Sharp Timer macOS application development"
---

# Tasks: Sharp Timer

**Input**: Design documents from `.specify.md` and `speckit.plan.md`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

Based on plan.md structure:
- **Core App**: `SharpTimerApp.swift`, `ContentView.swift`
- **ViewModels**: `ViewModels/TimerViewModel.swift`, `ViewModels/MenuBarViewModel.swift`
- **Models**: `Models/Timer.swift`, `Models/TimerState.swift`
- **Services**: `Services/TimerService.swift`, `Services/PersistenceService.swift`, `Services/NotificationService.swift`
- **Views**: `Views/MenuBarIconView.swift`, `Views/TimerPopupView.swift`, `Views/TimerDisplayView.swift`
- **Tests**: `SharpTimerTests/` directory

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create Xcode macOS App project with proper bundle identifier
- [ ] T002 Configure App Sandbox entitlements for menu bar access
- [ ] T003 [P] Set up project directory structure per implementation plan
- [ ] T004 [P] Create initial SwiftUI and AppKit file templates
- [ ] T005 Configure build settings for macOS 12.0+ minimum deployment

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Implement Timer model in Models/Timer.swift (duration, state, remainingTime)
- [ ] T007 Implement TimerState model in Models/TimerState.swift (persistent state data)
- [ ] T008 Create base TimerService in Services/TimerService.swift (Foundation.Timer integration)
- [ ] T009 Create MenuBarIconView in Views/MenuBarIconView.swift (basic NSStatusItem setup)
- [ ] T010 Set up basic app lifecycle in SharpTimerApp.swift (menu bar integration)

**Checkpoint**: Foundation ready - timer models exist, basic menu bar shows icon

---

## Phase 3: User Story 1 - Basic Timer Functionality (Priority: P1) 🎯 MVP

**Goal**: Click menu bar icon → open popup → start countdown timer → receive notification

**Independent Test**: Can start a 1-minute test timer and verify it counts down and completes with notification

### Implementation for User Story 1

- [ ] T011 [US1] Implement TimerViewModel in ViewModels/TimerViewModel.swift (start/stop/pause logic)
- [ ] T012 [US1] Enhance TimerService with accurate countdown (updates every second)
- [ ] T013 [US1] Create TimerDisplayView in Views/TimerDisplayView.swift (countdown UI)
- [ ] T014 [US1] Implement basic NotificationService in Services/NotificationService.swift
- [ ] T015 [US1] Create TimerPopupView in Views/TimerPopupView.swift (timer controls)
- [ ] T016 [US1] Connect popup window to menu bar icon click (AppKit integration)
- [ ] T017 [US1] Add basic timer controls (Start, Stop, Pause buttons) to popup

**Checkpoint**: At this point, User Story 1 should be fully functional - can click menu bar icon, start timer, see countdown, receive notification

---

## Phase 4: User Story 2 - Timer State Persistence (Priority: P1) 🔄

**Goal**: Timer continues running after app quit/restart cycle

**Independent Test**: Start a timer, quit app, restart app, verify timer continues from correct remaining time

### Implementation for User Story 2

- [ ] T018 [US2] Implement PersistenceService in Services/PersistenceService.swift (UserDefaults integration)
- [ ] T019 [US2] Save timer state on app quit (Timer + TimerState to UserDefaults)
- [ ] T020 [US2] Load timer state on app launch (restore from UserDefaults)
- [ ] T021 [US2] Auto-save timer state every 30 seconds during operation
- [ ] T022 [US2] Handle edge cases (app force quit, system restart, time changes)
- [ ] T023 [US2] Add state validation (check for corrupted saved data)

**Checkpoint**: At this point, User Story 2 should work - timer survives app restarts with accurate remaining time

---

## Phase 5: User Story 3 - Multiple Timer Types (Priority: P2) ⚙️

**Goal**: Choose between Focus (25min), Break (5min), and Custom duration timers

**Independent Test**: Can select different preset timers and verify each starts with correct duration

### Implementation for User Story 3

- [ ] T024 [US3] Define TimerPreset enum in Models/Timer.swift (Focus, Break, Custom cases)
- [ ] T025 [US3] Update TimerViewModel to support preset selection
- [ ] T026 [US3] Create preset selection UI in TimerPopupView (three buttons + custom input)
- [ ] T027 [US3] Implement custom duration input with validation (text field)
- [ ] T028 [US3] Add preset-specific styling/colors to timer display
- [ ] T029 [US3] Store user preferences for custom durations in UserDefaults

**Checkpoint**: At this point, User Story 3 should work - can select presets and create custom timers

---

## Phase 6: User Story 4 - Menu Bar Status Display (Priority: P2) 📊

**Goal**: Menu bar icon shows timer status and provides quick access

**Independent Test**: Can glance at menu bar icon to see timer status without opening popup

### Implementation for User Story 4

- [ ] T030 [US4] Enhance MenuBarIconView with status indicators (default/running/paused icons)
- [ ] T031 [US4] Add tooltip showing current timer information (remaining time, preset type)
- [ ] T032 [US4] Implement right-click context menu (Start/Stop/Resume options)
- [ ] T033 [US4] Add keyboard shortcut support (spacebar for start/stop)
- [ ] T034 [US4] Update icon appearance when timer is active vs inactive
- [ ] T035 [US4] Integrate quick actions from menu bar without opening full popup

**Checkpoint**: At this point, User Story 4 should work - menu bar clearly shows timer status

---

## Phase 7: Testing & Quality Assurance

**Purpose**: Ensure quality and performance requirements are met

- [ ] T036 Create unit tests for TimerService accuracy (±1 second tolerance)
- [ ] T037 Create integration tests for timer state persistence
- [ ] T038 Test timer functionality on macOS 12.0, 13.0, 14.0
- [ ] T039 Performance testing: verify <50MB RAM usage with Instruments
- [ ] T040 Test app startup time (should be <0.5 seconds)
- [ ] T041 Test edge cases (system sleep/wake, time changes, multiple timers)
- [ ] T042 Accessibility testing (VoiceOver labels, keyboard navigation)

---

## Phase 8: Final Polish & Distribution

**Purpose**: Production-ready application

- [ ] T043 Create app icon and update Assets.xcassets
- [ ] T044 Configure Info.plist with proper app metadata
- [ ] T045 Implement proper error handling throughout app
- [ ] T046 Create minimal README with setup instructions
- [ ] T047 Set up code signing certificates and provisioning profiles
- [ ] T048 Test App Store submission requirements (sandbox, privacy)
- [ ] T049 Create simple privacy policy for offline-only app
- [ ] T050 Final testing on multiple Mac models and OS versions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can proceed in priority order (P1 → P2) or in parallel
- **Testing (Phase 7)**: Depends on all user stories being complete
- **Polish (Phase 8)**: Depends on testing completion

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 completion for timer functionality

### Within Each User Story

- Models before services
- Services before views
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel
- User Story 1 and User Story 2 can be developed in parallel (both P1 priority)
- Models within a story marked [P] can be developed in parallel

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Basic Timer)
4. Complete Phase 4: User Story 2 (State Persistence)
5. **STOP and VALIDATE**: Test MVP functionality
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (Basic Timer MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo (Persistent Timer!)
4. Add User Story 3 → Test independently → Deploy/Demo (Multiple Timer Types!)
5. Add User Story 4 → Test independently → Deploy/Demo (Full Feature Set!)

---

## Notes

- **[P]** tasks = different files, no dependencies
- **[Story]** label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Timer accuracy must be verified with ±1 second tolerance
- Resource usage must stay under 50MB RAM at all times
- All functionality must work offline without network connectivity
- App must be App Store compliant with proper sandbox configuration
