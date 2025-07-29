from precicecasegenerate.controller_utils.myutils.UT_PCErrorLogging import (
    UT_PCErrorLogging,
)
from precicecasegenerate.controller_utils.precice_struct.PS_ParticipantSolver import (
    PS_ParticipantSolver,
)
from precicecasegenerate.controller_utils.ui_struct.UI_UserInput import UI_UserInput
import xml.etree.ElementTree as etree


class PS_CouplingScheme(object):
    """Class to represent the Coupling schemes"""

    def __init__(self):
        """Ctor to initialize all the fields"""
        self.firstSolver = None
        self.secondSolver = None
        pass

    def init_from_UI(self, ui_config: UI_UserInput, conf):  # : PS_PreCICEConfig
        """This method should be overwritten by the subclasses"""
        pass

    def write_precice_xml_config(self, tag: etree, config):  # config: PS_PreCICEConfig
        """parent function to write out XML file"""
        pass

    def write_participants_and_coupling_scheme(
        self, tag: etree, config, coupling_str: str
    ):
        """write out the config XMl file"""
        if len(config.solvers) <= 2:
            # for only
            coupling_scheme = etree.SubElement(tag, "coupling-scheme:" + coupling_str)
            # print the participants, ASSUMPTION! we assume there is at least two
            mylist = ["NONE", "NONE"]
            mycomplexity = [-1, -1]
            myindex = 0
            for participant_name in config.solvers:
                p = config.solvers[participant_name]
                mylist[myindex] = participant_name
                mycomplexity[myindex] = p.solver_domain.value
                myindex = myindex + 1
                pass
            # the solver with the higher complexity should be first
            if mycomplexity[0] < mycomplexity[1]:
                i = etree.SubElement(
                    coupling_scheme, "participants", first=mylist[0], second=mylist[1]
                )
                config.couplingScheme_participants = mylist[0], mylist[1]
            else:
                i = etree.SubElement(
                    coupling_scheme, "participants", first=mylist[1], second=mylist[0]
                )
                config.couplingScheme_participants = mylist[1], mylist[0]

        else:
            # TODO: is "multi" good for all
            coupling_scheme = etree.SubElement(tag, "coupling-scheme:multi")
            # first find the solver with the most meshes and this should be the one who controls the coupling
            nr_max_meshes = -1
            control_participant_name = "NONE"
            for participant_name in config.solvers:
                participant = config.solvers[participant_name]
                # TODO: we should select the solver with the most meshes ?
                if len(participant.meshes) > nr_max_meshes:
                    nr_max_meshes = len(participant.meshes)
                    control_participant_name = participant.name
                pass
            # second print all the participants
            for participant_name in config.solvers:
                participant = config.solvers[participant_name]
                if participant.name == control_participant_name:
                    i = etree.SubElement(
                        coupling_scheme,
                        "participant",
                        name=participant_name,
                        control="yes",
                    )
                else:
                    i = etree.SubElement(
                        coupling_scheme, "participant", name=participant_name
                    )
                    pass
                pass
            pass
        return coupling_scheme

    def _find_simplest_solver(self, config):
        """Find the solver with minimal complexity"""
        simple_solver = None
        solver_simplicity = -2
        for q_name in config.coupling_quantities:
            q = config.coupling_quantities[q_name]
            solver = q.source_solver
            if solver_simplicity < solver.solver_domain.value:
                simple_solver = solver
        return simple_solver

    def _find_other_solver_for_coupling(self, quantity, solver):
        """Find the other solver involved in the coupling"""
        other_solver_for_coupling = None
        other_mesh_name = None
        for oq in quantity.list_of_solvers:
            other_solver = quantity.list_of_solvers[oq]
            if other_solver.name != solver.name:
                other_solver_for_coupling = other_solver
                for allm in other_solver.meshes:
                    if allm != quantity.source_mesh_name:
                        other_mesh_name = allm
        return other_solver_for_coupling, other_mesh_name

    def write_exchange_and_convergance(
        self, config, coupling_scheme, relative_conv_str: str
    ):
        """Writes to the XML the exchange list"""
        for exchange in config.exchanges:
            from_s = exchange.get("from")
            to_s = exchange.get("to")
            data = exchange.get("data")

            # Process mappings
            read_mappings = [m.copy() for m in config.mappings_read]
            write_mappings = [m.copy() for m in config.mappings_write]

            read_mapping = next(
                (
                    m
                    for m in read_mappings
                    if (m["from"] == from_s + "-Mesh" and m["to"] == to_s + "-Mesh")
                ),
                None,
            )
            write_mapping = next(
                (
                    m
                    for m in write_mappings
                    if (m["from"] == from_s + "-Mesh" and m["to"] == to_s + "-Mesh")
                ),
                None,
            )

            # Choose mesh based on mapping constraint
            if read_mapping and read_mapping["constraint"] == "conservative":
                exchange_mesh_name = read_mapping["to"]
            elif read_mapping and read_mapping["constraint"] == "consistent":
                exchange_mesh_name = read_mapping["from"]
            elif write_mapping and write_mapping["constraint"] == "conservative":
                exchange_mesh_name = write_mapping["to"]
            elif write_mapping and write_mapping["constraint"] == "consistent":
                exchange_mesh_name = write_mapping["from"]
            else:
                exchange_mesh_name = from_s + "-Mesh"
            if exchange_mesh_name not in config.exchange_mesh_names:
                config.exchange_mesh_names.append(exchange_mesh_name)
            e = etree.SubElement(
                coupling_scheme,
                "exchange",
                data=data,
                mesh=exchange_mesh_name,
                from___=from_s,
                to=to_s,
            )
            # Use the same mesh for the relative convergence measure
            if relative_conv_str != "":
                c = etree.SubElement(
                    coupling_scheme,
                    "relative-convergence-measure",
                    limit=relative_conv_str,
                    mesh=exchange_mesh_name,
                    data=data,
                )
            pass


