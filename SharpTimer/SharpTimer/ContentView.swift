//
//  ContentView.swift
//  SharpTimer
//
//  Created by Valutico on 13/11/25.
//

import SwiftUI

struct ContentView: View {
    @EnvironmentObject var timerViewModel: TimerViewModel
    
    var body: some View {
        VStack {
            TimerPopupView()
                .environmentObject(timerViewModel)
        }
        .frame(minWidth: 400, minHeight: 600)
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button("Settings") {
                    // This will open the settings window
                    if let settingsURL = URL(string: "x-apple.systempreferences:com.apple.Settings") {
                        NSWorkspace.shared.open(settingsURL)
                    }
                }
            }
        }
    }
}

#Preview {
    ContentView()
        .environmentObject(TimerViewModel())
}
