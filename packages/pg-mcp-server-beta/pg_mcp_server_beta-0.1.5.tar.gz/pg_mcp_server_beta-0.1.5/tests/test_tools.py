import pytest
from unittest.mock import Mock, patch, AsyncMock
import json
from mcp.server.models import InitializationOptions
from pg_mcp_server_beta.tools.list_docs import list_docs
from pg_mcp_server_beta.tools.get_docs import get_docs
from pg_mcp_server_beta.tools.search_docs import search_docs
from typing import Any, cast
# 문서 저장소 초기화용 import
from pg_mcp_server_beta.core.document_repository import initialize_repository
from pg_mcp_server_beta.core import documents
import typing

@pytest.fixture(autouse=True, scope="module")
def setup_docs_repository():
    initialize_repository(documents)

class TestListDocs:
    """문서 목록 조회 도구 테스트"""
    
    def test_list_docs_returns_json(self):
        """list_docs가 유효한 dict(JSON) 객체를 반환하는지 테스트"""
        result = cast(dict[str, Any], list_docs())
        assert isinstance(result, dict)
        assert "문서목록" in result or "오류" in result
    
    def test_list_docs_has_documents(self):
        """문서 목록이 비어있지 않은지 테스트"""
        result = cast(dict[str, Any], list_docs())
        
        assert len(result["문서목록"]) > 0
        
        # 각 문서에 필수 필드가 있는지 확인
        for doc in result["문서목록"]:
            assert "문서ID" in doc
            assert "제목" in doc
            assert "카테고리" in doc
            assert "파일명" in doc
            assert "태그" in doc


class TestGetDoc:
    """문서 조회 도구 테스트"""
    
    def test_get_doc_valid_id(self):
        """유효한 문서 ID로 조회 테스트"""
        # 먼저 문서 목록을 가져와서 유효한 ID를 얻음
        list_result = cast(dict[str, Any], list_docs())
        if list_result["문서목록"]:
            valid_id = list_result["문서목록"][0]["문서ID"]
            result = cast(dict[str, Any], get_docs(doc_id=valid_id))
            
            # JSON 파싱 가능한지 확인
            assert isinstance(result, dict)
            
            # 필수 키가 있는지 확인
            assert "문서ID" in result
            assert result["문서ID"] == valid_id
    
    def test_get_doc_invalid_id(self):
        """잘못된 문서 ID로 조회 테스트"""
        result = cast(dict[str, Any], get_docs(doc_id="999999"))
        
        # JSON 파싱 가능한지 확인
        assert isinstance(result, dict)
        
        # 에러 메시지가 있는지 확인
        assert "안내" in result or "오류" in result


class TestSearchDocs:
    """문서 검색 도구 테스트"""
    
    def test_search_docs_with_keywords(self):
        """키워드로 검색 테스트"""
        result = cast(dict[str, Any], search_docs("결제"))
        assert isinstance(result, dict)
        assert "검색어" in result or "검색결과" in result or "안내" in result

    def test_search_docs_empty_keywords(self):
        """빈 키워드로 검색 테스트"""
        result = cast(dict[str, Any], search_docs(""))
        assert isinstance(result, dict)
        assert "안내" in result

    def test_search_docs_multiple_keywords(self):
        """여러 키워드로 검색 테스트"""
        result = cast(dict[str, Any], search_docs("결제,연동"))
        assert isinstance(result, dict)

    def test_search_docs_space_separated_keywords(self):
        """공백으로 구분된 키워드 검색 테스트"""
        result = cast(dict[str, Any], search_docs("내통장 결제"))
        assert isinstance(result, dict)
        assert "검색결과" in result or "안내" in result

    def test_search_docs_special_characters(self):
        """특수문자 포함 키워드 검색 테스트"""
        result = cast(dict[str, Any], search_docs("내통장!@# 결제$"))
        assert isinstance(result, dict)
        # 안내 또는 검색결과가 있어야 함
        assert "검색결과" in result or "안내" in result

    def test_search_docs_case_insensitive(self):
        """대소문자 구분 없이 검색되는지 테스트"""
        result_lower = cast(dict[str, Any], search_docs("ezauth"))
        result_upper = cast(dict[str, Any], search_docs("EZAUTH"))
        if "검색결과" in result_lower and "검색결과" in result_upper:
            assert result_lower["검색결과"] == result_upper["검색결과"]
        else:
            assert result_lower.get("안내") == result_upper.get("안내")

    def test_search_docs_no_result_suggestion(self):
        """검색 결과가 없을 때 제안 메시지 테스트"""
        result = cast(dict[str, Any], search_docs("없는키워드123"))
        assert "검색결과" in result or "안내" in result

    def test_search_docs_partial_match(self):
        """부분 일치 키워드로도 결과가 나오는지 테스트"""
        result = cast(dict[str, Any], search_docs("내통"))
        assert isinstance(result, dict)
        # 검색결과가 있거나, 제안이 있어야 함
        assert "검색결과" in result

    def test_search_docs_tag_suggestion(self):
        """태그 기반 제안이 실제로 포함되는지 테스트"""
        result = cast(dict[str, Any], search_docs("간편현금결제"))
        assert isinstance(result, dict)
        # 검색 결과가 없을 때 제안에 태그가 포함되는지 확인
        if "검색결과" in result and isinstance(result["검색결과"], str):
            assert "간편현금결제" in result["검색결과"] or "ezauth" in result["검색결과"]

    def test_search_each_keyword(self):
        """'내통장', '결제', '결제창', '파라미터' 각각의 키워드로 검색 시 결과가 있는지 테스트"""
        keywords = ["내통장", "결제", "결제창", "파라미터"]
        from pg_mcp_server_beta.tools.search_docs import search_docs
        for kw in keywords:
            result = search_docs(kw)
            assert isinstance(result, dict)
            assert "검색결과" in result
            assert isinstance(result["검색결과"], list)
            assert len(result["검색결과"]) > 0


class TestIntegration:
    """통합 테스트"""
    
    def test_all_tools_return_json(self):
        """모든 도구가 JSON을 반환하는지 테스트"""
        tools = [
            (list_docs, ()),
            (lambda: get_docs("1"), ()),
            (lambda: search_docs("테스트"), ()),
        ]
        for tool, args in tools:
            result = tool(*args) if args else tool()
            assert isinstance(result, dict)
    
    def test_tools_handle_exceptions(self):
        """도구들이 예외를 적절히 처리하는지 테스트"""
        # 잘못된 ID로 조회
        result = cast(dict[str, Any], get_docs(doc_id="999"))
        assert isinstance(result, dict)
        
        # 빈 검색어로 검색
        result = cast(dict[str, Any], search_docs(query=""))
        assert isinstance(result, dict)


if __name__ == "__main__":
    # 간단한 테스트 실행
    print("=== 헥토파이낸셜 MCP 도구 테스트 ===")
    
    # 문서 목록 테스트
    print("\n1. 문서 목록 조회 테스트")
    list_result = list_docs()
    print(f"결과: {str(list_result)[:200]}...")
    
    # 문서 조회 테스트
    print("\n2. 문서 조회 테스트")
    fetch_result = get_docs(doc_id="1")
    print(f"결과: {str(fetch_result)[:200]}...")
    
    # 검색 테스트
    print("\n3. 검색 테스트")
    search_result = search_docs(query="결제")
    print(f"결과: {str(search_result)[:200]}...")
    
    print("\n=== 테스트 완료 ===") 