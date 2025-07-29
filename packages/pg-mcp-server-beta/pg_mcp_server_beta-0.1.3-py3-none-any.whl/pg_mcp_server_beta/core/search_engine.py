import re
import math
import itertools
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from .utils.category_utils import extract_category
from .utils.markdown_utils import parse_markdown_to_ast

@dataclass
class DocumentChunk:
    id: int
    text: str
    word_count: int
    origin_title: str
    filename: str
    category: str

@dataclass
class SearchResult:
    id: int
    score: float
    total_tf: int

def _extract_text_from_ast(children):
    if not children:
        return ""
    texts = []
    for node in children:
        if isinstance(node, dict):
            t = node.get("type")
            if t == "emphasis":
                inner = _extract_text_from_ast(node.get("children", []))
                texts.append(f"_{inner}_")
                continue
            if t == "strong":
                inner = _extract_text_from_ast(node.get("children", []))
                texts.append(f"**{inner}**")
                continue
            if t == "codespan":
                inner = node.get("text", "")
                texts.append(f"`{inner}`")
                continue
            if t == "linebreak":
                texts.append("<br>")
                continue
            if t == "html_inline" or t == "html_block":
                # HTML 태그(예: <br>, <td colspan=...>)도 텍스트로 보존
                texts.append(node.get("text", ""))
                continue
            if "raw" in node:
                texts.append(node["raw"])
                continue
            if "text" in node:
                texts.append(node["text"])
            if "children" in node:
                texts.append(_extract_text_from_ast(node["children"]))
    return "".join(texts)

def _table_ast_to_markdown(node):
    if not isinstance(node, dict):
        return ""
    header = node.get("header", [])
    cells = node.get("cells", [])
    n_cols = len(header)
    # 헤더 추출
    header_line = "| " + " | ".join([
        _extract_text_from_ast(h.get("children", [])) for h in header if isinstance(h, dict)
    ]) + " |"
    sep_line = "|" + "---|" * n_cols
    # 셀 추출 (멀티라인, 셀 개수 불일치 보정)
    cell_lines = []
    for row in cells:
        row_cells = [
            _extract_text_from_ast(c.get("children", [])) if isinstance(c, dict) else ""
            for c in row
        ]
        # 셀 개수 맞추기
        if len(row_cells) < n_cols:
            row_cells += ["" for _ in range(n_cols - len(row_cells))]
        elif len(row_cells) > n_cols:
            row_cells = row_cells[:n_cols]
        cell_lines.append("| " + " | ".join(row_cells) + " |")
    return "\n".join([header_line, sep_line] + cell_lines)

def _list_ast_to_markdown(node):
    if not isinstance(node, dict):
        return ""
    items = node.get("children", [])
    ordered = node.get("ordered", False)
    lines = []
    for idx, item in enumerate(items, 1):
        prefix = f"{idx}. " if ordered else "- "
        if isinstance(item, dict):
            lines.append(prefix + _extract_text_from_ast(item.get("children", [])))
    return "\n".join(lines)

