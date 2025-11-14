//
//  SettingsView.swift
//  SharpTimer
//
//  Created by Sharp Timer on 2025-11-14.
//  Copyright © 2025 Sharp Timer. All rights reserved.
//

import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var timerViewModel: TimerViewModel
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        VStack(spacing: 20) {
            // Header
            HStack {
                Image(systemName: "gear")
                    .font(.title)
                    .foregroundColor(.accentColor)
                
                Text("Settings")
                    .font(.title)
                    .fontWeight(.bold)
                
                Spacer()
                
                Button("Done") {
                    dismiss()
                }
            }
            .padding(.horizontal)
            
            Divider()
            
            // Timer Presets
            VStack(alignment: .leading, spacing: 16) {
                Text("Timer Presets")
                    .font(.headline)
                    .fontWeight(.semibold)
                
                VStack(spacing: 8) {
                    ForEach(TimerPreset.allCases, id: \.self) { preset in
                        HStack {
                            Image(systemName: getPresetIcon(preset))
                                .foregroundColor(getPresetColor(preset))
                            
                            VStack(alignment: .leading) {
                                Text(preset.displayName)
                                    .font(.body)
                                    .fontWeight(.medium)
                                
                                Text("\(Int(preset.defaultDuration / 60)) minutes")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                            
                            Spacer()
                        }
                        .padding()
                        .background(
                            RoundedRectangle(cornerRadius: 8)
                                .fill(getPresetColor(preset).opacity(0.1))
                        )
                    }
                }
            }
            .padding(.horizontal)
            
            Divider()
            
            // App Information
            VStack(alignment: .leading, spacing: 12) {
                Text("About")
                    .font(.headline)
                    .fontWeight(.semibold)
                
                VStack(alignment: .leading, spacing: 4) {
                    Text("Sharp Timer")
                        .font(.body)
                        .fontWeight(.medium)
                    
                    Text("Version 1.0")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    
                    Text("A simple and elegant timer app for macOS")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .padding(.horizontal)
            
            Spacer()
        }
        .frame(width: 400, height: 500)
        .background(Color(.windowBackgroundColor))
    }
    
    private func getPresetIcon(_ preset: TimerPreset) -> String {
        switch preset {
        case .focus:
            return "brain.head.profile"
        case .breakTime:
            return "cup.and.saucer.fill"
        case .custom:
            return "clock.arrow.circlepath"
        }
    }
    
    private func getPresetColor(_ preset: TimerPreset) -> Color {
        switch preset {
        case .focus:
            return .blue
        case .breakTime:
            return .green
        case .custom:
            return .purple
        }
    }
}

#Preview {
    SettingsView()
        .environmentObject(TimerViewModel())
}
