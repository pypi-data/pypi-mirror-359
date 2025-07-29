from typing import Any
import numpy as np
import pytest

from paulicirc.utils.numpy import canonicalize_phase
from paulicirc.circuits import Circuit
from paulicirc.gadgets import Gadget, are_same_phase

RNG_SEED = 0
RNG_ALT_SEED = 1
NUM_RNG_SAMPLES = 10
NUM_QUBITS_RANGE = range(0, 9)

rng = np.random.default_rng(RNG_SEED)


@pytest.mark.parametrize(
    "num_qubits,num_gadgets",
    [
        (num_qubits, num_gadgets)
        for num_qubits in NUM_QUBITS_RANGE
        for num_gadgets in rng.integers(0, 20, size=NUM_RNG_SAMPLES)
    ],
)
def test_zero_circuit(num_qubits: int, num_gadgets: int) -> None:
    circ = Circuit.zero(num_gadgets, num_qubits)
    assert circ.num_qubits == num_qubits
    assert circ.num_gadgets == num_gadgets
    gs = list(circ)
    assert len(gs) == num_gadgets
    assert all(g.num_qubits == num_qubits for g in gs)
    assert all(g.is_zero for g in gs)


rng = np.random.default_rng(RNG_SEED)


@pytest.mark.parametrize(
    "num_qubits,num_gadgets,seed",
    [
        (num_qubits, num_gadgets, rng.integers(0, 65536))
        for num_qubits in NUM_QUBITS_RANGE
        for num_gadgets in rng.integers(0, 20, size=NUM_RNG_SAMPLES)
    ],
)
def test_random_circuit(num_qubits: int, num_gadgets: int, seed: int) -> None:
    circ = Circuit.random(num_gadgets, num_qubits, rng=seed)
    assert circ.num_qubits == num_qubits
    assert circ.num_gadgets == num_gadgets
    gs = list(circ)
    assert len(gs) == num_gadgets
    assert all(g.num_qubits == num_qubits for g in gs)
    assert all(
        are_same_phase(g.phase, float(phase)) for g, phase in zip(gs, circ.phases)
    )
    v = np.eye(2**num_qubits, dtype=np.complex128)
    for i, g in enumerate(gs):
        v = g.unitary() @ v
    canonicalize_phase(v)
    u = circ.unitary()
    assert u.dtype == v.dtype
    assert u.shape == v.shape
    assert np.allclose(u, v)


rng = np.random.default_rng(RNG_SEED)


@pytest.mark.parametrize(
    "num_qubits,num_gadgets,seed",
    [
        (num_qubits, num_gadgets, rng.integers(0, 65536))
        for num_qubits in NUM_QUBITS_RANGE
        for num_gadgets in rng.integers(0, 20, size=NUM_RNG_SAMPLES)
    ],
)
def test_circuit_from_gadgets(num_qubits: int, num_gadgets: int, seed: int) -> None:
    circ = Circuit.random(num_gadgets, num_qubits, rng=seed)
    assert circ == Circuit.from_gadgets(circ, num_qubits)
    if num_gadgets > 0:
        assert circ == Circuit.from_gadgets(circ, None)


rng = np.random.default_rng(RNG_SEED)


@pytest.mark.parametrize(
    "num_qubits,num_gadgets,seed",
    [
        (num_qubits, num_gadgets, rng.integers(0, 65536))
        for num_qubits in NUM_QUBITS_RANGE
        for num_gadgets in rng.integers(0, 20, size=NUM_RNG_SAMPLES)
    ],
)
def test_circuit_clone(num_qubits: int, num_gadgets: int, seed: int) -> None:
    circ = Circuit.random(num_gadgets, num_qubits, rng=seed)
    assert circ == circ.clone()


rng = np.random.default_rng(RNG_SEED)


@pytest.mark.parametrize(
    "num_qubits,num_gadgets,seed",
    [
        (num_qubits, num_gadgets, rng.integers(0, 65536))
        for num_qubits in NUM_QUBITS_RANGE
        for num_gadgets in rng.integers(0, 20, size=NUM_RNG_SAMPLES)
    ],
)
def test_circuit_serialization(num_qubits: int, num_gadgets: int, seed: int) -> None:
    circ = Circuit.random(num_gadgets, num_qubits, rng=seed)
    circ_bytes = bytes(circ)
    _circ = Circuit.from_bytes(circ_bytes)
    assert circ == _circ


rng = np.random.default_rng(RNG_SEED)


