//
//  TimerPopupView.swift
//  SharpTimer
//
//  Created by Sharp Timer on 2025-11-13.
//  Copyright © 2025 Sharp Timer. All rights reserved.
//

import SwiftUI
import AppKit

/// Main popup window view for timer control and display
struct TimerPopupView: View {
    // MARK: - Environment
    @Environment(\.colorScheme) var colorScheme
    @Environment(\.dismiss) private var dismiss
    
    // MARK: - ViewModel
    @StateObject private var viewModel = TimerViewModel()
    
    // MARK: - State
    @State private var selectedPreset: TimerPreset = .focus
    @State private var customMinutes: String = "25"
    @State private var showCustomInput = false
    @State private var isWindowVisible = false
    
    // MARK: - Body
    var body: some View {
        VStack(spacing: 16) {
            // Header with app title and close button
            headerView
            
            // Timer Display
            if viewModel.currentTimer != nil {
                TimerDisplayView(
                    remainingTime: $viewModel.remainingTime,
                    totalDuration: $viewModel.totalDuration,
                    timerState: $viewModel.currentState,
                    preset: $viewModel.currentPreset
                )
                .transition(.scale.combined(with: .opacity))
            } else {
                emptyStateView
            }
            
            // Timer Controls
            timerControlsView
            
            // Preset Selection
            presetSelectionView
            
            // Custom Duration Input
            if showCustomInput {
                customDurationInputView
            }
            
            // Quick Actions
            quickActionsView
            
            Spacer(minLength: 8)
        }
        .padding(20)
        .frame(width: 320, height: autoHeight)
        .background(backgroundColor)
        .cornerRadius(16)
        .shadow(color: shadowColor, radius: 20, x: 0, y: 8)
        .onAppear {
            setupWindow()
        }
        .onReceive(viewModel.$currentTimer) { _ in
            withAnimation(.easeInOut(duration: 0.3)) {
                // Trigger height recalculation
            }
        }
        .onReceive(viewModel.$isTimerActive) { _ in
            withAnimation(.easeInOut(duration: 0.3)) {
                // Update UI based on timer activity
            }
        }
    }
    
    // MARK: - View Components
    
    /// Header with title and close button
    private var headerView: some View {
        HStack {
            HStack(spacing: 8) {
                Image(systemName: "timer")
                    .font(.title2)
                    .foregroundColor(.accentColor)
                
                Text("Sharp Timer")
                    .font(.headline)
                    .fontWeight(.semibold)
                    .foregroundColor(.primary)
            }
            
            Spacer()
            
            Button(action: {
                closeWindow()
            }) {
                Image(systemName: "xmark.circle.fill")
                    .font(.title3)
                    .foregroundColor(.secondary)
            }
            .buttonStyle(PlainButtonStyle())
            .help("Close")
        }
        .padding(.bottom, 8)
    }
    
    /// Empty state when no timer is running
    private var emptyStateView: some View {
        VStack(spacing: 16) {
            Image(systemName: "timer")
                .font(.system(size: 48, weight: .light))
                .foregroundColor(.secondary)
            
            VStack(spacing: 4) {
                Text("Ready to Focus?")
                    .font(.headline)
                    .fontWeight(.medium)
                
                Text("Choose a preset or set custom time")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .frame(height: 200)
        .frame(maxWidth: .infinity)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.secondary.opacity(0.05))
        )
    }
    
