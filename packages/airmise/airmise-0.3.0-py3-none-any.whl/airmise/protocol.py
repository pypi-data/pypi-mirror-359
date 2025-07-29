import typing as t


class AutoId:
    def __init__(self):
        self._number = 0
        
    def __call__(self):
        self._number += 1
        return self._number


_autoid = AutoId()


class Flag:
    COMPLEX_OBJECT = _autoid()
    ITERATING = _autoid()
    ITERATION_DONE = _autoid()
    NORMAL_OBJECT = _autoid()


class Iterator:
    def __init__(self, iterator) -> None:
        self._iterator = iterator
    
    def next(self) -> t.Tuple[int, t.Any]:
        try:
            x = next(self._iterator)
        except StopIteration:
            return Flag.ITERATION_DONE, None
        else:
            return Flag.ITERATING, x
