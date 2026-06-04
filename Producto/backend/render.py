import asyncio
from playwright.async_api import async_playwright
import os
import pypdf
import docx

async def render_html(html_path, output_path):
    print(f"Rendering {html_path} to {output_path}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        file_uri = f"file:///{os.path.abspath(html_path).replace(chr(92), '/')}"
        await page.goto(file_uri)
        # wait a little bit for animations
        await page.wait_for_timeout(1000)
        # get page dimensions
        body_handle = await page.evaluate_handle('document.body')
        bounding_box = await body_handle.bounding_box()
        # Set viewport to bounding box size
        if bounding_box:
            await page.set_viewport_size({"width": int(bounding_box["width"]), "height": int(bounding_box["height"])})
        await page.screenshot(path=output_path, full_page=True)
        await browser.close()

async def main():
    doc_dir = r"c:\Users\yelia\LexiScan-PAES-1\Documentacion"
    
    # 1. Extract PDF Template
    pdf_path = os.path.join(doc_dir, "Plan de Pruebas_plantilla.pdf")
    try:
        reader = pypdf.PdfReader(pdf_path)
        pdf_text = []
        for i, page in enumerate(reader.pages):
            pdf_text.append(f"--- PAGE {i} ---")
            pdf_text.append(page.extract_text())
        
        with open("pdf_template.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(pdf_text))
        print("Extracted PDF Template")
    except Exception as e:
        print(f"Error reading PDF: {e}")

    # 2. Extract Docx Template
    docx_path = os.path.join(doc_dir, "Manual de usuario [Donante].docx")
    try:
        doc = docx.Document(docx_path)
        docx_text = [p.text for p in doc.paragraphs if p.text.strip()]
        with open("docx_template.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(docx_text))
        print("Extracted Docx Template")
    except Exception as e:
        print(f"Error reading Docx: {e}")

    # 3. Render HTMLs
    htmls = ["Arquitectura del Sistema.html", "Diagrama_Clases.html", "MER.html"]
    for html_file in htmls:
        html_path = os.path.join(doc_dir, html_file)
        png_path = os.path.join(doc_dir, html_file.replace('.html', '.png'))
        if os.path.exists(html_path):
            await render_html(html_path, png_path)

if __name__ == "__main__":
    asyncio.run(main())
