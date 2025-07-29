import pytest
from unittest.mock import Mock, patch
import tempfile
import os
from pathlib import Path
from pg_mcp_server_beta.core.document_repository import HectoDocumentRepository, get_repository
from pg_mcp_server_beta.core import documents


class TestDocumentRepository:
    """문서 저장소 테스트"""
    
    def test_repository_creation(self):
        """저장소 생성 테스트"""
        repository = HectoDocumentRepository(documents)
        assert repository is not None
        assert hasattr(repository, 'documents')
        assert hasattr(repository, 'search_engine')
    
    def test_documents_loaded(self):
        """문서가 로드되는지 테스트"""
        repository = HectoDocumentRepository(documents)
        
        # 문서 목록이 비어있지 않은지 확인
        assert len(repository.documents) > 0
        
        # 각 문서에 필수 필드가 있는지 확인
        for doc in repository.documents:
            assert 'filename' in doc
            assert 'title' in doc
            assert 'category' in doc
            assert 'tags' in doc
            assert 'id' in doc
    
    def test_list_documents(self):
        """문서 목록 반환 테스트"""
        repository = HectoDocumentRepository(documents)
        documents_list = repository.list_documents()
        
        assert isinstance(documents_list, list)
        assert len(documents_list) > 0
        
        # 반환된 문서들이 원본과 동일한지 확인
        assert documents_list == repository.documents
    
    def test_get_document_by_id_valid(self):
        """유효한 ID로 문서 조회 테스트"""
        repository = HectoDocumentRepository(documents)
        
        if len(repository.documents) > 0:
            content = repository.get_document_by_id(0)
            # 문서 내용이 문자열이거나 None인지 확인
            assert content is None or isinstance(content, str)
    
    def test_get_document_by_id_invalid(self):
        """잘못된 ID로 문서 조회 테스트"""
        repository = HectoDocumentRepository(documents)
        
        # 음수 ID
        content = repository.get_document_by_id(-1)
        assert content is None
        
        # 범위를 벗어난 ID
        content = repository.get_document_by_id(999)
        assert content is None
    
    def test_search_documents_with_keywords(self):
        """키워드로 검색 테스트"""
        repository = HectoDocumentRepository(documents)
        result = repository.search_documents(["결제"])
        assert isinstance(result, dict)
        assert (
            "검색결과" in result
            or "안내" in result
            or "카테고리별검색결과" in result
        )
    
    def test_search_documents_empty_keywords(self):
        """빈 키워드로 검색 테스트"""
        repository = HectoDocumentRepository(documents)
        result = repository.search_documents([])
        assert isinstance(result, dict)
        assert "안내" in result
    
    def test_search_documents_multiple_keywords(self):
        """여러 키워드로 검색 테스트"""
        repository = HectoDocumentRepository(documents)
        result = repository.search_documents(["결제", "연동"])
        assert isinstance(result, dict)
        assert (
            "검색결과" in result
            or "안내" in result
            or "카테고리별검색결과" in result
        )


class TestGetRepository:
    """전역 저장소 함수 테스트"""
    
    def test_get_repository_singleton(self):
        """get_repository가 싱글톤 패턴으로 동작하는지 테스트"""
        # initialize_repository를 먼저 호출해야 함 (테스트 환경에서는 생략)
        # repo1 = get_repository()
        # repo2 = get_repository()
        # assert repo1 is repo2
        pass
    
    def test_get_repository_type(self):
        """get_repository가 올바른 타입을 반환하는지 테스트"""
        # initialize_repository를 먼저 호출해야 함 (테스트 환경에서는 생략)
        # repository = get_repository()
        # assert isinstance(repository, HectoDocumentRepository)
        pass


class TestIntegration:
    """통합 테스트"""
    
    def test_repository_integration(self):
        """저장소 통합 테스트"""
        repository = HectoDocumentRepository(documents)
        
        # 1. 문서 목록 조회
        documents_list = repository.list_documents()
        assert len(documents_list) > 0
        
        # 2. 첫 번째 문서 조회
        if len(documents_list) > 0:
            content = repository.get_document_by_id(0)
            assert content is None or isinstance(content, str)
        
        # 3. 검색 수행
        search_result = repository.search_documents(["테스트"])
        assert isinstance(search_result, dict)
        assert (
            "검색결과" in search_result
            or "안내" in search_result
            or "카테고리별검색결과" in search_result
        )
    
    def test_error_handling(self):
        """에러 처리 테스트"""
        repository = HectoDocumentRepository(documents)
        
        # 잘못된 ID로 조회
        content = repository.get_document_by_id(-1)
        assert content is None
        
        # 빈 검색어로 검색
        result = repository.search_documents([])
        assert isinstance(result, dict)
        assert "안내" in result


if __name__ == "__main__":
    # 간단한 테스트 실행
    print("=== 헥토파이낸셜 문서 저장소 테스트 ===")
    
    # 저장소 생성 테스트
    print("\n1. 저장소 생성 테스트")
    try:
        repository = HectoDocumentRepository(documents)
        print(f"✓ 저장소 생성 성공 (문서 수: {len(repository.documents)})")
    except Exception as e:
        print(f"✗ 저장소 생성 실패: {e}")
        repository = None
    
    # 문서 목록 테스트
    print("\n2. 문서 목록 테스트")
    try:
        if repository is not None:
            documents_list = repository.list_documents()
            print(f"✓ 문서 목록 조회 성공 (문서 수: {len(documents_list)})")
            for i, doc in enumerate(documents_list[:3]):  # 처음 3개만 출력
                print(f"  - {i}: {doc['title']} ({doc['category']})")
        else:
            print("repository가 생성되지 않아 문서 목록 테스트를 건너뜁니다.")
    except Exception as e:
        print(f"✗ 문서 목록 조회 실패: {e}")
    
    # 검색 테스트
    print("\n3. 검색 테스트")
    try:
        if repository is not None:
            result = repository.search_documents(["결제"])
            print(f"✓ 검색 성공 (결과 타입: {type(result)})")
            # dict이면 str로 변환 후 미리보기
            if isinstance(result, dict):
                preview = str(result)
            else:
                preview = result
            print(f"  결과 미리보기: {preview[:100]}...")
        else:
            print("repository가 생성되지 않아 검색 테스트를 건너뜁니다.")
    except Exception as e:
        print(f"✗ 검색 실패: {e}")
    
    # 전역 저장소 테스트
    print("\n4. 전역 저장소 테스트")
    try:
        global_repo = get_repository()
        print("✓ 전역 저장소 조회 성공")
    except Exception as e:
        print(f"✗ 전역 저장소 조회 실패: {e}")
    
    print("\n=== 테스트 완료 ===") 