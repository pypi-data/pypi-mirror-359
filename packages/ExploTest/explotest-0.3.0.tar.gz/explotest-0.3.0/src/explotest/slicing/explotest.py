"""
Used only for slicing!
Sets up tracer that will track every executed line
"""

import ast
import os
import runpy
import sys
import sysconfig
import types
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TrackedFile:
    nodes: ast.Module
    executed_lines: set[int] = field(default_factory=set)


tracked_files: dict[Path, TrackedFile] = {}


# TODO: check if OS independent
def is_stdlib_file(filepath: str) -> bool:
    """Determine if a file is part of the standard library;
    E.g., /Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/..."""
    stdlib_path = sysconfig.get_path("stdlib")
    abs_filename = os.path.abspath(filepath)
    abs_stdlib_path = os.path.abspath(stdlib_path)
    return abs_filename.startswith(abs_stdlib_path)


def is_venv_file(filepath: str) -> bool:
    return ".venv" in filepath


def is_frozen_file(filepath: str) -> bool:
    return filepath.startswith("<frozen ")


class ASTTracer(ast.NodeTransformer):
    tracked_file: TrackedFile

    @staticmethod
    def _get_all_linenos(nodes):
        """Recursively collect all line numbers from a list of AST nodes"""
        linenos = set()
        for node in nodes:
            if hasattr(node, "lineno"):
                linenos.add(node.lineno)
            # Recursively collect from all child nodes
            for child in ast.walk(node):
                if hasattr(child, "lineno"):
                    linenos.add(child.lineno)

        return set(x for x in range(min(linenos), max(linenos) + 1))

    def visit_If(self, node):

        # visit children recursively
        super().generic_visit(node)

        body_linenos = self._get_all_linenos(node.body)
        body_was_executed = bool(
            self.tracked_file.executed_lines.intersection(body_linenos)
        )

        if body_was_executed:
            return node.body
        else:
            return node.orelse

    def visit_For(self, node):

        super().generic_visit(node)

        body_linenos = self._get_all_linenos(node.body)
        body_was_executed = bool(
            self.tracked_file.executed_lines.intersection(body_linenos)
        )

        # condition is false
        if not body_was_executed:
            return None
        return node

    def visit_FunctionDef(self, node):
        super().generic_visit(node)

        body_linenos = (x for x in range(node.lineno + 1, node.end_lineno + 1))
        body_was_executed = bool(
            self.tracked_file.executed_lines.intersection(body_linenos)
        )
        if not body_was_executed:
            return None
        return node

    def visit_Try(self, node):
        super().generic_visit(node)
        handler_linenos = self._get_all_linenos(node.handlers)
        handler_was_executed = bool(
            self.tracked_file.executed_lines.intersection(handler_linenos)
        )

        if not handler_was_executed:
            # change catching exception to pass
            return ast.Try(
                node.body,
                [
                    ast.ExceptHandler(
                        type=ast.Name(id="Exception", ctx=ast.Load()),
                        name="e",
                        body=[ast.Pass()],
                    )
                ],
                node.orelse,
                node.finalbody,
            )

        # remove else since exception was raised
        return ast.Try(
            node.body,
            node.handlers,
            None,
            node.finalbody,
        )


