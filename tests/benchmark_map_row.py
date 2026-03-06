"""Benchmark: hand-written map_row vs generic map_row with cached get_fields().

Measures only the difference between:
  - Generic: get_fields() (cached list) + loop with setattr(self, f.name, row[f.order])
  - Hand-written: 7 direct setattrs with row[0]..row[6]

No full package imports needed.
"""
import timeit


class FakeMapped:
    def __init__(self, name: str, order: int):
        self.name = name
        self.order = order


# Cached field list (simulates get_fields() after first call)
CACHED_FIELDS = [
    FakeMapped("id", 0),
    FakeMapped("name", 1),
    FakeMapped("address", 2),
    FakeMapped("number_1", 3),
    FakeMapped("number_2", 4),
    FakeMapped("create_date", 5),
    FakeMapped("active", 6),
]


class Entity:
    pass


def generic_map_row(entity, row):
    for f in CACHED_FIELDS:
        setattr(entity, f.name, row[f.order])
    return entity


def hand_written_map_row(entity, row):
    setattr(entity, "id", row[0])
    setattr(entity, "name", row[1])
    setattr(entity, "address", row[2])
    setattr(entity, "number_1", row[3])
    setattr(entity, "number_2", row[4])
    setattr(entity, "create_date", row[5])
    setattr(entity, "active", row[6])
    return entity


def run_generic():
    e = Entity()
    generic_map_row(e, (1, "n", "a", 10, 3.14, None, True))
    return e


def run_hand_written():
    e = Entity()
    hand_written_map_row(e, (1, "n", "a", 10, 3.14, None, True))
    return e


N = 200_000
generic_time = timeit.timeit(run_generic, number=N)
hand_time = timeit.timeit(run_hand_written, number=N)

print(f"Generic (cached get_fields + loop):  {generic_time:.4f}s for {N} calls")
print(f"Hand-written (direct setattrs):      {hand_time:.4f}s for {N} calls")
if generic_time > 0:
    pct_faster = (1 - hand_time / generic_time) * 100
    print(f"Hand-written is {pct_faster:.1f}% faster")
    print(f"(Generic takes {generic_time / hand_time:.2f}x longer)")
