from __future__ import annotations

import functools
import inspect
import traceback
from collections.abc import AsyncGenerator, Awaitable, Callable, Generator
from typing import Any, Generic, Literal, NoReturn, TypeVar, Union, cast

try:
  from typing import ParamSpec
except ImportError:
  try:
    from typing_extensions import ParamSpec  # type: ignore
  except ImportError:
    pass

# TypeIs was added to typing in Python 3.11.
# For older versions, we fall back to typing_extensions.
try:
  from typing import TypeIs
except ImportError:
  try:
    from typing_extensions import TypeIs  # type: ignore
  except ImportError:
    pass

T = TypeVar('T', covariant=True)  # Success type
E = TypeVar('E', covariant=True)  # Error type
U = TypeVar('U')
F = TypeVar('F')
P = ParamSpec('P')
R = TypeVar('R')
TBE = TypeVar('TBE', bound=BaseException)


class UnwrapError(Exception):
  """
  Exception raised from ``.unwrap_<...>`` and ``.expect_<...>`` calls.
  """

  _result: Result[object, object]

  def __init__(self, result: Result[object, object], message: str) -> None:
    self._result = result
    super().__init__(message)

  @property
  def result(self) -> Result[..., Any]:
    """Returns the original result."""
    return self._result


class Ok(Generic[T]):
  """
  A value that indicates success and which stores arbitrary data for the return value.
  """

  __match_args__ = ('ok_value',)
  __slots__ = ('_value',)

  def __init__(self, value: T) -> None:
    self._value = value

  def __repr__(self) -> str:
    return f'Ok({self._value!r})'

  def __eq__(self, other: Any) -> bool:
    return isinstance(other, Ok) and self._value == other._value

  def __ne__(self, other: Any) -> bool:
    return not (self == other)

  def __hash__(self) -> int:
    return hash((True, self._value))

  def is_ok(self) -> Literal[True]:
    return True

  def is_err(self) -> Literal[False]:
    return False

  def ok(self) -> T:
    """Return the value."""
    return self._value

  def err(self) -> None:
    """Return `None`."""
    return None

  @property
  def ok_value(self) -> T:
    """Return the inner value."""
    return self._value

  def swap(self) -> Err[T]:
    """Swap success/error cases. Returns `Err` with the value."""
    return Err(self._value)

  def value_or(self, default: Any) -> T:
    """Return the value (alias for `unwrap_or`)."""
    return self._value

  def alt(self, op: Callable[[Any], Any]) -> Ok[T]:
    """Transforms error value (no-op for `Ok`)."""
    return self

  def expect(self, _message: str) -> T:
    """Return the value."""
    return self._value

  def expect_err(self, message: str) -> NoReturn:
    """Raise an UnwrapError since this type is `Ok`."""
    raise UnwrapError(self, message)

  def unwrap(self) -> T:
    """Return the value."""
    return self._value

  def unwrap_err(self) -> NoReturn:
    """Raise an UnwrapError since this type is `Ok`."""
    raise UnwrapError(self, 'Called `Result.unwrap_err()` on an `Ok` value')

  def unwrap_or(self, _default: U) -> T:
    """Return the value."""
    return self._value

  def unwrap_or_else(self, op: Callable[[Any], T]) -> T:
    """Return the value."""
    return self._value

  def unwrap_or_raise(self, e: object) -> T:
    """Return the value."""
    return self._value

  def map(self, op: Callable[[T], U]) -> Ok[U]:
    """Map the value using the given function."""
    return Ok(op(self._value))

  async def map_async(self, op: Callable[[T], Awaitable[U]]) -> Ok[U]:
    """Map the value asynchronously using the given function."""
    return Ok(await op(self._value))

  def map_or(self, default: object, op: Callable[[T], U]) -> U:
    """Map the value or return the default (not used for `Ok`)."""
    return op(self._value)

  def map_or_else(self, default_op: object, op: Callable[[T], U]) -> U:
    """Map the value or run the default operation (not used for `Ok`)."""
    return op(self._value)

  def map_err(self, op: object) -> Ok[T]:
    """Map the error value (no-op for `Ok`)."""
    return self

  def and_then(self, op: Callable[[T], Result[U, E]]) -> Result[U, E]:
    """Bind the value to a function returning `Result`."""
    return op(self._value)

  async def and_then_async(self, op: Callable[[T], Awaitable[Result[U, E]]]) -> Result[U, E]:
    """Bind the value asynchronously to a function returning `Result`."""
    return await op(self._value)

  def or_else(self, op: object) -> Ok[T]:
    """Handle error case (no-op for `Ok`)."""
    return self

  def inspect(self, op: Callable[[T], Any]) -> Result[T, E]:
    """Call a function with the value and return the original result."""
    op(self._value)
    return self

  def inspect_err(self, op: Callable[[E], Any]) -> Result[T, E]:
    """Call a function with the error value (no-op for `Ok`)."""
    return self


class DoException(Exception):
  """Used to signal to `do()` that the result is an `Err`."""

  def __init__(self, err: Err[E]) -> None:
    self.err = err


