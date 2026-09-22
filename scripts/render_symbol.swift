import AppKit

let width = 200
let height = 200
let output = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "source-symbol.png"

guard let bitmap = NSBitmapImageRep(
    bitmapDataPlanes: nil,
    pixelsWide: width,
    pixelsHigh: height,
    bitsPerSample: 8,
    samplesPerPixel: 4,
    hasAlpha: true,
    isPlanar: false,
    colorSpaceName: .deviceRGB,
    bytesPerRow: width * 4,
    bitsPerPixel: 32
) else {
    fatalError("Could not create bitmap")
}

NSGraphicsContext.saveGraphicsState()
guard let context = NSGraphicsContext(bitmapImageRep: bitmap) else {
    fatalError("Could not create graphics context")
}
NSGraphicsContext.current = context

NSColor.black.setFill()
NSRect(x: 0, y: 0, width: width, height: height).fill()

let paragraph = NSMutableParagraphStyle()
paragraph.alignment = .center
let attributes: [NSAttributedString.Key: Any] = [
    .font: NSFont.systemFont(ofSize: 156, weight: .black),
    .foregroundColor: NSColor.white,
    .paragraphStyle: paragraph,
]

let symbol = NSAttributedString(string: "‽", attributes: attributes)
let bounds = symbol.boundingRect(
    with: NSSize(width: width, height: 240),
    options: [.usesLineFragmentOrigin, .usesFontLeading]
)
let drawRect = NSRect(
    x: 0,
    y: (CGFloat(height) - bounds.height) / 2 - 8,
    width: CGFloat(width),
    height: bounds.height
)
symbol.draw(with: drawRect, options: [.usesLineFragmentOrigin, .usesFontLeading])

context.flushGraphics()
NSGraphicsContext.restoreGraphicsState()

guard let png = bitmap.representation(using: .png, properties: [:]) else {
    fatalError("Could not encode PNG")
}
try png.write(to: URL(fileURLWithPath: output))
