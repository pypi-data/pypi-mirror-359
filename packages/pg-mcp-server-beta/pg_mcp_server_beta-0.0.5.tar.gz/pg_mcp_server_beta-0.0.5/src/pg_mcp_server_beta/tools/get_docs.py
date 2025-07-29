import json

from ..core.document_repository import get_repository


def get_docs(doc_id: str = "1") -> dict[str, object]:
    """
    문서 ID(숫자) 또는 파일 경로(문자열)로 헥토파이낸셜 연동 문서의 전체 내용을 확인할 수 있습니다.

    Args:
        doc_id (str): 문서 ID (예: "1", "2") 또는 파일 경로(예: "pg/hecto_financial_pg.md")

    Returns:
        dict: {
            "문서ID": str,         # 요청한 문서의 ID 또는 파일명
            "내용": str,           # 문서의 전체 텍스트(마크다운 원문)
            "비고": str            # 안내 메시지(고정)
        }
        ※ 문서가 없을 경우 {"안내": "..."} 또는 {"오류": "..."} 형태로 반환
    """
    try:
        repository = get_repository()
        content = None
        try:
            doc_id_int = int(doc_id)
            content = repository.get_document_by_id(doc_id_int)
        except ValueError:
            doc_meta = next((doc for doc in repository.documents if doc["filename"] == doc_id), None)
            if doc_meta:
                content = repository._load_document_content(doc_meta["filename"])
            else:
                content = None

        if content is None:
            return {
                "안내": f"문서 ID 또는 경로 '{doc_id}'에 해당하는 자료가 없습니다."
            }

        return {
            "문서ID": doc_id,
            "내용": content,
            "비고": "헥토파이낸셜 연동 문서의 원문 전체입니다.",
        }

    except Exception as e:
        return {
            "오류": f"문서 조회 중 문제가 발생했습니다: {str(e)}"
        }
