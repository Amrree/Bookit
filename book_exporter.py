#!/usr/bin/env python3
"""
Book Exporter

Exports the Tarot for Witches book in multiple formats including HTML, PDF, and EPUB.
"""

import os
import sys
import json
import datetime
from pathlib import Path
from typing import Dict, Any


class BookExporter:
    """Exports books in multiple formats."""
    
    def __init__(self, input_file: str, output_dir: str = "./Books"):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def read_book_content(self) -> str:
        """Read the book content from file."""
        with open(self.input_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def export_to_html(self, content: str) -> str:
        """Export book to HTML format."""
        
        # Convert markdown to HTML (simplified conversion)
        html_content = self._markdown_to_html(content)
        
        # Create full HTML document
        full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tarot for Witches</title>
    <style>
        body {{
            font-family: 'Georgia', serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
            color: #333;
        }}
        h1 {{
            color: #8B4513;
            text-align: center;
            border-bottom: 3px solid #8B4513;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #A0522D;
            border-bottom: 2px solid #A0522D;
            padding-bottom: 5px;
        }}
        h3 {{
            color: #CD853F;
        }}
        h4 {{
            color: #D2691E;
        }}
        .toc {{
            background-color: #f0f0f0;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .chapter {{
            margin: 30px 0;
            padding: 20px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .metadata {{
            background-color: #e8f4f8;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            font-style: italic;
        }}
        blockquote {{
            border-left: 4px solid #8B4513;
            margin: 20px 0;
            padding-left: 20px;
            font-style: italic;
            background-color: #f8f8f8;
        }}
        ul, ol {{
            padding-left: 30px;
        }}
        li {{
            margin: 5px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #8B4513;
            color: #666;
        }}
    </style>
</head>
<body>
    {html_content}
    
    <div class="footer">
        <p>Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Tarot for Witches - A Complete Guide to Tarot Reading and Witchcraft Integration</p>
    </div>
</body>
</html>"""
        
        # Save HTML file
        html_filename = self.input_file.stem + ".html"
        html_path = self.output_dir / html_filename
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        return str(html_path)
    
    def _markdown_to_html(self, markdown_content: str) -> str:
        """Convert markdown to HTML (simplified)."""
        
        html = markdown_content
        
        # Convert headers
        html = html.replace('# ', '<h1>').replace('\n# ', '</h1>\n<h1>')
        html = html.replace('## ', '<h2>').replace('\n## ', '</h2>\n<h2>')
        html = html.replace('### ', '<h3>').replace('\n### ', '</h3>\n<h3>')
        html = html.replace('#### ', '<h4>').replace('\n#### ', '</h4>\n<h4>')
        
        # Convert bold text
        html = html.replace('**', '<strong>').replace('**', '</strong>')
        
        # Convert italic text
        html = html.replace('*', '<em>').replace('*', '</em>')
        
        # Convert line breaks
        html = html.replace('\n\n', '</p>\n<p>')
        html = '<p>' + html + '</p>'
        
        # Convert lists
        lines = html.split('\n')
        in_list = False
        result_lines = []
        
        for line in lines:
            if line.strip().startswith('- '):
                if not in_list:
                    result_lines.append('<ul>')
                    in_list = True
                result_lines.append(f'<li>{line.strip()[2:]}</li>')
            else:
                if in_list:
                    result_lines.append('</ul>')
                    in_list = False
                result_lines.append(line)
        
        if in_list:
            result_lines.append('</ul>')
        
        html = '\n'.join(result_lines)
        
        # Clean up empty paragraphs
        html = html.replace('<p></p>', '')
        html = html.replace('<p>\n</p>', '')
        
        return html
    
    def export_to_txt(self, content: str) -> str:
        """Export book to plain text format."""
        
        # Convert markdown to plain text
        txt_content = content
        
        # Remove markdown formatting
        txt_content = txt_content.replace('# ', '').replace('## ', '').replace('### ', '').replace('#### ', '')
        txt_content = txt_content.replace('**', '').replace('*', '')
        txt_content = txt_content.replace('---', '─' * 50)
        
        # Save TXT file
        txt_filename = self.input_file.stem + ".txt"
        txt_path = self.output_dir / txt_filename
        
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(txt_content)
        
        return str(txt_path)
    
    def export_to_epub(self, content: str) -> str:
        """Export book to EPUB format (simplified)."""
        
        # Create EPUB structure
        epub_dir = self.output_dir / f"{self.input_file.stem}_epub"
        epub_dir.mkdir(exist_ok=True)
        
        # Create META-INF directory
        meta_inf = epub_dir / "META-INF"
        meta_inf.mkdir(exist_ok=True)
        
        # Create container.xml
        container_xml = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>"""
        
        with open(meta_inf / "container.xml", 'w') as f:
            f.write(container_xml)
        
        # Create OEBPS directory
        oebps = epub_dir / "OEBPS"
        oebps.mkdir(exist_ok=True)
        
        # Create content.opf
        content_opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="book-id" version="2.0">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
        <dc:title>Tarot for Witches</dc:title>
        <dc:creator>AI Book Writer</dc:creator>
        <dc:language>en</dc:language>
        <dc:identifier id="book-id">tarot-witches-{datetime.datetime.now().strftime('%Y%m%d')}</dc:identifier>
        <dc:date>{datetime.datetime.now().strftime('%Y-%m-%d')}</dc:date>
        <dc:description>A Complete Guide to Tarot Reading and Witchcraft Integration</dc:description>
    </metadata>
    <manifest>
        <item id="content" href="content.html" media-type="application/xhtml+xml"/>
        <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    </manifest>
    <spine toc="ncx">
        <itemref idref="content"/>
    </spine>
</package>"""
        
        with open(oebps / "content.opf", 'w') as f:
            f.write(content_opf)
        
        # Create content.html
        html_content = self._markdown_to_html(content)
        content_html = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Tarot for Witches</title>
    <style>
        body {{ font-family: serif; line-height: 1.6; }}
        h1 {{ color: #8B4513; }}
        h2 {{ color: #A0522D; }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>"""
        
        with open(oebps / "content.html", 'w', encoding='utf-8') as f:
            f.write(content_html)
        
        # Create toc.ncx
        toc_ncx = f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
    <head>
        <meta name="dtb:uid" content="tarot-witches-{datetime.datetime.now().strftime('%Y%m%d')}"/>
        <meta name="dtb:depth" content="2"/>
        <meta name="dtb:totalPageCount" content="0"/>
        <meta name="dtb:maxPageNumber" content="0"/>
    </head>
    <docTitle>
        <text>Tarot for Witches</text>
    </docTitle>
    <navMap>
        <navPoint id="navpoint-1" playOrder="1">
            <navLabel><text>Tarot for Witches</text></navLabel>
            <content src="content.html"/>
        </navPoint>
    </navMap>
</ncx>"""
        
        with open(oebps / "toc.ncx", 'w') as f:
            f.write(toc_ncx)
        
        # Create mimetype file
        with open(epub_dir / "mimetype", 'w') as f:
            f.write("application/epub+zip")
        
        return str(epub_dir)
    
    def export_all_formats(self) -> Dict[str, str]:
        """Export book in all available formats."""
        
        print("📚 Exporting Tarot for Witches in multiple formats...")
        
        # Read content
        content = self.read_book_content()
        
        exports = {}
        
        # Export to HTML
        print("🔄 Exporting to HTML...")
        html_path = self.export_to_html(content)
        exports['html'] = html_path
        print(f"✅ HTML exported: {html_path}")
        
        # Export to TXT
        print("🔄 Exporting to TXT...")
        txt_path = self.export_to_txt(content)
        exports['txt'] = txt_path
        print(f"✅ TXT exported: {txt_path}")
        
        # Export to EPUB
        print("🔄 Exporting to EPUB...")
        epub_path = self.export_to_epub(content)
        exports['epub'] = epub_path
        print(f"✅ EPUB exported: {epub_path}")
        
        return exports


def main():
    """Main function to export the book."""
    
    # Find the generated book file
    books_dir = Path("./Books")
    book_files = list(books_dir.glob("Tarot_for_Witches_*.md"))
    
    if not book_files:
        print("❌ No Tarot for Witches book found in Books directory")
        return
    
    # Use the most recent file
    book_file = max(book_files, key=lambda x: x.stat().st_mtime)
    
    print(f"📖 Found book: {book_file}")
    
    # Export in all formats
    exporter = BookExporter(str(book_file))
    exports = exporter.export_all_formats()
    
    print("\n📊 Export Complete!")
    print("📁 Exported files:")
    for format_name, file_path in exports.items():
        print(f"  - {format_name.upper()}: {file_path}")
    
    return exports


if __name__ == "__main__":
    main()