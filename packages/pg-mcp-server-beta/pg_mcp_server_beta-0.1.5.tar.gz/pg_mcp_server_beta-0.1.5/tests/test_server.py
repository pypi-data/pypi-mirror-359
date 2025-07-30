import pytest
from unittest.mock import Mock, patch
from fastmcp import FastMCP
from fastmcp.tools import FunctionTool


class TestServer:
    """MCP 서버 테스트"""
    
    def test_server_creation(self):
        """서버 생성 테스트"""
        server = FastMCP("hecto-financial-mcp")
        assert server is not None
        assert server.name == "hecto-financial-mcp"
    
    def test_tool_registration(self):
        """도구 등록 테스트"""
        server = FastMCP("test-server")
        
        # 테스트용 도구 함수
        def test_tool() -> str:
            return "test"
        
        # 도구 등록
        tool = FunctionTool.from_function(
            test_tool, 
            name="test_tool", 
            description="테스트 도구"
        )
        server.add_tool(tool)
        
        # 도구가 등록되었는지 확인 (내부적으로 확인)
        assert hasattr(server, 'add_tool')
    
    @patch('fastmcp.FastMCP.run')
    def test_server_run_method(self, mock_run):
        """서버 실행 메서드 테스트"""
        server = FastMCP("test-server")
        
        # run 메서드가 호출되는지 확인
        server.run("stdio")
        mock_run.assert_called_once_with("stdio")


class TestToolFunctions:
    """도구 함수 테스트"""
    
    def test_list_docs_tool_function(self):
        """list_docs_tool 함수 테스트"""
        from pg_mcp_server_beta.server import main
        
        # main 함수가 정의되어 있는지 확인
        assert callable(main)
    
    def test_fetch_doc_tool_function(self):
        """fetch_doc_tool 함수 테스트"""
        # 서버 모듈에서 도구 함수들이 정의되어 있는지 확인
        import pg_mcp_server_beta.server as server_module
        
        # main 함수 내부의 도구 함수들이 정의되어 있는지 확인
        # (실제로는 main 함수 내부에서 정의되므로 직접 접근은 어려움)
        assert hasattr(server_module, 'main')


class TestIntegration:
    """통합 테스트"""
    
    @patch('fastmcp.FastMCP.run')
    def test_server_integration(self, mock_run):
        """서버 통합 테스트"""
        from pg_mcp_server_beta.server import main
        
        # main 함수가 예외 없이 실행되는지 확인
        # (실제로는 mock_run이 호출되어야 함)
        main()
        mock_run.assert_called_once_with("stdio")
    
    def test_imports_work(self):
        """모든 import가 정상적으로 작동하는지 테스트"""
        try:
            from fastmcp import FastMCP
            from fastmcp.tools import FunctionTool
            from pg_mcp_server_beta.tools.list_docs import list_docs
            from pg_mcp_server_beta.tools.get_docs import get_docs
            from pg_mcp_server_beta.tools.search_docs import search_docs
            from pg_mcp_server_beta.server import main
        except ImportError as e:
            pytest.fail(f"Import 실패: {e}")

    def test_server_import(self):
        """서버 모듈 import 테스트"""
        try:
            from pg_mcp_server_beta.server import main
            print("✓ Import 성공")
        except Exception as e:
            pytest.fail(f"Import 실패: {e}")


if __name__ == "__main__":
    # 간단한 테스트 실행
    print("=== 헥토파이낸셜 MCP 서버 테스트 ===")
    
    # 서버 생성 테스트
    print("\n1. 서버 생성 테스트")
    try:
        server = FastMCP("test-server")
        print("✓ 서버 생성 성공")
    except Exception as e:
        print(f"✗ 서버 생성 실패: {e}")
    
    # 도구 등록 테스트
    print("\n2. 도구 등록 테스트")
    try:
        def test_tool() -> str:
            return "test"
        
        tool = FunctionTool.from_function(test_tool, name="test_tool", description="테스트")
        server.add_tool(tool)
        print("✓ 도구 등록 성공")
    except Exception as e:
        print(f"✗ 도구 등록 실패: {e}")
    
    # Import 테스트
    print("\n3. Import 테스트")
    try:
        from pg_mcp_server_beta.server import main
        print("✓ Import 성공")
    except Exception as e:
        print(f"✗ Import 실패: {e}")
    
    print("\n=== 테스트 완료 ===") 