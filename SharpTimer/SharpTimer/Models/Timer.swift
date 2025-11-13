//
//  Timer.swift
//  SharpTimer
//
//  Created by Sharp Timer on 2025-11-13.
//  Copyright © 2025 Sharp Timer. All rights reserved.
//

import Foundation

/// Timer presets for different use cases
enum TimerPreset: String, CaseIterable {
    case focus = "focus"
    case breakTime = "break"
    case custom = "custom"
    
    var defaultDuration: TimeInterval {
        switch self {
        case .focus:
            return 25 * 60 // 25 minutes
        case .breakTime:
            return 5 * 60 // 5 minutes
        case .custom:
            return 0 // User will specify
        }
    }
    
    var displayName: String {
        switch self {
        case .focus:
            return "Focus"
        case .breakTime:
            return "Break"
        case .custom:
            return "Custom"
        }
    }
}

/// Core Timer model representing a countdown timer
struct Timer {
    var id: UUID
    var name: String
    var duration: TimeInterval // Total duration in seconds
    var remainingTime: TimeInterval // Current remaining time in seconds
    var state: TimerState
    var preset: TimerPreset
    var startDate: Date?
    var createdDate: Date
    
    init(
        name: String = "Timer",
        duration: TimeInterval,
        preset: TimerPreset = .focus
    ) {
        self.id = UUID()
        self.name = name
        self.duration = duration
        self.remainingTime = duration
        self.state = .stopped
        self.preset = preset
        self.startDate = nil
        self.createdDate = Date()
    }
    
    /// Initialize from saved state
    init?(fromDictionary dict: [String: Any]) {
        guard let idString = dict["id"] as? String,
              let id = UUID(uuidString: idString),
              let name = dict["name"] as? String,
              let duration = dict["duration"] as? TimeInterval,
              let remainingTime = dict["remainingTime"] as? TimeInterval,
              let stateRawValue = dict["state"] as? String,
              let state = TimerState(rawValue: stateRawValue),
              let presetRawValue = dict["preset"] as? String,
              let preset = TimerPreset(rawValue: presetRawValue),
              let createdDate = dict["createdDate"] as? Date
        else {
            return nil
        }
        
        self.id = id
        self.name = name
        self.duration = duration
        self.remainingTime = remainingTime
        self.state = state
        self.preset = preset
        self.startDate = dict["startDate"] as? Date
        self.createdDate = createdDate
    }
    
    /// Convert to dictionary for persistence
    func toDictionary() -> [String: Any] {
        var dict: [String: Any] = [
            "id": id.uuidString,
            "name": name,
            "duration": duration,
            "remainingTime": remainingTime,
            "state": state.rawValue,
            "preset": preset.rawValue,
            "createdDate": createdDate
        ]
        
        if let startDate = startDate {
            dict["startDate"] = startDate
        }
        
        return dict
    }
    
    /// Check if timer has completed
    var isCompleted: Bool {
        return remainingTime <= 0
    }
    
    /// Get formatted time string (MM:SS)
    var formattedTime: String {
        let totalSeconds = Int(remainingTime)
        let minutes = totalSeconds / 60
        let seconds = totalSeconds % 60
        return String(format: "%02d:%02d", minutes, seconds)
    }
    
    /// Get progress percentage (0.0 to 1.0)
    var progress: Double {
        guard duration > 0 else { return 0.0 }
        return (duration - remainingTime) / duration
    }
    
    /// Start the timer
    mutating func start() {
        guard state == .stopped || state == .paused else { return }
        
        state = .running
        startDate = Date()
    }
    
    /// Pause the timer
    mutating func pause() {
        guard state == .running else { return }
        state = .paused
    }
    
    /// Stop and reset the timer
    mutating func stop() {
        state = .stopped
        remainingTime = duration
        startDate = nil
    }
    
    /// Update remaining time based on elapsed time
    mutating func updateRemainingTime() {
        guard state == .running, let startDate = startDate else { return }
        
        let elapsed = Date().timeIntervalSince(startDate)
        remainingTime = max(0, duration - elapsed)
        
        if remainingTime <= 0 {
            state = .completed
        }
    }
}

// MARK: - CustomStringConvertible
extension Timer: CustomStringConvertible {
    var description: String {
        return "Timer(name: \(name), duration: \(Int(duration))s, state: \(state), remaining: \(formattedTime))"
    }
}
