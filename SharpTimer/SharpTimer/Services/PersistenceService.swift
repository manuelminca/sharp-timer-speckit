//
//  PersistenceService.swift
//  SharpTimer
//
//  Created by Sharp Timer on 2025-11-13.
//  Copyright © 2025 Sharp Timer. All rights reserved.
//

import Foundation

/// Service for persisting timer state using UserDefaults
class PersistenceService {
    // MARK: - Constants
    private enum Constants {
        static let timerStateKey = "SharpTimer_SavedTimerState"
        static let userPreferencesKey = "SharpTimer_UserPreferences"
        static let customDurationsKey = "SharpTimer_CustomDurations"
        static let lastSavedKey = "SharpTimer_LastSavedTimestamp"
    }
    
    // MARK: - UserDefaults
    private let defaults: UserDefaults
    
    // MARK: - Initialization
    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
        setupMigrationIfNeeded()
    }
    
    // MARK: - Timer State Persistence
    
    /// Save current timer state to UserDefaults
    func saveTimerState(_ timer: Timer) {
        let timerStateData = TimerStateData(from: timer)
        let encoder = JSONEncoder()
        
        do {
            let encodedData = try encoder.encode(timerStateData)
            defaults.set(encodedData, forKey: Constants.timerStateKey)
            defaults.set(Date().timeIntervalSince1970, forKey: Constants.lastSavedKey)
            defaults.synchronize()
            
            print("Timer state saved successfully")
        } catch {
            print("Failed to save timer state: \(error.localizedDescription)")
        }
    }
    
    /// Load saved timer state from UserDefaults
    func loadTimerState() -> TimerStateData? {
        guard let encodedData = defaults.data(forKey: Constants.timerStateKey) else {
            print("No saved timer state found")
            return nil
        }
        
        let decoder = JSONDecoder()
        
        do {
            let timerStateData = try decoder.decode(TimerStateData.self, from: encodedData)
            
            // Validate the loaded state
            guard timerStateData.isValid else {
                print("Saved timer state is expired or invalid")
                clearSavedTimerState()
                return nil
            }
            
            print("Timer state loaded successfully")
            return timerStateData
            
        } catch {
            print("Failed to load timer state: \(error.localizedDescription)")
            clearSavedTimerState()
            return nil
        }
    }
    
    /// Clear saved timer state from UserDefaults
    func clearSavedTimerState() {
        defaults.removeObject(forKey: Constants.timerStateKey)
        defaults.removeObject(forKey: Constants.lastSavedKey)
        defaults.synchronize()
        print("Timer state cleared from storage")
    }
    
    /// Check if there's a valid saved timer state
    func hasValidSavedState() -> Bool {
        return loadTimerState() != nil
    }
    
    /// Get time since last state save
    func getTimeSinceLastSave() -> TimeInterval? {
        guard let lastSavedTime = defaults.object(forKey: Constants.lastSavedKey) as? TimeInterval else {
            return nil
        }
        return Date().timeIntervalSince1970 - lastSavedTime
    }
    
    // MARK: - User Preferences
    
    /// Save user preferences
    func saveUserPreferences(_ preferences: [String: Any]) {
        defaults.set(preferences, forKey: Constants.userPreferencesKey)
        defaults.synchronize()
    }
    
    /// Load user preferences
    func loadUserPreferences() -> [String: Any]? {
        return defaults.dictionary(forKey: Constants.userPreferencesKey)
    }
    
    /// Save custom timer duration preference
    func saveCustomDuration(_ duration: TimeInterval, for preset: String) {
        var customDurations = loadCustomDurations()
        customDurations[preset] = duration
        defaults.set(customDurations, forKey: Constants.customDurationsKey)
        defaults.synchronize()
    }
    
    /// Load custom timer duration for a specific preset
    func loadCustomDuration(for preset: String) -> TimeInterval? {
        let customDurations = loadCustomDurations()
        return customDurations[preset] as? TimeInterval
    }
    
    /// Load all custom durations
    func loadCustomDurations() -> [String: Any] {
        return defaults.dictionary(forKey: Constants.customDurationsKey) ?? [:]
    }
    
    /// Clear all user preferences
    func clearAllPreferences() {
        defaults.removeObject(forKey: Constants.userPreferencesKey)
        defaults.removeObject(forKey: Constants.customDurationsKey)
        defaults.synchronize()
    }
    
    // MARK: - Data Validation and Safety
    
    /// Validate that timer state data is not corrupted
    func validateTimerStateData(_ data: Data) -> Bool {
        let decoder = JSONDecoder()
        
        do {
            let timerStateData = try decoder.decode(TimerStateData.self, from: data)
            return timerStateData.isValid
        } catch {
            return false
        }
    }
    
    /// Check for data corruption and attempt recovery
    func checkAndRecoverCorruptedData() {
        guard let savedState = loadTimerState() else { return }
        
        // Additional validation beyond TimerStateData.isValid
        guard validateTimeConsistency(savedState) else {
            print("Timer state data is temporally inconsistent, clearing...")
            clearSavedTimerState()
            return
        }
        
        print("Timer state data validation passed")
    }
    
    /// Validate time consistency in saved state
    private func validateTimeConsistency(_ stateData: TimerStateData) -> Bool {
        let now = Date()
        
        // Check if saved state is not in the future
        if stateData.lastUpdated > now.addingTimeInterval(60) { // Allow 1 minute tolerance
            return false
        }
        
        // Check if remaining time is not greater than total duration
        if stateData.remainingTime > stateData.totalDuration {
            return false
        }
        
        // Check if remaining time is not negative
        if stateData.remainingTime < 0 {
            return false
        }
        
        return true
    }
    
    // MARK: - Migration and Backup
    
    /// Setup any necessary data migration
    private func setupMigrationIfNeeded() {
        let currentVersion = 1
        let savedVersion = defaults.integer(forKey: "SharpTimer_DataVersion")
        
        if savedVersion < currentVersion {
            performMigration(from: savedVersion, to: currentVersion)
            defaults.set(currentVersion, forKey: "SharpTimer_DataVersion")
        }
    }
    
    /// Perform data migration between versions
    private func performMigration(from oldVersion: Int, to newVersion: Int) {
        print("Performing data migration from version \(oldVersion) to \(newVersion)")
        
        // Migration logic for future versions can be added here
        switch (oldVersion, newVersion) {
        case (0, 1):
            // Initial migration - ensure all required keys exist
            break
        default:
            break
        }
    }
    
    /// Create a backup of current state before making changes
    func createBackup() {
        guard let currentState = loadTimerState() else { return }
        
        let backupKey = "\(Constants.timerStateKey)_backup_\(Int(Date().timeIntervalSince1970))"
        let encoder = JSONEncoder()
        
        do {
            let encodedData = try encoder.encode(currentState)
            defaults.set(encodedData, forKey: backupKey)
            print("Backup created: \(backupKey)")
        } catch {
            print("Failed to create backup: \(error.localizedDescription)")
        }
    }
    
    /// Get information about stored data
    func getStorageInfo() -> (hasTimerState: Bool, hasPreferences: Bool, lastSaveTime: Date?) {
        let hasTimerState = defaults.data(forKey: Constants.timerStateKey) != nil
        let hasPreferences = defaults.dictionary(forKey: Constants.userPreferencesKey) != nil
        
        var lastSaveTime: Date?
        if let lastSavedTimestamp = defaults.object(forKey: Constants.lastSavedKey) as? TimeInterval {
            lastSaveTime = Date(timeIntervalSince1970: lastSavedTimestamp)
        }
        
        return (hasTimerState, hasPreferences, lastSaveTime)
    }
    
    // MARK: - Debug and Utility Methods
    
    /// Print debug information about current storage state
    func printDebugInfo() {
        let storageInfo = getStorageInfo()
        print("=== Persistence Service Debug Info ===")
        print("Has Timer State: \(storageInfo.hasTimerState)")
        print("Has Preferences: \(storageInfo.hasPreferences)")
        print("Last Save Time: \(storageInfo.lastSaveTime?.description ?? "None")")
        
        if let timeSinceLastSave = getTimeSinceLastSave() {
            print("Time Since Last Save: \(Int(timeSinceLastSave)) seconds")
        }
        
        let customDurations = loadCustomDurations()
        if !customDurations.isEmpty {
            print("Custom Durations: \(customDurations)")
        }
        print("=====================================")
    }
    
    /// Reset all saved data (useful for testing)
    func resetAllData() {
        clearSavedTimerState()
        clearAllPreferences()
        defaults.removeObject(forKey: "SharpTimer_DataVersion")
        print("All persistence data cleared")
    }
}

// MARK: - PersistenceService Mock for Testing
#if DEBUG
class MockPersistenceService: PersistenceService {
    private var mockTimerState: TimerStateData?
    private var mockPreferences: [String: Any] = [:]
    private var callLog: [String] = []
    
    override func saveTimerState(_ timer: Timer) {
        callLog.append("saveTimerState")
        mockTimerState = TimerStateData(from: timer)
    }
    
    override func loadTimerState() -> TimerStateData? {
        callLog.append("loadTimerState")
        return mockTimerState
    }
    
    override func clearSavedTimerState() {
        callLog.append("clearSavedTimerState")
        mockTimerState = nil
    }
    
    override func hasValidSavedState() -> Bool {
        callLog.append("hasValidSavedState")
        return mockTimerState != nil
    }
    
    func getCallLog() -> [String] {
        return callLog
    }
    
    func clearCallLog() {
        callLog.removeAll()
    }
    
    func setMockTimerState(_ timerStateData: TimerStateData?) {
        mockTimerState = timerStateData
    }
    
    func setMockPreferences(_ preferences: [String: Any]) {
        mockPreferences = preferences
    }
}
#endif
