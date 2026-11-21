// Recorta la "E" del logo y la centra sobre un cuadrado petróleo. Uso: favicon logo.png x0 x1 salida.png tamaño
import Foundation; import CoreGraphics; import ImageIO; import UniformTypeIdentifiers
let a = CommandLine.arguments
let src = CGImageSourceCreateWithURL(URL(fileURLWithPath: a[1]) as CFURL, nil)!
let logo = CGImageSourceCreateImageAtIndex(src, 0, nil)!
let x0 = Int(a[2])!, x1 = Int(a[3])!, S = Int(a[5])!
let e = logo.cropping(to: CGRect(x: x0, y: 0, width: x1 - x0 + 1, height: logo.height))!
let ctx = CGContext(data: nil, width: S, height: S, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
ctx.setFillColor(CGColor(red: 15/255, green: 42/255, blue: 44/255, alpha: 1))
ctx.fill(CGRect(x: 0, y: 0, width: S, height: S))
let margen = CGFloat(S) * 0.1
let esc = min((CGFloat(S) - 2*margen) / CGFloat(e.width), (CGFloat(S) - 2*margen) / CGFloat(e.height))
let w = CGFloat(e.width) * esc, h = CGFloat(e.height) * esc
ctx.interpolationQuality = .high
ctx.draw(e, in: CGRect(x: (CGFloat(S) - w)/2, y: (CGFloat(S) - h)/2, width: w, height: h))
let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: a[4]) as CFURL, UTType.png.identifier as CFString, 1, nil)!
CGImageDestinationAddImage(d, ctx.makeImage()!, nil); CGImageDestinationFinalize(d)