class PS_ExplicitCoupling(PS_CouplingScheme):
    """Explicit coupling scheme"""

    def __init__(self):
        self.NrTimeStep = -1
        self.Dt = 1e-4
        pass

    def initFromUI(self, ui_config: UI_UserInput, conf):  # conf : PS_PreCICEConfig
        # call theinitialization from the UI data structures
        super(PS_ExplicitCoupling, self).init_from_UI(ui_config, conf)
        simulation_conf = ui_config.sim_info
        self.NrTimeStep = simulation_conf.NrTimeStep
        self.Dt = simulation_conf.Dt
        self.display_standard_values = simulation_conf.display_standard_values
        self.coupling = simulation_conf.coupling
        pass

    def write_precice_xml_config(self, tag: etree, config):  # config: PS_PreCICEConfig
        """write out the config XMl file"""
        coupling_scheme = self.write_participants_and_coupling_scheme(
            tag, config, f"{self.coupling}-explicit"
        )
        config.coupling_scheme = coupling_scheme
        if str(self.display_standard_values).lower() == "true":
            if self.NrTimeStep is None:
                self.NrTimeStep = 1e-3
            if self.Dt is None:
                self.Dt = 1e-3
            i = etree.SubElement(
                coupling_scheme, "max-time", value=str(self.NrTimeStep)
            )
            attr = {"value": str(self.Dt)}
            i = etree.SubElement(coupling_scheme, "time-window-size", attr)
        else:
            if self.NrTimeStep is not None:
                i = etree.SubElement(
                    coupling_scheme, "max-time", value=str(self.NrTimeStep)
                )
            if self.Dt is not None:
                attr = {"value": str(self.Dt)}
                i = etree.SubElement(coupling_scheme, "time-window-size", attr)

        # write out the exchange but not the convergence (if empty it will not be written)
        self.write_exchange_and_convergance(config, coupling_scheme, "")


class PS_ImplicitCoupling(PS_CouplingScheme):
    """Implicit coupling scheme"""

    def __init__(self):

        # TODO: define here only implicit coupling specific measures

        self.NrTimeStep = -1
        self.Dt = 1e-4
        self.maxIteration = 50
        self.relativeConverganceEps = 1e-4
        self.extrapolation_order = 2
        self.acceleration = PS_ImplicitAcceleration()  # this is the acceleration
        self.display_standard_values = "false"
        pass

    def initFromUI(self, ui_config: UI_UserInput, conf):  # conf : PS_PreCICEConfig
        # call theinitialization from the UI data structures
        super(PS_ImplicitCoupling, self).init_from_UI(ui_config, conf)

        # TODO: should we add all quantities?
        # later do delete some quantities from the list?
        self.acceleration.post_process_quantities = conf.coupling_quantities

        simulation_conf = ui_config.sim_info

        self.NrTimeStep = simulation_conf.NrTimeStep
        self.Dt = simulation_conf.Dt
        self.maxIteration = simulation_conf.max_iterations
        self.display_standard_values = simulation_conf.display_standard_values
        self.coupling = simulation_conf.coupling

        pass

    def write_precice_xml_config(self, tag: etree, config):  # config: PS_PreCICEConfig
        """write out the config XMl file"""
        if self.coupling not in ["serial", "parallel"]:
            raise ValueError(
                f"coupling must be 'serial' or 'parallel', but got {self.coupling}"
            )
        coupling_scheme = self.write_participants_and_coupling_scheme(
            tag, config, f"{self.coupling}-implicit"
        )
        config.coupling_scheme = coupling_scheme

        if str(self.display_standard_values).lower() == "true":
            if self.NrTimeStep is None:
                self.NrTimeStep = 1e-3
            if self.Dt is None:
                self.Dt = 1e-3
            if self.maxIteration is None:
                self.maxIteration = 50
            i = etree.SubElement(
                coupling_scheme, "max-time", value=str(self.NrTimeStep)
            )
            attr = {"value": str(self.Dt)}
            i = etree.SubElement(coupling_scheme, "time-window-size", attr)
            i = etree.SubElement(
                coupling_scheme, "max-iterations", value=str(self.maxIteration)
            )
            # i = etree.SubElement(coupling_scheme, "extrapolation-order", value=str(self.extrapolation_order))
        else:
            if self.NrTimeStep is not None:
                i = etree.SubElement(
                    coupling_scheme, "max-time", value=str(self.NrTimeStep)
                )
            if self.Dt is not None:
                attr = {"value": str(self.Dt)}
                i = etree.SubElement(coupling_scheme, "time-window-size", attr)
            if self.maxIteration is not None:
                i = etree.SubElement(
                    coupling_scheme, "max-iterations", value=str(self.maxIteration)
                )
            # if self.extrapolation_order is not None:
            #    i = etree.SubElement(coupling_scheme, "extrapolation-order", value=str(self.extrapolation_order))

        # write out the exchange and the convergence rate
        self.write_exchange_and_convergance(
            config, coupling_scheme, str(self.relativeConverganceEps)
        )

        # finally we write out the post processing...
        self.acceleration.write_precice_xml_config(coupling_scheme, config, self)

        pass


