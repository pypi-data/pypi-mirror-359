"""
This graph is intended for the preCICE logical-checker https://github.com/precice-forschungsprojekt/config-checker.

You can find documentation under README.md, docs/Nodes.md and docs/Edges.md.

This graph was developed by Simon Wazynski, Alexander Hutter and Orlando Ackermann as part of https://github.com/precice-forschungsprojekt.
"""

import sys
from enum import Enum
import matplotlib.pyplot as plt
import networkx as nx
from lxml import etree

from . import nodes as n
from .edges import Edge
from .xml_processing import convert_string_to_bool

LINK_GRAPH_ISSUES: str = "'\033[1;36mhttps://github.com/precice-forschungsprojekt/config-graph/issues\033[0m'"


def get_graph(root: etree.Element) -> nx.Graph:
    assert root.tag == "precice-configuration"

    # Taken from config-visualizer. Modified to also return postfix.
    def find_all_with_prefix(e: etree.Element, prefix: str):
        for child in e.iterchildren():
            if child.tag.startswith(prefix):
                postfix = child.tag[child.tag.find(":") + 1 :]
                yield child, postfix

    def find_all_with_postfix(e: etree.Element, postfix: str):
        for child in e.iterchildren():
            if child.tag.endswith(postfix):
                prefix: str = child.tag.removesuffix(postfix)
                yield child, prefix

    def error(message: str):
        sys.exit(
            "\033[1;31m[ERROR]\033[0m Exiting graph generation."
            + "\n"
            + message
            + "\nPlease run 'precice-tools check' for syntax errors."
            + "\n\nIf you are sure this behaviour is incorrect, please leave a report at "
            + LINK_GRAPH_ISSUES
        )

    def error_missing_attribute(e: etree.Element, key: str):
        message: str = 'Missing attribute "' + key + '" for element "' + e.tag + '".'
        error(message)

    def get_enum_values(enum: Enum) -> list:
        return list(map(lambda x: x.value, enum._member_map_.values()))

    def list_to_string(values: list) -> str:
        string: str = ""
        size = len(values)
        for i in range(size - 2):
            string += f'"{values[i]}", '
        string += f'"{values[size-2]}" or "{values[size-1]}".'
        return string

    def error_unknown_type(e: etree.Element, type: str, possible_types_list: list):
        possible_types = list_to_string(possible_types_list)
        message: str = (
            'Unknown type "'
            + type
            + '" for element "'
            + e.tag
            + '".\nUse one of '
            + possible_types
        )
        error(message)

    def get_attribute(e: etree.Element, key: str):
        attribute = e.get(key)
        if not attribute:
            error_missing_attribute(e, key)
        return attribute

    # FIND NODES

    # Keep track of these types of nodes, since we cannot construct them on demand when referenced,
    # since the reference does not contain relevant data.
    data_nodes: dict[str, n.DataNode] = {}
    mesh_nodes: dict[str, n.MeshNode] = {}
    participant_nodes: dict[str, n.ParticipantNode] = {}
    write_data_nodes: list[n.WriteDataNode] = []
    read_data_nodes: list[n.ReadDataNode] = []
    receive_mesh_nodes: list[n.ReceiveMeshNode] = []
    coupling_nodes: list[n.CouplingSchemeNode] = []
    multi_coupling_nodes: list[n.MultiCouplingSchemeNode] = []
    mapping_nodes: list[n.MappingNode] = []
    export_nodes: list[n.ExportNode] = []
    exchange_nodes: list[n.ExchangeNode] = []
    acceleration_nodes: list[n.AccelerationNode] = []
    acceleration_data_nodes: list[n.AccelerationDataNode] = []
    convergence_measure_nodes: list[n.ConvergenceMeasureNode] = []
    action_nodes: list[n.ActionNode] = []
    m2n_nodes: list[n.M2NNode] = []
    watch_point_nodes: list[n.WatchPointNode] = []
    watch_integral_nodes: list[n.WatchIntegralNode] = []

    # Data items – <data:… />
    for (data_el, kind) in find_all_with_prefix(root, "data"):
        name = get_attribute(data_el, "name")
        try:
            type = n.DataType(kind)
        except ValueError:
            possible_types_list = get_enum_values(n.DataType)
            error_unknown_type(data_el, kind, possible_types_list)
        line: int = data_el.sourceline
        node = n.DataNode(name, type, line)
        data_nodes[name] = node

    # Meshes – <mesh />
    for mesh_el in root.findall("mesh"):
        name = get_attribute(mesh_el, "name")
        line: int = mesh_el.sourceline
        mesh = n.MeshNode(name, line=line)

        # Data usages – <use-data />: Will be mapped to edges
        for use_data in mesh_el.findall("use-data"):
            data_name = get_attribute(use_data, "name")
            data_node = data_nodes[data_name]
            mesh.use_data.append(data_node)

        # Now that mesh_node is completely built, add it to our dictionary
        mesh_nodes[name] = mesh

    # Participants – <participant />
    for participant_el in root.findall("participant"):
        name = get_attribute(participant_el, "name")
        line: int = participant_el.sourceline
        participant = n.ParticipantNode(name, line=line)

        # Provide- and Receive-Mesh
        # <provide-mesh />
        for provide_mesh_el in participant_el.findall("provide-mesh"):
            mesh_name = get_attribute(provide_mesh_el, "name")
            participant.provide_meshes.append(mesh_nodes[mesh_name])

        # Read and write data
        # <write-data />
        for write_data_el in participant_el.findall("write-data"):
            data_name = get_attribute(write_data_el, "name")
            data = data_nodes[data_name]
            mesh_name = get_attribute(write_data_el, "mesh")
            mesh = mesh_nodes[mesh_name]
            line: int = write_data_el.sourceline

            write_data = n.WriteDataNode(participant, data, mesh, line)
            participant.write_data.append(write_data)
            write_data_nodes.append(write_data)

        # <read-data />
        # TODO: Refactor to reduce code duplication
        for read_data_el in participant_el.findall("read-data"):
            data_name = get_attribute(read_data_el, "name")
            data = data_nodes[data_name]
            mesh_name = get_attribute(read_data_el, "mesh")
            mesh = mesh_nodes[mesh_name]
            line: int = read_data_el.sourceline

            read_data = n.ReadDataNode(participant, data, mesh, line)
            participant.read_data.append(read_data)
            read_data_nodes.append(read_data)

        # Mapping
        for (mapping_el, kind) in find_all_with_prefix(participant_el, "mapping"):
            direction = get_attribute(mapping_el, "direction")
            # From mesh might not exist due to just-in-time mapping
            from_mesh_name = mapping_el.get("from")
            from_mesh = mesh_nodes[from_mesh_name] if from_mesh_name else None
            # From mesh might not exist due to just-in-time mapping
            to_mesh_name = mapping_el.get("to")
            to_mesh = mesh_nodes[to_mesh_name] if to_mesh_name else None

            try:
                method = n.MappingMethod(kind)
            except ValueError:
                possible_method_list = get_enum_values(n.MappingMethod)
                possible_methods: str = list_to_string(possible_method_list)
                message: str = (
                    'Unknown method "'
                    + kind
                    + '" for element "'
                    + mapping_el.tag
                    + '".\nUse one of '
                    + possible_methods
                )
                error(message)
            constraint = n.MappingConstraint(get_attribute(mapping_el, "constraint"))

            if not from_mesh and not to_mesh:
                error_missing_attribute(mapping_el, 'from" or "to')
            just_in_time = not (from_mesh and to_mesh)
            line: int = mapping_el.sourceline

            mapping = n.MappingNode(
                participant,
                n.Direction(direction),
                just_in_time,
                method,
                constraint,
                from_mesh,
                to_mesh,
                line,
            )

            participant.mappings.append(mapping)
            mapping_nodes.append(mapping)

        # Exports
        # <export:… />
        for (_, kind) in find_all_with_prefix(participant_el, "export"):
            try:
                type = n.ExportFormat(kind)
            except ValueError:
                possible_types_list = get_enum_values(n.ExportFormat)
                error_unknown_type(_, kind, possible_types_list)
            line: int = _.sourceline
            export = n.ExportNode(participant, type, line)
            export_nodes.append(export)

        # Actions
        # <action:… />
        for (action_el, kind) in find_all_with_prefix(participant_el, "action"):
            mesh = mesh_nodes[get_attribute(action_el, "mesh")]
            timing = n.TimingType(get_attribute(action_el, "timing"))

            target_data = None
            if kind in ["multiply-by-area", "divide-by-area", "summation", "python"]:
                target_data_el = action_el.find("target-data")
                if target_data_el is not None:
                    target_data = data_nodes[get_attribute(target_data_el, "name")]

            source_data: list[n.DataNode] = []
            if kind in ["summation", "python"]:
                source_data_els = action_el.findall("source-data")
                for source_data_el in source_data_els:
                    source_data.append(
                        data_nodes[get_attribute(source_data_el, "name")]
                    )

            try:
                type = n.ActionType(kind)
            except ValueError:
                possible_types_list = get_enum_values(n.ActionType)
                error_unknown_type(action_el, kind, possible_types_list)
            line: int = action_el.sourceline

            action = n.ActionNode(
                participant, type, mesh, timing, target_data, source_data, line
            )
            action_nodes.append(action)

        # Watch-Points
        # <watch-point />
        for watch_point_el in participant_el.findall("watch-point"):
            point_name = get_attribute(watch_point_el, "name")
            mesh = mesh_nodes[get_attribute(watch_point_el, "mesh")]
            line: int = watch_point_el.sourceline

            watch_point = n.WatchPointNode(point_name, participant, mesh, line)
            watch_point_nodes.append(watch_point)

        # Watch-Integral
        # <watch-integral />
        for watch_integral_el in participant_el.findall("watch-integral"):
            integral_name = get_attribute(watch_integral_el, "name")
            mesh = mesh_nodes[get_attribute(watch_integral_el, "mesh")]
            line: int = watch_integral_el.sourceline

            watch_integral = n.WatchIntegralNode(integral_name, participant, mesh, line)
            watch_integral_nodes.append(watch_integral)

        # Now that participant_node is completely built, add it and children to the graph and our dictionary
        participant_nodes[name] = participant

    # Receive Mesh Participants
    # This can't be done in the participants loop, since it references participants which might not yet be created
    # <participant />
    for participant_el in root.findall("participant"):
        name = get_attribute(participant_el, "name")
        participant = participant_nodes[
            name
        ]  # This should not fail, because we created participants before

        # <receive-mesh />
        for receive_mesh_el in participant_el.findall("receive-mesh"):
            mesh_name = get_attribute(receive_mesh_el, "name")
            mesh = mesh_nodes[mesh_name]

            from_participant_name = get_attribute(receive_mesh_el, "from")
            from_participant = participant_nodes[from_participant_name]

            api_access_str = receive_mesh_el.get("api-access")
            if api_access_str:
                api_access = convert_string_to_bool(api_access_str)
            else:
                api_access = False
            line: int = receive_mesh_el.sourceline

            receive_mesh = n.ReceiveMeshNode(
                participant, mesh, from_participant, api_access, line
            )
            participant.receive_meshes.append(receive_mesh)
            receive_mesh_nodes.append(receive_mesh)

    # Coupling Scheme – <coupling-scheme:… />
    for (coupling_scheme_el, kind) in find_all_with_prefix(root, "coupling-scheme"):
        coupling_scheme = None
        line: int = coupling_scheme_el.sourceline
        match kind:
            case "serial-explicit" | "serial-implicit" | "parallel-explicit" | "parallel-implicit":
                # <participants />
                participants_list = coupling_scheme_el.findall("participants")
                if len(participants_list) > 1:
                    message: str = (
                        "Multiple 'participants' tags in '"
                        + coupling_scheme_el.tag
                        + "'"
                    )
                    error(message)
                elif len(participants_list) < 1:
                    error_missing_attribute(coupling_scheme_el, "participants")
                participants = participants_list[0]
                first_participant_name = get_attribute(participants, "first")
                first_participant = participant_nodes[first_participant_name]
                second_participant_name = get_attribute(participants, "second")
                second_participant = participant_nodes[second_participant_name]

                type = n.CouplingSchemeType(kind)

                coupling_scheme = n.CouplingSchemeNode(
                    type, first_participant, second_participant, line=line
                )
            case "multi":
                control_participant = None
                participants = []
                # <participant name="..." />
                for participant_el in coupling_scheme_el.findall("participant"):
                    name = get_attribute(participant_el, "name")
                    participant = participant_nodes[name]
                    participants.append(participant)

                    control = (
                        "control" in participant_el.attrib
                        and convert_string_to_bool(participant_el.get("control"))
                    )
                    if control:
                        assert (
                            control_participant is None
                        )  # there must not be multiple control participants
                        control_participant = participant

                assert (
                    control_participant is not None
                ), "There must be a control participant"

                coupling_scheme = n.MultiCouplingSchemeNode(
                    control_participant, participants, line=line
                )
            case _:
                possible_types_list = [
                    "serial-explicit",
                    "serial-implicit",
                    "parallel-explicit",
                    "parallel-implicit",
                    "multi",
                ]
                error_unknown_type(coupling_scheme_el, kind, possible_types_list)

        assert (
            coupling_scheme is not None
        )  # there must always be one participant that is in control

        # Exchanges – <exchange />
        for exchange_el in coupling_scheme_el.findall("exchange"):
            data_name = get_attribute(exchange_el, "data")
            data = data_nodes[data_name]
            mesh_name = get_attribute(exchange_el, "mesh")
            mesh = mesh_nodes[mesh_name]
            from_participant_name = get_attribute(exchange_el, "from")
            from_participant = participant_nodes[from_participant_name]
            to_participant_name = get_attribute(exchange_el, "to")
            to_participant = participant_nodes[to_participant_name]
            line: int = exchange_el.sourceline

            exchange = n.ExchangeNode(
                coupling_scheme, data, mesh, from_participant, to_participant, line
            )
            coupling_scheme.exchanges.append(exchange)
            exchange_nodes.append(exchange)

        for (acceleration_el, a_kind) in find_all_with_prefix(
            coupling_scheme_el, "acceleration"
        ):
            if kind in ["serial-explicit", "parallel-explicit"]:
                possible_types = list_to_string(
                    ["serial-implicit", "parallel-implicit", "multi"]
                )
                message: str = (
                    f"The coupling scheme of type '{kind}' does not support acceleration.\nUse one of "
                    + possible_types
                    + "\nOtherwise remove the acceleration tag."
                )
                error(message)

            try:
                type = n.AccelerationType(a_kind)
            except ValueError:
                possible_types_list = get_enum_values(n.AccelerationType)
                error_unknown_type(acceleration_el, a_kind, possible_types_list)
            line: int = acceleration_el.sourceline

            acceleration = n.AccelerationNode(coupling_scheme, type, line=line)

            possible_types_list = ["aitken", "IQN-ILS", "IQN-IMVJ"]

            if a_kind == "constant" and acceleration_el.find("data"):
                possible_types: str = list_to_string(possible_types_list)
                message: str = (
                    "No data tag is expected for 'constant' acceleration.\nUse one of "
                    + possible_types
                    + "\nOtherwise remove the acceleration tag."
                )
                error(message)

            if a_kind in possible_types_list:
                for a_data in acceleration_el.findall("data"):
                    a_data_name = get_attribute(a_data, "name")
                    data = data_nodes[a_data_name]
                    a_mesh_name = get_attribute(a_data, "mesh")
                    mesh = mesh_nodes[a_mesh_name]
                    line: int = a_data.sourceline
                    a_data_node = n.AccelerationDataNode(acceleration, data, mesh, line)
                    acceleration.data.append(a_data_node)
                    acceleration_data_nodes.append(a_data_node)

            coupling_scheme.accelerations.append(acceleration)
            acceleration_nodes.append(acceleration)

        for (convergence_measure_el, c_kind) in find_all_with_postfix(
            coupling_scheme_el, "-convergence-measure"
        ):
            match kind:
                case "serial-implicit" | "parallel-implicit" | "multi":
                    try:
                        type = n.ConvergenceMeasureType(c_kind)
                    except ValueError:
                        possible_types_list = get_enum_values(n.ConvergenceMeasureType)
                        error_unknown_type(
                            convergence_measure_el, c_kind, possible_types_list
                        )

                    c_data_name = get_attribute(convergence_measure_el, "data")
                    c_data = data_nodes[c_data_name]
                    c_mesh_name = get_attribute(convergence_measure_el, "mesh")
                    c_mesh = mesh_nodes[c_mesh_name]
                    line: int = convergence_measure_el.sourceline

                    convergence_measure = n.ConvergenceMeasureNode(
                        coupling_scheme, type, c_data, c_mesh, line
                    )
                    coupling_scheme.convergence_measures.append(convergence_measure)
                    convergence_measure_nodes.append(convergence_measure)

                case "parallel-explicit" | "serial-explicit":
                    possible_types: str = list_to_string(
                        ["serial-implicit", "parallel-implicit", "multi"]
                    )
                    message: str = (
                        f"The coupling scheme of type '{kind}' does not support convergence-measure.\nUse one of "
                        + possible_types
                        + f"\nOtherwise remove the {c_kind}-convergence-measure tag."
                    )
                    error(message)

        match kind:
            case "serial-explicit" | "serial-implicit" | "parallel-explicit" | "parallel-implicit":
                coupling_nodes.append(coupling_scheme)
            case "multi":
                multi_coupling_nodes.append(coupling_scheme)

    # M2N – <m2n:… />
    for (m2n_el, kind) in find_all_with_prefix(root, "m2n"):
        try:
            type = n.M2NType(kind)
        except ValueError:
            possible_types_list = get_enum_values(n.M2NType)
            error_unknown_type(m2n_el, kind, possible_types_list)
        acceptor_name = get_attribute(m2n_el, "acceptor")
        acceptor = participant_nodes[acceptor_name]
        connector_name = get_attribute(m2n_el, "connector")
        connector = participant_nodes[connector_name]
        line: int = m2n_el.sourceline

        m2n = n.M2NNode(type, acceptor, connector, line)
        m2n_nodes.append(m2n)

    # BUILD GRAPH
    # from found nodes and inferred edges

    # Use an undirected graph
    g = nx.Graph()

    for data in data_nodes.values():
        g.add_node(data)

    for mesh in mesh_nodes.values():
        g.add_node(mesh)
        for data in mesh.use_data:
            g.add_edge(data, mesh, attr=Edge.USE_DATA)

    for participant in participant_nodes.values():
        g.add_node(participant)
        for mesh in participant.provide_meshes:
            g.add_edge(participant, mesh, attr=Edge.PROVIDE_MESH__PARTICIPANT_PROVIDES)
        # Use data and write data, as well as receive mesh nodes are added later

    for read_data in read_data_nodes:
        g.add_node(read_data)
        g.add_edge(read_data, read_data.data, attr=Edge.READ_DATA__DATA_READ_BY)
        g.add_edge(read_data, read_data.mesh, attr=Edge.READ_DATA__MESH_READ_BY)
        g.add_edge(
            read_data,
            read_data.participant,
            attr=Edge.READ_DATA__PARTICIPANT__BELONGS_TO,
        )

    for write_data in write_data_nodes:
        g.add_node(write_data)
        g.add_edge(write_data, write_data.data, attr=Edge.WRITE_DATA__WRITES_TO_DATA)
        g.add_edge(write_data, write_data.mesh, attr=Edge.WRITE_DATA__WRITES_TO_MESH)
        g.add_edge(
            write_data,
            write_data.participant,
            attr=Edge.WRITE_DATA__PARTICIPANT__BELONGS_TO,
        )

    for receive_mesh in receive_mesh_nodes:
        g.add_node(receive_mesh)
        g.add_edge(receive_mesh, receive_mesh.mesh, attr=Edge.RECEIVE_MESH__MESH)
        g.add_edge(
            receive_mesh,
            receive_mesh.from_participant,
            attr=Edge.RECEIVE_MESH__PARTICIPANT_RECEIVED_FROM,
        )
        g.add_edge(
            receive_mesh,
            receive_mesh.participant,
            attr=Edge.RECEIVE_MESH__PARTICIPANT__BELONGS_TO,
        )

    for mapping in mapping_nodes:
        g.add_node(mapping)
        if mapping.from_mesh:
            g.add_edge(mapping, mapping.from_mesh, attr=Edge.MAPPING__FROM_MESH)
        if mapping.to_mesh:
            g.add_edge(mapping, mapping.to_mesh, attr=Edge.MAPPING__TO_MESH)
        g.add_edge(
            mapping,
            mapping.parent_participant,
            attr=Edge.MAPPING__PARTICIPANT__BELONGS_TO,
        )

    for export in export_nodes:
        g.add_node(export)
        g.add_edge(
            export, export.participant, attr=Edge.EXPORT__PARTICIPANT__BELONGS_TO
        )

    for action in action_nodes:
        g.add_node(action)
        g.add_edge(
            action, action.participant, attr=Edge.ACTION__PARTICIPANT__BELONGS_TO
        )
        g.add_edge(action, action.mesh, attr=Edge.ACTION__MESH)
        if action.target_data is not None:
            g.add_edge(action, action.target_data, attr=Edge.ACTION__TARGET_DATA)
        for source_data in action.source_data:
            g.add_edge(action, source_data, attr=Edge.ACTION__SOURCE_DATA)

    for watch_point in watch_point_nodes:
        g.add_node(watch_point)
        g.add_edge(
            watch_point,
            watch_point.participant,
            attr=Edge.WATCH_POINT__PARTICIPANT__BELONGS_TO,
        )
        g.add_edge(watch_point, watch_point.mesh, attr=Edge.WATCH_POINT__MESH)

    for watch_integral in watch_integral_nodes:
        g.add_node(watch_integral)
        g.add_edge(
            watch_integral,
            watch_integral.participant,
            attr=Edge.WATCH_INTEGRAL__PARTICIPANT__BELONGS_TO,
        )
        g.add_edge(watch_integral, watch_integral.mesh, attr=Edge.WATCH_INTEGRAL__MESH)

    for coupling in coupling_nodes:
        g.add_node(coupling)
        # Edges to and from exchanges will be added by exchange nodes
        g.add_edge(
            coupling,
            coupling.first_participant,
            attr=Edge.COUPLING_SCHEME__PARTICIPANT_FIRST,
        )
        g.add_edge(
            coupling,
            coupling.second_participant,
            attr=Edge.COUPLING_SCHEME__PARTICIPANT_SECOND,
        )

    for coupling in multi_coupling_nodes:
        g.add_node(coupling)
        for participant in coupling.participants:
            g.add_edge(
                coupling, participant, attr=Edge.MULTI_COUPLING_SCHEME__PARTICIPANT
            )
        # Previous, “regular” multi-coupling scheme participant edge, gets overwritten
        g.add_edge(
            coupling,
            coupling.control_participant,
            attr=Edge.MULTI_COUPLING_SCHEME__PARTICIPANT__CONTROL,
        )

    for exchange in exchange_nodes:
        g.add_node(exchange)
        g.add_edge(
            exchange, exchange.from_participant, attr=Edge.EXCHANGE__EXCHANGED_FROM
        )
        g.add_edge(exchange, exchange.to_participant, attr=Edge.EXCHANGE__EXCHANGES_TO)
        g.add_edge(exchange, exchange.data, attr=Edge.EXCHANGE__DATA)
        g.add_edge(exchange, exchange.mesh, attr=Edge.EXCHANGE__MESH)
        g.add_edge(
            exchange,
            exchange.coupling_scheme,
            attr=Edge.EXCHANGE__COUPLING_SCHEME__BELONGS_TO,
        )

    for acceleration in acceleration_nodes:
        g.add_node(acceleration)
        g.add_edge(
            acceleration,
            acceleration.coupling_scheme,
            attr=Edge.ACCELERATION__COUPLING_SCHEME__BELONGS_TO,
        )

    for acceleration_data in acceleration_data_nodes:
        g.add_node(acceleration_data)
        g.add_edge(
            acceleration_data,
            acceleration_data.acceleration,
            attr=Edge.ACCELERATION_DATA__ACCELERATION__BELONGS_TO,
        )
        g.add_edge(
            acceleration_data, acceleration_data.data, attr=Edge.ACCELERATION_DATA__DATA
        )
        g.add_edge(
            acceleration_data, acceleration_data.mesh, attr=Edge.ACCELERATION_DATA__MESH
        )

    for convergence_measure in convergence_measure_nodes:
        g.add_node(convergence_measure)
        g.add_edge(
            convergence_measure,
            convergence_measure.coupling_scheme,
            attr=Edge.CONVERGENCE_MEASURE__COUPLING_SCHEME__BELONGS_TO,
        )
        g.add_edge(
            convergence_measure,
            convergence_measure.data,
            attr=Edge.CONVERGENCE_MEASURE__DATA,
        )
        g.add_edge(
            convergence_measure,
            convergence_measure.mesh,
            attr=Edge.CONVERGENCE_MEASURE__MESH,
        )

    for m2n in m2n_nodes:
        g.add_node(m2n)
        g.add_edge(m2n, m2n.acceptor, attr=Edge.M2N__PARTICIPANT_ACCEPTOR)
        g.add_edge(m2n, m2n.connector, attr=Edge.M2N__PARTICIPANT_CONNECTOR)

    return g


