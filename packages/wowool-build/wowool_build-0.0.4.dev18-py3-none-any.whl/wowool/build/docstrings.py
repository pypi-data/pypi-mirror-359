from argparse import ArgumentParser
import docstring_parser
import ast
from pathlib import Path
import json
import sys
from dataclasses import dataclass, field, asdict


@dataclass
class ParamInfo:
    arg: str
    description: str | None = None
    type: str | None = None
    default: str | None = None


@dataclass
class ReturnsInfo:
    description: str | None = None
    type: str | None = None


@dataclass
class RaisesInfo:
    type: str | None = None
    description: str | None = None


@dataclass
class MethodInfo:
    name: str
    params: list[ParamInfo] | None = None
    returns: ReturnsInfo | None = None
    short_description: str | None = None
    long_description: str | None = None
    raises: list[RaisesInfo] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class DocStringInfo:
    name: str
    params: list[ParamInfo] | None = None
    returns: ReturnsInfo | None = None
    short_description: str | None = None
    long_description: str | None = None
    raises: list[RaisesInfo] | None = None
    decorators: list[str] = field(default_factory=list)  # List of decorator names
    examples: list[str] = field(default_factory=list)  # List of example strings, if any
    notes: list[str] = field(default_factory=list)  # List of note strings


@dataclass
class PropertyInfo:
    name: str
    returns: ReturnsInfo | None = None
    short_description: str | None = None
    long_description: str | None = None
    raises: list[RaisesInfo] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class ClassInfo:
    name: str
    methods: list[MethodInfo] = field(default_factory=list)  # Will contain MethodInfo objects
    property_methods: list[PropertyInfo] = field(default_factory=list)  # Will contain MethodInfo objects for properties
    static_methods: list[MethodInfo] = field(default_factory=list)


@dataclass
class ModuleInfo:
    module: str
    file: str
    methods: list[MethodInfo] = field(default_factory=list)
    classes: list[ClassInfo] = field(default_factory=list)  # Will contain class info with MethodInfo objects


def parse_arguments():
    """
    Parses the command line arguments.
    """
    parser = ArgumentParser(prog="extract docstrings")
    parser.add_argument("-f", "--file", nargs="+", required=True, help="files to process.")
    parser.add_argument(
        "-r",
        "--root",
        required=False,
        help="root directory to use for relative module names (default: current directory)",
    )
    parser.add_argument("-o", "--output", required=False, help="output file to write the JSON result")
    return parser.parse_args()


def parse_docstrings(item, docstring: str) -> DocStringInfo:
    parsed = docstring_parser.parse(trim(docstring))

    decorators = [decorator.id for decorator in item.decorator_list if isinstance(decorator, ast.Name)]
    # Create ParamInfo objects for each parameter
    params = None
    if "property" not in decorators:
        params = []
        for param in parsed.params:
            params.append(
                ParamInfo(
                    arg=param.arg_name,
                    description=param.description,
                    type=param.type_name,
                    default=param.default,
                )
            )

    # Create returns info
    returns = None
    if parsed.returns:
        returns = ReturnsInfo(
            description=parsed.returns.description,
            type=parsed.returns.type_name,
        )

    # Extract examples and notes from the raw docstring
    examples = []
    notes = []

    # Parse the raw docstring to extract examples and notes
    raw_docstring = trim(docstring)
    lines = raw_docstring.split("\n")

    current_section = None
    current_content = []

    for line in lines:
        stripped = line.strip()

        # Detect section headers
        if stripped.lower().startswith("example:") or stripped.lower().startswith("examples:"):
            # Save previous section
            if current_section == "note" and current_content:
                notes.append("\n".join(current_content).strip())
            elif current_section == "example" and current_content:
                examples.append("\n".join(current_content).strip())

            current_section = "example"
            current_content = []
            # Add content after "Example:" if any
            example_content = stripped[stripped.lower().find(":") + 1 :].strip()
            if example_content:
                current_content.append(example_content)

        elif stripped.lower().startswith("note:") or stripped.lower().startswith("notes:"):
            # Save previous section
            if current_section == "note" and current_content:
                notes.append("\n".join(current_content).strip())
            elif current_section == "example" and current_content:
                examples.append("\n".join(current_content).strip())

            current_section = "note"
            current_content = []
            # Add content after "Note:" if any
            note_content = stripped[stripped.lower().find(":") + 1 :].strip()
            if note_content:
                current_content.append(note_content)

        elif stripped.lower().startswith(("args:", "arguments:", "parameters:", "returns:", "return:", "raises:", "yields:", "yield:")):
            # Save current section and stop parsing examples/notes
            if current_section == "note" and current_content:
                notes.append("\n".join(current_content).strip())
            elif current_section == "example" and current_content:
                examples.append("\n".join(current_content).strip())
            current_section = None
            current_content = []

        elif current_section in ["example", "note"] and stripped:
            current_content.append(stripped)
        elif current_section in ["example", "note"] and not stripped and current_content:
            # Empty line might continue the section or end it
            current_content.append("")

    # Save any remaining content
    if current_section == "note" and current_content:
        notes.append("\n".join(current_content).strip())
    elif current_section == "example" and current_content:
        examples.append("\n".join(current_content).strip())

    # Additional note extraction from meta sections (if available)
    if hasattr(parsed, "meta") and parsed.meta:
        for meta in parsed.meta:
            if meta.args and len(meta.args) > 0 and meta.args[0].lower() == "note":
                if meta.description not in notes:
                    notes.append(meta.description)

    # Create raises info
    raises = []
    if parsed.raises:
        raises = [RaisesInfo(type=r.type_name, description=r.description) for r in parsed.raises]

    retval = DocStringInfo(
        name=item.name,
        params=params,
        returns=returns,
        short_description=parsed.short_description,
        long_description=parsed.long_description,
        raises=raises,
        decorators=decorators,
        examples=examples,
        notes=notes,
    )

    return retval


