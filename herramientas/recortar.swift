// Recorta el contorno de la persona principal de una foto con Vision (macOS 14+).
// Uso:
//   swift recortar.swift entrada.jpg salida.png            -> figura en color con fondo transparente
//   swift recortar.swift entrada.jpg salida.png 1f4b4f     -> silueta plana del color indicado
import Foundation
import Vision
import CoreImage
import ImageIO
import UniformTypeIdentifiers

let args = CommandLine.arguments
guard args.count >= 3 else { print("uso: recortar entrada salida [colorhex]"); exit(1) }
let entrada = URL(fileURLWithPath: args[1])
let salida = URL(fileURLWithPath: args[2])
let colorHex = args.count > 3 ? args[3] : nil

guard let fuente = CGImageSourceCreateWithURL(entrada as CFURL, nil),
      let cg = CGImageSourceCreateImageAtIndex(fuente, 0, nil) else { print("no se pudo leer"); exit(1) }

let handler = VNImageRequestHandler(cgImage: cg, options: [:])
let peticion = VNGenerateForegroundInstanceMaskRequest()
try handler.perform([peticion])
guard let resultado = peticion.results?.first else { print("sin figura"); exit(1) }

// Elegir la instancia con más píxeles (la persona principal).
let mapa = resultado.instanceMask
CVPixelBufferLockBaseAddress(mapa, .readOnly)
let w = CVPixelBufferGetWidth(mapa), h = CVPixelBufferGetHeight(mapa)
let fila = CVPixelBufferGetBytesPerRow(mapa)
let base = CVPixelBufferGetBaseAddress(mapa)!.assumingMemoryBound(to: UInt8.self)
var cuenta = [Int: Int]()
for y in 0..<h { for x in 0..<w { let v = Int(base[y * fila + x]); if v > 0 { cuenta[v, default: 0] += 1 } } }
CVPixelBufferUnlockBaseAddress(mapa, .readOnly)
guard let principal = cuenta.max(by: { $0.value < $1.value })?.key else { print("sin figura"); exit(1) }

let buffer = try resultado.generateMaskedImage(ofInstances: IndexSet(integer: principal), from: handler, croppedToInstancesExtent: true)
var imagen = CIImage(cvPixelBuffer: buffer)

if let hex = colorHex, let valor = UInt32(hex, radix: 16) {
    let r = CGFloat((valor >> 16) & 0xff) / 255, g = CGFloat((valor >> 8) & 0xff) / 255, b = CGFloat(valor & 0xff) / 255
    let plano = CIImage(color: CIColor(red: r, green: g, blue: b)).cropped(to: imagen.extent)
    // Usa el alfa de la figura como máscara sobre un color plano.
    let alfa = imagen.applyingFilter("CIColorMatrix", parameters: [
        "inputRVector": CIVector(x: 0, y: 0, z: 0, w: 1),
        "inputGVector": CIVector(x: 0, y: 0, z: 0, w: 1),
        "inputBVector": CIVector(x: 0, y: 0, z: 0, w: 1),
        "inputAVector": CIVector(x: 0, y: 0, z: 0, w: 1)])
    imagen = plano.applyingFilter("CIBlendWithMask", parameters: [
        kCIInputBackgroundImageKey: CIImage.empty().cropped(to: imagen.extent),
        kCIInputMaskImageKey: alfa])
}

let contexto = CIContext()
guard let destino = CGImageDestinationCreateWithURL(salida as CFURL, UTType.png.identifier as CFString, 1, nil),
      let final = contexto.createCGImage(imagen, from: imagen.extent) else { print("no se pudo escribir"); exit(1) }
CGImageDestinationAddImage(destino, final, nil)
CGImageDestinationFinalize(destino)
print("ok \(salida.lastPathComponent) \(final.width)x\(final.height) instancia \(principal) de \(cuenta.count)")
