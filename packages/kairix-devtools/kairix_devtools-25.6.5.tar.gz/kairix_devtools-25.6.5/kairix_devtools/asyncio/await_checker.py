"""
Async function checker module for validating proper async/await usage.

This module provides functionality to analyze Python code and identify
async functions that are called without proper await or asyncio handling.
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Set, Union, override

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AsyncViolation(BaseModel):
    """Represents a violation where an async function is called without await."""

    file_path: str = Field(
        ..., description="Path to the file containing the violation"
    )
    line_number: int = Field(
        ..., ge=1, description="Line number where the violation occurs"
    )
    column_number: int = Field(
        ..., ge=0, description="Column number where the violation occurs"
    )
    function_name: str = Field(
        ..., description="Name of the async function called without await"
    )
    violation_type: Literal["missing_await", "missing_asyncio"] = Field(
        ..., description="Type of violation: missing_await or missing_asyncio"
    )
    source_line: str = Field(..., description="The actual source line content")


class AsyncCheckResult(BaseModel):
    """Result of async function checking."""

    total_files: int = Field(
        ..., ge=0, description="Total number of files checked"
    )
    violations: List[AsyncViolation] = Field(
        default_factory=lambda: [], description="List of violations found"
    )
    passed: bool = Field(..., description="Whether all checks passed")
    violation_count: int = Field(
        ..., ge=0, description="Total number of violations found"
    )

    def __init__(self, **data: Any) -> None:
        if "violation_count" not in data and "violations" in data:
            data["violation_count"] = len(data["violations"])
        if "passed" not in data and "violations" in data:
            data["passed"] = len(data["violations"]) == 0
        super().__init__(**data)


class AsyncFunctionAnalyzer(ast.NodeVisitor):
    """Second pass: analyze async function calls for violations."""

    def __init__(self, file_path: str, source_lines: List[str]):
        super().__init__()
        self.file_path = file_path
        self.source_lines = source_lines  # Store source lines for context
        self.violations: List[AsyncViolation] = []
        self.current_scope_is_async = False
        self.current_class: Optional[str] = None
        self.current_function: Optional[str] = (
            None  # Track current function for coroutine analysis
        )
        self.awaited_calls: Set[ast.Call] = set()  # Track awaited calls
        self.parent_map: Dict[ast.AST, Optional[ast.AST]] = (
            {}
        )  # Track parent relationships

        # Enhanced coroutine tracking
        self.created_coroutines: Dict[str, List[ast.Call]] = (
            {}
        )  # function -> list of coroutine calls
        self.consumed_coroutines: Dict[str, Set[ast.Call]] = (
            {}
        )  # function -> set of consumed coroutines
        self.returned_coroutines: Dict[str, Set[ast.Call]] = (
            {}
        )  # function -> set of returned coroutines
        self.function_return_types: Dict[str, bool] = (
            {}
        )  # function -> returns_coroutines

        # These will be populated from the first pass
        self.async_functions: Set[str] = set()
        self.async_methods: Set[str] = set()
        self.imported_modules: Dict[str, str] = {}
        self.imported_functions: Dict[str, str] = {}
        self.imported_async_functions: Set[str] = set()
        self.function_definitions: Dict[str, ast.AsyncFunctionDef] = {}

    @override
    def visit(self, node: ast.AST) -> None:
        """Override visit to track parent relationships."""
        # Set parent for all child nodes
        for child in ast.iter_child_nodes(node):
            self.parent_map[child] = node

        # Call the original visit method
        super().visit(node)

    @override
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions to track current class context."""
        prev_class = self.current_class
        self.current_class = node.name

        self.generic_visit(node)

        self.current_class = prev_class

    @override
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definitions to track scope."""
        # Enter async scope
        prev_async_scope = self.current_scope_is_async
        prev_function = self.current_function
        self.current_scope_is_async = True
        self.current_function = node.name

        # Initialize tracking for this function
        self.created_coroutines[node.name] = []
        self.consumed_coroutines[node.name] = set()
        self.returned_coroutines[node.name] = set()
        self.function_return_types[node.name] = (
            self._function_returns_coroutines(node)
        )

        self.generic_visit(node)

        # Before leaving function, check for unhandled coroutines
        self._check_unhandled_coroutines(node)

        # Restore previous scope
        self.current_scope_is_async = prev_async_scope
        self.current_function = prev_function

    @override
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit regular function definitions."""
        # Enter non-async scope
        prev_async_scope = self.current_scope_is_async
        prev_function = self.current_function
        self.current_scope_is_async = False
        self.current_function = node.name

        # Initialize tracking for this function
        self.created_coroutines[node.name] = []
        self.consumed_coroutines[node.name] = set()
        self.returned_coroutines[node.name] = set()
        self.function_return_types[node.name] = (
            self._function_returns_coroutines(node)
        )

        self.generic_visit(node)

        # Before leaving function, check for unhandled coroutines
        self._check_unhandled_coroutines(node)

        # Restore previous scope
        self.current_scope_is_async = prev_async_scope
        self.current_function = prev_function

    @override
    def visit_Call(self, node: ast.Call) -> None:
        """Visit function calls to check for async violations."""
        # Check if this call is awaited
        parent = self.parent_map.get(node)
        is_awaited = isinstance(parent, ast.Await)

        # Check if this call is in an asyncio context (e.g., asyncio.create_task, asyncio.run)
        is_in_asyncio_context = self._is_in_asyncio_context(node)

        # Check if this call is passed to asyncio.gather
        is_in_gather_context = self._is_in_gather_context(node)

        # Get function name and check if it's async
        func_info = self._get_function_info(node.func)
        if (
            func_info
            and func_info["name"]
            and self._is_async_function(func_info)
        ):
            # Track coroutine creation
            if self.current_function:
                self.created_coroutines[self.current_function].append(node)

            # Mark as consumed if awaited, in asyncio context, or in gather
            if is_awaited or is_in_asyncio_context or is_in_gather_context:
                if self.current_function:
                    self.consumed_coroutines[self.current_function].add(node)

            # Don't create violations here anymore - we'll handle them in _check_unhandled_coroutines
            # This allows for more sophisticated analysis of coroutine lifecycle

        self.generic_visit(node)

    @override
    def visit_Await(self, node: ast.Await) -> None:
        """Visit await expressions to track which calls are awaited."""
        if isinstance(node.value, ast.Call):
            self.awaited_calls.add(node.value)
        self.generic_visit(node)

    @override
    def visit_Return(self, node: ast.Return) -> None:
        """Visit return statements to track returned coroutines."""
        if node.value and self.current_function:
            # Check if returning coroutines directly or in containers
            returned_calls = self._extract_coroutines_from_return(node.value)
            for call in returned_calls:
                if call in self.created_coroutines[self.current_function]:
                    self.returned_coroutines[self.current_function].add(call)
                    self.consumed_coroutines[self.current_function].add(call)

        self.generic_visit(node)

    def _extract_coroutines_from_return(
        self, return_value: ast.expr
    ) -> List[ast.Call]:
        """Extract coroutine calls from a return statement value."""
        coroutines: List[ast.Call] = []

        if isinstance(return_value, ast.Call):
            # Direct coroutine return
            func_info = self._get_function_info(return_value.func)
            if (
                func_info
                and func_info["name"]
                and self._is_async_function(func_info)
            ):
                coroutines.append(return_value)

        elif isinstance(return_value, (ast.List, ast.Tuple)):
            # List or tuple of values
            for elt in return_value.elts:
                coroutines.extend(self._extract_coroutines_from_return(elt))

        elif isinstance(return_value, ast.Name):
            # Variable reference - we can't easily track this, but if the function
            # is typed to return coroutines, we should assume it's valid
            # This is handled by the function return type checking
            pass

        else:
            # For other expression types, recursively extract calls
            for call in self._extract_calls_from_expression(return_value):
                func_info = self._get_function_info(call.func)
                if (
                    func_info
                    and func_info["name"]
                    and self._is_async_function(func_info)
                ):
                    coroutines.append(call)

        return coroutines

    def _get_function_info(
        self, func_node: ast.expr
    ) -> Optional[Dict[str, Optional[str]]]:
        """Extract function information from a call node."""
        if isinstance(func_node, ast.Name):
            return {"name": func_node.id, "module": None}
        elif isinstance(func_node, ast.Attribute):
            if isinstance(func_node.value, ast.Name):
                # This could be module.function or instance.method
                return {"name": func_node.attr, "module": func_node.value.id}
            else:
                # For more complex expressions like obj.attr.method, just get the method name
                return {"name": func_node.attr, "module": None}
        return None

    def _is_async_function(self, func_info: Dict[str, Optional[str]]) -> bool:
        """Determine if a function is async based on AST analysis only."""
        func_name = func_info["name"]
        if not func_name:
            return False

        module = func_info.get("module")

        # Check if it's a local async function
        if func_name in self.async_functions:
            return True

        # Check if it's an async method call (obj.method_name where method_name is async)
        if module and f"{module}.{func_name}" in self.async_methods:
            return True

        # For method calls, also check if the method name itself is async
        if func_name in self.async_functions:
            return True

        # Check if it's a known imported async function
        if func_name in self.imported_async_functions:
            return True

        # Check specific asyncio functions that are known to be async
        # Check both direct module name and aliased module name
        is_asyncio_module = module == "asyncio" or (
            module and self.imported_modules.get(module) == "asyncio"
        )

        if is_asyncio_module:
            known_async_functions = {
                "sleep",
                "wait",
                "wait_for",
                "gather",
                "shield",
                "timeout",
            }

            if func_name in known_async_functions:
                return True

        # Do NOT use name patterns - only use actual AST analysis
        return False

    def _is_in_asyncio_context(self, node: ast.Call) -> bool:
        """Check if the call is in an asyncio context like asyncio.run, create_task, etc."""
        # Walk up the parent chain to find if this call is inside asyncio.run or asyncio.create_task
        current: Optional[ast.AST] = node
        while current:
            parent = self.parent_map.get(current)
            if isinstance(parent, ast.Call):
                # Check if parent call is asyncio.run or asyncio.create_task
                parent_func_info = self._get_function_info(parent.func)
                if parent_func_info:
                    module = parent_func_info.get("module")
                    func_name = parent_func_info.get("name")

                    if module == "asyncio" and func_name in {
                        "run",
                        "create_task",
                    }:
                        return True

            current = parent

        return False

    def _get_context_line(self, node: ast.AST) -> str:
        """Get the source line for context."""
        lineno = getattr(node, "lineno", 0)
        if lineno > 0 and lineno <= len(self.source_lines):
            return self.source_lines[lineno - 1].strip()
        return f"<line {lineno} not available>"

    def _get_line_preview(self, node: ast.AST) -> str:
        """Get a preview of the line with error indicator."""
        lineno = getattr(node, "lineno", 0)
        col_offset = getattr(node, "col_offset", 0)

        if lineno > 0 and lineno <= len(self.source_lines):
            line = self.source_lines[lineno - 1]
            # Create a visual indicator showing where the error is
            stripped_line = line.strip()
            leading_spaces = len(line) - len(line.lstrip())
            adjusted_col = max(0, col_offset - leading_spaces)

            # Create the preview with error indicator
            preview = stripped_line + "\n"
            preview += " " * min(adjusted_col, len(stripped_line)) + "^"
            return preview
        return f"<line {lineno} not available>"

    def _get_file_link(self, node: ast.AST) -> str:
        """Generate a file link with line and column."""
        lineno = getattr(node, "lineno", 0)
        col_offset = getattr(node, "col_offset", 0)
        return f"file://{self.file_path}:{lineno}:{col_offset + 1}"

    def _is_in_gather_context(self, node: ast.Call) -> bool:
        """Check if the call is passed as an argument to asyncio.gather."""
        current: Optional[ast.AST] = node
        while current:
            parent = self.parent_map.get(current)

            # Check if we're an argument to a function call
            if isinstance(parent, ast.Call):
                # Check if this is asyncio.gather
                parent_func_info = self._get_function_info(parent.func)
                if parent_func_info:
                    module = parent_func_info.get("module")
                    func_name = parent_func_info.get("name")

                    if module == "asyncio" and func_name == "gather":
                        return True

                    # Also check for direct gather calls (imported as `from asyncio import gather`)
                    if (
                        func_name == "gather"
                        and func_name in self.imported_async_functions
                    ):
                        return True

            # Check if we're in a list/tuple that might be unpacked to gather
            elif isinstance(parent, (ast.List, ast.Tuple)):
                # Check if this list/tuple is used with gather via unpacking (*args)
                list_parent = self.parent_map.get(parent)
                if isinstance(list_parent, ast.Starred):
                    # This is part of *args - check if the starred expression is passed to gather
                    starred_parent = self.parent_map.get(list_parent)
                    if isinstance(starred_parent, ast.Call):
                        starred_func_info = self._get_function_info(
                            starred_parent.func
                        )
                        if starred_func_info:
                            module = starred_func_info.get("module")
                            func_name = starred_func_info.get("name")

                            if module == "asyncio" and func_name == "gather":
                                return True

                            if (
                                func_name == "gather"
                                and func_name in self.imported_async_functions
                            ):
                                return True

                # Also check if the list/tuple variable is later used with gather
                # For now, we'll do a simpler check: look for gather calls in the same function
                # that use variables which might contain this list
                if self._is_list_used_in_gather(parent):
                    return True

            # Move up the tree
            current = parent

        return False

    def _is_list_used_in_gather(self, list_node: ast.expr) -> bool:
        """Check if a list/tuple is likely used with gather in the same function."""
        # This is a heuristic: if we're in a function that has gather calls,
        # and this is a list of coroutines, it's likely used with gather

        # Find the containing function
        current: Optional[ast.AST] = list_node
        while current:
            parent = self.parent_map.get(current)
            if isinstance(parent, (ast.AsyncFunctionDef, ast.FunctionDef)):
                # Look for gather calls in this function
                for node in ast.walk(parent):
                    if isinstance(node, ast.Call):
                        func_info = self._get_function_info(node.func)
                        if func_info:
                            module = func_info.get("module")
                            func_name = func_info.get("name")

                            if (
                                module == "asyncio" and func_name == "gather"
                            ) or (
                                func_name == "gather"
                                and func_name in self.imported_async_functions
                            ):
                                # Check if this gather call uses starred expressions
                                for arg in node.args:
                                    if isinstance(arg, ast.Starred):
                                        return True
                break
            current = parent

        return False

    def _is_coroutine_expression(self, expr: ast.expr) -> bool:
        """Check if an expression represents a coroutine or contains coroutine calls."""
        if isinstance(expr, ast.Call):
            func_info = self._get_function_info(expr.func)
            return bool(
                func_info
                and func_info["name"]
                and self._is_async_function(func_info)
            )

        elif isinstance(expr, ast.Name):
            # Could be a variable holding a coroutine, but we can't easily track this
            return False

        elif isinstance(expr, ast.Await):
            # Awaited expressions are not coroutines themselves
            return False

        elif isinstance(expr, (ast.Tuple, ast.List)):
            # Check if any element is a coroutine
            return any(self._is_coroutine_expression(elt) for elt in expr.elts)

        elif hasattr(expr, "__dict__"):
            # For other expression types, recursively check for coroutine calls
            for child in ast.iter_child_nodes(expr):
                if isinstance(
                    child, ast.expr
                ) and self._is_coroutine_expression(child):
                    return True

        return False

    def _extract_calls_from_expression(self, expr: ast.expr) -> List[ast.Call]:
        """Extract all function calls from an expression."""
        calls: List[ast.Call] = []

        if isinstance(expr, ast.Call):
            calls.append(expr)

        # Recursively search for calls in child nodes
        for child in ast.iter_child_nodes(expr):
            if isinstance(child, ast.expr):
                calls.extend(self._extract_calls_from_expression(child))

        return calls

    def _function_returns_coroutines(
        self, func_node: Union[ast.AsyncFunctionDef, ast.FunctionDef]
    ) -> bool:
        """Check if a function is typed to return coroutines."""
        if not func_node.returns:
            return False

        # Check if return type annotation indicates coroutines
        result = self._type_annotation_contains_coroutines(func_node.returns)
        # Debug: print the function name and result
        if hasattr(func_node, "name"):
            logger.debug(
                f"Function {func_node.name} returns coroutines: {result}"
            )
        return result

    def _type_annotation_contains_coroutines(
        self, type_node: ast.expr
    ) -> bool:
        """Check if a type annotation contains coroutine types."""
        if isinstance(type_node, ast.Name):
            # Direct type names like 'Coroutine', 'Awaitable'
            return type_node.id in {"Coroutine", "Awaitable"}

        elif isinstance(type_node, ast.Attribute):
            # Types like typing.Coroutine, collections.abc.Coroutine
            if isinstance(type_node.value, ast.Name):
                module = type_node.value.id
                type_name = type_node.attr
                return module in {
                    "typing",
                    "collections.abc",
                } and type_name in {"Coroutine", "Awaitable"}

        elif isinstance(type_node, ast.Subscript):
            # Generic types like Coroutine[Any, Any, str], list[Coroutine[...]], etc.
            base_type = type_node.value

            # Check if the base type itself is a coroutine type
            if self._type_annotation_contains_coroutines(base_type):
                return True

            # Check if it's a container of coroutines (like list[Coroutine[...]])
            if isinstance(base_type, ast.Name) and base_type.id in {
                "list",
                "List",
                "tuple",
                "Tuple",
                "set",
                "Set",
            }:
                # Check the type arguments
                if isinstance(type_node.slice, ast.Tuple):
                    # Multiple type arguments
                    for elt in type_node.slice.elts:
                        if self._type_annotation_contains_coroutines(elt):
                            return True
                else:
                    # Single type argument
                    return self._type_annotation_contains_coroutines(
                        type_node.slice
                    )

            # Handle qualified container types like typing.List[Coroutine[...]]
            elif isinstance(base_type, ast.Attribute):
                if isinstance(base_type.value, ast.Name):
                    module = base_type.value.id
                    type_name = base_type.attr
                    if module == "typing" and type_name in {
                        "List",
                        "Tuple",
                        "Set",
                        "Sequence",
                    }:
                        # Check the type arguments for coroutines
                        if isinstance(type_node.slice, ast.Tuple):
                            for elt in type_node.slice.elts:
                                if self._type_annotation_contains_coroutines(
                                    elt
                                ):
                                    return True
                        else:
                            return self._type_annotation_contains_coroutines(
                                type_node.slice
                            )

        elif isinstance(type_node, ast.Constant):
            # String type annotations
            if isinstance(type_node.value, str):
                # Simple heuristic for string annotations
                return any(
                    keyword in type_node.value.lower()
                    for keyword in ["coroutine", "awaitable"]
                )

        return False

    def _check_unhandled_coroutines(
        self, func_node: Union[ast.AsyncFunctionDef, ast.FunctionDef]
    ) -> None:
        """Check for unhandled coroutines at the end of function processing."""
        func_name = func_node.name

        if func_name not in self.created_coroutines:
            return

        created = set(self.created_coroutines[func_name])
        consumed = self.consumed_coroutines.get(func_name, set())
        returned = self.returned_coroutines.get(func_name, set())
        returns_coroutines = self.function_return_types.get(func_name, False)

        # Find unhandled coroutines
        unhandled = created - consumed

        # If function is typed to return coroutines, don't report violations for unhandled coroutines
        # This handles cases where coroutines are returned in containers or variables that we can't track
        if returns_coroutines:
            return

        # If all created coroutines are returned, don't report violations
        if returned == created:
            return

        # Report violations for truly unhandled coroutines
        for call in unhandled:
            func_info = self._get_function_info(call.func)
            if func_info and func_info["name"]:
                # Determine violation type based on function type
                violation_type: Literal["missing_await", "missing_asyncio"] = (
                    "missing_await"
                    if isinstance(func_node, ast.AsyncFunctionDef)
                    else "missing_asyncio"
                )

                violation = AsyncViolation(
                    file_path=self.file_path,
                    line_number=call.lineno,
                    column_number=call.col_offset,
                    function_name=func_info["name"],
                    violation_type=violation_type,
                    source_line=self._get_context_line(call),
                )
                self.violations.append(violation)


