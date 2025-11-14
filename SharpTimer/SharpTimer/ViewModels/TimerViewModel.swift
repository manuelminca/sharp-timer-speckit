//
//  TimerViewModel.swift
//  SharpTimer
//
//  Created by Sharp Timer on 2025-11-13.
//  Copyright © 2025 Sharp Timer. All rights reserved.
//

import Foundation
import SwiftUI
import Combine

/// ViewModel for managing timer business logic and coordinating between services and views
class TimerViewModel: ObservableObject {
    // MARK: - Published Properties
    @Published var currentTimer: Timer?
    @Published var isTimerActive: Bool = false
    @Published var isTimerRunning: Bool = false
    @Published var remainingTime: TimeInterval = 0
    @Published var totalDuration: TimeInterval = 0
    @Published var timerProgress: Double = 0.0
    @Published var formattedTime: String = "00:00"
    @Published var currentState: TimerState = .stopped
    @Published var currentPreset: TimerPreset = .focus
    
    // MARK: - Services
    private let timerService: TimerService
    private let notificationService: NotificationService
    private let persistenceService: PersistenceService
    
    // MARK: - Cancellables
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Initialization
    init(
        timerService: TimerService = TimerService(),
        notificationService: NotificationService = NotificationService(),
        persistenceService: PersistenceService = PersistenceService()
    ) {
        self.timerService = timerService
        self.notificationService = notificationService
        self.persistenceService = persistenceService
        
        setupTimerServiceDelegate()
        setupNotifications()
        
        // Try to load saved timer state on initialization
        loadSavedTimerState()
    }
    
    // MARK: - Timer Control Methods
    
    /// Start a new timer with specified duration and preset
    func startTimer(duration: TimeInterval, preset: TimerPreset = .focus, name: String? = nil) {
        let timerName = name ?? "\(preset.displayName) Timer"
        currentTimer = timerService.startTimer(name: timerName, duration: duration, preset: preset)
        updatePublishedProperties()
        
        // Request notification permissions if not already granted
        notificationService.requestPermission { [weak self] granted in
            if granted {
                self?.scheduleTimerNotifications()
            }
        }
        
        // Save initial state
        saveTimerState()
    }
    
    /// Pause the current timer
    func pauseTimer() {
        guard var timer = currentTimer else { return }
        timerService.pauseTimer(&timer)
        currentTimer = timer
        updatePublishedProperties()
        saveTimerState()
    }
    
    /// Resume the current timer
    func resumeTimer() {
        guard var timer = currentTimer else { return }
        timerService.resumeTimer(&timer)
        currentTimer = timer
        updatePublishedProperties()
        saveTimerState()
    }
    
    /// Stop and reset the current timer
    func stopTimer() {
        timerService.stopTimer()
        currentTimer = nil
        resetPublishedProperties()
        persistenceService.clearSavedTimerState()
    }
    
    /// Update timer manually (useful for app resume)
    func updateTimer() {
        guard var timer = currentTimer else { return }
        timerService.updateTimer(&timer)
        currentTimer = timer
        updatePublishedProperties()
        
        if timer.isCompleted {
            handleTimerCompletion()
        }
    }
    
    // MARK: - Timer Information
    
    /// Check if a timer is currently paused
    var isTimerPaused: Bool {
        return currentState == .paused
    }
    
    /// Get formatted remaining time for display
    var displayTime: String {
        return formattedTime
    }
    
    /// Get timer completion percentage
    var progressPercentage: Double {
        return timerProgress * 100
    }
    
    // MARK: - Preset Management
    
    /// Get all available presets with their default durations
    var availablePresets: [(preset: TimerPreset, duration: TimeInterval)] {
        return [
            (.focus, TimerPreset.focus.defaultDuration),
            (.breakTime, TimerPreset.breakTime.defaultDuration),
            (.custom, 0) // User will specify
        ]
    }
    
