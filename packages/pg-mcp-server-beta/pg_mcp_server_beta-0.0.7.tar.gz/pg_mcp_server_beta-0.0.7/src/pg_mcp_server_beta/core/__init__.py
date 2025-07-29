import os

base_dir = os.path.join(os.path.dirname(__file__), "..", "resource", "docs")

def load_docs(root_dir):
    docs = {}
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.startswith('.'):
                continue
            # .md, .js 파일만 로딩
            if not (filename.endswith('.md') or filename.endswith('.js')):
                continue
            abs_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(abs_path, root_dir)
            with open(abs_path, encoding="utf-8") as f:
                docs[rel_path] = f.read()
    return docs

# 전체 문서 딕셔너리 (자동 로딩)
documents = load_docs(base_dir)

from .document_repository import HectoDocumentRepository, get_repository, initialize_repository
from . import documents

__all__ = ["documents", "load_docs"] 