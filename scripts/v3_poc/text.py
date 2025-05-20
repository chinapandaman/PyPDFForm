from pypdf import PdfReader, PdfWriter
from pypdf.generic import TextStringObject
from pypdf.generic import DictionaryObject, NameObject, StreamObject, NumberObject, ArrayObject
from typing import cast

def add_ttf_font_to_acroform(input_pdf, output_pdf, font_path, font_resource_name="/F1"):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # Read font bytes
    with open(font_path, "rb") as f:
        font_data = f.read()

    # Create FontFile2 stream (TrueType font file)
    font_file_stream = StreamObject()
    font_file_stream._data = font_data
    font_file_stream.update({
        NameObject("/Length1"): NumberObject(len(font_data)),
    })
    font_file_ref = writer._add_object(font_file_stream)

    # Build FontDescriptor
    font_descriptor = DictionaryObject()
    font_descriptor.update({
        NameObject("/Type"): NameObject("/FontDescriptor"),
        NameObject("/FontName"): NameObject("/MyFont"),
        NameObject("/FontFile2"): font_file_ref,
    })
    font_descriptor_ref = writer._add_object(font_descriptor)

    # Build Font dictionary
    font_dict = DictionaryObject()
    font_dict.update({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/TrueType"),
        NameObject("/BaseFont"): NameObject("/MyFont"),
        NameObject("/FontDescriptor"): font_descriptor_ref,
        NameObject("/Encoding"): NameObject("/WinAnsiEncoding"),
    })
    font_dict_ref = writer._add_object(font_dict)

    # Add /AcroForm if missing
    if "/AcroForm" not in writer._root_object:
        writer._root_object[NameObject("/AcroForm")] = DictionaryObject({NameObject("/Fields"): ArrayObject([])})
    acroform = writer._root_object["/AcroForm"]

    # Add /DR if missing
    if "/DR" not in acroform:
        acroform[NameObject("/DR")] = DictionaryObject()
    dr = acroform["/DR"]

    # Add /Font if missing
    if "/Font" not in dr:
        dr[NameObject("/Font")] = DictionaryObject()
    fonts = dr["/Font"]

    # Register your font resource name (e.g. /F1)
    fonts[NameObject(font_resource_name)] = font_dict_ref

    # Update the default appearance string to use your font
    if "/DA" in acroform:
        da = acroform["/DA"]
        # Replace any existing font reference with your font resource
        new_da = TextStringObject(f"{font_resource_name} 12 Tf 0 g")
        acroform[NameObject("/DA")] = new_da
    else:
        acroform[NameObject("/DA")] = TextStringObject(f"{font_resource_name} 12 Tf 0 g")

    # Save the modified PDF
    with open(output_pdf, "wb") as f_out:
        writer.write(f_out)

# Usage example:
add_ttf_font_to_acroform(
    input_pdf="pdf_samples/sample_template.pdf",
    output_pdf="temp/final_output_with_font.pdf",
    font_path="font_samples/LiberationSerif-Bold.ttf",
    font_resource_name="/F1"
)

pdf = PdfReader("temp/final_output_with_font.pdf")
out = PdfWriter()

out.append(pdf)

for page in out.pages:
    for annot in page.get("/Annots", []):
        annot = cast(DictionaryObject, annot.get_object())
        if annot["/T"] != "test":
            continue

        da = annot["/DA"].split(" ")
        da[0] = "/F1"  # font
        annot[NameObject("/DA")] = TextStringObject(" ".join(da))

with open("temp/output.pdf", "wb+") as f:
    out.write(f)