class Err(Generic[E]):
  """A value that signifies failure and which stores arbitrary data for the error."""

  __match_args__ = ('err_value',)
  __slots__ = ('_trace', '_value')

  def __init__(self, value: E) -> None:
    self._value = value
    self._trace: list[str] | None = self._capture_traceback(value)

  def _capture_traceback(self, exc: E) -> list[str] | None:
    """Capture traceback if the values is a BaseException with __traceback__."""
    if isinstance(exc, BaseException) and exc.__traceback__ is not None:
      stack_summary = traceback.extract_tb(exc.__traceback__)
      return traceback.format_list(stack_summary)
    return None

  @property
  def trace(self) -> list[str] | None:
    """Return the captured stack trace as a list of formatted strings."""
    return self._trace

  def __repr__(self) -> str:
    return f'Err({self._value!r})'

  def __eq__(self, other: Any) -> bool:
    return isinstance(other, Err) and self._value == other._value

  def __ne__(self, other: Any) -> bool:
    return not (self == other)

  def __hash__(self) -> int:
    return hash((False, self._value))

  def is_ok(self) -> Literal[False]:
    return False

  def is_err(self) -> Literal[True]:
    return True

  def ok(self) -> None:
    """Return `None`."""
    return None

  def err(self) -> E:
    """Return the error."""
    return self._value

  @property
  def err_value(self) -> E:
    """Return the inner value."""
    return self._value

  def swap(self) -> Ok[E]:
    """Swap success/error cases. Returns `Ok` with the error value."""
    return Ok(self._value)

  def value_or(self, default: U) -> U:
    """Return the default value (alias for `unwrap_or`)."""
    return default

  def alt(self, op: Callable[[E], F]) -> Err[F]:
    """Transform the error value using the given function."""
    return Err(op(self._value))

  def expect(self, message: str) -> NoReturn:
    """Raise an UnwrapError."""
    exc = UnwrapError(
      self,
      f'{message}: {self._value!r}',
    )
    if isinstance(self._value, BaseException):
      raise exc from self._value
    raise exc

  def expect_err(self, _message: str) -> E:
    """Return the inner value."""
    return self._value

  def unwrap(self) -> NoReturn:
    """Raise an UnwrapError."""
    exc = UnwrapError(
      self,
      f'Called `Result.unwrap()` on an `Err` value: {self._value!r}',
    )
    if isinstance(self._value, BaseException):
      raise exc from self._value
    raise exc

  def unwrap_err(self) -> E:
    """Return the inner value."""
    return self._value

  def unwrap_or(self, default: U) -> U:
    """Return the default value."""
    return default

  def unwrap_or_else(self, op: Callable[[E], T]) -> T:
    """Return the result of applying `op` to the error value."""
    return op(self._value)

  def unwrap_or_raise(self, e: type[TBE]) -> NoReturn:
    """Raise the exception with the error value."""
    raise e(self._value)

  def map(self, op: object) -> Err[E]:
    """Map the value (no-op for `Err`)."""
    return self

  async def map_async(self, op: object) -> Err[E]:
    """Map the value asynchronously (no-op for `Err`)."""
    return self

  def map_or(self, default: U, op: object) -> U:
    """Return the default value."""
    return default

  def map_or_else(self, default_op: Callable[[], U], op: object) -> U:
    """Return the result of the default operation."""
    return default_op()

  def map_err(self, op: Callable[[E], F]) -> Err[F]:
    """Map the error value using the given function."""
    return Err(op(self._value))

  def and_then(self, op: object) -> Err[E]:
    """Bind the error value (no-op for `Err`)."""
    return self

  async def and_then_async(self, op: object) -> Err[E]:
    """Bind the error value asynchronously (no-op for `Err`)."""
    return self

  def or_else(self, op: Callable[[E], Result[T, F]]) -> Result[T, F]:
    """Handle error case and return a new result."""
    return op(self._value)

  def inspect(self, op: Callable[[T], Any]) -> Result[T, E]:
    """Call a function with the value (no-op for `Err`)."""
    return self

  def inspect_err(self, op: Callable[[E], Any]) -> Result[T, E]:
    """Call a function with the error value and return the original result."""
    op(self._value)
    return self


Result = Union[Ok[T], Err[E]]
OkErr = (Ok, Err)


def as_result(
  *exceptions: type[TBE],
) -> Callable[[Callable[..., R]], Callable[..., Result[R, TBE]]]:
  """
  Make a decorator to turn a function into one that returns a ``Result``.
  """
  if not exceptions or not all(
    inspect.isclass(exception) and issubclass(exception, BaseException) for exception in exceptions
  ):
    raise TypeError('as_result() requires one or more exception types')

  def decorator(f: Callable[..., R]) -> Callable[..., Result[R, TBE]]:
    @functools.wraps(f)
    def wrapper(*args: ..., **kwargs: Any) -> Result[R, TBE]:
      try:
        return Ok(f(*args, **kwargs))
      except exceptions as exc:
        return Err(exc)

    return wrapper

  return decorator


