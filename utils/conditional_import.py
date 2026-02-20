def get_spc_language(lang: str):
    lang = lang.lower()

    if lang == "py":
        from tree_sitter_python import language as python_lang
        return python_lang()

    elif lang == "js":
        from tree_sitter_javascript import language as javascript_lang
        return javascript_lang()

    elif lang == "ts":
        from tree_sitter_typescript import language_typescript as ts_lang
        return ts_lang()   # note: may return TS or TSX depending on version
    elif lang == "tsx":
        from tree_sitter_typescript import language_tsx as tsx_lang
        return tsx_lang() 
    elif lang == "java":
        from tree_sitter_java import language as java_lang
        return java_lang()

    elif lang == "cpp":
        from tree_sitter_cpp import language as cpp_lang
        return cpp_lang()

    elif lang == "go":
        from tree_sitter_go import language as go_lang
        return go_lang()

    elif lang == "rs":
        from tree_sitter_rust import language as rust_lang
        return rust_lang()

    else:
        raise ValueError(f"Unsupported language: {lang}")