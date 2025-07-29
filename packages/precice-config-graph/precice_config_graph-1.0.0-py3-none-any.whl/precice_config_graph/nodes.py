"""
This graph is intended for the preCICE logical-checker https://github.com/precice-forschungsprojekt/config-checker.

You can find documentation under README.md, docs/Nodes.md and docs/Edges.md.

This graph was developed by Simon Wazynski, Alexander Hutter and Orlando Ackermann as part of https://github.com/precice-forschungsprojekt.
"""

from __future__ import annotations

from enum import Enum


class MappingMethod(Enum):
    NEAREST_NEIGHBOR = "nearest-neighbor"
    NEAREST_PROJECTION = "nearest-projection"
    NEAREST_NEIGHBOR_GRADIENT = "nearest-neighbor-gradient"
    LINEAR_CELL_INTERPOLATION = "linear-cell-interpolation"
    RBF_GLOBAL_ITERATIVE = "rbf-global-iterative"
    RBF_GLOBAL_DIRECT = "rbf-global-direct"
    RBF_PUM_DIRECT = "rbf-pum-direct"
    RBF = "rbf"
    AXIAL_GEOMETRIC_MULTISCALE = "axial-geometric-multiscale"
    RADIAL_GEOMETRIC_MULTISCALE = "radial-geometric-multiscale"


class MappingConstraint(Enum):
    CONSERVATIVE = "conservative"
    CONSISTENT = "consistent"
    SCALED_CONSISTENT_SURFACE = "scaled-consistent-surface"
    SCALED_CONSISTENT_VOLUME = "scaled-consistent-volume"


class M2NType(Enum):
    SOCKETS = "sockets"
    MPI = "mpi"
    MPI_MULTIPLE_PORTS = "mpi-multiple-ports"


class Direction(Enum):
    READ = "read"
    WRITE = "write"


class DataType(Enum):
    SCALAR = "scalar"
    VECTOR = "vector"


class TimingType(Enum):
    WRITE_MAPPING_POST = "write-mapping-post"
    READ_MAPPING_POST = "read-mapping-post"


class CouplingSchemeType(Enum):
    SERIAL_EXPLICIT = "serial-explicit"
    PARALLEL_EXPLICIT = "parallel-explicit"
    SERIAL_IMPLICIT = "serial-implicit"
    PARALLEL_IMPLICIT = "parallel-implicit"
    # This enum does not include coupling-scheme:multi, since it is modeled with a different node type


class ActionType(Enum):
    MULTIPLY_BY_AREA = "multiply-by-area"
    DIVIDE_BY_AREA = "divide-by-area"
    SUMMATION = "summation"
    PYTHON = "python"
    RECORDER = "recorder"


class ExportFormat(Enum):
    VTK = "vtk"
    VTU = "vtu"
    VTP = "vtp"
    CSV = "csv"


class AccelerationType(Enum):
    AITKEN = "aitken"
    IQN_ILS = "IQN-ILS"
    IQN_IMVJ = "IQN-IMVJ"
    CONSTANT = "constant"


class ConvergenceMeasureType(Enum):
    ABSOLUTE = "absolute"
    ABSOLUTE_OR_RELATIVE = "absolute-or-relative"
    RELATIVE = "relative"
    RESIDUAL_RELATIVE = "residual-relative"


class ParticipantNode:
    def __init__(
        self,
        name: str,
        write_data: list[WriteDataNode] = None,
        read_data: list[ReadDataNode] = None,
        receive_meshes: list[ReceiveMeshNode] = None,
        provide_meshes: list[MeshNode] = None,
        mappings: list[MappingNode] = None,
        exports: list[ExportNode] = None,
        actions: list[ActionNode] = None,
        watchpoints: list[WatchPointNode] = None,
        watch_integrals: list[WatchIntegralNode] = None,
        line: int = None,
    ):
        self.name = name

        if write_data is None:
            self.write_data = []
        else:
            self.write_data = write_data

        if read_data is None:
            self.read_data = []
        else:
            self.read_data = read_data

        if receive_meshes is None:
            self.receive_meshes = []
        else:
            self.receive_meshes = receive_meshes

        if provide_meshes is None:
            self.provide_meshes = []
        else:
            self.provide_meshes = provide_meshes

        if mappings is None:
            self.mappings = []
        else:
            self.mappings = mappings

        if exports is None:
            self.exports = []
        else:
            self.exports = exports

        if actions is None:
            self.actions = []
        else:
            self.actions = actions

        if watchpoints is None:
            self.watchpoints = []
        else:
            self.watchpoints = watchpoints

        if watch_integrals is None:
            self.watch_integrals = []
        else:
            self.watch_integrals = watch_integrals

        self.line = line


class MeshNode:
    def __init__(self, name: str, use_data: list[DataNode] = None, line: int = None):
        self.name = name

        if use_data is None:
            self.use_data = []
        else:
            self.use_data = use_data

        self.line = line


class ReceiveMeshNode:
    def __init__(
        self,
        participant: ParticipantNode,
        mesh: MeshNode,
        from_participant: ParticipantNode,
        api_access: bool,
        line: int = None,
    ):
        self.participant = participant
        self.mesh = mesh
        self.from_participant = from_participant
        self.api_access = api_access
        self.line = line


