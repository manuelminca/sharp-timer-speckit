//
//  TimerService.swift
//  SharpTimer
//
//  Created by Sharp Timer on 2025-11-13.
//  Copyright © 2025 Sharp Timer. All rights reserved.
//

import Foundation

/// Timer service responsible for managing Foundation.Timer and countdown logic
protocol TimerServiceDelegate: AnyObject {
    func timerService(_ service: TimerService, didUpdateTimer timer: Timer)
    func timerService(_ service: TimerService, didCompleteTimer timer: Timer)
    func timerService(_ service: TimerService, didStopTimer timer: Timer)
}

class TimerService {
    // MARK: - Properties
    weak var delegate: TimerServiceDelegate?
    private var foundationTimer: Timer?
    private var updateInterval: TimeInterval = 1.0 // Update every second
    
    // Timer accuracy tracking
    private var lastUpdateTime: Date?
    private var accumulatedDrift: TimeInterval = 0.0
    
    // MARK: - Initialization
    init() {
        setupNotifications()
    }
    
    deinit {
        stopTimer()
    }
    
    // MARK: - Timer Management
    
    /// Start a timer with specified duration and name
    func startTimer(name: String, duration: TimeInterval, preset: TimerPreset = .focus) -> Timer {
        stopTimer() // Stop any existing timer
        
        var timer = Timer(name: name, duration: duration, preset: preset)
        timer.start()
        
        startFoundationTimer()
        notifyDelegate(of: timer)
        
        return timer
    }
    
    /// Pause the current timer
    func pauseTimer(_ timer: inout Timer) {
        timer.pause()
        stopFoundationTimer()
        notifyDelegate(of: timer)
    }
    
    /// Resume the current timer
    func resumeTimer(_ timer: inout Timer) {
        timer.start()
        startFoundationTimer()
        notifyDelegate(of: timer)
    }
    
    /// Stop the current timer
    func stopTimer() {
        guard foundationTimer != nil else { return }
        
        foundationTimer?.stop()
        foundationTimer = nil
        lastUpdateTime = nil
        accumulatedDrift = 0.0
        
        stopFoundationTimer()
        
        if let timer = foundationTimer {
            delegate?.timerService(self, didStopTimer: timer)
        }
    }
    
    /// Update timer manually (useful for app resume)
    func updateTimer(_ timer: inout Timer) {
        timer.updateRemainingTime()
        notifyDelegate(of: timer)
        
        if timer.isCompleted {
            stopTimer()
            delegate?.timerService(self, didCompleteTimer: timer)
        }
    }
    
    // MARK: - Foundation.Timer Integration
    
    private func startFoundationTimer() {
        stopFoundationTimer()
        
        foundationTimer = Timer.scheduledTimer(
            withTimeInterval: updateInterval,
            repeats: true
        ) { [weak self] _ in
            self?.handleTimerTick()
        }
        
        foundationTimer?.tolerance = 0.1 // Allow 100ms tolerance for better performance
        lastUpdateTime = Date()
    }
    
    private func stopFoundationTimer() {
        foundationTimer?.invalidate()
        foundationTimer = nil
    }
    
    private func handleTimerTick() {
        guard let timer = foundationTimer else { return }
        
        // Calculate accurate time elapsed since last update
        let now = Date()
        let timeElapsed = now.timeIntervalSince(lastUpdateTime ?? now)
        
        // Update the timer with accurate elapsed time
        timer.updateRemainingTime()
        
        // Track accuracy
        accumulatedDrift += (timeElapsed - updateInterval)
        lastUpdateTime = now
        
        notifyDelegate(of: timer)
        
        // Check for completion
        if timer.isCompleted {
            stopTimer()
            delegate?.timerService(self, didCompleteTimer: timer)
        }
    }
    
    // MARK: - Accuracy and Performance
    
    /// Get current timer accuracy metrics
    var accuracyMetrics: (drift: TimeInterval, tolerance: Double) {
        return (accumulatedDrift, 0.1) // 100ms tolerance
    }
    
    /// Reset accuracy tracking
    func resetAccuracyMetrics() {
        accumulatedDrift = 0.0
    }
    
    /// Check if timer is currently running
    var isTimerRunning: Bool {
        return foundationTimer != nil
    }
    
    // MARK: - Notifications
    
    private func setupNotifications() {
        // Handle app going to background/foreground
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(appDidEnterBackground),
            name: NSApplication.didResignActiveNotification,
            object: nil
        )
        
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(appDidEnterForeground),
            name: NSApplication.didBecomeActiveNotification,
            object: nil
        )
        
        // Handle system time changes
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(systemTimeChanged),
            name: NSSystemTimeZoneChangedNotification,
            object: nil
        )
    }
    
    @objc private func appDidEnterBackground() {
        // Timer continues to run in background, no action needed
        // Foundation.Timer is not paused by app backgrounding
    }
    
    @objc private func appDidEnterForeground() {
        // Update timer when app becomes active
        guard var timer = foundationTimer else { return }
        updateTimer(&timer)
    }
    
    @objc private func systemTimeChanged() {
        // System time changed, update timer accordingly
        guard var timer = foundationTimer else { return }
        updateTimer(&timer)
    }
    
    // MARK: - Private Methods
    
    private func notifyDelegate(of timer: Timer) {
        delegate?.timerService(self, didUpdateTimer: timer)
    }
}

// MARK: - TimerService Mock for Testing
#if DEBUG
class MockTimerService: TimerService {
    private var isRunning = false
    private var mockTimer: Timer?
    
    override func startTimer(name: String, duration: TimeInterval, preset: TimerPreset = .focus) -> Timer {
        let timer = Timer(name: name, duration: duration, preset: preset)
        mockTimer = timer
        isRunning = true
        return timer
    }
    
    override func pauseTimer(_ timer: inout Timer) {
        timer.pause()
        isRunning = false
    }
    
    override func resumeTimer(_ timer: inout Timer) {
        timer.start()
        isRunning = true
    }
    
    override func stopTimer() {
        isRunning = false
        mockTimer = nil
    }
    
    override var isTimerRunning: Bool {
        return isRunning
    }
}
#endif