def as_async_result(
  *exceptions: type[TBE],
) -> Callable[[Callable[..., Awaitable[R]]], Callable[..., Awaitable[Result[R, TBE]]]]:
  """
  Make a decorator to turn an async function into one that returns a ``Result``.
  """
  if not exceptions or not all(
    inspect.isclass(exception) and issubclass(exception, BaseException) for exception in exceptions
  ):
    raise TypeError('as_result() requires one or more exception types')

  def decorator(
    f: Callable[..., Awaitable[R]],
  ) -> Callable[..., Awaitable[Result[R, TBE]]]:
    @functools.wraps(f)
    async def async_wrapper(*args: ..., **kwargs: Any) -> Result[R, TBE]:
      try:
        return Ok(await f(*args, **kwargs))
      except exceptions as exc:
        return Err(exc)

    return async_wrapper

  return decorator


def is_ok(result: Result[T, E]) -> TypeIs[Ok[T]]:
  """Type guard to check if a result is an ``Ok``."""
  return result.is_ok()


def is_err(result: Result[T, E]) -> TypeIs[Err[E]]:
  """Type guard to check if a result is an ``Err``."""
  return result.is_err()


def do(
  fn_or_gen: Callable[..., Generator[Result[T, E], None, R]] | Generator[Result[T, E], None, R],
) -> Callable[..., Result[T | R, E]] | Result[T | R, E]:
  """
  A dual-purpose function for emulating do-notation.

  Can be used as a decorator:
  @do
  def my_func() -> Generator[...]:
      ...

  Or as a helper function:
  my_gen = my_func()
  result = do(my_gen)
  """
  if isinstance(fn_or_gen, Generator):
    # Helper usage: do(my_generator)
    return _run_do(fn_or_gen)

  if callable(fn_or_gen):
    # Decorator usage: @do
    fn = fn_or_gen

    @functools.wraps(fn)
    def wrapper(*args: ..., **kwargs: Any) -> Result[T | R, E]:
      gen = fn(*args, **kwargs)
      return _run_do(gen)

    return wrapper

  raise TypeError('do() must be used as a decorator or called with a generator instance.')


def do_async(
  fn_or_gen: Callable[..., AsyncGenerator[Result[T, E], None]] | AsyncGenerator[Result[T, E], None],
) -> Callable[..., Awaitable[Result[T, E]]] | Awaitable[Result[T, E]]:
  """
  A dual-purpose function for emulating async do-notation.

  Can be used as a decorator:
  @do_async
  async def my_func() -> AsyncGenerator[...]:
      ...

  Or as a helper function:
  my_gen = my_func()
  result = await do_async(my_gen)
  """
  if inspect.isasyncgen(fn_or_gen):
    return _run_do_async(fn_or_gen)

  if callable(fn_or_gen):
    fn = fn_or_gen

    @functools.wraps(fn)
    async def wrapper(*args: ..., **kwargs: Any) -> Result[T, E]:
      async_gen = fn(*args, **kwargs)
      return await _run_do_async(async_gen)

    return wrapper

  raise TypeError('do_async() must be used as a decorator or called with an async generator.')


def catch(
  *errors: type[E],
) -> Callable[[Callable[..., T]], Callable[..., Result[T, E]]]:
  """
  Make a decorator to catch specified exceptions and return them as ``Err``.
  """

  def decorator(func: Callable[..., T]) -> Callable[..., Result[T, E]]:
    @functools.wraps(func)
    def wrapper(*args: ..., **kwargs: Any) -> Result[T, E]:
      try:
        result = func(*args, **kwargs)
      except errors as e:
        return Err(e)
      return Ok(result)

    return wrapper

  return decorator


def catch_async(
  *errors: type[E],
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[Result[T, E]]]]:
  """
  Make a decorator to catch specified exceptions in async functions and return them as ``Err``.
  """

  def decorator(
    func: Callable[..., Awaitable[T]],
  ) -> Callable[..., Awaitable[Result[T, E]]]:
    @functools.wraps(func)
    async def wrapper(*args: ..., **kwargs: Any) -> Result[T, E]:
      try:
        result = await func(*args, **kwargs)
      except errors as e:
        return Err(e)
      return Ok(result)

    return wrapper

  return decorator


def _run_do(gen: Generator[Result[T, E], None, R]) -> Result[T | R, E]:
  try:
    value = None
    while True:
      res = gen.send(value)
      if isinstance(res, Err):
        return res
      value = res.unwrap()
  except StopIteration as e:
    return Ok(e.value)


async def _run_do_async(gen: AsyncGenerator[Result[T, E], None]) -> Result[T, E]:
  """
  Helper function that executes an async generator and returns the final ``Result``.
  """
  try:
    value = None
    while True:
      res = await gen.asend(value)
      if isinstance(res, Err):
        return res
      value = res.unwrap()
  except StopAsyncIteration:
    return Ok(cast(T, value))
