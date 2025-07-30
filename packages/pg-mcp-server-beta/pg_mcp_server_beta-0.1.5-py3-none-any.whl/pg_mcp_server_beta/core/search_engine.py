import re
import math
import itertools
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from .utils.category_utils import extract_category
from .utils.markdown_utils import parse_markdown_to_ast, convert_numbered_headings

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
        content = convert_numbered_headings(content)
        ast = parse_markdown_to_ast(content)
        sections = []
        context_stack = []
        buffer = []
        last_level2 = None  # 1단계 번호형 헤딩
        for node in ast:
            if not isinstance(node, dict):
                continue
            if node.get("type") == "heading":
                # 청크 flush
                if buffer:
                    # 2단계 헤딩이면 context_stack에 [상위 1단계, 현재 2단계]가 남도록
                    if len(context_stack) == 2:
                        context = context_stack.copy()
                    elif len(context_stack) == 1 and last_level2:
                        context = [last_level2, context_stack[0]]
                    else:
                        context = context_stack.copy()
                    sections.append(f"[{ ' > '.join(context) }]\n" + "\n".join(buffer))
                    buffer = []
                # 헤딩 텍스트 추출
                heading_text = "".join([c.get('raw', '') for c in node.get('children', []) if isinstance(c, dict)])
                level = node.get('attrs', {}).get('level')
                # 1단계 번호형 헤딩(level==2)
                if level == 2:
                    context_stack = [heading_text]
                    last_level2 = heading_text
                # 2단계 번호형 헤딩(level==3)
                elif level == 3:
                    if last_level2:
                        context_stack = [last_level2, heading_text]
                    else:
                        context_stack = [heading_text]
                else:
                    context_stack = [heading_text]
            elif node.get("type") == "table":
                buffer.append(_table_ast_to_markdown(node))
            elif node.get("type") == "list":
                buffer.append(_list_ast_to_markdown(node))
            elif node.get("type") == "block_code":
                info = node.get("info")
                code = node.get("text", "")
                buffer.append(f"```{info}\n{code}\n```" if info else f"```\n{code}\n```")
            elif node.get("type") == "paragraph":
                buffer.append(_extract_text_from_ast(node.get("children", [])))
            elif node.get("type") == "text":
                buffer.append(node.get("text", ""))
        # 마지막 flush
        if buffer:
            if len(context_stack) == 2:
                context = context_stack.copy()
            elif len(context_stack) == 1 and last_level2:
                context = [last_level2, context_stack[0]]
            else:
                context = context_stack.copy()
            sections.append(f"[{ ' > '.join(context) }]\n" + "\n".join(buffer))
        return sections

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
        term_frequencies, doc_frequencies = self._calculate_frequencies(keywords)
        scores = self._calculate_score(term_frequencies, doc_frequencies)
        filtered_scores = [s for s in scores if s.total_tf > 0]
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
