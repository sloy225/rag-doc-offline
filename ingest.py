from __future__ import annotations

import json
from pathlib import Path
from typing import List, Tuple

import pandas as pd
from langchain_core.documents import Document
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
INDEX_DIR = BASE_DIR / "index_store"
META_FILE = INDEX_DIR / "metadata.json"
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".csv", ".xlsx"}


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)


def load_txt(path: Path) -> List[Document]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return [Document(page_content=text, metadata={"source": path.name, "type": path.suffix})]


def load_csv(path: Path) -> List[Document]:
    df = pd.read_csv(path)
    text = df.astype(str).to_csv(index=False)
    return [Document(page_content=text, metadata={"source": path.name, "type": path.suffix})]


def load_xlsx(path: Path) -> List[Document]:
    xls = pd.ExcelFile(path)
    docs = []
    for sheet in xls.sheet_names:
        df = pd.read_excel(path, sheet_name=sheet)
        text = df.astype(str).to_csv(index=False)
        docs.append(
            Document(
                page_content=text,
                metadata={"source": path.name, "sheet": sheet, "type": path.suffix},
            )
        )
    return docs


def load_documents_from_file(path: Path) -> List[Document]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return PyPDFLoader(str(path)).load()
    if suffix == ".docx":
        return Docx2txtLoader(str(path)).load()
    if suffix in {".txt", ".md"}:
        return load_txt(path)
    if suffix == ".csv":
        return load_csv(path)
    if suffix == ".xlsx":
        return load_xlsx(path)
    return []


def list_supported_files() -> List[Path]:
    return sorted(
        [p for p in DATA_DIR.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS]
    )


def collect_documents() -> Tuple[List[Document], List[dict]]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    all_docs: List[Document] = []
    file_infos = []

    for path in list_supported_files():
        raw_docs = load_documents_from_file(path)
        for d in raw_docs:
            d.metadata["source_path"] = str(path)

        chunks = splitter.split_documents(raw_docs)
        all_docs.extend(chunks)
        file_infos.append({"file": path.name, "path": str(path), "chunks": len(chunks)})

    return all_docs, file_infos


def save_metadata(meta: dict) -> None:
    META_FILE.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def load_metadata() -> dict:
    if META_FILE.exists():
        return json.loads(META_FILE.read_text(encoding="utf-8"))
    return {}


def build_vectorstore(embed_model: str) -> Tuple[int, List[dict]]:
    docs, file_infos = collect_documents()
    if not docs:
        return 0, []

    embeddings = OllamaEmbeddings(model=embed_model)
    vs = FAISS.from_documents(docs, embeddings)
    vs.save_local(str(INDEX_DIR))
    save_metadata({"embed_model": embed_model, "files": file_infos, "chunks_total": len(docs)})

    return len(docs), file_infos