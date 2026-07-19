#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Sudoku: Generator & Solver + stepwise solving support

from __future__ import annotations
import random
from typing import List, Tuple, Optional, Set, Iterable

Grid = List[List[int]]


def peers_of(r: int, c: int) -> Set[Tuple[int, int]]:
    ps = set()
    for i in range(9):
        ps.add((r, i))
        ps.add((i, c))
    br, bc = (r // 3) * 3, (c // 3) * 3
    for rr in range(br, br + 3):
        for cc in range(bc, bc + 3):
            ps.add((rr, cc))
    ps.remove((r, c))
    return ps


def copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def is_complete(grid: Grid) -> bool:
    return all(all(v != 0 for v in row) for row in grid)


def find_empty(grid: Grid) -> Optional[Tuple[int, int]]:
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                return (r, c)
    return None


def valid_placement(grid: Grid, r: int, c: int, val: int) -> bool:
    if any(grid[r][cc] == val for cc in range(9)):
        return False
    if any(grid[rr][c] == val for rr in range(9)):
        return False
    br, bc = (r // 3) * 3, (c // 3) * 3
    for rr in range(br, br + 3):
        for cc in range(bc, bc + 3):
            if grid[rr][cc] == val:
                return False
    return True


def print_grid(grid: Grid):
    for r in range(9):
        line = ""
        for c in range(9):
            v = grid[r][c]
            line += "." if v == 0 else str(v)
            if c in [2, 5]:
                line += " | "
            else:
                line += " "
        print(line.strip())
        if r in [2, 5]:
            print("------+-------+------")


def compute_candidates(grid: Grid) -> List[List[Set[int]]]:
    cands = [
        [set(range(1, 10)) if grid[r][c] == 0 else set() for c in range(9)]
        for r in range(9)
    ]
    for r in range(9):
        for c in range(9):
            if grid[r][c] != 0:
                val = grid[r][c]
                for rr, cc in peers_of(r, c):
                    if cands[rr][cc]:
                        cands[rr][cc].discard(val)
    return cands


def apply_naked_singles_yield(grid: Grid) -> Iterable[Tuple[int, int, int]]:
    changed = True
    while changed:
        changed = False
        cands = compute_candidates(grid)
        for r in range(9):
            for c in range(9):
                if grid[r][c] == 0 and len(cands[r][c]) == 1:
                    val = next(iter(cands[r][c]))
                    grid[r][c] = val
                    yield (r, c, val)
                    changed = True


def apply_hidden_singles_yield(grid: Grid) -> Iterable[Tuple[int, int, int]]:
    changed = True
    while changed:
        changed = False
        cands = compute_candidates(grid)
        for r in range(9):
            positions = [c for c in range(9) if grid[r][c] == 0]
            counter = {d: [] for d in range(1, 10)}
            for c in positions:
                for d in cands[r][c]:
                    counter[d].append((r, c))
            for d, locs in counter.items():
                if len(locs) == 1:
                    rr, cc = locs[0]
                    if grid[rr][cc] == 0:
                        grid[rr][cc] = d
                        yield (rr, cc, d)
                        changed = True
        cands = compute_candidates(grid)
        for c in range(9):
            positions = [r for r in range(9) if grid[r][c] == 0]
            counter = {d: [] for d in range(1, 10)}
            for r in positions:
                for d in cands[r][c]:
                    counter[d].append((r, c))
            for d, locs in counter.items():
                if len(locs) == 1:
                    rr, cc = locs[0]
                    if grid[rr][cc] == 0:
                        grid[rr][cc] = d
                        yield (rr, cc, d)
                        changed = True
        cands = compute_candidates(grid)
        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                cells = [
                    (r, c)
                    for r in range(br, br + 3)
                    for c in range(bc, bc + 3)
                    if grid[r][c] == 0
                ]
                counter = {d: [] for d in range(1, 10)}
                for r, c in cells:
                    for d in cands[r][c]:
                        counter[d].append((r, c))
                for d, locs in counter.items():
                    if len(locs) == 1:
                        rr, cc = locs[0]
                        if grid[rr][cc] == 0:
                            grid[rr][cc] = d
                            yield (rr, cc, d)
                            changed = True


def logical_reduce(grid: Grid) -> bool:
    changed = False
    while True:
        cands = compute_candidates(grid)
        progress = False
        for r in range(9):
            for c in range(9):
                if grid[r][c] == 0 and len(cands[r][c]) == 1:
                    val = next(iter(cands[r][c]))
                    grid[r][c] = val
                    progress = True
        cands = compute_candidates(grid)
        for r in range(9):
            positions = [c for c in range(9) if grid[r][c] == 0]
            counter = {d: [] for d in range(1, 10)}
            for c in positions:
                for d in cands[r][c]:
                    counter[d].append((r, c))
            for d, locs in counter.items():
                if len(locs) == 1:
                    rr, cc = locs[0]
                    grid[rr][cc] = d
                    progress = True
        cands = compute_candidates(grid)
        for c in range(9):
            positions = [r for r in range(9) if grid[r][c] == 0]
            counter = {d: [] for d in range(1, 10)}
            for r in positions:
                for d in cands[r][c]:
                    counter[d].append((r, c))
            for d, locs in counter.items():
                if len(locs) == 1:
                    rr, cc = locs[0]
                    grid[rr][cc] = d
                    progress = True
        cands = compute_candidates(grid)
        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                cells = [
                    (r, c)
                    for r in range(br, br + 3)
                    for c in range(bc, bc + 3)
                    if grid[r][c] == 0
                ]
                counter = {d: [] for d in range(1, 10)}
                for r, c in cells:
                    for d in cands[r][c]:
                        counter[d].append((r, c))
                for d, locs in counter.items():
                    if len(locs) == 1:
                        rr, cc = locs[0]
                        grid[rr][cc] = d
                        progress = True
        if not progress:
            break
        changed = True
    return changed


def solve(
    grid: Grid, count_solutions: bool = False, max_solutions: int = 2
) -> Tuple[bool, Optional[Grid], int]:
    work = copy_grid(grid)
    logical_reduce(work)

    cands = compute_candidates(work)
    for r in range(9):
        for c in range(9):
            if work[r][c] == 0 and len(cands[r][c]) == 0:
                return (False, None, 0)

    sols = []

    def bt(g: Grid):
        if count_solutions and len(sols) >= max_solutions:
            return
        if is_complete(g):
            sols.append(copy_grid(g))
            return
        cands_local = compute_candidates(g)
        m = 10
        target = None
        for r in range(9):
            for c in range(9):
                if g[r][c] == 0:
                    l = len(cands_local[r][c])
                    if l < m:
                        m = l
                        target = (r, c)
        if target is None:
            sols.append(copy_grid(g))
            return
        r, c = target
        options = list(cands_local[r][c])
        random.shuffle(options)
        for v in options:
            if valid_placement(g, r, c, v):
                g[r][c] = v
                logical_reduce(g)
                bt(g)
                g[r][c] = 0
                if not count_solutions and sols:
                    return

    bt(work)
    if sols:
        return (True, sols[0], len(sols) if count_solutions else 1)
    else:
        return (False, None, 0)


def solve_steps(grid: Grid) -> Iterable[Tuple[int, int, int]]:
    """Yield (r, c, val) for each placement performed while solving."""
    g = copy_grid(grid)
    for r, c, v in apply_naked_singles_yield(g):
        yield (r, c, v)
    for r, c, v in apply_hidden_singles_yield(g):
        yield (r, c, v)

    if is_complete(g):
        return

    def bt_yield() -> Optional[bool]:
        if is_complete(g):
            return True
        cands_local = compute_candidates(g)
        m = 10
        target = None
        for r in range(9):
            for c in range(9):
                if g[r][c] == 0:
                    l = len(cands_local[r][c])
                    if l < m:
                        m = l
                        target = (r, c)
        if target is None:
            return True
        r, c = target
        options = list(cands_local[r][c])
        random.shuffle(options)
        for v in options:
            if valid_placement(g, r, c, v):
                g[r][c] = v
                yield (r, c, v)
                for rr, cc, vv in apply_naked_singles_yield(g):
                    yield (rr, cc, vv)
                for rr, cc, vv in apply_hidden_singles_yield(g):
                    yield (rr, cc, vv)
                res = yield from bt_yield()
                if res:
                    return True
                g[r][c] = 0
        return None

    yield from bt_yield()


def generate_full_solution() -> Grid:
    grid = [[0] * 9 for _ in range(9)]
    nums = list(range(1, 10))
    random.shuffle(nums)
    grid[0] = nums[:]

    def fill(g: Grid) -> bool:
        pos = find_empty(g)
        if not pos:
            return True
        r, c = pos
        options = list(range(1, 10))
        random.shuffle(options)
        for v in options:
            if valid_placement(g, r, c, v):
                g[r][c] = v
                if fill(g):
                    return True
                g[r][c] = 0
        return False

    fill(grid)
    return grid


def generate_puzzle(min_clues: int = 30, symmetry: bool = True) -> Grid:
    solution = generate_full_solution()
    puzzle = copy_grid(solution)
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)

    def symmetric_pairs(r: int, c: int) -> List[Tuple[int, int]]:
        return [(r, c), (8 - r, 8 - c)]

    for r, c in cells:
        positions = symmetric_pairs(r, c) if symmetry else [(r, c)]
        if all(puzzle[rr][cc] == 0 for rr, cc in positions):
            continue
        backup = [puzzle[rr][cc] for rr, cc in positions]
        for rr, cc in positions:
            puzzle[rr][cc] = 0
        _, _, nsol = solve(puzzle, count_solutions=True, max_solutions=2)
        if nsol != 1:
            for val, (rr, cc) in zip(backup, positions):
                puzzle[rr][cc] = val
        clues = sum(1 for rr in range(9) for cc in range(9) if puzzle[rr][cc] != 0)
        if clues <= min_clues:
            break

    ok, _, nsol = solve(puzzle, count_solutions=True, max_solutions=2)
    if not ok or nsol != 1:
        return generate_puzzle(min_clues=min_clues, symmetry=symmetry)
    return puzzle


def export_grid(grid: Grid, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in range(9):
            f.write("".join(str(grid[r][c]) for c in range(9)) + "\n")


def import_grid(path: str) -> Grid:
    g = [[0] * 9 for _ in range(9)]
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    if len(lines) != 9:
        raise ValueError("Datei muss 9 Zeilen enthalten.")
    for r in range(9):
        if len(lines[r]) != 9 or any(ch not in "0123456789" for ch in lines[r]):
            raise ValueError("Jede Zeile muss 9 Ziffern (0..9) enthalten.")
        g[r] = [int(ch) for ch in lines[r]]
    return g
