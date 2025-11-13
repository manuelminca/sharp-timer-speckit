//
//  MenuBarIconView.swift
//  SharpTimer
//
//  Created by Sharp Timer on 2025-11-13.
//  Copyright © 2025 Sharp Timer. All rights reserved.
//

import SwiftUI
import AppKit

/// SwiftUI view that can be embedded in NSStatusItem button
struct MenuBarIconView: NSViewRepresentable {
    // MARK: - Properties
    @State private var currentIcon: String = "timer"
    @State private var iconColor: NSColor = .controlAccentColor
    @State private var backgroundColor: NSColor = .clear
    
    // MARK: - NSViewRepresentable
    func makeNSView(context: Context) -> NSView {
        let view = NSView()
        view.wantsLayer = true
        view.layer?.backgroundColor = backgroundColor.cgColor
        return view
    }
    
    func updateNSView(_ nsView: NSView, context: Context) {
        nsView.layer?.backgroundColor = backgroundColor.cgColor
        updateIcon(in: nsView)
    }
    
    // MARK: - Icon Management
    
    /// Update the icon based on timer state
    func updateTimerState(_ state: TimerState, remainingTime: TimeInterval = 0, preset: TimerPreset = .focus) {
        DispatchQueue.main.async {
            switch state {
            case .stopped:
                currentIcon = "timer"
                iconColor = .secondaryLabelColor
                backgroundColor = .clear
            case .running:
                currentIcon = getRunningIcon(for: preset)
                iconColor = .controlAccentColor
                backgroundColor = .clear
            case .paused:
                currentIcon = "pause.circle.fill"
                iconColor = .systemOrange
                backgroundColor = .clear
            case .completed:
                currentIcon = "checkmark.circle.fill"
                iconColor = .systemGreen
                backgroundColor = .clear
            }
        }
    }
    
    /// Get the appropriate running icon based on preset
    private func getRunningIcon(for preset: TimerPreset) -> String {
        switch preset {
        case .focus:
            return "timer" // SF Symbol for timer
        case .breakTime:
            return "cup.and.saucer.fill" // SF Symbol for break
        case .custom:
            return "clock.arrow.circlepath" // SF Symbol for custom
        }
    }
    
    // MARK: - Private Methods
    
    private func updateIcon(in view: NSView) {
        // Clear existing subviews
        view.subviews.forEach { $0.removeFromSuperview() }
        
        // Create SF Symbol image
        let image = NSImage(systemSymbolName: currentIcon, accessibilityDescription: "Timer Icon")?
            .withSymbolConfiguration(NSImage.SymbolConfiguration(pointSize: 14, weight: .regular))
        
        if let image = image {
            let imageView = NSImageView(image: image)
            imageView.imageScaling = .scaleProportionallyDown
            imageView.isEditable = false
            imageView.image?.isTemplate = true // Allow tinting
            
            // Set tint color
            imageView.contentTintColor = iconColor
            
            // Center the image in the view
            imageView.frame = view.bounds
            imageView.autoresizingMask = [.width, .height]
            
            view.addSubview(imageView)
        }
    }
}

/// Simple timer icon that can be used when no timer is running
struct SimpleTimerIcon: View {
    var body: some View {
        Image(systemName: "timer")
            .font(.system(size: 14, weight: .regular))
            .foregroundColor(.secondary)
    }
}

/// View for showing timer in menu bar when active
struct ActiveTimerIcon: View {
    let state: TimerState
    let remainingTime: TimeInterval
    let preset: TimerPreset
    
    var body: some View {
        HStack(spacing: 2) {
            // Timer state icon
            Image(systemName: getStateIcon())
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(getStateColor())
            
            // Optional: Show remaining time when running
            if state == .running {
                Text(remainingTime.formattedTime)
                    .font(.system(size: 10, weight: .medium, design: .monospaced))
                    .foregroundColor(.primary)
            }
        }
        .padding(.horizontal, 4)
        .padding(.vertical, 2)
        .background(getBackgroundColor())
        .cornerRadius(4)
    }
    
    private func getStateIcon() -> String {
        switch state {
        case .running:
            return "play.circle.fill"
        case .paused:
            return "pause.circle.fill"
        case .stopped:
            return "stop.circle"
        case .completed:
            return "checkmark.circle.fill"
        }
    }
    
    private func getStateColor() -> Color {
        switch state {
        case .running:
            return .accentColor
        case .paused:
            return .orange
        case .stopped:
            return .secondary
        case .completed:
            return .green
        }
    }
    
    private func getBackgroundColor() -> Color {
        switch state {
        case .running, .paused, .completed:
            return Color.white.opacity(0.1)
        case .stopped:
            return Color.clear
        }
    }
}

// MARK: - Preview
struct MenuBarIconView_Previews: PreviewProvider {
    static var previews: some View {
        VStack(spacing: 20) {
            MenuBarIconView()
                .frame(width: 30, height: 22)
                .onAppear {
                    // Test different states
                    DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
                        // This would update to running state
                    }
                }
            
            Text("Menu Bar Timer Icon")
                .font(.caption)
        }
        .padding()
    }
}

// MARK: - TimeInterval Extension
extension TimeInterval {
    var formattedTime: String {
        let totalSeconds = Int(self)
        let minutes = totalSeconds / 60
        let seconds = totalSeconds % 60
        return String(format: "%02d:%02d", minutes, seconds)
    }
}
