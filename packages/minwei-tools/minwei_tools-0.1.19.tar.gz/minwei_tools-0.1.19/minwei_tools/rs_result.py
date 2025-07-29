from __future__ import annotations
from typing import Generic, Union, TypeVar, Callable, Optional

T = TypeVar('T')
E = TypeVar('E')

class Result(Generic[T, E]):
    
    def __init__(self):
        self.__value : Optional[T] = None
        self.__error : Optional[E] = None

    @property
    def value(self) -> Optional[T]:
        return self.__value
    
    @value.setter
    def value(self, value: T) -> None:
        self.__value = value

    @property
    def error(self) -> Optional[E]:
        return self.__error
    
    @error.setter
    def error(self, value: E) -> None:
        self.__error : E = value
        
    def is_ok(self) -> bool:
        return isinstance(self, Ok)
    
    def is_err(self) -> bool:
        return isinstance(self, Err)
    
    def unwrap(self) -> T:
        if isinstance(self, Ok):
            return self.value
        raise ValueError("Called unwrap on an Err value")
    
    def unwrap_err(self) -> E:
        if isinstance(self, Err):
            return self.error
        raise ValueError("Called unwrap_err on an Ok value")
    
    def map(self, func: Callable[[T], T]) -> Result[T, E]:
        if isinstance(self, Ok):
            return Ok(func(self.value))
        return self  # Return the Err unchanged

    def map_err(self, func: Callable[[E], E]) -> Result[T, E]:
        if isinstance(self, Err):
            return Err(func(self.error))
        return self  # Return the Ok unchanged

    def and_then(self, func: Callable[[T], Result[T, E]]) -> Result[T, E]:
        if isinstance(self, Ok):
            return Ok(func(self.value))
        return self  # Return the Err unchanged

    def or_else(self, func: Callable[[E], Result[T, E]]) -> Result[T, E]:
        if isinstance(self, Err):
            return Err(func(self.error))
        return self  # Return the Ok unchanged

    def __str__(self) -> str:
        if isinstance(self, Ok):
            return f"Ok({self.value})"
        elif isinstance(self, Err):
            return f"Err(\"{self.error}\")"

class Ok(Result[T, E]):
    __match_args__ = ('value',)
    def __init__(self, value: T) -> None:
        super().__init__()
        self.__value : T = value
        
    @property
    def value(self) -> T:
        return self.__value
    
    @value.setter
    def value(self, value: T) -> None:
        self.__value = value


class Err(Result[T, E]):
    __match_args__ = ('error',)
    def __init__(self, error: E) -> None:
        super().__init__()
        self.__error : E           = error
        
    @property
    def error(self) -> E:
        return self.__error
    
    @error.setter
    def error(self, value: E) -> None:
        self.__error : E = value