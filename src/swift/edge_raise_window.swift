#!/usr/bin/env swift

// Edge Window Raiser
// A helper utility to raise specific Edge windows without bringing all windows forward
// Usage: edge_raise_window <pid> <window_number>

import Cocoa
import ApplicationServices

// Declare the private API
@_silgen_name("_AXUIElementGetWindow")
func _AXUIElementGetWindow(_ element: AXUIElement, _ outWindow: UnsafeMutablePointer<CGWindowID>) -> AXError

func raiseWindow(pid: Int, windowNumber: Int) -> Bool {
    let axApp = AXUIElementCreateApplication(pid_t(pid))
    var axWindows: AnyObject?
    let result = AXUIElementCopyAttributeValue(axApp, kAXWindowsAttribute as CFString, &axWindows)
    
    guard result == .success, let windows = axWindows as? [AXUIElement] else {
        print("Error: Failed to get windows for PID \(pid)", to: &stderr)
        return false
    }
    
    for axWindow in windows {
        var axWindowNumber: CGWindowID = 0
        let getWindowResult = _AXUIElementGetWindow(axWindow, &axWindowNumber)
        
        if getWindowResult == .success && axWindowNumber == windowNumber {
            // Found the target window
            // EXACTLY like Alfred does: activate first, then immediately raise
            if let app = NSRunningApplication(processIdentifier: pid_t(pid)) {
                app.activate(options: .activateIgnoringOtherApps)
            }
            
            // Then immediately raise the specific window
            let raiseResult = AXUIElementPerformAction(axWindow, kAXRaiseAction as CFString)
            
            if raiseResult == .success {
                return true
            } else {
                print("Error: Failed to raise window. Error code: \(raiseResult.rawValue)", to: &stderr)
                return false
            }
        }
    }
    
    print("Error: Window \(windowNumber) not found for PID \(pid)", to: &stderr)
    return false
}

// Custom stderr stream
var stderr = FileHandle.standardError

extension FileHandle: TextOutputStream {
    public func write(_ string: String) {
        guard let data = string.data(using: .utf8) else { return }
        self.write(data)
    }
}

// Main execution
guard CommandLine.arguments.count == 3,
      let pid = Int(CommandLine.arguments[1]),
      let windowNumber = Int(CommandLine.arguments[2]) else {
    print("Usage: edge_raise_window <pid> <window_number>", to: &stderr)
    print("Example: edge_raise_window 57622 203368", to: &stderr)
    exit(64) // Usage error
}

let success = raiseWindow(pid: pid, windowNumber: windowNumber)
exit(success ? 0 : 1)