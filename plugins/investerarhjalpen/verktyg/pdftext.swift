import PDFKit
let url = URL(fileURLWithPath: CommandLine.arguments[1])
guard let doc = PDFDocument(url: url) else { print("FAIL"); exit(1) }
print(doc.string ?? "")