class PS_ImplicitAcceleration(object):
    """Class to model the post-processing part of the implicit coupling"""

    def __init__(self):
        """Ctor for the acceleration"""
        self.name = "IQN-ILS"
        self.precondition_type = "residual-sum"
        self.post_process_quantities = {}  # The quantities that are in the acceleration

    def write_precice_xml_config(self, tag: etree.Element, config, parent):
        """Write out the config XML file of the acceleration in case of implicit coupling
        Only for explicit coupling (one directional) this should not write out anything"""

        self.name = (
            config.acceleration["name"]
            if config.acceleration is not None
            else "IQN-ILS"
        )
        self.display_standard_values = (
            config.acceleration["display_standard_values"]
            if config.acceleration is not None
            else "false"
        )

        post_processing = etree.SubElement(tag, "acceleration:" + self.name)

        # Identify unique solvers and their meshes
        solver_meshes = {}
        for q_name, q in config.coupling_quantities.items():
            solver = q.source_solver
            if solver.name not in solver_meshes:
                solver_meshes[solver.name] = set()
            solver_meshes[solver.name].add(q.source_mesh_name)

        # Attempt to find the 'simplest' solver (e.g., solid solver)
        # This is a heuristic and might need adjustment based on specific use cases
        def solver_complexity(solver_name):
            complexity_map = {"solid": 1, "structural": 1, "fluid": 2, "thermal": 3}
            return complexity_map.get(solver_name.lower(), 10)

        sorted_solvers = sorted(solver_meshes.keys(), key=solver_complexity)

        # Choose the simplest solver's mesh
        simple_solver = sorted_solvers[0] if sorted_solvers else None

        from_s = "___"
        to_s = "__"
        exchange_mesh_name = ""
        read_mappings = [m.copy() for m in config.mappings_read]
        write_mappings = [m.copy() for m in config.mappings_write]

        acceleration = config.acceleration
        if acceleration is not None and self.display_standard_values:
            for a, b in acceleration.items():
                if b is not None:
                    if self.name == "IQN-ILS":
                        if a == "initial-relaxation":
                            if b.get("enforce") is not None:
                                i = etree.SubElement(
                                    post_processing,
                                    a,
                                    value=str(b.get("value")),
                                    enforce=str(b.get("enforce")),
                                )
                            else:
                                i = etree.SubElement(
                                    post_processing, a, value=str(b.get("value"))
                                )
                        elif a == "max-used-iterations" or a == "time-windows-reused":
                            i = etree.SubElement(post_processing, a, value=str(b))
                        elif a == "filter":
                            if b.get("type") is not None:
                                i = etree.SubElement(
                                    post_processing,
                                    a,
                                    limit=str(b.get("limit")),
                                    type=str(b.get("type")),
                                )
                            else:
                                i = etree.SubElement(
                                    post_processing, a, limit=str(b.get("limit"))
                                )
                        elif a == "preconditioner":
                            if b.get("type") is not None:
                                i = etree.SubElement(
                                    post_processing, a, type=str(b.get("type"))
                                )
                                i.set("freeze-after", str(b.get("freeze-after")))
                            else:
                                i = etree.SubElement(
                                    post_processing,
                                    a,
                                    freeze_after=str(b.get("freeze-after")),
                                )
                    if self.name == "aitken":
                        if a == "initial-relaxation":
                            if b.get("enforce") is not None:
                                i = etree.SubElement(
                                    post_processing,
                                    a,
                                    value=str(b.get("value")),
                                    enforce=str(b.get("enforce")),
                                )
                            else:
                                i = etree.SubElement(
                                    post_processing, a, value=str(b.get("value"))
                                )
                        elif a == "preconditioner":
                            if b.get("type") is not None:
                                i = etree.SubElement(
                                    post_processing, a, type=str(b.get("type"))
                                )
                                i.set("freeze-after", str(b.get("freeze-after")))
                            else:
                                i = etree.SubElement(
                                    post_processing,
                                    a,
                                    freeze_after=str(b.get("freeze-after")),
                                )
                    if self.name == "IQN-IMVJ":
                        if a == "initial-relaxation":
                            if b.get("enforce") is not None:
                                i = etree.SubElement(
                                    post_processing,
                                    a,
                                    value=str(b.get("value")),
                                    enforce=str(b.get("enforce")),
                                )
                            else:
                                i = etree.SubElement(
                                    post_processing, a, value=str(b.get("value"))
                                )
                        elif a == "max-used-iterations" or a == "time-windows-reused":
                            i = etree.SubElement(post_processing, a, value=str(b))
                        elif a == "filter":
                            if b.get("type") is not None:
                                i = etree.SubElement(
                                    post_processing,
                                    a,
                                    limit=str(b.get("limit")),
                                    type=str(b.get("type")),
                                )
                            else:
                                i = etree.SubElement(
                                    post_processing, a, limit=str(b.get("limit"))
                                )
                        elif a == "preconditioner":
                            if b.get("type") is not None:
                                i = etree.SubElement(
                                    post_processing, a, type=str(b.get("type"))
                                )
                                i.set("freeze-after", str(b.get("freeze-after")))
                            else:
                                i = etree.SubElement(
                                    post_processing,
                                    a,
                                    freeze_after=str(b.get("freeze-after")),
                                )
                        elif a == "imvj-restart-mode":
                            i = etree.SubElement(
                                post_processing,
                                a,
                                {
                                    "truncation-threshold": str(
                                        b.get("truncation-threshold")
                                    ),
                                    "chunk-size": str(b.get("chunk-size")),
                                    "reused-time-windows-at-restart": str(
                                        b.get("reused-time-windows-at-restart")
                                    ),
                                    "type": str(b.get("type")),
                                },
                            )

        if simple_solver:
            for q_name, q in config.coupling_quantities.items():
                # Use the first mesh from the simplest solver
                mesh_name = list(solver_meshes[simple_solver])[0]

                # i = etree.SubElement(post_processing, "data",
                #                      name=q.instance_name,
                #                      mesh=mesh_name)

                # Copy over logic from _determine_exchange_mesh to determine right mesh
                for exchange in config.exchanges:
                    # print("Exchange data: " + exchange.get('data'))
                    # print("Quantity name: " + q.instance_name)
                    if exchange.get("data").lower() == q.instance_name.lower():
                        from_s = exchange.get("from")
                        to_s = exchange.get("to")

                        # Process mappings
                        read_mapping = next(
                            (
                                m
                                for m in read_mappings
                                if (
                                    m["from"] == from_s + "-Mesh"
                                    and m["to"] == to_s + "-Mesh"
                                )
                            ),
                            None,
                        )
                        write_mapping = next(
                            (
                                m
                                for m in write_mappings
                                if (
                                    m["from"] == from_s + "-Mesh"
                                    and m["to"] == to_s + "-Mesh"
                                )
                            ),
                            None,
                        )

                        # Choose mesh based on mapping constraint
                        if (
                            read_mapping
                            and read_mapping["constraint"] == "conservative"
                        ):
                            exchange_mesh_name = read_mapping["to"]
                        elif (
                            read_mapping and read_mapping["constraint"] == "consistent"
                        ):
                            exchange_mesh_name = read_mapping["from"]
                        elif (
                            write_mapping
                            and write_mapping["constraint"] == "conservative"
                        ):
                            exchange_mesh_name = write_mapping["to"]
                        elif (
                            write_mapping
                            and write_mapping["constraint"] == "consistent"
                        ):
                            exchange_mesh_name = write_mapping["from"]
                        else:
                            exchange_mesh_name = q.source_mesh_name

                # print(exchange_mesh_name)
                if exchange_mesh_name != "":
                    if config.couplingScheme.coupling == "serial":
                        if (
                            exchange_mesh_name
                            == config.couplingScheme_participants[1] + "-Mesh"
                        ):
                            i = etree.SubElement(
                                post_processing,
                                "data",
                                name=q.instance_name,
                                mesh=exchange_mesh_name,
                            )
                    # parallel coupling
                    else:
                        i = etree.SubElement(
                            post_processing,
                            "data",
                            name=q.instance_name,
                            mesh=exchange_mesh_name,
                        )
