from dataclasses import dataclass

@dataclass
class Ok[T]:
    value: T

@dataclass
class Error[E]:
    error: E

type Result[T, E] = Ok[T] | Error[E]
