# -*- coding: utf-8 -*-

"""
soft-deps is a Python pattern for elegant optional dependency management that
prioritizes developer experience over lazy loading. Unlike true lazy imports,
soft-deps immediately attempts to import dependencies at module load time -
if the dependency is installed, you get the real module with full functionality.
If it's missing, you get a helpful proxy object that provides complete IDE
type hints and auto-completion, but raises informative error messages only
when you actually try to use the missing functionality. This approach gives you
the best of both worlds: seamless development experience with full IDE support
when dependencies are available, and graceful degradation with clear
installation guidance when they're not, all while maintaining zero code
invasiveness in your implementation.
"""

from functools import total_ordering


@total_ordering
class MissingDependency:
    def __init__(
        self,
        name: str,
        error_message: str = "please install it",
    ):
        self.name = name
        self.error_message = error_message

    def _raise_error(self):
        raise ImportError(f"To use `{self.name}`, {self.error_message}.")

    def __repr__(self):  # pragma: no cover
        self._raise_error()

    def __getattr__(self, attr: str):  # pragma: no cover
        self._raise_error()

    def __getitem__(self, item):  # pragma: no cover
        self._raise_error()

    def __call__(self, *args, **kwargs):  # pragma: no cover
        self._raise_error()

    def __iter__(self):  # pragma: no cover
        self._raise_error()

    def __eq__(self, other):  # pragma: no cover
        self._raise_error()

    def __lt__(self, other):  # pragma: no cover
        self._raise_error()

    def __hash__(self):  # pragma: no cover
        self._raise_error()

    def __add__(self, other):  # pragma: no cover
        self._raise_error()

    def __sub__(self, other):  # pragma: no cover
        self._raise_error()

    def __mul__(self, other):  # pragma: no cover
        self._raise_error()

    def __truediv__(self, other):  # pragma: no cover
        self._raise_error()
