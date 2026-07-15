import AppKit
import CoreGraphics
import Foundation

guard let frontmost = NSWorkspace.shared.frontmostApplication,
      frontmost.bundleIdentifier == "com.google.Chrome" else {
    fputs("Google Chrome is not the frontmost application.\n", stderr)
    exit(2)
}

let options: CGWindowListOption = [.optionOnScreenOnly, .excludeDesktopElements]
guard let windows = CGWindowListCopyWindowInfo(options, kCGNullWindowID)
        as? [[String: Any]] else {
    fputs("Unable to read on-screen windows.\n", stderr)
    exit(3)
}

let chromePID = frontmost.processIdentifier
let chromeWindows = windows.compactMap { window -> CGRect? in
    let ownerPID = (window[kCGWindowOwnerPID as String] as? NSNumber)?.int32Value
    let layer = (window[kCGWindowLayer as String] as? NSNumber)?.intValue
    guard ownerPID == chromePID,
          layer == 0,
          let boundsDictionary = window[kCGWindowBounds as String] as? [String: Any],
          let bounds = CGRect(dictionaryRepresentation: boundsDictionary as CFDictionary),
          bounds.width >= 400,
          bounds.height >= 300 else {
        return nil
    }
    return bounds
}

guard let bounds = chromeWindows.max(by: {
    ($0.width * $0.height) < ($1.width * $1.height)
}) else {
    fputs("Unable to find the frontmost Chrome window bounds.\n", stderr)
    exit(4)
}

let point = CGPoint(x: bounds.midX, y: bounds.midY)
guard let move = CGEvent(
    mouseEventSource: nil,
    mouseType: .mouseMoved,
    mouseCursorPosition: point,
    mouseButton: .left
) else {
    fputs("Unable to create the mouse-move event.\n", stderr)
    exit(5)
}

move.post(tap: .cghidEventTap)
usleep(300_000)
print("Moved pointer to Google Chrome window center at \(Int(point.x)),\(Int(point.y)).")
