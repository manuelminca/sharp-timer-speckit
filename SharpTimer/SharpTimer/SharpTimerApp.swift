//
//  SharpTimerApp.swift
//  SharpTimer
//
//  Created by Sharp Timer on 2025-11-13.
//  Copyright © 2025 Sharp Timer. All rights reserved.
//

import SwiftUI
import AppKit

// MARK: - Notification Names
extension Notification.Name {
    static let appWillTerminate = Notification.Name("appWillTerminate")
}

// MARK: - Window Delegate for Proper App Termination
class MainWindowDelegate: NSObject, NSWindowDelegate {
    private let appTermination: () -> Void
    
    init(termination: @escaping () -> Void) {
        self.appTermination = termination
        super.init()
    }
    
    func windowShouldClose(_ sender: NSWindow) -> Bool {
        // For menu bar apps, close the main window should terminate the app
        appTermination()
        return true
    }
    
    func windowWillClose(_ notification: Notification) {
        // Additional cleanup if needed
        print("SharpTimer: Main window closing")
    }
}

@main
struct SharpTimerApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    
    var body: some Scene {
        // Hidden window for menu bar app - not shown to user
        WindowGroup("Sharp Timer", id: "main") {
            EmptyView()
                .onAppear {
                    // Hide the window immediately when it appears
                    if let window = NSApplication.shared.windows.first {
                        window.setIsVisible(false)
                    }
                }
        }
        .defaultSize(width: 1, height: 1)
        .windowStyle(.hiddenTitleBar)
        .windowResizability(.contentMinSize)
        .commands {
            CommandGroup(replacing: CommandGroupPlacement.newItem) { }
            CommandGroup(replacing: CommandGroupPlacement.windowArrangement) { }
        }
        
        Settings {
            SettingsView()
                .environmentObject(TimerViewModel())
        }
    }
}

// MARK: - App Delegate for Menu Bar Integration
class AppDelegate: NSObject, NSApplicationDelegate {
    private var statusItem: NSStatusItem?
    private var popupWindow: NSWindow?
    private var timerViewModel: TimerViewModel?
    private var mainWindowDelegate: MainWindowDelegate?
    
    func applicationDidFinishLaunching(_ notification: Notification) {
        print("SharpTimer: App did finish launching")
        
        // Set up window termination handler
        setupWindowTermination()
        
        // Hide the main window immediately for menu bar app behavior
        hideMainWindow()
        
        // Add a small delay to ensure app is fully initialized
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            self.setupMenuBarIcon()
            self.setupTimerViewModel()
        }
        
        // Backup: Try to create status item immediately if async fails
        setupMenuBarIcon()
        setupTimerViewModel()
        