    /// Timer control buttons
    private var timerControlsView: some View {
        HStack(spacing: 12) {
            if viewModel.currentTimer != nil {
                // Timer is running/paused - show control buttons
                Button(action: {
                    if viewModel.isTimerRunning {
                        viewModel.pauseTimer()
                    } else {
                        viewModel.resumeTimer()
                    }
                }) {
                    HStack(spacing: 6) {
                        Image(systemName: viewModel.isTimerRunning ? "pause.fill" : "play.fill")
                        Text(viewModel.isTimerRunning ? "Pause" : "Resume")
                    }
                    .font(.headline)
                    .fontWeight(.medium)
                }
                .buttonStyle(PrimaryButtonStyle())
                
                Button(action: {
                    viewModel.stopTimer()
                }) {
                    HStack(spacing: 6) {
                        Image(systemName: "stop.fill")
                        Text("Stop")
                    }
                    .font(.headline)
                    .fontWeight(.medium)
                }
                .buttonStyle(DestructiveButtonStyle())
            } else {
                // No timer - show start button
                Button(action: {
                    startTimer()
                }) {
                    HStack(spacing: 6) {
                        Image(systemName: "play.fill")
                        Text("Start Timer")
                    }
                    .font(.headline)
                    .fontWeight(.medium)
                }
                .buttonStyle(PrimaryButtonStyle())
            }
        }
        .frame(maxWidth: .infinity)
    }
    
    /// Preset selection buttons
    private var presetSelectionView: some View {
        VStack(spacing: 8) {
            Text("Timer Preset")
                .font(.subheadline)
                .fontWeight(.medium)
                .foregroundColor(.secondary)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 8), count: 3), spacing: 8) {
                ForEach(TimerPreset.allCases, id: \.self) { preset in
                    PresetButton(
                        preset: preset,
                        isSelected: selectedPreset == preset,
                        action: {
                            selectPreset(preset)
                        }
                    )
                }
            }
        }
    }
    
    /// Custom duration input
    private var customDurationInputView: some View {
        VStack(spacing: 8) {
            Text("Custom Duration")
                .font(.subheadline)
                .fontWeight(.medium)
                .foregroundColor(.secondary)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            HStack(spacing: 8) {
                TextField("Minutes", text: $customMinutes)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .frame(width: 80)
                    .onSubmit {
                        validateAndStartTimer()
                    }
                
                Text("minutes")
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Spacer()
                
                Button("Start") {
                    validateAndStartTimer()
                }
                .buttonStyle(SecondaryButtonStyle())
                .disabled(customMinutes.isEmpty)
            }
        }
        .transition(.move(edge: .top).combined(with: .opacity))
    }
    
    /// Quick action buttons
    private var quickActionsView: some View {
        HStack(spacing: 8) {
            Button("Settings") {
                openSettings()
            }
            .buttonStyle(SecondaryButtonStyle())
            
            Button("Clear Saved State") {
                clearSavedState()
            }
            .buttonStyle(SecondaryButtonStyle())
            
            Spacer()
        }
        .font(.caption)
        .foregroundColor(.secondary)
    }
    
    // MARK: - Computed Properties
    
    /// Auto-calculated window height
    private var autoHeight: CGFloat {
        let baseHeight: CGFloat = 420
        let customInputHeight: CGFloat = showCustomInput ? 60 : 0
        let timerHeight: CGFloat = viewModel.currentTimer != nil ? 280 : 200
        
        return CGFloat(baseHeight + customInputHeight + timerHeight)
    }
    
    /// Background color based on color scheme
    private var backgroundColor: Color {
        colorScheme == .dark ? Color.black.opacity(0.8) : Color.white
    }
    
    /// Shadow color
    private var shadowColor: Color {
        colorScheme == .dark ? .black : .gray.opacity(0.3)
    }
    
    // MARK: - Actions
    
    private func startTimer() {
        let duration: TimeInterval
        
        switch selectedPreset {
        case .focus:
            duration = 25 * 60 // 25 minutes
        case .breakTime:
            duration = 5 * 60 // 5 minutes
        case .custom:
            duration = viewModel.minutesToTimeInterval(Int(customMinutes) ?? 25)
        }
        
        viewModel.startTimer(duration: duration, preset: selectedPreset)
    }
    
    private func validateAndStartTimer() {
        guard let minutes = Int(customMinutes),
              viewModel.validateCustomDuration(minutes) else {
            showInvalidInputAlert()
            return
        }
        
        selectedPreset = .custom
        startTimer()
    }
    
    private func selectPreset(_ preset: TimerPreset) {
        selectedPreset = preset
        showCustomInput = (preset == .custom)
        
        if preset != .custom {
            // Auto-start when preset is selected (unless custom)
            startTimer()
        }
    }
    
    private func showInvalidInputAlert() {
        let alert = NSAlert()
        alert.messageText = "Invalid Duration"
        alert.informativeText = "Please enter a duration between 1 and 480 minutes."
        alert.alertStyle = .warning
        alert.runModal()
    }
    
    private func closeWindow() {
        dismiss()
    }
    
    private func setupWindow() {
        // Configure window behavior if needed
    }
    
    private func openSettings() {
        // Placeholder for settings functionality
        print("Settings clicked")
    }
    
    private func clearSavedState() {
        let alert = NSAlert()
        alert.messageText = "Clear Saved State?"
        alert.informativeText = "This will remove any saved timer state. Continue?"
        alert.alertStyle = .warning
        alert.addButton(withTitle: "Clear")
        alert.addButton(withTitle: "Cancel")
        
        if alert.runModal() == .alertFirstButtonReturn {
            viewModel.stopTimer()
        }
    }
}