    /// Validate custom duration input
    func validateCustomDuration(_ minutes: Int) -> Bool {
        return minutes >= 1 && minutes <= 480 // 1 minute to 8 hours
    }
    
    /// Convert minutes to TimeInterval
    func minutesToTimeInterval(_ minutes: Int) -> TimeInterval {
        return TimeInterval(minutes * 60)
    }
    
    // MARK: - Private Methods
    
    private func setupTimerServiceDelegate() {
        timerService.delegate = self
    }
    
    private func setupNotifications() {
        // Save timer state every 30 seconds during operation
        Foundation.Timer.publish(every: 30, on: .main, in: .common)
            .autoconnect()
            .sink { [weak self] (_: Date) in
                self?.saveTimerState()
            }
            .store(in: &cancellables)
        
        // Handle app lifecycle
        NotificationCenter.default.publisher(for: NSApplication.willTerminateNotification)
            .sink { [weak self] _ in
                self?.saveTimerState()
            }
            .store(in: &cancellables)
    }
    
    private func updatePublishedProperties() {
        guard let timer = currentTimer else {
            resetPublishedProperties()
            return
        }
        
        remainingTime = timer.remainingTime
        totalDuration = timer.duration
        timerProgress = timer.progress
        formattedTime = timer.formattedTime
        isTimerActive = timer.state.isActive
        isTimerRunning = (timer.state == .running)
        currentState = timer.state
        currentPreset = timer.preset
    }
    
    private func resetPublishedProperties() {
        currentTimer = nil
        remainingTime = 0
        totalDuration = 0
        timerProgress = 0
        formattedTime = "00:00"
        isTimerActive = false
        isTimerRunning = false
        currentState = .stopped
        currentPreset = .focus
    }
    
    private func handleTimerCompletion() {
        notificationService.sendTimerCompletionNotification(
            title: "Timer Complete!",
            body: "Your \(currentTimer?.preset.displayName ?? "timer") timer has finished."
        )
        
        // Auto-stop timer after completion
        stopTimer()
    }
    
    private func scheduleTimerNotifications() {
        guard let timer = currentTimer, timer.state == .running else { return }
        
        notificationService.scheduleNotification(
            title: "Timer Almost Done",
            body: "\(timer.formattedTime) remaining",
            identifier: "timer-almost-done",
            timeInterval: timer.remainingTime - 300 // 5 minutes before completion
        )
        
        notificationService.scheduleNotification(
            title: "Timer Complete!",
            body: "Your \(timer.preset.displayName) timer has finished.",
            identifier: "timer-complete",
            timeInterval: timer.remainingTime
        )
    }
    
    private func saveTimerState() {
        guard let timer = currentTimer else { return }
        persistenceService.saveTimerState(timer)
    }
    
    private func loadSavedTimerState() {
        if let savedTimer = persistenceService.loadTimerState(),
           savedTimer.isValid {
            currentTimer = Timer.recreateTimer(from: savedTimer)
            updatePublishedProperties()
            
            // If timer was running, resume it
            if currentTimer?.state == .running {
                // Update remaining time based on elapsed time
                updateTimer()
            }
        }
    }
}

// MARK: - TimerServiceDelegate
extension TimerViewModel: TimerServiceDelegate {
    func timerService(_ service: TimerService, didUpdateTimer timer: Timer) {
        DispatchQueue.main.async {
            self.currentTimer = timer
            self.updatePublishedProperties()
        }
    }
    
    func timerService(_ service: TimerService, didCompleteTimer timer: Timer) {
        DispatchQueue.main.async {
            self.currentTimer = timer
            self.updatePublishedProperties()
            self.handleTimerCompletion()
        }
    }
    
    func timerService(_ service: TimerService, didStopTimer timer: Timer) {
        DispatchQueue.main.async {
            self.currentTimer = nil
            self.resetPublishedProperties()
            self.persistenceService.clearSavedTimerState()
        }
    }
}
