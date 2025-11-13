//
//  TimerDisplayView.swift
//  SharpTimer
//
//  Created by Sharp Timer on 2025-11-13.
//  Copyright © 2025 Sharp Timer. All rights reserved.
//

import SwiftUI

/// View that displays the countdown timer with visual progress
struct TimerDisplayView: View {
    // MARK: - Properties
    @Binding var remainingTime: TimeInterval
    @Binding var totalDuration: TimeInterval
    @Binding var timerState: TimerState
    @Binding var preset: TimerPreset
    
    // Animation states
    @State private var animationOffset: CGFloat = 0
    @State private var pulseAnimation = false
    
    // MARK: - Body
    var body: some View {
        VStack(spacing: 20) {
            // Timer State Icon
            timerStateIcon
            
            // Main Timer Display
            timerTimeDisplay
            
            // Progress Bar
            progressBar
            
            // Timer Status Text
            timerStatusText
            
            Spacer()
        }
        .padding(24)
        .background(backgroundGradient)
        .cornerRadius(16)
        .shadow(color: shadowColor.opacity(0.3), radius: 10, x: 0, y: 4)
        .onAppear {
            startAnimations()
        }
        .onChange(of: timerState) { newState in
            handleStateChange(newState)
        }
    }
    
    // MARK: - Timer Components
    
    /// Timer state icon with animations
    private var timerStateIcon: some View {
        ZStack {
            // Background circle
            Circle()
                .fill(stateIconBackground)
                .frame(width: 80, height: 80)
            
            // Icon
            Image(systemName: stateIconName)
                .font(.system(size: 32, weight: .bold))
                .foregroundColor(stateIconColor)
                .scaleEffect(pulseAnimation ? 1.1 : 1.0)
                .animation(
                    pulseAnimation ? 
                    Animation.easeInOut(duration: 1.0).repeatForever(autoreverses: true) :
                    .default,
                    value: pulseAnimation
                )
        }
        .shadow(color: stateIconColor.opacity(0.3), radius: 8, x: 0, y: 4)
    }
    
    /// Main timer display with large, clear time
    private var timerTimeDisplay: some View {
        VStack(spacing: 8) {
            Text(formattedTime)
                .font(.system(size: 72, weight: .bold, design: .monospaced))
                .foregroundColor(timeTextColor)
                .minimumScaleFactor(0.5)
                .lineLimit(1)
                .shadow(color: .black.opacity(0.1), radius: 2, x: 0, y: 1)
            
            // Preset indicator
            presetBadge
        }
        .offset(y: animationOffset)
        .animation(.spring(response: 0.6, dampingFraction: 0.8), value: animationOffset)
    }
    
    /// Visual progress bar
    private var progressBar: some View {
        VStack(spacing: 8) {
            // Background track
            RoundedRectangle(cornerRadius: 4)
                .fill(Color.secondary.opacity(0.2))
                .frame(height: 8)
                .overlay(
                    // Progress fill
                    GeometryReader { geometry in
                        RoundedRectangle(cornerRadius: 4)
                            .fill(progressGradient)
                            .frame(
                                width: geometry.size.width * progress,
                                height: geometry.size.height
                            )
                            .animation(.easeInOut(duration: 0.3), value: progress)
                    }
                )
            
            // Progress percentage text
            Text("\(Int(progress * 100))% complete")
                .font(.caption)
                .foregroundColor(.secondary)
                .fontWeight(.medium)
        }
        .frame(maxWidth: .infinity)
    }
    
