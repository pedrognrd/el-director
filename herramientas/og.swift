// Genera la imagen para redes sociales (1200x630) a partir del hero de la portada.
// Uso: swift og.swift fondo.jpg logo.png salida.jpg
import AppKit
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

let a = CommandLine.arguments
func cargar(_ p: String) -> CGImage {
    let src = CGImageSourceCreateWithURL(URL(fileURLWithPath: p) as CFURL, nil)!
    return CGImageSourceCreateImageAtIndex(src, 0, nil)!
}
let fondo = cargar(a[1]), logo = cargar(a[2])
let W = 1200, H = 630
let ctx = CGContext(data: nil, width: W, height: H, bitsPerComponent: 8, bytesPerRow: 0,
                    space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!

// Foto a sangre (cover), encuadrada hacia la derecha como en el hero
let s = max(CGFloat(W) / CGFloat(fondo.width), CGFloat(H) / CGFloat(fondo.height))
let fw = CGFloat(fondo.width) * s, fh = CGFloat(fondo.height) * s
ctx.draw(fondo, in: CGRect(x: (CGFloat(W) - fw) * 0.7, y: (CGFloat(H) - fh) / 2, width: fw, height: fh))

// Degradado oscuro de izquierda a derecha (mismo que el hero)
let col = CGColorSpaceCreateDeviceRGB()
let paradas: [(CGFloat, CGFloat)] = [(0, 0.96), (0.30, 0.86), (0.52, 0.55), (0.75, 0.18), (1, 0.05)]
let grad = CGGradient(colorsSpace: col, colors: paradas.map { CGColor(red: 4/255, green: 13/255, blue: 15/255, alpha: $0.1) } as CFArray,
                      locations: paradas.map { $0.0 })!
ctx.drawLinearGradient(grad, start: CGPoint(x: 0, y: 0), end: CGPoint(x: W, y: 0), options: [])

// Logo, líneas y subtítulo (origen de CoreGraphics abajo a la izquierda)
let x: CGFloat = 70, ancho: CGFloat = 540
let lh = ancho * CGFloat(logo.height) / CGFloat(logo.width)
let yLogo: CGFloat = 330
ctx.draw(logo, in: CGRect(x: x, y: yLogo, width: ancho, height: lh))
let papel = CGColor(red: 236/255, green: 232/255, blue: 223/255, alpha: 1)
ctx.setFillColor(papel)
ctx.fill(CGRect(x: x, y: yLogo - 22, width: ancho, height: 5))
ctx.fill(CGRect(x: x, y: yLogo - 112, width: ancho, height: 5))

let gctx = NSGraphicsContext(cgContext: ctx, flipped: false)
NSGraphicsContext.current = gctx
let fuente = NSFont(name: "Impact", size: 50) ?? NSFont.boldSystemFont(ofSize: 50)
let texto = NSAttributedString(string: "DEL LIBRO A LA PELÍCULA", attributes: [.font: fuente, .foregroundColor: NSColor(cgColor: papel)!, .kern: 0.5])
let t = texto.size()
texto.draw(at: CGPoint(x: x + (ancho - t.width) / 2, y: yLogo - 22 - 45 - t.height / 2))
let pie = NSAttributedString(string: "QUIÉN ES QUIÉN · DAVID JIMÉNEZ · DANI DE LA ORDEN",
                             attributes: [.font: NSFont(name: "Impact", size: 22) ?? fuente, .foregroundColor: NSColor(calibratedRed: 227/255, green: 178/255, blue: 60/255, alpha: 1), .kern: 1.2])
pie.draw(at: CGPoint(x: x, y: yLogo - 170))

let img = ctx.makeImage()!
let dest = CGImageDestinationCreateWithURL(URL(fileURLWithPath: a[3]) as CFURL, UTType.jpeg.identifier as CFString, 1, nil)!
CGImageDestinationAddImage(dest, img, [kCGImageDestinationLossyCompressionQuality: 0.82] as CFDictionary)
CGImageDestinationFinalize(dest)
print("ok")
