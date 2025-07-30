from dataclasses import dataclass

@dataclass
class Just[T]:
    value: T

@dataclass
class Nothing:
    pass

type Maybe[T] = Just[T] | Nothing
