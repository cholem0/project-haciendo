QUERIES = {
    "py": """
    (function_definition
      name: (identifier) @name
      body: (_) @body) @function.def
    """,

    "ts": """
    (function_declaration
      name: (identifier) @name
      body: (_) @body) @function.def
    (lexical_declaration
      (variable_declarator
        name: (identifier) @name
        value: [
          (arrow_function body: (_) @body)
          (function_expression body: (_) @body)
        ] @value)) @function.def
    (method_definition
      name: (property_identifier) @name
      body: (_) @body) @method.def
    """,

    "js": """
    (function_declaration
      name: (identifier) @name
      body: (_) @body) @function.def
    (lexical_declaration
      (variable_declarator
        name: (identifier) @name
        value: [
          (arrow_function body: (_) @body)
          (function_expression body: (_) @body)
        ] @value)) @function.def
    (method_definition
      name: (property_identifier) @name
      body: (_) @body) @method.def
    """,

    "tsx": """
    ; same as typescript (TSX grammar is usually very similar)
    (function_declaration
      name: (identifier) @name
      body: (_) @body) @function.def
    (lexical_declaration
      (variable_declarator
        name: (identifier) @name
        value: [
          (arrow_function body: (_) @body)
          (function_expression body: (_) @body)
        ] @value)) @function.def
    (method_definition
      name: (property_identifier) @name
      body: (_) @body) @method.def
    """,

    "java": """
    (method_declaration
      name: (identifier) @name
      body: (block) @body) @function.def
    """,

    "go": """
    (function_declaration
      name: (identifier) @name
      body: (block) @body) @function.def
    (method_declaration
      name: (field_identifier) @name
      body: (block) @body) @method.def
    """,

    "rs": """
    (function_item
      name: (identifier) @name
      body: (block) @body) @function.def
    (method_item
      name: (identifier) @name
      body: (block) @body) @method.def
    """,

    "cs": """
    (method_declaration
      name: (identifier) @name
      body: (block) @body) @function.def
    """,

    "kt": """
    (function_declaration
      name: (simple_identifier) @name
      body: (block) @body) @function.def
    (class_body
      (function_declaration
        name: (simple_identifier) @name
        body: (block) @body)) @method.def
    """,

    "rb": """
    (method
      name: (identifier) @name
      body: (body_statement) @body) @function.def
    (singleton_method
      name: (identifier) @name
      body: (body_statement) @body) @function.def
    """,

    "php": """
    (method_declaration
      name: (name) @name
      body: (compound_statement) @body) @function.def
    (function_definition
      name: (name) @name
      body: (compound_statement) @body) @function.def
    """,

    "cpp": """
    (function_definition
      declarator: (function_declarator
        declarator: (identifier) @name)
      body: (compound_statement) @body) @function.def
    """,

    "c": """
    (function_definition
      declarator: (function_declarator
        declarator: (identifier) @name)
      body: (compound_statement) @body) @function.def
    """,

    "swift": """
    (function_declaration
      name: (identifier) @name
      body: (_) @body) @function.def
    """,
}
