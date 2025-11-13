//
//  TimerState.swift
//  SharpTimer
//
//  Created by Sharp Timer on 2025-11-13.
//  Copyright © 2025 Sharp Timer. All rights reserved.
//

import Foundation

/// Timer states representing the current lifecycle of a timer
enum TimerState: String, CaseIterable {
    case stopped = "stopped"
    case running = "running"
    case paused = "paused"
    case completed = "completed"
    
    var displayName: String {
        switch self {
        case .stopped:
            return "Stopped"
        case .running:
            return "Running"
        case .paused:
            return "Paused"
        case .completed:
            return "Completed"
        }
    }
    
    var isActive: Bool {
        switch self {
        case .running, .paused:
            return true
        case .stopped, .completed:
            return false
        }
    }
}

/// Persistent timer state for app restart recovery
struct TimerStateData {
    let timerId: UUID
    let timerName: String
    let remainingTime: TimeInterval
    let totalDuration: TimeInterval
    let state: TimerState
    let preset: TimerPreset
    let startDate: Date?
    let lastUpdated: Date
    
    init(from timer: Timer) {
        self.timerId = timer.id
        self.timerName = timer.name
        self.remainingTime = timer.remainingTime
        self.totalDuration = timer.duration
        self.state = timer.state
        self.preset = timer.preset
        self.startDate = timer.startDate
        self.lastUpdated = Date()
    }
    
    /// Initialize from UserDefaults dictionary
    init?(fromDictionary dict: [String: Any]) {
        guard let idString = dict["timerId"] as? String,
              let timerId = UUID(uuidString: idString),
              let timerName = dict["timerName"] as? String,
              let remainingTime = dict["remainingTime"] as? TimeInterval,
              let totalDuration = dict["totalDuration"] as? TimeInterval,
              let stateRawValue = dict["state"] as? String,
              let state = TimerState(rawValue: stateRawValue),
              let presetRawValue = dict["preset"] as? String,
              let preset = TimerPreset(rawValue: presetRawValue),
              let lastUpdated = dict["lastUpdated"] as? Date
        else {
            return nil
        }
        
        self.timerId = timerId
        self.timerName = timerName
        self.remainingTime = remainingTime
        self.totalDuration = totalDuration
        self.state = state
        self.preset = preset
        self.startDate = dict["startDate"] as? Date
        self.lastUpdated = lastUpdated
    }
    
    /// Convert to dictionary for UserDefaults persistence
    func toDictionary() -> [String: Any] {
        var dict: [String: Any] = [
            "timerId": timerId.uuidString,
            "timerName": timerName,
            "remainingTime": remainingTime,
            "totalDuration": totalDuration,
            "state": state.rawValue,
            "preset": preset.rawValue,
            "lastUpdated": lastUpdated
        ]
        
        if let startDate = startDate {
            dict["startDate"] = startDate
        }
        
        return dict
    }
    
    /// Check if the saved state is still valid (not too old)
    var isValid: Bool {
        let timeSinceUpdate = Date().timeIntervalSince(lastUpdated)
        // State is valid if it's less than 7 days old
        return timeSinceUpdate < (7 * 24 * 60 * 60)
    }
    
    /// Recreate timer object from persistent state
    func recreateTimer() -> Timer {
        var timer = Timer(name: timerName, duration: totalDuration, preset: preset)
        timer.id = timerId
        timer.remainingTime = remainingTime
        timer.state = state
        timer.startDate = startDate
        return timer
    }
}
