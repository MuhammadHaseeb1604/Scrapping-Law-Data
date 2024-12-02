import os
import re
from pathlib import Path
from langchain_text_splitters import MarkdownHeaderTextSplitter

DATA_PATH = Path('Work System')
TARGET_PATH = Path('./Work System Processed/English')
TITLE_REGEX = r"[^\w\s\-_]"

def sanitize_title(title):
    return re.sub(TITLE_REGEX, '', title).strip()

def truncate_path(path, max_length=250):
    """Truncate the path to fit within the maximum allowed length."""
    if len(path) > max_length:
        base, ext = os.path.splitext(path)
        suffix = '...'
        allowed_length = max_length - len(suffix) - len(ext)
        return base[:allowed_length] + suffix + ext
    return path

def splitParts(path, markdown):
    headers_to_split = [('####', 'Chapter')]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split, strip_headers=False)
    chapters = markdown_splitter.split_text(markdown)
    for chapter in chapters:
        chapter_title = chapter.page_content.split('\n')[0].replace('#', '')
        chapter_title = sanitize_title(chapter_title)
        try:
            file_path = os.path.join(path, f'{chapter_title}.md')
            file_path = truncate_path(file_path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as file:
                file.write(chapter.page_content.replace('#### Chapter', '## Chapter'))
        except Exception as e:
            print(f'File issue: {file_path} - {e}')

def splitMarkdown(file_name, markdown):
    headers_to_split = [
        ("#", "Title"),
        ("##", "Part"),
    ]
    
    markdown = markdown.replace('### Chapter', '#### Chapter')
    
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split, strip_headers=False)
    parts = markdown_splitter.split_text(markdown)
    print("Length of parts: ", len(parts))
    for part in parts:
        if part.metadata:
            if 'Part' in part.metadata.keys():
                title = part.metadata['Part']
            else:
                title = part.metadata['Title']

            title = sanitize_title(title)
            dst_path = os.path.join(TARGET_PATH, file_name, title)
            dst_path = truncate_path(dst_path)
            if not os.path.exists(dst_path):
                try:
                    os.makedirs(dst_path, exist_ok=True)
                except Exception as e:
                    print(f'Error creating directory {dst_path} - {e}')
                    continue
        part_text = part.page_content.replace('#### Chapter', '### Chapter')
        splitParts(dst_path, part_text)

def processMDFiles(directory: Path):
    md_files = directory.glob("**/*.md")  # Find all .md files in the directory
    for idx, file in enumerate(md_files):
        print(file)
        with open(file, "r", encoding="utf-8") as f:
            print(f'{idx + 1} -> Processing file: {file.name}')
            content = f.read()
            print(len(content.split(" ")))
            splitMarkdown(str(file.name).replace('.md', ''), content)

def main():
    processMDFiles(DATA_PATH)

if __name__ == "__main__":
    main()
