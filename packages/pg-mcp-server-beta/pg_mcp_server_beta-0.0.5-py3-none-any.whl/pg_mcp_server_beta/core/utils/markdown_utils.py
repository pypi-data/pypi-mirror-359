import mistune


def parse_markdown_to_ast(markdown_text: str):
    """
    마크다운 텍스트를 mistune의 AST(구문 트리)로 파싱합니다.
    """
    markdown = mistune.create_markdown(renderer="ast")
    return markdown(markdown_text) 