@pytest.mark.parametrize(
    "num_qubits,num_gadgets,seed,fast",
    [
        (num_qubits, num_gadgets, rng.integers(0, 65536), fast)
        for num_qubits in NUM_QUBITS_RANGE
        for num_gadgets in rng.integers(0, 20, size=NUM_RNG_SAMPLES)
        for fast in (False, True)
    ],
)
def test_circuit_iter_gadgets(
    num_qubits: int, num_gadgets: int, seed: int, fast: bool
) -> None:
    circ = Circuit.random(num_gadgets, num_qubits, rng=seed)
    gs = list(circ)
    assert all(g == h for g, h in zip(gs, circ.iter_gadgets(fast=fast), strict=True))


rng = np.random.default_rng(RNG_SEED)


@pytest.mark.parametrize(
    "num_qubits,num_gadgets,seed",
    [
        (num_qubits, num_gadgets, rng.integers(0, 65536))
        for num_qubits in NUM_QUBITS_RANGE
        for num_gadgets in rng.integers(0, 20, size=NUM_RNG_SAMPLES)
    ],
)
def test_circuit_getitem(
    num_qubits: int,
    num_gadgets: int,
    seed: int,
) -> None:
    circ = Circuit.random(num_gadgets, num_qubits, rng=seed)
    gs = list(circ)
    assert all(g == circ[i] for i, g in enumerate(gs))


rng = np.random.default_rng(RNG_SEED)


@pytest.mark.parametrize(
    "num_qubits,num_gadgets,seed,start,stop,step",
    [
        (
            num_qubits,
            num_gadgets,
            rng.integers(0, 65536),
            (start := int(rng.integers(0, num_gadgets))),
            (stop := int(rng.integers(start, num_gadgets + 1))),
            (step := int(rng.integers(1, num_gadgets + 1))),
        )
        for num_qubits in NUM_QUBITS_RANGE
        for num_gadgets in rng.integers(1, 20, size=NUM_RNG_SAMPLES)
        for _ in range(NUM_RNG_SAMPLES)
    ],
)
def test_circuit_getitem_slice(
    num_qubits: int,
    num_gadgets: int,
    seed: int,
    start: int,
    stop: int,
    step: int,
) -> None:
    circ = Circuit.random(num_gadgets, num_qubits, rng=seed)
    gs = list(circ)
    assert all(g == circ[i] for i, g in enumerate(gs))
    slice_idxs = range(num_gadgets)[s := slice(start, stop, step)]
    slice_gs = circ[s]
    assert all(gs[i] == g for i, g in zip(slice_idxs, slice_gs, strict=True))


rng = np.random.default_rng(RNG_SEED)


@pytest.mark.parametrize(
    "num_qubits,num_gadgets,seed",
    [
        (num_qubits, num_gadgets, rng.integers(0, 65536))
        for num_qubits in NUM_QUBITS_RANGE
        for num_gadgets in rng.integers(1, 20, size=NUM_RNG_SAMPLES)
    ],
)
def test_circuit_setitem(
    num_qubits: int,
    num_gadgets: int,
    seed: int,
) -> None:
    circ = Circuit.random(num_gadgets, num_qubits, rng=seed)
    original_gs = list(circ)
    new_gs = [Gadget.random(num_qubits, rng=seed + 1 + i) for i in range(num_gadgets)]
    for i, g in enumerate(new_gs):
        circ[i] = g
        gs_i = list(circ)
        assert gs_i[: i + 1] == new_gs[: i + 1]
        assert gs_i[i + 1 :] == original_gs[i + 1 :]
    assert list(circ) == new_gs


rng = np.random.default_rng(RNG_SEED)


@pytest.mark.parametrize(
    "num_qubits,num_gadgets,seed,start,stop,step",
    [
        (
            num_qubits,
            num_gadgets,
            rng.integers(0, 65536),
            (start := int(rng.integers(0, num_gadgets))),
            (stop := int(rng.integers(start, num_gadgets + 1))),
            (step := int(rng.integers(1, num_gadgets + 1))),
        )
        for num_qubits in NUM_QUBITS_RANGE
        for num_gadgets in rng.integers(1, 20, size=NUM_RNG_SAMPLES)
        for _ in range(NUM_RNG_SAMPLES)
    ],
)
def test_circuit_setitem_slice(
    num_qubits: int,
    num_gadgets: int,
    seed: int,
    start: int,
    stop: int,
    step: int,
) -> None:
    circ = Circuit.random(num_gadgets, num_qubits, rng=seed)
    original_gs = list(circ)
    new_gs = [Gadget.random(num_qubits, rng=seed + 1 + i) for i in range(num_gadgets)]
    slice_idxs = range(num_gadgets)[s := slice(start, stop, step)]
    slice_gs = [new_gs[i] for i in slice_idxs]
    slice_circ = Circuit.from_gadgets(slice_gs, num_qubits)
    circ[s] = slice_circ
    slice_idxs_set = set(slice_idxs)
    for i, g in enumerate(circ):
        if i in slice_idxs_set:
            assert g == new_gs[i]
        else:
            assert g == original_gs[i]


