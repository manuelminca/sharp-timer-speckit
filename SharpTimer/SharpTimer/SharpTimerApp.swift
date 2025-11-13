//
//  SharpTimerApp.swift
//  SharpTimer
//
//  Created by Sharp Timer on 2025-11-13.
//  Copyright © 2025 Sharp Timer. All rights reserved.
//

import SwiftUI

@main
struct SharpTimerApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    
    var body: some Scene {
        Settings {
            EmptyView()
        }
    }
}

// MARK: - App Delegate for Menu Bar Integration
class AppDelegate: NSObject, NSApplicationDelegate {
    private var statusItem: NSStatusItem?
    private var popupWindow: NSWindow?
    private var timerViewModel: TimerViewModel?
    
    func applicationDidFinishLaunching(_ notification: Notification) {
        setupMenuBarIcon()
        setupTimerViewModel()
    }
    
    func applicationWillTerminate(_ notification: Notification) {
        cleanup()
    }
    
    private func setupMenuBarIcon() {
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        
        guard let statusItem = statusItem,
              let button = statusItem.button else { return }
        
        // Set up the menu bar icon
        button.image = NSImage(systemSymbolName: "timer", accessibilityDescription: "Sharp Timer")
        button.image?.isTemplate = true
        button.target = self
        button.action = #selector(menuBarIconClicked(_:))
        
        // Add tooltip
        button.toolTip = "Sharp Timer - Click to open timer controls"
    }
    
    private func setupTimerViewModel() {
        timerViewModel = TimerViewModel()
    }
    
    @objc private func menuBarIconClicked(_ sender: NSStatusItem) {
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
    }
}
