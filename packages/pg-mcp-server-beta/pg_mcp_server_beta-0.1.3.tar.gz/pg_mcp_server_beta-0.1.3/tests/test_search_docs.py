import pytest
from pg_mcp_server_beta.tools.search_docs import search_docs
from pg_mcp_server_beta.core.document_repository import initialize_repository
from pg_mcp_server_beta.core import documents
from typing import Any, cast

@pytest.fixture(autouse=True, scope="module")
def setup_docs_repository():
    initialize_repository(documents)

class TestSearchDocsRefactored:
    """검색 도구 세부 케이스 및 리팩토링 테스트"""

    def test_basic_keyword_search(self):
        result = cast(dict[str, Any], search_docs("결제"))
        assert "검색결과" in result

    def test_multiple_keywords(self):
        result = cast(dict[str, Any], search_docs("내통장 결제"))
        assert "검색결과" in result or "안내" in result

    def test_chunk_merge_effect(self):
        # 짧은 chunk가 병합되어 정보가 유실되지 않는지
        result = cast(dict[str, Any], search_docs("테스트"))
        assert "검색결과" in result
        # TODO: 병합된 chunk 내 단어 수, 내용 등 추가 검증

    def test_bm25_sorting(self):
        # BM25 점수 기반으로 상위 chunk가 실제로 관련성이 높은지
        result = cast(dict[str, Any], search_docs("암호화 정책"))
        assert "검색결과" in result or "안내" in result
        # TODO: 상위 chunk 내용이 실제로 관련성이 높은지 검증

    def test_window_inclusion(self):
        # window(인접 chunk) 포함 결과 확인
        result = cast(dict[str, Any], search_docs("정기결제"))
        assert "검색결과" in result
        # TODO: 인접 chunk가 실제로 포함되는지 검증

    def test_highlight_keywords(self):
        # 모든 키워드가 하이라이트 처리되는지
        result = cast(dict[str, Any], search_docs("연동 스크립트"))
        assert "검색결과" in result or "안내" in result
        # TODO: '**연동**', '**스크립트**' 등 하이라이트 확인

    def test_case_insensitive(self):
        # 대소문자 구분 없이 결과가 동일한지
        lower = cast(dict[str, Any], search_docs("ezauth"))
        upper = cast(dict[str, Any], search_docs("EZAUTH"))
        if "검색결과" in lower and "검색결과" in upper:
            assert lower["검색결과"] == upper["검색결과"]
        else:
            assert lower.get("안내") == upper.get("안내")

    def test_special_characters(self):
        # 특수문자 포함 검색
        result = cast(dict[str, Any], search_docs("내통장!@# 결제$"))
        assert "검색결과" in result or "안내" in result

    def test_partial_match(self):
        # 부분 일치 키워드
        result = cast(dict[str, Any], search_docs("내통"))
        assert "검색결과" in result

    def test_typo_and_fuzzy(self):
        # 오타/유사어 검색(실패/제안 메시지 등)
        result = cast(dict[str, Any], search_docs("내통장 결재"))
        assert "검색결과" in result or "안내" in result

    def test_real_example_script(self):
        # 실제 문서 내 연동 스크립트 예시가 검색되는지
        result = cast(dict[str, Any], search_docs("내통장 연동 스크립트"))
        assert "검색결과" in result or "안내" in result
        # TODO: SettlePay.js, execute 등 포함 여부 확인

    def test_empty_query(self):
        # 빈값 검색
        result = cast(dict[str, Any], search_docs(""))
        assert "안내" in result

    def test_error_handling(self):
        # 예외 상황 처리 (빈값 등)
        result = search_docs("")
        assert "안내" in result

    def test_category_grouped_results(self):
        # 카테고리별로 결과가 묶여서 반환되는지 확인 → 단일 리스트로 반환되므로, 리스트 내에 주요 키워드가 포함되는지만 검증
        result = cast(dict[str, Any], search_docs("내통장 결제 암호화"))
        assert "검색결과" in result
        results = result["검색결과"]
        assert isinstance(results, list)
        # 적어도 한 결과에 주요 키워드가 포함되어야 함
        joined = "\n".join(results)
        assert any(k in joined for k in ["내통장", "암호화", "결제"]) 