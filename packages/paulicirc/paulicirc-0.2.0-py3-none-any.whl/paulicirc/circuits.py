"""Circuits of Pauli gadgets."""

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations
from collections.abc import Iterable, Iterator
from fractions import Fraction
from math import ceil, log10
import sys
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    Self,
    Sequence,
    SupportsFloat,
    SupportsIndex,
    TypeAlias,
    cast,
    final,
    overload,
)
import numpy as np


from .utils.numpy import (
    RNG,
    Complex128Array1D,
    Complex128Array2D,
    ComplexArray1D,
    FloatArray1D,
    UInt8Array1D,
    UInt8Array2D,
    UIntArray1D,
    canonicalize_phase,
    numba_jit,
)
from .gadgets import (
    PHASE_DTYPE,
    PHASE_NBYTES,
    Gadget,
    PauliArray,
    Phase,
    PhaseArray,
    PauliArray2D,
    QubitIdxs,
    are_same_phases,
    decode_phases,
    encode_phases,
    gadget_data_len,
    invert_phases,
    commute_gadget_pair,
)

if __debug__:
    from typing_validation import validate

if TYPE_CHECKING:
    try:
        from qiskit import QuantumCircuit as QiskitQuantumCircuit  # type: ignore[import-untyped]
    except ModuleNotFoundError:
        pass


CircuitData: TypeAlias = UInt8Array2D
"""Type alias for data encoding a circuit of Pauli gadgets."""

CommutationCodeArray: TypeAlias = UInt8Array1D
"""
A 1D array of commutation codes, used by :meth:`Circuit.commute`.

See :class:`Gadget.commute_past` for a description of the commutation procedure
and associated commutation code conventions.
"""


