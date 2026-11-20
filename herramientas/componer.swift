// Compone un fondo de slide (2000x741) a partir de una foto y siluetas opcionales.
// Uso:
//   swift componer.swift base.jpg salida.jpg recorteY recorteAlto [--oscuro] [--x=inicio:fin] [figura.png:x:y:ancho ...]
// recorteY / recorteAlto: franja horizontal de la foto (en píxeles de la foto, origen arriba).
// x, y, ancho: posición de cada silueta en el lienzo de 2000x741 (origen arriba a la izquierda).
// Cada silueta recibe un contorno negro fino, como en el diseño.
import Foundation
import CoreImage
import ImageIO
import UniformTypeIdentifiers

let W: CGFloat = 2000, H: CGFloat = 741
var args = Array(CommandLine.arguments.dropFirst())
guard args.count >= 4 else { print("uso: componer base salida recorteY recorteAlto [--oscuro] [png:x:y:ancho]"); exit(1) }
func cargar(_ ruta: String) -> CIImage {
    guard let img = CIImage(contentsOf: URL(fileURLWithPath: ruta)) else { print("no se pudo leer \(ruta)"); exit(1) }
    return img
}
let base = cargar(args[0]); let salida = args[1]
let ry = CGFloat(Double(args[2])!), rh = CGFloat(Double(args[3])!)
args = Array(args.dropFirst(4))
let oscuro = args.contains("--oscuro"); args.removeAll { $0 == "--oscuro" }
// --x=inicio:fin recorta también en horizontal (p. ej. para quitar bordes transparentes).
var rx: CGFloat = 0, rw: CGFloat = -1
if let i = args.firstIndex(where: { $0.hasPrefix("--x=") }) {
    let v = args[i].dropFirst(4).split(separator: ":").map { CGFloat(Double($0)!) }
    rx = v[0]; rw = v[1] - v[0]; args.remove(at: i)
}

// Franja: en Core Image el origen está abajo.
let bh = base.extent.height
let bw = rw > 0 ? rw : base.extent.width
let franja = base.cropped(to: CGRect(x: rx, y: bh - ry - rh, width: bw, height: rh))
let escala = W / bw
var lienzo = franja.transformed(by: CGAffineTransform(translationX: -rx, y: -(bh - ry - rh)).concatenating(CGAffineTransform(scaleX: escala, y: escala)))
lienzo = lienzo.cropped(to: CGRect(x: 0, y: 0, width: W, height: H))

if oscuro {
    // Oscurece y tiñe hacia el petróleo de la marca.
    lienzo = lienzo.applyingFilter("CIColorMatrix", parameters: [
        "inputRVector": CIVector(x: 0.38, y: 0, z: 0, w: 0),
        "inputGVector": CIVector(x: 0, y: 0.42, z: 0, w: 0),
        "inputBVector": CIVector(x: 0, y: 0, z: 0.44, w: 0),
        "inputBiasVector": CIVector(x: 0.02, y: 0.06, z: 0.07, w: 0)])
}

for capa in args {
    let p = capa.split(separator: ":").map(String.init)
    guard p.count == 4 else { continue }
    let fig = cargar(p[0])
    let x = CGFloat(Double(p[1])!), y = CGFloat(Double(p[2])!), ancho = CGFloat(Double(p[3])!)
    let s = ancho / fig.extent.width
    let alto = fig.extent.height * s
    let t = CGAffineTransform(scaleX: s, y: s).concatenating(CGAffineTransform(translationX: x, y: H - y - alto))
    let colocada = fig.transformed(by: t)
    // Contorno: alfa dilatado en negro debajo de la figura.
    let alfa = colocada.applyingFilter("CIColorMatrix", parameters: [
        "inputRVector": CIVector(x: 0, y: 0, z: 0, w: 0), "inputGVector": CIVector(x: 0, y: 0, z: 0, w: 0),
        "inputBVector": CIVector(x: 0, y: 0, z: 0, w: 0), "inputAVector": CIVector(x: 0, y: 0, z: 0, w: 1)])
    let contorno = alfa.applyingFilter("CIMorphologyMaximum", parameters: ["inputRadius": 2.5])
    lienzo = colocada.composited(over: contorno.composited(over: lienzo)).cropped(to: CGRect(x: 0, y: 0, width: W, height: H))
}

let ctx = CIContext()
guard let cg = ctx.createCGImage(lienzo, from: CGRect(x: 0, y: 0, width: W, height: H)),
      let dest = CGImageDestinationCreateWithURL(URL(fileURLWithPath: salida) as CFURL, UTType.jpeg.identifier as CFString, 1, nil)
else { print("no se pudo escribir"); exit(1) }
CGImageDestinationAddImage(dest, cg, [kCGImageDestinationLossyCompressionQuality: 0.62] as CFDictionary)
CGImageDestinationFinalize(dest)
print("ok \(salida)")