// MARK: - Supporting Views

/// Preset selection button
struct PresetButton: View {
    let preset: TimerPreset
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 6) {
                Image(systemName: presetIconName)
                    .font(.title3)
                    .foregroundColor(isSelected ? .white : presetColor)
                
                Text(preset.displayName)
                    .font(.caption)
                    .fontWeight(.medium)
                    .foregroundColor(isSelected ? .white : .primary)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 12)
            .background(
                RoundedRectangle(cornerRadius: 8)
                    .fill(isSelected ? presetColor : presetColor.opacity(0.1))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(presetColor.opacity(isSelected ? 0 : 0.3), lineWidth: 1)
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var presetColor: Color {
        switch preset {
        case .focus:
            return .blue
        case .breakTime:
            return .green
        case .custom:
            return .purple
        }
    }
    
    private var presetIconName: String {
        switch preset {
        case .focus:
            return "brain.head.profile"
        case .breakTime:
            return "cup.and.saucer.fill"
        case .custom:
            return "clock.arrow.circlepath"
        }
    }
}

// MARK: - Button Styles

struct PrimaryButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .padding(.horizontal, 16)
            .padding(.vertical, 10)
            .background(Color.accentColor)
            .foregroundColor(.white)
            .cornerRadius(8)
            .shadow(color: .accentColor.opacity(0.3), radius: 4, x: 0, y: 2)
            .scaleEffect(configuration.isPressed ? 0.95 : 1.0)
            .animation(.easeInOut(duration: 0.1), value: configuration.isPressed)
    }
}

struct DestructiveButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .padding(.horizontal, 16)
            .padding(.vertical, 10)
            .background(Color.red)
            .foregroundColor(.white)
            .cornerRadius(8)
            .shadow(color: .red.opacity(0.3), radius: 4, x: 0, y: 2)
            .scaleEffect(configuration.isPressed ? 0.95 : 1.0)
            .animation(.easeInOut(duration: 0.1), value: configuration.isPressed)
    }
}

struct SecondaryButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .padding(.horizontal, 12)
            .padding(.vertical, 6)
            .background(Color.secondary.opacity(0.1))
            .foregroundColor(.primary)
            .cornerRadius(6)
            .scaleEffect(configuration.isPressed ? 0.95 : 1.0)
            .animation(.easeInOut(duration: 0.1), value: configuration.isPressed)
    }
}

// MARK: - Preview

struct TimerPopupView_Previews: PreviewProvider {
    static var previews: some View {
        TimerPopupView()
            .frame(width: 320, height: 600)
            .padding()
            .previewLayout(.sizeThatFits)
    }
}