def _to_method(doc_str: DocStringInfo) -> MethodInfo:
    method = MethodInfo(
        name=doc_str.name,
        params=doc_str.params,
        returns=doc_str.returns,
        short_description=doc_str.short_description,
        long_description=doc_str.long_description,
        raises=doc_str.raises or [],
        examples=doc_str.examples,
        notes=doc_str.notes,
    )
    return method


def _to_property(doc_str: DocStringInfo) -> PropertyInfo:
    property = PropertyInfo(
        name=doc_str.name,
        returns=doc_str.returns,
        short_description=doc_str.short_description,
        long_description=doc_str.long_description,
        raises=doc_str.raises or [],
        examples=doc_str.examples,
        notes=doc_str.notes,
    )
    return property


def trim(docstring):
    if not docstring:
        return ""
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return "\n".join(trimmed)


def get_module_name(filename: Path, root: Path | None = None):
    """
    Get the module name from a file path.
    If root is provided, it will be used to determine the relative path.
    """
    if root:
        filename = filename.relative_to(root)
    parts = list(filename.parts)
    if parts[0] == "/":
        # If the first part is a root directory, we can ignore it for module naming
        parts = parts[1:]
    if parts[-1] == "__init__.py":
        # If the file is __init__.py, return the parent directory as the module name
        parts = parts[:-1]  # Remove the __init__.py from the parts
    else:
        parts[-1] = Path(parts[-1]).stem  # Remove the filename part
    return ".".join(parts)  # Join the parent directories as the module name


def has_decorator(node, decorator_name):
    """
    Check if the given AST node has a specific decorator.
    """
    if not hasattr(node, "decorator_list"):
        return False
    return any(decorator.id == decorator_name for decorator in node.decorator_list if isinstance(decorator, ast.Name))


def docstring_to_json(filename: Path, root: Path | None = None, output: Path | None = None):

    # Load the module to get its actual name
    module_name = get_module_name(filename, root)  # Default to filename without extension
    file_path = filename
    data: str = Path(file_path).read_text(encoding="utf-8")

    # Initialize ModuleInfo
    module_info = ModuleInfo(module=module_name, file=str(file_path))
    tree = ast.parse(data)
    print(f"Parsed AST: {module_name} , from {file_path}")
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # print(f"Function: {node.name}")
            docstring = ast.get_docstring(node)
            if docstring:
                # print(f"  Docstring: {docstring}")
                doc_string_info = parse_docstrings(node, docstring)
                module_info.methods.append(_to_method(doc_string_info))
                # print(f"Docstring:\n {json.dumps(doc_string_info, indent=2)}")
            # else:
            #     print(f"  Function: {node.name} - No docstring")
        # elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
        elif isinstance(node, ast.ClassDef):
            # print(f"Class: {node.name}")
            class_info = ClassInfo(name=node.name)
            ast.get_docstring(node)
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    docstring = ast.get_docstring(item)
                    if docstring:
                        # print(f"  Method: {item.name} - {docstring}")

                        doc_string_info = parse_docstrings(item, docstring)
                        if "property" in doc_string_info.decorators:
                            class_info.property_methods.append(_to_property(doc_string_info))
                        elif "staticmethod" in doc_string_info.decorators:
                            class_info.static_methods.append(_to_method(doc_string_info))
                        else:
                            class_info.methods.append(_to_method(doc_string_info))
                        # print(f"Docstring:\n {json.dumps(doc_string_info, indent=2)}")
                # else:
                # print(f"  !!! Method: {item} - No docstring")
                #     print(f"  Method: {item.name} - No docstring")
            module_info.classes.append(class_info)

    json_string = json.dumps(asdict(module_info), indent=2)
    if output:
        dir = Path(output)
        filename = Path(filename)
        if root:
            filename = filename.relative_to(Path(root))
        else:
            filename = Path(filename)
        filename = dir / filename.with_suffix(".json")
        filename.parent.mkdir(parents=True, exist_ok=True)
        filename.write_text(json_string, encoding="utf-8")
        print(f"Module Info written to {filename}")
    else:

        print(f"Module Info as JSON:\n{json_string}")


def main():

    args = parse_arguments()
    args.file = [Path(f) for f in args.file]
    for fn in args.file:
        if not fn.exists():
            raise FileNotFoundError(f"File {fn} does not exist.")
        docstring_to_json(
            filename=fn,
            root=Path(args.root) if args.root else None,
            output=Path(args.output) if args.output else None,
        )


if __name__ == "__main__":
    main()