class HectoSearchEngine:
    def __init__(self, documents, k1=1.2, b=0.75, min_words=10, window_size=5):
        self.k1 = k1
        self.b = b
        self.min_words = min_words
        self.window_size = window_size
        self.all_chunks = self._create_chunks_from_docs(documents)
        self.total_count = sum(chunk.word_count for chunk in self.all_chunks)
        self.average_doc_length = self.total_count / len(self.all_chunks) if self.all_chunks else 0
        self.N = len(self.all_chunks)

    def _create_chunks_from_docs(self, documents) -> List[DocumentChunk]:
        chunks = []
        for rel_path, content in documents.items():
            if not rel_path.endswith('.md'):
                continue
            category = extract_category(rel_path)
            sections = self._split_into_sections(content, self.min_words, self.window_size)
            for section in sections:
                word_count = len(section.split())
                if word_count > 0:
                    chunks.append(DocumentChunk(
                        id=len(chunks),
                        text=section,
                        word_count=word_count,
                        origin_title=rel_path,
                        filename=rel_path,
                        category=category
                    ))
        return chunks

    def _split_into_sections(self, content: str, min_words: int = 30, window_size: int = 1) -> List[str]:
        ast = parse_markdown_to_ast(content)
        sections, buffer = [], []
        heading_stack = []  # heading context stack
        def update_heading_stack_from_line(line):
            # '1. 제목' (대제목), '1.1 소제목', '2.3.1 ...' 등 번호 패턴 인식
            m = re.match(r'^(\d+(?:\.\d+)*)([.)])?\s+(.+)', line)
            if m:
                num = m.group(1)
                title = m.group(3).strip()
                depth = num.count('.') + 1
                # stack을 현재 depth에 맞게 자름
                nonlocal heading_stack
                heading_stack = heading_stack[:depth-1]
                heading_stack.append(f"{num}. {title}")
        for node in ast:
            if not isinstance(node, dict):
                continue
            if node.get("type") == "heading":
                level = node.get("level", 1)
                text = _extract_text_from_ast(node.get("children", []))
                # stack을 현재 heading level에 맞게 자름
                heading_stack = heading_stack[:level-1]
                heading_stack.append(text)
                if buffer:
                    sections.append("\n".join(buffer).strip())
                    buffer = []
                buffer.append("#" * level + " " + text)
                # heading 텍스트도 번호 패턴이면 stack에 반영
                update_heading_stack_from_line(text)
            elif node.get("type") == "table":
                table_md = _table_ast_to_markdown(node)
                if buffer:
                    sections.append("\n".join(buffer).strip())
                    buffer = []
                # heading context를 표 청크에 붙임
                if heading_stack:
                    context = " > ".join(heading_stack)
                    sections.append(f"[{context}]\n{table_md.strip()}")
                else:
                    sections.append(table_md.strip())
            elif node.get("type") == "list":
                buffer.append(_list_ast_to_markdown(node))
            elif node.get("type") == "block_code":
                info = node.get("info")
                code = node.get("text", "")
                buffer.append(f"```{info}\n{code}\n```" if info else f"```\n{code}\n```")
            elif node.get("type") == "paragraph" or node.get("type") == "text":
                text = _extract_text_from_ast(node.get("children", [])) if node.get("type") == "paragraph" else node.get("text", "")
                # 줄 단위로 번호 패턴 인식
                for line in text.splitlines():
                    update_heading_stack_from_line(line)
                buffer.append(text)
        if buffer:
            sections.append("\n".join(buffer).strip())

        sections = [s for s in sections if s]
        if window_size > 1:
            overlapped = []
            for i in range(len(sections) - window_size + 1):
                window = sections[i:i + window_size]
                merged = "\n\n".join(window).strip()
                if len(merged.split()) >= min_words:
                    overlapped.append(merged)
            for i in range(len(sections)):
                if len(sections[i].split()) < min_words:
                    overlapped.append(sections[i])
            return overlapped
        else:
            merged, buf, buf_count = [], "", 0
            for chunk in sections:
                wc = len(chunk.split())
                if wc < min_words:
                    buf += ("\n\n" if buf else "") + chunk
                    buf_count += wc
                    continue
                if buf:
                    merged.append(buf.strip())
                    buf = ""
                    buf_count = 0
                merged.append(chunk.strip())
            if buf:
                merged.append(buf.strip())
            return merged

    def calculate(self, query: str) -> List[SearchResult]:
        if not self.all_chunks:
            return []

        raw_keywords = [k for k in re.split(r'[ ,|]+', query) if k]
        keywords = set(raw_keywords)
        for k in raw_keywords:
            if re.match(r'[가-힣 ]+', k):
                keywords.add(k.replace(' ', ''))
                keywords.update(k.split())
        MAX_COMB_LENGTH = 3
        for r in range(2, min(len(raw_keywords), MAX_COMB_LENGTH) + 1):
            for comb in itertools.combinations(raw_keywords, r):
                keywords.add(''.join(comb))

        keywords = list(keywords)
        # 전체 chunk에서 카테고리 목록 동적 추출
        all_categories = set(chunk.category for chunk in self.all_chunks)
        # 검색어와 일치하는 카테고리 추출
        category_keywords = set(k for k in keywords if k in all_categories)
        term_frequencies, doc_frequencies = self._calculate_frequencies(keywords)
        scores = self._calculate_score(term_frequencies, doc_frequencies)
        filtered_scores = []
        for s in scores:
            chunk = self.get_chunk_by_id(s.id)
            if not chunk:
                continue
            # 카테고리 일치 시 가중치 부여 (예: 1.5배)
            if chunk.category in category_keywords:
                new_score = s.score * 1.5
                filtered_scores.append(SearchResult(id=s.id, score=new_score, total_tf=s.total_tf))
            else:
                filtered_scores.append(s)
        filtered_scores = [s for s in filtered_scores if s.total_tf > 0]
        filtered_scores.sort(key=lambda x: (-x.score, -x.total_tf))
        return filtered_scores

    def _calculate_frequencies(self, keywords: List[str]) -> Tuple[Dict[int, Dict[str, int]], Dict[str, int]]:
        term_frequencies = {}
        doc_frequencies = {}
        for chunk in self.all_chunks:
            text = chunk.text.replace(' ', '').lower()
            term_counts = {}
            for keyword in keywords:
                k = keyword.replace(' ', '').lower()
                count = text.count(k)
                if count > 0:
                    term_counts[keyword] = count
            if term_counts:
                term_frequencies[chunk.id] = term_counts
                for term in term_counts:
                    doc_frequencies[term] = doc_frequencies.get(term, 0) + 1
        return term_frequencies, doc_frequencies

    def _calculate_score(self, term_frequencies: Dict[int, Dict[str, int]], doc_frequencies: Dict[str, int]) -> List[SearchResult]:
        results = []
        for chunk in self.all_chunks:
            if chunk.id not in term_frequencies:
                continue
            tf = term_frequencies[chunk.id]
            length = chunk.word_count
            score = 0.0
            for term in tf:
                df = doc_frequencies.get(term, 0)
                idf = math.log((self.N - df + 0.5) / (df + 0.5) + 1) if df > 0 else 0
                numerator = tf[term] * (self.k1 + 1)
                denominator = tf[term] + self.k1 * (1 - self.b + self.b * (length / self.average_doc_length))
                score += idf * (numerator / denominator)
            total_tf = sum(tf.values())
            results.append(SearchResult(id=chunk.id, score=score, total_tf=total_tf))
        return results

    def get_chunk_by_id(self, chunk_id: int) -> Optional[DocumentChunk]:
        if 0 <= chunk_id < len(self.all_chunks):
            return self.all_chunks[chunk_id]
        return None

    def highlight_terms(self, chunk_text: str, keywords: List[str]) -> str:
        def replacer(match):
            word = match.group(0)
            return word if word.startswith('**') and word.endswith('**') else f'**{word}**'

        for keyword in sorted(keywords, key=len, reverse=True):
            if re.match(r'[가-힣]+', keyword):
                pattern = re.compile(rf'(?<!\*){re.escape(keyword)}(?!\*)', re.IGNORECASE)
            else:
                pattern = re.compile(rf'(?<!\*)\b{re.escape(keyword)}\b(?!\*)', re.IGNORECASE)
            chunk_text = pattern.sub(replacer, chunk_text)
        return chunk_text