class ASTFlattener(ast.NodeTransformer):

    temp_assignments: list[ast.Assign] = None

    def visit_Assign(self, node):
        """
        unpack x, y, z = a, b, c into multiple lines
        """
        self.generic_visit(node)

        # check for a tuple unpacking assignment
        if (
            isinstance(node.targets[0], ast.Tuple)
            and isinstance(node.value, ast.Tuple)
            and len(node.targets[0].elts) == len(node.value.elts)
        ):
            # generate one assignment per target-value pair
            self.temp_assignments = [
                ast.Assign(targets=[target], value=value)
                for target, value in zip(node.targets[0].elts, node.value.elts)
            ]
            return None

        if isinstance(node.value, ast.IfExp):
            return ast.If(
                node.value.test,
                [ast.Assign(targets=[node.targets[0]], value=node.value.body)],
                [ast.Assign(targets=[node.targets[0]], value=node.value.orelse)],
            )

        return node

    def visit_Call(self, node):
        """
        unpack expressions in call contexts
        """
        self.generic_visit(node)
        self.temp_assignments = [
            ast.Assign(
                targets=[ast.Name(id=f"temp_{i}", ctx=ast.Store())],
                value=arg.value if isinstance(arg, ast.Starred) else arg,
            )
            for i, arg in enumerate(node.args)
        ]
        node.args = [
            (
                ast.Starred(value=ast.Name(id=f"temp_{i}", ctx=ast.Load()), ctx=arg.ctx)
                if isinstance(arg, ast.Starred)
                else ast.Name(id=f"temp_{i}", ctx=ast.Load())
            )
            for i, arg in enumerate(node.args)
        ]

        return node

    def visit_Subscript(self, node):
        self.generic_visit(node)

        if isinstance(node.slice, ast.Slice):
            self.temp_assignments = [
                ast.Assign(
                    targets=[ast.Name(id=f"temp_0", ctx=ast.Store())],
                    value=node.slice.lower,
                ),
                ast.Assign(
                    targets=[ast.Name(id=f"temp_1", ctx=ast.Store())],
                    value=node.slice.upper,
                ),
            ]

            node.slice = ast.Slice(
                ast.Name(id="temp_0", ctx=ast.Load()),
                ast.Name(id="temp_1", ctx=ast.Load()),
            )
            return node
        else:
            self.temp_assignments = [
                ast.Assign(
                    targets=[ast.Name(id=f"temp", ctx=ast.Store())], value=node.slice
                )
            ]
            node.slice = ast.Name("temp", ctx=ast.Load())
            return node

    def flatten(self, stmt: ast.AST) -> list[ast.AST]:
        self.temp_assignments = []

        new_stmt = self.visit(stmt)
        all_statements = self.temp_assignments + [new_stmt]
        all_statements = filter(lambda x: x is not None, all_statements)
        return list(map(ast.fix_missing_locations, all_statements))


def tracer(frame: types.FrameType, event, arg):
    """
    #     Hooks onto Python default tracer to add instrumentation for ExploTest.
    #     :param frame:
    #     :param event:
    #     :param __arg:
    #     :return: must return this object for tracing to work
    """
    filename = frame.f_globals.get("__file__", "<unknown>")
    # ignore files we don't have access to
    if is_frozen_file(filename) or is_stdlib_file(filename) or is_venv_file(filename):
        return tracer

    path = Path(filename)
    path.resolve()

    source = path.read_text()
    lineno = frame.f_lineno

    if tracked_files.get(path):
        t = tracked_files[path]
    else:
        tree = ast.parse(source, filename=path.name)
        t = TrackedFile(tree)
        tracked_files[path] = t

    if event == "line":
        t.executed_lines.add(lineno)

    return tracer


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 -m explotest <filename>")
        sys.exit(1)
    target = sys.argv[1]
    sys.argv = sys.argv[1:]

    script_dir = os.path.abspath(os.path.dirname(target))
    sys.path.insert(0, script_dir)

    sys.settrace(tracer)
    runpy.run_path(target, run_name="__main__")
    sys.settrace(None)

    for f in tracked_files.values():
        t = ASTTracer()
        t.tracked_file = f
        n = t.visit(f.nodes)
        n = ast.fix_missing_locations(n)

        flattener = ASTFlattener()
        new_statements = []
        for stmt in n.body:
            new_statements.extend(flattener.flatten(stmt))

        # Create new module with flattened statements
        new_tree = ast.Module(body=new_statements, type_ignores=[])

        print(ast.unparse(ast.fix_missing_locations(new_tree)))


if __name__ == "__main__":
    main()
