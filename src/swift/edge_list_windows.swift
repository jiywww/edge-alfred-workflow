#!/usr/bin/env swift

// Edge Window Lister
// Lists all Edge windows with their PID and window numbers in JSON format

import Cocoa
import Foundation

struct WindowInfo: Codable {
    let pid: Int
    let windowNumber: Int
    let title: String
    let index: Int
}

func getEdgeWindows() -> [WindowInfo] {
    var windows: [WindowInfo] = []
    
    let options: CGWindowListOption = [.optionOnScreenOnly, .excludeDesktopElements]
    guard let windowList = CGWindowListCopyWindowInfo(options, kCGNullWindowID) as? [[String: Any]] else {
        return windows
    }
    
    var edgeWindowIndex = 0
    for windowInfo in windowList {
        guard let ownerName = windowInfo[kCGWindowOwnerName as String] as? String,
              ownerName == "Microsoft Edge",
              let windowNumber = windowInfo[kCGWindowNumber as String] as? Int,
              let pid = windowInfo[kCGWindowOwnerPID as String] as? Int else {
            continue
        }
        
        let title = windowInfo[kCGWindowName as String] as? String ?? "Untitled"
        windows.append(WindowInfo(
            pid: pid,
            windowNumber: windowNumber,
            title: title,
            index: edgeWindowIndex
        ))
        edgeWindowIndex += 1
    }
    
    return windows
}

// Main execution
let windows = getEdgeWindows()
let encoder = JSONEncoder()
encoder.outputFormatting = .prettyPrinted

if let jsonData = try? encoder.encode(windows),
   let jsonString = String(data: jsonData, encoding: .utf8) {
    print(jsonString)
} else {
    print("[]")
}