rng = np.random.default_rng(RNG_SEED)


@pytest.mark.parametrize(
    "num_qubits,num_gadgets,seed",
    [
        (num_qubits, num_gadgets, rng.integers(0, 65536))
        for num_qubits in NUM_QUBITS_RANGE
        for num_gadgets in rng.integers(0, 20, size=NUM_RNG_SAMPLES)
    ],
)
def test_circuit_inverse(num_qubits: int, num_gadgets: int, seed: int) -> None:
    circ = Circuit.random(num_gadgets, num_qubits, rng=seed)
    gs = list(circ)
    circ_inv = circ.inverse()
    gs_inv = list(circ_inv)
    assert all(g.inverse() == g_inv for g, g_inv in zip(gs, reversed(gs_inv)))


rng = np.random.default_rng(RNG_SEED)


@pytest.mark.parametrize(
    "num_qubits,num_gadgets,seed,non_zero",
    [
        (
            num_qubits,
            num_gadgets,
            rng.integers(0, 65536),
            non_zero,
        )
        for num_qubits in NUM_QUBITS_RANGE
        for num_gadgets in rng.integers(0, 20, size=NUM_RNG_SAMPLES)
        for non_zero in (False, True)
    ],
)
def test_circuit_random_commute(
    num_qubits: int, num_gadgets: int, seed: int, non_zero: bool
) -> None:
    circ = Circuit.random(num_gadgets, num_qubits, rng=seed)
    u = circ.unitary()
    canonicalize_phase(u)
    rng = np.random.default_rng(seed + 1)
    codes = rng.integers(int(non_zero), 8, num_gadgets // 2, dtype=np.uint8)
    circ = circ.commute(codes)
    v = circ.unitary()
    canonicalize_phase(v)
    assert np.allclose(u, v)


def bit_reverse(i: int, n: int) -> int:
    return int(f"{i:0>{n}b}"[::-1], 2)


def reorder_qiskit_unitary(u: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
    n = int(np.log2(u.shape[0]))
    assert u.shape == (2**n, 2**n)
    perm = [bit_reverse(i, n) for i in range(2**n)]
    return u[np.ix_(perm, perm)]


try:
    from qiskit.quantum_info import Operator  # type: ignore[import-untyped]

    rng = np.random.default_rng(RNG_SEED)

    @pytest.mark.parametrize(
        "num_qubits,num_gadgets,seed",
        [
            (num_qubits, num_gadgets, rng.integers(0, 65536))
            for num_qubits in NUM_QUBITS_RANGE
            for num_gadgets in rng.integers(0, 20, size=NUM_RNG_SAMPLES)
        ],
    )
    def test_random_circuit_qiskit(
        num_qubits: int, num_gadgets: int, seed: int
    ) -> None:
        circ = Circuit.random(num_gadgets, num_qubits, rng=seed)
        qiskit_circ = circ.to_qiskit()

        qiskit_unitary = reorder_qiskit_unitary(Operator(qiskit_circ).data)
        canonicalize_phase(qiskit_unitary)
        assert np.allclose(circ.unitary(), qiskit_unitary)

except ModuleNotFoundError:
    pass


## This is a very intensive test, we only do it in selected occasions ##

# rng = np.random.default_rng(RNG_SEED)

# @pytest.mark.parametrize(
#     "num_qubits,num_gadgets,seed,repeat,non_zero",
#     [
#         (
#             num_qubits,
#             num_gadgets,
#             rng.integers(0, 65536),
#             repeat,
#             non_zero,
#         )
#         for num_qubits in NUM_QUBITS_RANGE
#         for num_gadgets in rng.integers(0, 10, size=NUM_RNG_SAMPLES)
#         for repeat in rng.integers(2, 10, size=NUM_RNG_SAMPLES)
#         for non_zero in (False, True)
#     ],
# )
# def test_circuit_random_commute_repeated(
#     num_qubits: int, num_gadgets: int, seed: int, repeat: int, non_zero: bool
# ) -> None:
#     circ = Circuit.random(num_gadgets, num_qubits, rng=seed)
#     u = circ.unitary()
#     canonicalize_phase(u)
#     for k in range(repeat):
#         rng = np.random.default_rng(seed + 1 + k)
#         codes = rng.integers(int(non_zero), 8, len(circ) // 2, dtype=np.uint8)
#         circ = circ.commute(codes)
#         v = circ.unitary()
#         canonicalize_phase(v)
#         # print(f"Max abs diff at {k=}: {np.max(np.abs(v-u))} with {codes=}")
#         assert (abs(u-v) <= 1e-3).all(), f"Failed at step {k}, with codes {codes}"