def zero_circ(m: int, n: int) -> CircuitData:
    """
    Returns a circuit with ``m`` gadgets on ``n`` qubits,
    where all gadgets have no legs and zero phase.

    Presumes that the number ``n`` of qubits is divisible by 4.
    """
    ncols = PHASE_NBYTES - (-n // 4)
    return np.zeros((m, ncols), dtype=np.uint8)


def rand_circ(m: int, n: int, *, rng: RNG) -> CircuitData:
    """
    Returns a uniformly random circuit with ``m`` gadgets on ``n`` qubits.
    """
    ncols = PHASE_NBYTES - (-n // 4)
    data = rng.integers(0, 256, (m, ncols), dtype=np.uint8)
    if n % 4 != 0:
        # zeroes out the padding leg bits (up to 6 bits)
        mask = np.uint8(0b11111111 << 2 * (-n % 4) & 0b11111111)
        data[:, -PHASE_NBYTES - 1] &= mask
    # sets the phase bytes
    phases = rng.uniform(0.0, 2 * np.pi, size=m).astype(PHASE_DTYPE)
    data[:, -PHASE_NBYTES:] = encode_phases(phases)
    return data


@numba_jit
def get_circuit_legs(circ: CircuitData) -> PauliArray2D:
    """
    Extract a 2D array of leg information from given circuit data.
    The returned array has values in ``range(4)``,
    where the encoding is explained in :obj:`~paulicirc.gadgets.GadgetData`.
    """
    leg_bytes = circ[:, :-PHASE_NBYTES]
    m, n = leg_bytes.shape
    legs = np.zeros((m, 4 * n), dtype=np.uint8)
    legs[:, ::4] = (leg_bytes & 0b11_00_00_00) >> 6
    legs[:, 1::4] = (leg_bytes & 0b00_11_00_00) >> 4
    legs[:, 2::4] = (leg_bytes & 0b00_00_11_00) >> 2
    legs[:, 3::4] = leg_bytes & 0b00_00_00_11
    return legs


def set_circuit_legs(circ: CircuitData, legs: PauliArray2D) -> None:
    """
    Sets leg information in the given circuit data.
    The input array should have values in ``range(4)``,
    where the encoding is explained in :obj:`~paulicirc.gadgets.GadgetData`.
    """
    _, n = legs.shape
    leg_data = circ[:, :-PHASE_NBYTES]
    leg_data[:, :] = 0
    leg_data[:, : -(-(n - 0) // 4)] |= legs[:, 0::4] << 6  # type: ignore
    leg_data[:, : -(-(n - 1) // 4)] |= legs[:, 1::4] << 4  # type: ignore
    leg_data[:, : -(-(n - 2) // 4)] |= legs[:, 2::4] << 2  # type: ignore
    leg_data[:, : -(-(n - 3) // 4)] |= legs[:, 3::4]


@numba_jit
def transversal_set_gadget_leg_at(
    circ: CircuitData, p: int, qs: UIntArray1D, start: int, end: int
) -> None:
    """
    Sets single leg data to the given circuit data, transversally over multiple
    gadget indices and qubits.
    """
    _qs = np.array(qs, np.uint64)
    shifts = 2 * (3 - _qs % 4)
    idxs = np.arange(start, end)
    circ[idxs, _qs // 4] &= 0b11111111 ^ (0b11 << shifts)
    circ[idxs, _qs // 4] |= np.uint8(p) << shifts


@numba_jit
def transversal_set_phase(
    circ: CircuitData, phase: Phase, start: int, end: int
) -> None:
    """Sets phase data, transversally over multiple gadget indices."""
    circ[start:end, -PHASE_NBYTES:] = np.array(
        [phase % (2 * np.pi)], dtype=np.float64
    ).view(np.uint8)


def commute_circuit(circ: CircuitData, codes: CommutationCodeArray) -> CircuitData:
    """
    Commutes subsequent gadget pairs in the circuit according to the given codes.
    Expects the number of codes to be ``m//2``, where ``m`` is the number of gadgets.

    See :class:`Gadget.commute_past` for a description of the commutation procedure
    and associated commutation code conventions.
    """
    m, _n = circ.shape
    _m = m + m // 2 + 2 * (m % 2)
    exp_circ = np.zeros((_m, _n), dtype=np.uint8)
    exp_circ[::3] = circ[::2]
    exp_circ[1 : _m - 2 * (m % 2) : 3] = circ[1::2]
    exp_circ[2 : _m - (m % 2) : 3, -1] = codes % 8
    reshaped_exp_circ = exp_circ.reshape(_m // 3, 3 * _n)
    np.apply_along_axis(commute_gadget_pair, 1, reshaped_exp_circ)
    return exp_circ[~np.all(exp_circ == 0, axis=1)]  # type: ignore


def unitary_from_gadgets(
    self: Iterable[Gadget],
    num_qubits: int,
    canonical_phase: bool = True,
    _use_cupy: bool = False,  # currently in alpha
) -> Complex128Array2D:
    """Returns the unitary matrix associated to the given sequence of gadgets."""
    res: Complex128Array2D = np.eye(2**num_qubits, dtype=np.complex128)
    if _use_cupy:
        import cupy as cp  # type: ignore[import-untyped]

        res = cp.asarray(res)
    for gadget in self:
        gadget_u = gadget.unitary(canonical_phase=False)
        if _use_cupy:
            gadget_u = cp.asarray(res)
        res = gadget_u @ res
    if _use_cupy:
        res = cp.asnumpy(res).astype(np.complex128)
    if canonical_phase:
        canonicalize_phase(res)
    return res


def statevec_from_gadgets(
    self: Iterable[Gadget],
    input: ComplexArray1D | FloatArray1D,
    canonical_phase: bool = True,
    _use_cupy: bool = False,  # currently in alpha
) -> Complex128Array1D:
    """
    Computes the statevector resulting from the application of the given gadgets
    to the given input statevector.
    """
    assert validate(input, ComplexArray1D | FloatArray1D)
    res = input.astype(np.complex128)
    if _use_cupy:
        import cupy as cp

        res = cp.asarray(res)
    for gadget in self:
        gadget_u = gadget.unitary(canonical_phase=False)
        if _use_cupy:
            gadget_u = cp.asarray(res)
        res = gadget_u @ res
    if canonical_phase:
        canonicalize_phase(res)
    return res


@final
class CircuitListing:
    """A listing for a quantum circuit."""

    _circuit: Circuit
    _selection: tuple[int, int] | None

    __slots__ = ("__weakref__", "_circuit", "_selection")

    def __new__(
        cls, circuit: Circuit, selection: tuple[int, int] | None = None
    ) -> Self:
        """
        Instantiates a new listing for the given circuit, with optional starting and/or
        stopping gadget indices.

        :meta public:
        """
        if selection is not None:
            start, stop = selection
            start, stop, _ = slice(start, stop).indices(len(circuit))
            selection = (start, stop)
        self = super().__new__(cls)
        self._circuit = circuit
        self._selection = selection
        return self

    def __getitem__(
        self, idx: int | slice[int | None, int | None, None]
    ) -> CircuitListing:
        if self._selection is not None:
            raise ValueError("Circuit listings can only be sliced once.")
        if isinstance(idx, int):
            return CircuitListing(self._circuit, (idx, idx + 1))
        start, stop, _ = idx.indices(len(self._circuit))
        return CircuitListing(self._circuit, (start, stop))

    def __repr__(self) -> str:
        """
        Creates a string listing of the circuit, with gadgets listed one per line,
        in the format ``idx phase paulistr``.

        :meta public:
        """
        circuit = self._circuit
        if self._selection is not None:
            start, stop = self._selection
            if stop <= start or stop <= 0:
                return ""
        else:
            start, stop = 0, len(circuit)
        data = tuple(
            (g.phase_str, g.leg_paulistr)
            for g in circuit.iter_gadgets(start=start, stop=stop, fast=True)
        )
        _max_phase_strlen = max(len(s) for s, _ in data)
        data = tuple(
            (f"{phase_str: >{_max_phase_strlen}}", paulistr)
            for phase_str, paulistr in data
        )
        num_idx_digits = int(ceil(log10(stop)))
        idx_range = range(start, stop)
        return "\n".join(
            f"{str(idx): >{num_idx_digits}} {phase_str} {paulistr}"
            for idx, (phase_str, paulistr) in zip(idx_range, data)
        )


@final
class Circuit:
    """A quantum circuit, represented as a sequential composition of Pauli gadgets."""

    @classmethod
    def zero(cls, num_gadgets: int, num_qubits: int) -> Self:
        """
        Constructs a circuit with the given number of gadgets and qubits,
        where all gadgets have no legs and zero phase.
        """
        assert Circuit.__validate_circ_shape(num_gadgets, num_qubits)
        data = zero_circ(num_gadgets, num_qubits)
        return cls(data, num_qubits)

    @classmethod
    def random(
        cls, num_gadgets: int, num_qubits: int, *, rng: int | RNG | None = None
    ) -> Self:
        """
        Constructs a circuit with the given number of gadgets and qubits,
        where all gadgets have random legs and random phase.
        """
        assert Circuit.__validate_circ_shape(num_gadgets, num_qubits)
        if not isinstance(rng, RNG):
            rng = np.random.default_rng(rng)
        data = rand_circ(num_gadgets, num_qubits, rng=rng)
        return cls(data, num_qubits)

    @classmethod
    def from_gadgets(
        cls, gadgets: Iterable[Gadget], num_qubits: int | None = None
    ) -> Self:
        """Constructs a circuit from the given gadgets."""
        gadgets = list(gadgets)
        assert Circuit.__validate_gadgets(gadgets, num_qubits)
        if num_qubits is None:
            num_qubits = gadgets[0].num_qubits
        data = np.array([g._data for g in gadgets], dtype=np.uint8).reshape(
            len(gadgets), gadget_data_len(num_qubits)
        )
        return cls(data, num_qubits)

    @staticmethod
    def from_bytes(bs: bytes) -> Circuit:
        """
        Deserializes a circuit from bytes.
        See :meth:`Circuit.__bytes__` for discussion of the encoding.
        """
        if len(bs) <= 10:
            raise ValueError("Circuit encodings are >= 18B.")
        if bs[0] != 0x01:
            raise ValueError("First byte must be 0x01.")
        if bs[1] != 0x04:
            raise NotImplementedError(
                f"Phase dtype code 0x{bs[2]:0>2x} not implemented."
                "The only phase dtype currently implemented is 0x04 for float64."
            )
        num_gadgets = int.from_bytes(bs[2:10], byteorder="big", signed=False)
        num_qubits = int.from_bytes(bs[10:18], byteorder="big", signed=False)
        if num_gadgets == 0:
            return Circuit(zero_circ(num_gadgets, num_qubits), num_qubits)
        data = np.frombuffer(memoryview(bs)[18:], dtype=np.uint8).reshape(
            num_gadgets, -1
        )
        expected_ncols = PHASE_NBYTES - (-num_qubits // 4)
        if data.shape[1] != expected_ncols:
            raise ValueError(
                f"Expected data of shape ({num_gadgets}, {expected_ncols})"
                f", found data of shape {data.shape} instead."
            )
        return Circuit(data, num_qubits)

    _data: CircuitData
    _num_qubits: int

    __slots__ = ("__weakref__", "_data", "_num_qubits")

    def __new__(cls, data: CircuitData, num_qubits: int | None = None) -> Self:
        """
        Constructs a gadget circuit from the given data.

        :meta public:
        """
        assert Circuit.__validate_new_args(data, num_qubits)
        if num_qubits is None:
            num_qubits = (data.shape[1] - PHASE_NBYTES) * 4
        self = super().__new__(cls)
        self._data = data
        self._num_qubits = num_qubits
        return self

    @property
    def num_gadgets(self) -> int:
        """Number of gadgets in the circuit."""
        return len(self._data)

    @property
    def num_qubits(self) -> int:
        """Number of qubits in the circuit."""
        return self._num_qubits

    @property
    def phases(self) -> PhaseArray:
        """Array of phases for the gadgets in the circuit."""
        return decode_phases(self._data[:, -PHASE_NBYTES:])

    @phases.setter
    def phases(self, value: PhaseArray | Sequence[SupportsFloat | Fraction]) -> None:
        """Sets phases for the gadgets in the circuit."""
        if not isinstance(value, np.ndarray):
            assert validate(value, Sequence[SupportsFloat | Fraction])
            value = np.array(
                [
                    (
                        float(phase)
                        if isinstance(phase, SupportsFloat)
                        else Gadget.frac2phase(phase)
                    )
                    for phase in value
                ],
                dtype=PHASE_DTYPE,
            )
        assert self.__validate_phases_value(value)
        self._data[:, -PHASE_NBYTES:] = encode_phases(value)

    @property
    def legs(self) -> PauliArray2D:
        """The 2D array of gadget legs for this circuit."""
        return get_circuit_legs(self._data)[:, : self._num_qubits]

    @legs.setter
    def legs(
        self, value: PauliArray2D | Sequence[str | PauliArray | Sequence[int]]
    ) -> None:
        """Sets the legs of the circuit."""
        if isinstance(value, np.ndarray):
            assert self.__validate_legs_value(value)
            set_circuit_legs(self._data, value)
        else:
            assert validate(value, Sequence[Any])
            for idx, line in enumerate(value):
                self[idx].legs = line  # type: ignore

    @property
    def is_zero(self) -> bool:
        """Whether the circuit is all zero (legs set to '_', phases set to 0)."""
        return not np.any(self._data)

    @property
    def listing(self) -> CircuitListing:
        """Returns a listing of the circuit."""
        return CircuitListing(self)

    def clone(self) -> Self:
        """Creates a copy of the gadget circuit."""
        return Circuit(self._data.copy(), self._num_qubits)

    def inverse(self) -> Self:
        """
        Returns the inverse of this graph, with both phases and gadget order inverted.
        """
        inverse = self[::-1].clone()
        inverse.invert_phases()
        return inverse

    def invert_phases(self) -> None:
        """Inverts phases inplace, keeping gadget order unchanged."""
        invert_phases(self._data[:, -PHASE_NBYTES:])

    def commute(self, codes: Sequence[int] | CommutationCodeArray) -> Self:
        """
        Commutes adjacent gadget pairs in the circuit according to the given commutation
        codes.

        See :class:`Gadget.commute_past` for a description of the commutation procedure
        and associated commutation code conventions.
        """
        codes = np.asarray(codes, dtype=np.uint8)
        assert self.__validate_commutation_codes(codes)
        if len(self) == 0:
            return self.clone()
        return Circuit(commute_circuit(self._data, codes), self._num_qubits)

    def unitary(
        self,
        *,
        canonical_phase: bool = True,
        _use_cupy: bool = False,  # currently in alpha
    ) -> Complex128Array2D:
        """Returns the unitary matrix associated to this Pauli gadget circuit."""
        return unitary_from_gadgets(self, self.num_qubits, canonical_phase, _use_cupy)

    def statevec(
        self,
        input: ComplexArray1D | FloatArray1D,
        canonical_phase: bool = True,
        _use_cupy: bool = False,  # currently in alpha
    ) -> Complex128Array1D:
        """
        Computes the statevector resulting from the application of this gadget circuit
        to the given input statevector.
        """
        return statevec_from_gadgets(self, input, canonical_phase, _use_cupy)

    def iter_gadgets(
        self, *, start: int = 0, stop: int | None = None, fast: bool = False
    ) -> Iterable[Gadget]:
        """
        Iterates over the gadgets in the circuit.

        If ``fast`` is set to ``True``, the gadgets yielded are ephemeral:
        they should not be stored, as the same object will be reused in each iteration.
        """
        data = self._data[start:stop]
        if len(data) == 0:
            return
        if not fast:
            for row in data:
                yield Gadget(row, self._num_qubits)
        else:
            g = Gadget(self._data[0], self._num_qubits, _ephemeral=True)
            for row in data:
                g._data = row
                yield g

    def __iter__(self) -> Iterator[Gadget]:
        """
        Iterates over the gadgets in the circuit.

        :meta public:
        """
        for row in self._data:
            yield Gadget(row, self._num_qubits)

    @overload
    def __getitem__(self, idx: SupportsIndex) -> Gadget: ...
    @overload
    def __getitem__(self, idx: slice | list[SupportsIndex]) -> Circuit: ...
    def __getitem__(
        self, idx: SupportsIndex | slice | list[SupportsIndex]
    ) -> Gadget | Circuit:
        """
        Accesses the gadget at a given index, or selects/slices a sub-circuit.

        :meta public:
        """
        if isinstance(idx, SupportsIndex):
            return Gadget(self._data[int(idx)], self._num_qubits)
        assert validate(idx, slice | list[SupportsIndex])
        return Circuit(self._data[idx, :], self._num_qubits)  # type: ignore[index]

    @overload
    def __setitem__(self, idx: SupportsIndex, value: Gadget) -> None: ...
    @overload
    def __setitem__(self, idx: slice | list[SupportsIndex], value: Circuit) -> None: ...
    def __setitem__(
        self,
        idx: SupportsIndex | slice | list[SupportsIndex],
        value: Gadget | Circuit,
    ) -> None:
        """
        Writes a gadget at the given index of this circuit,
        or writes a sub-circuit onto the given selection/slice of this circuit.

        :meta public:
        """
        assert self.__validate_setitem_args(idx, value)
        self._data[idx, :] = value._data  # type: ignore[index]

    def __len__(self) -> int:
        """
        Number of gadgets in the circuit.

        :meta public:
        """
        return len(self._data)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Circuit):
            return NotImplemented
        return (
            self.num_qubits == other.num_qubits
            and self.num_gadgets == other.num_gadgets
            and np.array_equal(self._data[:-PHASE_NBYTES], other._data[:-PHASE_NBYTES])
            and are_same_phases(self.phases, other.phases)
        )

    def __repr__(self) -> str:
        m, n = self.num_gadgets, self.num_qubits
        return f"<Circuit: {m} gadgets, {n} qubits>"

    def __sizeof__(self) -> int:
        return (
            object.__sizeof__(self)
            + self._num_qubits.__sizeof__()
            + self._data.__sizeof__()
        )

    def __bytes__(self) -> bytes:
        """
        Serializes a circuit to bytes:

        - 1B fixed to 0x01, to indicate a :class:`Circuit` encoding
        - 1B encoding the circuit phase dtype (currently, fixed to 0x04 for float64)
        - 8B encoding the number of gadgets, encoded as unsigned big endian
        - 8B encoding the number of qubits, encoded as unsigned big endian
        - the bytes of the underlying data array, using :meth:`numpy.ndarray.tobytes`

        :meta public:
        """
        return b"".join(
            [
                b"\x01",  # 0x01 = Circuit
                b"\x04",  # phase dtype = float64
                self.num_gadgets.to_bytes(8, byteorder="big", signed=False),
                self.num_qubits.to_bytes(8, byteorder="big", signed=False),
                self._data.tobytes(),
            ]
        )

    def to_qiskit(self) -> QiskitQuantumCircuit:
        try:
            from qiskit import QuantumCircuit as QiskitQuantumCircuit
            from qiskit.circuit.library import PauliEvolutionGate as QiskitPauliEvolutionGate  # type: ignore[import-untyped]
            from qiskit.quantum_info import Pauli as QiskitPauli  # type: ignore[import-untyped]
        except ModuleNotFoundError:
            raise ModuleNotFoundError("The 'qiskit' package is not installed.")
        qiskit_circ = QiskitQuantumCircuit(num_qubits := self.num_qubits)
        for g in self:
            gate = QiskitPauliEvolutionGate(
                QiskitPauli(g.leg_paulistr.replace("_", "I")[::-1]), g.phase / 2
            )
            qiskit_circ.append(gate, range(num_qubits))
        return qiskit_circ

    if __debug__:

        @staticmethod
        def __validate_circ_shape(num_gadgets: int, num_qubits: int) -> Literal[True]:
            """Validates the shape of a circuit."""
            validate(num_gadgets, SupportsIndex)
            validate(num_qubits, SupportsIndex)
            num_gadgets = int(num_gadgets)
            num_qubits = int(num_qubits)
            if num_gadgets < 0:
                raise ValueError("Number of gadgets must be non-negative.")
            if num_qubits < 0:
                raise ValueError("Number of qubits must be non-negative.")
            return True

        @staticmethod
        def __validate_new_args(
            data: CircuitData, num_qubits: int | None
        ) -> Literal[True]:
            """Validates the arguments of the :meth:`__new__` method."""
            validate(data, CircuitData)
            if num_qubits is not None:
                validate(num_qubits, SupportsIndex)
                num_qubits = int(num_qubits)
                if num_qubits < 0:
                    raise ValueError("Number of qubits must be non-negative.")
                if num_qubits > data.shape[1] * 4:
                    raise ValueError("Number of qubits exceeds circuit width.")
            return True

        @staticmethod
        def __validate_gadgets(
            gadgets: Sequence[Gadget], num_qubits: int | None
        ) -> Literal[True]:
            validate(gadgets, Sequence[Gadget])
            if num_qubits is None:
                if not gadgets:
                    raise ValueError(
                        "At least one gadget must be supplied if num_qubits is omitted."
                    )
                num_qubits = gadgets[0].num_qubits
            for gadget in gadgets:
                if gadget.num_qubits != num_qubits:
                    raise ValueError("All gadgets must have the same number of qubits.")
            return True

        def __validate_setitem_args(
            self,
            idx: SupportsIndex | slice | list[SupportsIndex],
            value: Gadget | Circuit,
        ) -> Literal[True]:
            """Validates the arguments to the :meth:`__setitem__` method."""
            if isinstance(idx, SupportsIndex):
                validate(value, Gadget)
            else:
                validate(value, Circuit)
                m_lhs = len(self._data[idx])  # type: ignore[index]
                m_rhs = cast(Circuit, value).num_gadgets
                if m_lhs != m_rhs:
                    raise ValueError(
                        "Mismatch in number of gadgets while writing sub-circuit:"
                        f"selection has {m_lhs} gadgets, rhs has {m_rhs}"
                    )
            if self.num_qubits != value.num_qubits:
                raise ValueError(
                    "Mismatch in number of qubits while writing circuit gadgets:"
                    f" lhs has {self.num_qubits} qubits, rhs has {value.num_qubits}."
                )
            return True

        def __validate_phases_value(self, value: PhaseArray) -> Literal[True]:
            """Validates the value of the :attr:`phases` property."""
            validate(value, PhaseArray)
            if len(value) != self.num_gadgets:
                raise ValueError("Number of phases does not match number of gadgets.")
            return True

        def __validate_legs_value(self, legs: PauliArray2D) -> Literal[True]:
            """Validates the value of the :attr:`legs` property."""
            validate(legs, PauliArray2D)
            if legs.shape != (self.num_gadgets, self.num_qubits):
                raise ValueError("Shape of legs does not match shape of circuit.")
            return True

        def __validate_commutation_codes(
            self, codes: CommutationCodeArray
        ) -> Literal[True]:
            """Validates commutation codes passed to :meth:`commute`."""
            if len(codes) != self.num_gadgets // 2:
                raise ValueError(
                    f"Expected {self.num_gadgets//2} communication codes,"
                    f"found {len(codes)} instead."
                )
            if np.any(codes >= 8):
                raise ValueError("Communication codes must be in range(8).")
            return True