class AsyncDefinitionCollector(ast.NodeVisitor):
    """First pass: collect all async function definitions and imports."""

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.async_functions: Set[str] = set()  # Local async function names
        self.async_methods: Set[str] = (
            set()
        )  # Async method names (class.method)
        self.current_class: Optional[str] = None
        self.imported_modules: Dict[str, str] = {}  # alias -> module_name
        self.imported_functions: Dict[str, str] = (
            {}
        )  # function_name -> module_name
        self.imported_async_functions: Set[str] = (
            set()
        )  # Known async functions from imports
        self.function_definitions: Dict[str, ast.AsyncFunctionDef] = (
            {}
        )  # Store function definitions

    @override
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions to track async methods."""
        prev_class = self.current_class
        self.current_class = node.name

        self.generic_visit(node)

        self.current_class = prev_class

    @override
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definitions."""
        if self.current_class:
            # This is an async method
            method_name = f"{self.current_class}.{node.name}"
            self.async_methods.add(method_name)
            self.async_functions.add(node.name)  # Also add simple name
        else:
            # This is an async function
            self.async_functions.add(node.name)

        # Store the function definition for later analysis
        self.function_definitions[node.name] = node

        self.generic_visit(node)

    @override
    def visit_Import(self, node: ast.Import) -> None:
        """Track imported modules."""
        for alias in node.names:
            module_name = alias.name
            alias_name = alias.asname or alias.name
            self.imported_modules[alias_name] = module_name

    @override
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track imported functions from modules."""
        if node.module:
            for alias in node.names:
                func_name = alias.name
                alias_name = alias.asname or alias.name
                self.imported_functions[alias_name] = node.module

                # Track known async functions from common async libraries
                if node.module == "asyncio" and func_name in {
                    "sleep",
                    "wait",
                    "wait_for",
                    "gather",
                    "shield",
                    "timeout",
                }:
                    self.imported_async_functions.add(alias_name)


class AsyncChecker(object):
    """Main class for checking async function usage."""

    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def check_file(self, file_path: Union[str, Path]) -> AsyncCheckResult:
        """Check a single Python file for async violations."""
        file_path = Path(file_path)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()

            # Split source code into lines for context
            source_lines = source_code.splitlines()

            # Parse the AST
            tree = ast.parse(source_code, filename=str(file_path))

            # Two-pass analysis:
            # Pass 1: Collect all async function definitions and imports
            collector = AsyncDefinitionCollector(str(file_path))
            collector.visit(tree)

            # Pass 2: Analyze function calls with the collected information
            analyzer = AsyncFunctionAnalyzer(str(file_path), source_lines)
            # Transfer collected information
            analyzer.async_functions = collector.async_functions
            analyzer.async_methods = collector.async_methods
            analyzer.imported_async_functions = (
                collector.imported_async_functions
            )
            analyzer.imported_modules = collector.imported_modules
            analyzer.imported_functions = collector.imported_functions
            analyzer.function_definitions = collector.function_definitions

            analyzer.visit(tree)

            return AsyncCheckResult(
                total_files=1,
                violations=analyzer.violations,
                passed=len(analyzer.violations) == 0,
            )

        except SyntaxError as e:
            self.logger.error(f"Syntax error in {file_path}: {e}")
            # Return empty result for syntax errors
            return AsyncCheckResult(total_files=1, violations=[], passed=True)
        except Exception as e:
            self.logger.error(f"Error analyzing {file_path}: {e}")
            raise

    def check_directory(
        self,
        directory_path: Union[str, Path],
        exclude_patterns: Optional[List[str]] = None,
    ) -> AsyncCheckResult:
        """Check all Python files in a directory for async violations."""
        directory_path = Path(directory_path)
        exclude_patterns = exclude_patterns or []

        python_files: List[Path] = []
        for pattern in ["**/*.py"]:
            python_files.extend(directory_path.glob(pattern))

        # Filter out excluded patterns
        if exclude_patterns:
            filtered_files: List[Path] = []
            for file_path in python_files:
                if not any(
                    pattern in str(file_path) for pattern in exclude_patterns
                ):
                    filtered_files.append(file_path)
            python_files = filtered_files

        all_violations: List[AsyncViolation] = []
        for file_path in python_files:
            result = self.check_file(file_path)
            all_violations.extend(result.violations)

        return AsyncCheckResult(
            total_files=len(python_files), violations=all_violations
        )


def get_async_check_result_schema() -> Dict[str, Any]:
    """Get the JSON schema for AsyncCheckResult."""
    return AsyncCheckResult.model_json_schema()
