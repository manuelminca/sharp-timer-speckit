//
//  NotificationService.swift
//  SharpTimer
//
//  Created by Sharp Timer on 2025-11-13.
//  Copyright © 2025 Sharp Timer. All rights reserved.
//

import Foundation
import UserNotifications
import AppKit
import CoreAudio
import AudioToolbox

/// Service for managing macOS notifications and user alerts
class NotificationService: NSObject {
    // MARK: - Properties
    private let notificationCenter = UNUserNotificationCenter.current()
    
    // MARK: - Initialization
    override init() {
        super.init()
        setupNotifications()
    }
    
    // MARK: - Permission Management
    
    /// Request notification permissions from the user
    func requestPermission(completion: @escaping (Bool) -> Void) {
        notificationCenter.requestAuthorization(options: [.alert, .sound, .badge]) { granted, error in
            if let error = error {
                print("Notification permission error: \(error.localizedDescription)")
                completion(false)
                return
            }
            completion(granted)
        }
    }
    
    /// Check current notification permission status
    func checkPermissionStatus(completion: @escaping (UNAuthorizationStatus) -> Void) {
        notificationCenter.getNotificationSettings { settings in
            completion(settings.authorizationStatus)
        }
    }
    
    // MARK: - Notification Sending
    
    /// Send an immediate notification
    func sendNotification(
        title: String,
        body: String,
        identifier: String = UUID().uuidString,
        sound: UNNotificationSound = .default
    ) {
        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = sound
        content.userInfo = [
            "identifier": identifier,
            "timestamp": Date().timeIntervalSince1970
        ]
        
        let request = UNNotificationRequest(
            identifier: identifier,
            content: content,
            trigger: nil // Send immediately
        )
        
        notificationCenter.add(request) { error in
            if let error = error {
                print("Failed to send notification: \(error.localizedDescription)")
            }
        }
    }
    
    /// Schedule a notification for a future time
    func scheduleNotification(
        title: String,
        body: String,
        identifier: String,
        timeInterval: TimeInterval,
        sound: UNNotificationSound = .default
    ) {
        guard timeInterval > 0 else { return }
        
        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = sound
        content.userInfo = [
            "identifier": identifier,
            "timestamp": Date().timeIntervalSince1970
        ]
        
        let trigger = UNTimeIntervalNotificationTrigger(timeInterval: timeInterval, repeats: false)
        let request = UNNotificationRequest(
            identifier: identifier,
            content: content,
            trigger: trigger
        )
        
        notificationCenter.add(request) { error in
            if let error = error {
                print("Failed to schedule notification: \(error.localizedDescription)")
            }
        }
    }
    
    // MARK: - Timer-Specific Notifications
    
    /// Send timer completion notification
    func sendTimerCompletionNotification(title: String, body: String) {
        sendNotification(
            title: title,
            body: body,
            identifier: "timer-completion",
            sound: .default
        )
        
        // Also play system sound for additional feedback
        playSystemSound(soundType: .default)
    }
    
    /// Send timer almost done notification (5 minutes remaining)
    func sendTimerAlmostDoneNotification(remainingMinutes: Int, presetType: String) {
        let title = "Timer Almost Done"
        let body = "\(remainingMinutes) minutes remaining for your \(presetType) timer"
        
        sendNotification(
            title: title,
            body: body,
            identifier: "timer-almost-done"
        )
    }
    
    // MARK: - Sound Management
    
    /// Play system sounds for user feedback
    func playSystemSound(soundType: SystemSoundType) {
        let soundID: SystemSoundID
        
        switch soundType {
        case .default:
            soundID = kSystemSoundID_UserPreferredAlert
        case .completion:
            soundID = 1007 // SMSReceived_Alert
        case .warning:
            soundID = kSystemSoundID_UserPreferredAlert // Use preferred alert instead
        case .success:
            soundID = kSystemSoundID_UserPreferredAlert
        }
        
        AudioServicesPlaySystemSound(soundID)
    }
    
    // MARK: - Notification Management
    
    /// Cancel all pending notifications
    func cancelAllNotifications() {
        notificationCenter.removeAllPendingNotificationRequests()
    }
    
    /// Cancel specific notification by identifier
    func cancelNotification(identifier: String) {
        notificationCenter.removePendingNotificationRequests(withIdentifiers: [identifier])
    }
    
    /// Get all pending notifications
    func getPendingNotifications(completion: @escaping ([UNNotificationRequest]) -> Void) {
        notificationCenter.getPendingNotificationRequests { requests in
            completion(requests)
        }
    }
    
    // MARK: - Private Methods
    
    private func setupNotifications() {
        // Configure notification center delegate
        notificationCenter.delegate = self
        
        // Request initial permission
        checkPermissionStatus { status in
            switch status {
            case .notDetermined:
                // Will be requested when first timer is started
                break
            case .denied:
                print("Notification permission denied by user")
                break
            case .authorized:
                print("Notification permission granted")
                break
            case .provisional:
                print("Notification permission granted provisionally")
                break
            case .ephemeral:
                print("Notification permission granted ephemerally")
                break
            @unknown default:
                print("Unknown notification permission status")
            }
        }
    }
}

// MARK: - UNUserNotificationCenterDelegate
extension NotificationService: UNUserNotificationCenterDelegate {
    
    /// Called when notification is delivered to app while it's active
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification,
        withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void
    ) {
        // Show notification even when app is active
        if #available(macOS 14.0, *) {
            completionHandler([.banner, .sound, .badge])
        } else {
            completionHandler([.alert, .sound, .badge])
        }
    }
    
    /// Called when user interacts with notification
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse,
        withCompletionHandler completionHandler: @escaping () -> Void
    ) {
        let identifier = response.notification.request.content.userInfo["identifier"] as? String ?? ""
        
        // Handle different notification types
        switch identifier {
        case "timer-completion":
            handleTimerCompletionNotification()
        case "timer-almost-done":
            handleTimerAlmostDoneNotification()
        default:
            break
        }
        
        completionHandler()
    }
    
    private func handleTimerCompletionNotification() {
        // Bring app to front when timer completes
        NSApp.activate(ignoringOtherApps: true)
    }
    
    private func handleTimerAlmostDoneNotification() {
        // Could show a subtle alert or update UI
        print("Timer almost done notification received")
    }
}

// MARK: - Supporting Types

/// System sound types for different notification scenarios
enum SystemSoundType {
    case `default`
    case completion
    case warning
    case success
}

// MARK: - Mock NotificationService for Testing
#if DEBUG
class MockNotificationService: NotificationService {
    private var permissionsGranted = false
    private var sentNotifications: [(title: String, body: String, identifier: String)] = []
    
    override func requestPermission(completion: @escaping (Bool) -> Void) {
        permissionsGranted = true
        DispatchQueue.main.async {
            completion(true)
        }
    }
    
    override func sendNotification(title: String, body: String, identifier: String, sound: UNNotificationSound) {
        sentNotifications.append((title, body, identifier))
    }
    
    override func scheduleNotification(title: String, body: String, identifier: String, timeInterval: TimeInterval, sound: UNNotificationSound) {
        sentNotifications.append((title, body, identifier))
    }
    
    func getSentNotifications() -> [(title: String, body: String, identifier: String)] {
        return sentNotifications
    }
    
    func clearNotifications() {
        sentNotifications.removeAll()
    }
}
#endif