    /// Status text showing current state
    private var timerStatusText: some View {
        Text(statusText)
            .font(.headline)
            .fontWeight(.semibold)
            .foregroundColor(statusTextColor)
            .padding(.horizontal, 16)
            .padding(.vertical, 8)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(statusBackground)
            )
    }
    
    /// Preset badge showing timer type
    private var presetBadge: some View {
        HStack(spacing: 6) {
            Image(systemName: presetIconName)
                .font(.caption)
            Text(preset.displayName)
                .font(.caption)
                .fontWeight(.medium)
        }
        .foregroundColor(presetColor)
        .padding(.horizontal, 12)
        .padding(.vertical, 6)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(presetColor.opacity(0.15))
        )
    }
    
    // MARK: - Computed Properties
    
    /// Progress as 0.0 to 1.0
    private var progress: Double {
        guard totalDuration > 0 else { return 0.0 }
        return (totalDuration - remainingTime) / totalDuration
    }
    
    /// Formatted time string (MM:SS)
    private var formattedTime: String {
        let totalSeconds = Int(remainingTime)
        let minutes = totalSeconds / 60
        let seconds = totalSeconds % 60
        return String(format: "%02d:%02d", minutes, seconds)
    }
    
    /// Status text based on current state
    private var statusText: String {
        switch timerState {
        case .stopped:
            return "Ready to Start"
        case .running:
            return "Timer Running"
        case .paused:
            return "Timer Paused"
        case .completed:
            return "Timer Complete!"
        }
    }
    
    // MARK: - Color and Style Properties
    
    /// Background gradient based on timer state
    private var backgroundGradient: LinearGradient {
        let gradient: [(Color, Double)] = switch timerState {
        case .stopped:
            [(Color.gray.opacity(0.1), 0.0), (Color.gray.opacity(0.05), 1.0)]
        case .running:
            [(Color.accentColor.opacity(0.1), 0.0), (Color.accentColor.opacity(0.05), 1.0)]
        case .paused:
            [(Color.orange.opacity(0.1), 0.0), (Color.orange.opacity(0.05), 1.0)]
        case .completed:
            [(Color.green.opacity(0.1), 0.0), (Color.green.opacity(0.05), 1.0)]
        }
        
        return LinearGradient(
            colors: gradient.map { $0.0 },
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    }
    
    /// Timer state icon name
    private var stateIconName: String {
        switch timerState {
        case .stopped:
            return "timer"
        case .running:
            return "play.circle.fill"
        case .paused:
            return "pause.circle.fill"
        case .completed:
            return "checkmark.circle.fill"
        }
    }
    
    /// Timer state icon color
    private var stateIconColor: Color {
        switch timerState {
        case .stopped:
            return .gray
        case .running:
            return .accentColor
        case .paused:
            return .orange
        case .completed:
            return .green
        }
    }
    
    /// Timer state icon background
    private var stateIconBackground: Color {
        switch timerState {
        case .stopped:
            return .gray.opacity(0.15)
        case .running:
            return .accentColor.opacity(0.15)
        case .paused:
            return .orange.opacity(0.15)
        case .completed:
            return .green.opacity(0.15)
        }
    }
    
    /// Time display text color
    private var timeTextColor: Color {
        switch timerState {
        case .stopped:
            return .primary
        case .running:
            return .accentColor
        case .paused:
            return .orange
        case .completed:
            return .green
        }
    }
    
    /// Status text color
    private var statusTextColor: Color {
        switch timerState {
        case .stopped:
            return .secondary
        case .running:
            return .accentColor
        case .paused:
            return .orange
        case .completed:
            return .green
        }
    }
    
    /// Status background color
    private var statusBackground: Color {
        switch timerState {
        case .stopped:
            return .secondary.opacity(0.1)
        case .running:
            return .accentColor.opacity(0.1)
        case .paused:
            return .orange.opacity(0.1)
        case .completed:
            return .green.opacity(0.1)
        }
    }
    
    /// Preset-specific color
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
    
    /// Preset icon name
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
    
    /// Progress bar gradient
    private var progressGradient: LinearGradient {
        return LinearGradient(
            colors: [timeTextColor, timeTextColor.opacity(0.7)],
            startPoint: .leading,
            endPoint: .trailing
        )
    }
    
    /// Shadow color
    private var shadowColor: Color {
        switch timerState {
        case .stopped:
            return .gray
        case .running:
            return .accentColor
        case .paused:
            return .orange
        case .completed:
            return .green
        }
    }
    
    // MARK: - Animation Methods
    
    private func startAnimations() {
        if timerState == .running {
            startPulseAnimation()
        }
    }
    
    private func handleStateChange(_ newState: TimerState) {
        switch newState {
        case .running:
            startPulseAnimation()
            animateOffset()
        case .paused:
            stopPulseAnimation()
            resetOffset()
        case .completed:
            stopPulseAnimation()
            animateOffset()
        case .stopped:
            stopPulseAnimation()
            resetOffset()
        }
    }
    
    private func startPulseAnimation() {
        pulseAnimation = true
    }
    
    private func stopPulseAnimation() {
        pulseAnimation = false
    }
    
    private func animateOffset() {
        withAnimation(.easeInOut(duration: 0.6)) {
            animationOffset = timerState == .running ? -2 : 0
        }
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.6) {
            withAnimation(.easeInOut(duration: 0.6)) {
                animationOffset = 0
            }
        }
    }
    
    private func resetOffset() {
        animationOffset = 0
    }
}

// MARK: - Preview
struct TimerDisplayView_Previews: PreviewProvider {
    static var previews: some View {
        VStack {
            TimerDisplayView(
                remainingTime: .constant(900), // 15 minutes
                totalDuration: .constant(1500), // 25 minutes
                timerState: .constant(.running),
                preset: .constant(.focus)
            )
            .frame(width: 300, height: 400)
            
            TimerDisplayView(
                remainingTime: .constant(0),
                totalDuration: .constant(1500),
                timerState: .constant(.completed),
                preset: .constant(.breakTime)
            )
            .frame(width: 300, height: 400)
        }
        .padding()
        .previewLayout(.sizeThatFits)
    }
}
