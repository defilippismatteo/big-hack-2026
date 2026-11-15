import Foundation
import Vision
import AppKit

let args = CommandLine.arguments
if args.count < 2 { exit(1) }
let dir = args[1]
let fm = FileManager.default
let files = try fm.contentsOfDirectory(atPath: dir).filter { $0.hasSuffix(".png") }.sorted()

struct TextBox: Codable {
    let text: String
    let x: Double
    let y: Double
    let w: Double
    let h: Double
}
struct FrameReport: Codable {
    let file: String
    let idx: Int
    let timeSec: Double
    let texts: [TextBox]
}

var reports: [FrameReport] = []

for (i, file) in files.enumerated() {
    let path = (dir as NSString).appendingPathComponent(file)
    guard let nsImg = NSImage(contentsOfFile: path),
          let cgImg = nsImg.cgImage(forProposedRect: nil, context: nil, hints: nil) else { continue }
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.recognitionLanguages = ["en-US", "it-IT"]
    req.usesLanguageCorrection = false
    let handler = VNImageRequestHandler(cgImage: cgImg, options: [:])
    try? handler.perform([req])
    var boxes: [TextBox] = []
    if let obs = req.results {
        for o in obs {
            guard let top = o.topCandidates(1).first else { continue }
            let bb = o.boundingBox
            // Vision bbox origin is bottom-left; convert y to top-left
            boxes.append(TextBox(
                text: top.string,
                x: Double(round(bb.origin.x * 1000) / 1000),
                y: Double(round((1.0 - bb.origin.y - bb.height) * 1000) / 1000),
                w: Double(round(bb.width * 1000) / 1000),
                h: Double(round(bb.height * 1000) / 1000)
            ))
        }
    }
    reports.append(FrameReport(file: file, idx: i, timeSec: Double(i) / 3.0, texts: boxes))
}

let enc = JSONEncoder()
enc.outputFormatting = [.prettyPrinted]
let data = try enc.encode(reports)
print(String(data: data, encoding: .utf8)!)