class CouplingSchemeNode:
    def __init__(
        self,
        type: CouplingSchemeType,
        first_participant: ParticipantNode,
        second_participant: ParticipantNode,
        exchanges: list[ExchangeNode] = None,
        accelerations: list[AccelerationNode] = None,
        convergence_measures: list[ConvergenceMeasureNode] = None,
        line: int = None,
    ):
        self.type = type
        self.first_participant = first_participant
        self.second_participant = second_participant

        if exchanges is None:
            self.exchanges = []
        else:
            self.exchanges = exchanges

        if accelerations is None:
            self.accelerations = []
        else:
            self.accelerations = accelerations

        if convergence_measures is None:
            self.convergence_measures = []
        else:
            self.convergence_measures = convergence_measures

        self.line = line


class MultiCouplingSchemeNode:
    def __init__(
        self,
        control_participant: ParticipantNode,
        participants: list[ParticipantNode] = None,
        exchanges: list[ExchangeNode] = None,
        accelerations: list[AccelerationNode] = None,
        convergence_measures: list[ConvergenceMeasureNode] = None,
        line: int = None,
    ):
        self.control_participant = control_participant

        if participants is None:
            self.participants = []
        else:
            self.participants = participants

        if exchanges is None:
            self.exchanges = []
        else:
            self.exchanges = exchanges

        if accelerations is None:
            self.accelerations = []
        else:
            self.accelerations = accelerations

        if convergence_measures is None:
            self.convergence_measures = []
        else:
            self.convergence_measures = convergence_measures

        self.line = line


class DataNode:
    def __init__(self, name: str, data_type: DataType, line: int = None):
        self.name = name
        self.data_type = data_type
        self.line = line


class MappingNode:
    def __init__(
        self,
        parent_participant: ParticipantNode,
        direction: Direction,
        just_in_time: bool,
        method: MappingMethod,
        constraint: MappingConstraint,
        from_mesh: MeshNode | None = None,
        to_mesh: MeshNode | None = None,
        line: int = None,
    ):
        self.parent_participant = parent_participant
        self.direction = direction
        self.just_in_time = just_in_time
        self.method = method
        self.constraint = constraint
        self.from_mesh = from_mesh
        self.to_mesh = to_mesh
        self.line = line


class WriteDataNode:
    def __init__(
        self,
        participant: ParticipantNode,
        data: DataNode,
        mesh: MeshNode,
        line: int = None,
    ):
        self.participant = participant
        self.data = data
        self.mesh = mesh
        self.line = line


class ReadDataNode:
    def __init__(
        self,
        participant: ParticipantNode,
        data: DataNode,
        mesh: MeshNode,
        line: int = None,
    ):
        self.participant = participant
        self.data = data
        self.mesh = mesh
        self.line = line


class ExchangeNode:
    def __init__(
        self,
        coupling_scheme: CouplingSchemeNode | MultiCouplingSchemeNode,
        data: DataNode,
        mesh: MeshNode,
        from_participant: ParticipantNode,
        to_participant: ParticipantNode,
        line: int = None,
    ):
        self.coupling_scheme = coupling_scheme
        self.data = data
        self.mesh = mesh
        self.from_participant = from_participant
        self.to_participant = to_participant
        self.line = line


class ExportNode:
    def __init__(
        self, participant: ParticipantNode, format: ExportFormat, line: int = None
    ):
        self.participant = participant
        self.format = format
        self.line = line


class ActionNode:
    def __init__(
        self,
        participant: ParticipantNode,
        type: ActionType,
        mesh: MeshNode,
        timing: TimingType,
        target_data: DataNode | None = None,
        source_data: list[DataNode] = None,
        line: int = None,
    ):
        self.participant = participant
        self.type = type
        self.mesh = mesh
        self.timing = timing
        self.target_data = target_data

        if source_data is None:
            self.source_data = []
        else:
            self.source_data = source_data

        self.line = line


class WatchPointNode:
    def __init__(
        self, name: str, participant: ParticipantNode, mesh: MeshNode, line: int = None
    ):
        self.name = name
        self.participant = participant
        self.mesh = mesh
        self.line = line


class WatchIntegralNode:
    def __init__(
        self, name: str, participant: ParticipantNode, mesh: MeshNode, line: int = None
    ):
        self.name = name
        self.participant = participant
        self.mesh = mesh
        self.line = line


class M2NNode:
    def __init__(
        self,
        type: M2NType,
        acceptor: ParticipantNode,
        connector: ParticipantNode,
        line: int = None,
    ):
        self.type = type
        self.acceptor = acceptor
        self.connector = connector
        self.line = line


class AccelerationDataNode:
    def __init__(
        self,
        acceleration: AccelerationNode,
        data: DataNode,
        mesh: MeshNode,
        line: int = None,
    ):
        self.acceleration = acceleration
        self.data = data
        self.mesh = mesh
        self.line = line


class AccelerationNode:
    def __init__(
        self,
        coupling_scheme: CouplingSchemeNode | MultiCouplingSchemeNode,
        type: AccelerationType,
        data: list[AccelerationDataNode] = None,
        line: int = None,
    ):
        self.coupling_scheme = coupling_scheme
        self.type = type

        if data is None:
            self.data = []
        else:
            self.data = data

        self.line = line


class ConvergenceMeasureNode:
    def __init__(
        self,
        coupling_scheme: CouplingSchemeNode | MultiCouplingSchemeNode,
        type: ConvergenceMeasureType,
        data: DataNode,
        mesh: MeshNode,
        line: int = None,
    ):
        self.type = type
        self.coupling_scheme = coupling_scheme
        self.data = data
        self.mesh = mesh
        self.line = line