def print_graph(graph: nx.Graph):
    SIZE = 300

    def color_for_node(node):
        match node:
            case n.DataNode():
                return [1, 0.3, 0]
            case n.ReadDataNode() | n.WriteDataNode():
                return [1, 0.5, 0.5]
            case n.MeshNode():
                return [0.9, 0.6, 0]
            case n.ReceiveMeshNode():
                return [0.95, 0.75, 0]
            case n.ParticipantNode():
                return [0.3, 0.6, 1.0]
            case n.ExchangeNode():
                return [0.8, 0.8, 0.8]
            case n.CouplingSchemeNode() | n.MultiCouplingSchemeNode():
                return [0.65, 0.65, 0.65]
            case n.WriteDataNode():
                return [0.7, 0, 1.0]
            case n.MappingNode():
                return [0.1, 0.7, 0.1]
            case n.ExportNode():
                return [0.5, 0.8, 1.0]
            case n.ActionNode():
                return [0.3, 0.5, 0.8]
            case n.WatchPointNode() | n.WatchIntegralNode():
                return [0.5, 0.0, 1.0]
            case _:
                return [0.5, 0.5, 0.5]

    def append_list(list, node, color, size=SIZE):
        list[2].append(node)
        list[3].append(color)
        list[4].append(size * list[1])

    nodes_circle = ["o", 1, [], [], []]
    nodes_circle_small = [".", 1, [], [], []]
    nodes_triangle_up = ["^", 1, [], [], []]
    nodes_triangle_down = ["v", 1, [], [], []]
    nodes_triangle_left = ["<", 1, [], [], []]
    nodes_triangle_right = [">", 1, [], [], []]
    nodes_square = ["s", 0.9, [], [], []]
    nodes_diamond = ["d", 0.9, [], [], []]
    nodes_diamond_wide = ["D", 0.8, [], [], []]
    nodes_pentagon = ["p", 1.4, [], [], []]
    nodes_hexagon_vertical = ["h", 1.4, [], [], []]
    nodes_hexagon_horizontal = ["H", 1.4, [], [], []]
    nodes_octagon = ["8", 1.2, [], [], []]
    nodes_plus = ["P", 1.1, [], [], []]
    nodes_cross = ["X", 1, [], [], []]
    nodes_star = ["*", 1.5, [], [], []]
    node_lists = [
        nodes_circle,
        nodes_circle_small,
        nodes_triangle_up,
        nodes_triangle_down,
        nodes_triangle_left,
        nodes_triangle_right,
        nodes_square,
        nodes_diamond,
        nodes_diamond_wide,
        nodes_pentagon,
        nodes_hexagon_vertical,
        nodes_hexagon_horizontal,
        nodes_octagon,
        nodes_plus,
        nodes_cross,
        nodes_star,
    ]

    for node in graph.nodes():
        color = color_for_node(node)
        match node:
            case n.ParticipantNode():
                append_list(nodes_star, node, color)
            case n.MeshNode():
                append_list(nodes_square, node, color)
            case n.CouplingSchemeNode() | n.MultiCouplingSchemeNode():
                append_list(nodes_octagon, node, color)
            case n.DataNode():
                append_list(nodes_diamond_wide, node, color)
            case n.AccelerationNode():
                append_list(nodes_plus, node, color)
            case _:
                append_list(nodes_circle, node, color)

    def label_for_edge(edge):
        match edge["attr"]:
            case (
                Edge.RECEIVE_MESH__PARTICIPANT__BELONGS_TO
                | Edge.MAPPING__PARTICIPANT__BELONGS_TO
                | Edge.EXCHANGE__COUPLING_SCHEME__BELONGS_TO
                | Edge.WRITE_DATA__PARTICIPANT__BELONGS_TO
                | Edge.READ_DATA__PARTICIPANT__BELONGS_TO
                | Edge.EXPORT__PARTICIPANT__BELONGS_TO
                | Edge.ACTION__PARTICIPANT__BELONGS_TO
                | Edge.WATCH_POINT__PARTICIPANT__BELONGS_TO
                | Edge.WATCH_INTEGRAL__PARTICIPANT__BELONGS_TO
                | Edge.ACCELERATION__COUPLING_SCHEME__BELONGS_TO
                | Edge.CONVERGENCE_MEASURE__COUPLING_SCHEME__BELONGS_TO
            ):
                return "belongs to"
            case Edge.ACCELERATION_DATA__ACCELERATION__BELONGS_TO:
                return "accelerates"
            case Edge.RECEIVE_MESH__PARTICIPANT_RECEIVED_FROM:
                return "received from"
            case Edge.PROVIDE_MESH__PARTICIPANT_PROVIDES:
                return "provides"
            case Edge.MAPPING__TO_MESH | Edge.EXCHANGE__EXCHANGES_TO:
                return "to"
            case Edge.MAPPING__FROM_MESH | Edge.EXCHANGE__EXCHANGED_FROM:
                return "from"
            case Edge.ACTION__SOURCE_DATA:
                return "source data"
            case Edge.ACTION__TARGET_DATA:
                return "target data"
            case (
                Edge.WATCH_POINT__MESH
                | Edge.WATCH_INTEGRAL__MESH
                | Edge.ACTION__MESH
                | Edge.ACCELERATION_DATA__MESH
                | Edge.CONVERGENCE_MEASURE__MESH
            ):
                return "mesh"
            case Edge.ACCELERATION_DATA__DATA | Edge.CONVERGENCE_MEASURE__DATA:
                return "data"
            case Edge.M2N__PARTICIPANT_ACCEPTOR:
                return "acceptor"
            case Edge.M2N__PARTICIPANT_CONNECTOR:
                return "connector"
            case Edge.COUPLING_SCHEME__PARTICIPANT_FIRST:
                return "first"
            case Edge.COUPLING_SCHEME__PARTICIPANT_SECOND:
                return "second"
            case Edge.MULTI_COUPLING_SCHEME__PARTICIPANT:
                return "participant"
            case Edge.MULTI_COUPLING_SCHEME__PARTICIPANT__CONTROL:
                return "control"
            case Edge.USE_DATA:
                return "uses"
            case Edge.WRITE_DATA__WRITES_TO_MESH | Edge.WRITE_DATA__WRITES_TO_DATA:
                return "writes to"
            case Edge.READ_DATA__DATA_READ_BY | Edge.READ_DATA__MESH_READ_BY:
                return "read by"
            case _:
                return ""

    node_labels = dict()
    for node in graph.nodes():
        match node:
            case n.ParticipantNode() | n.MeshNode() | n.DataNode() | n.WatchPointNode() | n.WatchIntegralNode():
                node_labels[node] = node.name
            case n.CouplingSchemeNode():
                node_labels[node] = f"Coupling Scheme ({node.type.value})"
            case n.MultiCouplingSchemeNode():
                node_labels[node] = "Multi Coupling Scheme"
            case n.ExchangeNode():
                node_labels[node] = "Exchange"
            case n.MappingNode():
                node_labels[node] = f"Mapping ({node.direction.name})"
            case n.ExportNode():
                node_labels[node] = f"Export ({node.format.value})"
            case n.ActionNode():
                node_labels[node] = f"Action ({node.type.value})"
            case n.WriteDataNode():
                node_labels[node] = f"Write {node.data.name}"
            case n.ReadDataNode():
                node_labels[node] = f"Read {node.data.name}"
            case n.ReceiveMeshNode():
                node_labels[node] = f"Receive {node.mesh.name}"
            case n.M2NNode():
                node_labels[node] = f"M2N {node.type.value}"
            case n.AccelerationNode():
                node_labels[node] = f"Acceleration {node.type.value}"
            case n.AccelerationDataNode():
                node_labels[node] = f"Accelerate {node.data.name}"
            case n.ConvergenceMeasureNode():
                node_labels[node] = f"{node.type.value}-convergence-measure"
            case _:
                node_labels[node] = ""

    pos = nx.spring_layout(
        graph, seed=1
    )  # set the seed so that generated graph always has same layout

    for list in node_lists:
        if len(list[2]) == 0:
            continue
        nx.draw_networkx_nodes(
            graph,
            pos,
            node_shape=list[0],
            nodelist=list[2],
            node_color=list[3],
            node_size=list[4],
        )
    nx.draw_networkx_labels(graph, pos, labels=node_labels)
    nx.draw_networkx_edges(graph, pos)
    nx.draw_networkx_edge_labels(
        graph,
        pos,
        edge_labels={
            tuple(edge): label_for_edge(d) for *edge, d in graph.edges(data=True)
        },
    )

    # Create a plot for the debugging view of the graph
    handles = []
    unique_types = []
    for list in node_lists:
        marker_type = list[0]
        marker_mult = list[1]
        for node in list[2]:
            name = node.__class__.__name__
            # Only display each node type once
            if name not in unique_types:
                unique_types.append(name)
                # Remove the 'Node' suffix
                label = name[:-4]
                handles.append(
                    plt.Line2D(
                        [],
                        [],
                        marker=marker_type,
                        color="w",
                        markerfacecolor=color_for_node(node),
                        markersize=12 * marker_mult,
                        label=label,
                    )
                )

    plt.legend(handles=handles, loc="upper left", title="Node types:")

    plt.show()