        print("SharpTimer: Setup completed")
    }
    
    private func hideMainWindow() {
        // Hide all windows except popup windows
        for window in NSApplication.shared.windows {
            if window.title == "Sharp Timer" && window.styleMask.contains(.titled) {
                window.setIsVisible(false)
            }
        }
    }
    
    private func setupWindowTermination() {
        // Set up a window delegate for the main window to handle proper app termination
        mainWindowDelegate = MainWindowDelegate { [weak self] in
            self?.terminateApp()
        }
        
        // Find and set up the main window delegate
        if let window = NSApplication.shared.windows.first {
            window.delegate = mainWindowDelegate
        }
        
        // Monitor for app termination when all windows are closed
        NotificationCenter.default.addObserver(
            forName: NSApplication.didHideNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            self?.checkAppTermination()
        }
    }
    
    private func checkAppTermination() {
        // Check if the app should terminate based on window state
        let windows = NSApplication.shared.windows
        let hasVisibleWindows = windows.contains { window in
            window.isVisible && window != popupWindow && !window.styleMask.contains(.borderless)
        }
        
        // For menu bar apps, terminate when main window is closed
        if !hasVisibleWindows && popupWindow?.isVisible == false {
            terminateApp()
        }
    }
    
    private func terminateApp() {
        print("SharpTimer: Terminating app gracefully")
        
        // Clean up resources
        cleanup()
        
        // Post termination notification
        NotificationCenter.default.post(name: .appWillTerminate, object: nil)
        
        // Terminate the app
        NSApplication.shared.terminate(nil)
    }
    
    func applicationWillTerminate(_ notification: Notification) {
        print("SharpTimer: App will terminate")
        cleanup()
    }
    
    private func setupMenuBarIcon() {
        print("SharpTimer: Setting up menu bar icon")
        
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        
        guard let statusItem = statusItem,
              let button = statusItem.button else { 
            print("SharpTimer: Failed to create status item or button")
            return 
        }
        
        print("SharpTimer: Status item created successfully")
        
        // Create a simple, bold colored square that's impossible to miss
        let icon = NSImage(size: NSSize(width: 20, height: 20))
        icon.lockFocus()
        
        // Draw a bright blue background
        NSColor.systemBlue.setFill()
        NSRect(x: 0, y: 0, width: 20, height: 20).fill()
        
        // Draw white "ST" text
        let attributes: [NSAttributedString.Key: Any] = [
            .font: NSFont.systemFont(ofSize: 12, weight: .bold),
            .foregroundColor: NSColor.white
        ]
        let text = NSAttributedString(string: "ST", attributes: attributes)
        text.draw(at: NSPoint(x: 4, y: 4))
        
        icon.unlockFocus()
        button.image = icon
        button.image?.isTemplate = false
        
        // Set up button properties
        button.target = self
        button.action = #selector(menuBarIconClicked(_:))
        button.toolTip = "Sharp Timer - Click to open timer controls"
        
        print("SharpTimer: Custom icon created and assigned to button")
        print("SharpTimer: Menu bar icon setup completed")
    }
    
    private func setupTimerViewModel() {
        print("SharpTimer: Setting up TimerViewModel")
        timerViewModel = TimerViewModel()
        print("SharpTimer: TimerViewModel setup completed")
    }
    
    @objc private func menuBarIconClicked(_ sender: NSStatusItem) {
        print("SharpTimer: Menu bar icon clicked")
        toggleTimerPopup()
    }
    
    private func toggleTimerPopup() {
        if popupWindow?.isVisible == true {
            closeTimerPopup()
        } else {
            openTimerPopup()
        }
    }
    
    private func openTimerPopup() {
        closeTimerPopup() // Close any existing window
        
        // Create popup window with TimerPopupView
        let popupView = TimerPopupView()
        let hostingView = NSHostingView(rootView: popupView)
        
        // Create window
        popupWindow = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 320, height: 600),
            styleMask: [.titled, .closable, .resizable],
            backing: .buffered,
            defer: false
        )
        
        guard let popupWindow = popupWindow else { return }
        
        popupWindow.contentView = hostingView
        popupWindow.title = "Sharp Timer"
        popupWindow.isMovableByWindowBackground = true
        popupWindow.titlebarAppearsTransparent = true
        popupWindow.backgroundColor = NSColor.clear
        
        // Position window near menu bar
        if let statusItem = statusItem,
           let button = statusItem.button,
           let screen = button.window?.screen {
            
            let buttonFrame = button.convert(button.bounds, to: nil)
            let buttonWindowFrame = button.window?.convertToScreen(buttonFrame) ?? .zero
            
            var x = buttonWindowFrame.midX - popupWindow.frame.width / 2
            x = max(screen.frame.minX + 20, min(x, screen.frame.maxX - popupWindow.frame.width - 20))
            
            let y = screen.frame.maxY - popupWindow.frame.height - 40
            
            popupWindow.setFrameOrigin(NSPoint(x: x, y: y))
        }
        
        // Make window appear above other windows
        popupWindow.level = .floating
        
        // Show window
        popupWindow.makeKeyAndOrderFront(nil)
        
        // Center on screen if positioning failed
        popupWindow.center()
    }
    
    private func closeTimerPopup() {
        popupWindow?.close()
        popupWindow = nil
    }
    
    private func cleanup() {
        closeTimerPopup()
        statusItem = nil
        timerViewModel = nil
        mainWindowDelegate = nil
        
        // Remove observers
        NotificationCenter.default.removeObserver(self)
    }
}
