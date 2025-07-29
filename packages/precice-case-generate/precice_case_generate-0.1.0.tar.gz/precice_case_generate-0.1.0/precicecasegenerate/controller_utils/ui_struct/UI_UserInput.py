from precicecasegenerate.controller_utils.ui_struct.UI_SimulationInfo import (
    UI_SimulationInfo,
)
from precicecasegenerate.controller_utils.ui_struct.UI_Participant import UI_Participant
from precicecasegenerate.controller_utils.ui_struct.UI_Coupling import UI_Coupling
from precicecasegenerate.controller_utils.myutils.UT_PCErrorLogging import (
    UT_PCErrorLogging,
)
from precicecasegenerate.controller_utils.ui_struct.UI_Coupling import UI_CouplingType


class UI_UserInput(object):
    """
    This class represents the main object that contains either one YAML file
    or a user input through a GUI

    The main components are:
     - the list of participants
     - general simulation information
    """

    def __init__(self):
        """The constructor, dummy initialization of the fields"""
        self.sim_info = UI_SimulationInfo()
        self.participants = {}  # empty participants stored as a dictionary
        self.couplings = []  # empty coupling list
        self.exchanges = []  # empty exchanges list
        pass

    def init_from_yaml(self, etree, mylog: UT_PCErrorLogging):
        # Check if using new topology structure
        if (
            "coupling-scheme" in etree
            and "participants" in etree
            and "exchanges" in etree
        ):
            # --- Parse simulation info from 'coupling-scheme' ---
            simulation_info = etree["coupling-scheme"]
            self.sim_info.NrTimeStep = simulation_info.get("max-time")
            self.sim_info.Dt = simulation_info.get("time-window-size")
            self.sim_info.max_iterations = simulation_info.get("max-iterations")
            self.sim_info.display_standard_values = simulation_info.get(
                "display_standard_values", "false"
            )
            self.sim_info.coupling = simulation_info.get("coupling", "parallel")

            # Initialize coupling type+ acceleration to None
            self.coupling_type = None
            self.acceleration = None

            # Extract coupling type from exchanges
            if "exchanges" in etree:
                exchanges = etree["exchanges"]
                exchange_types = [
                    exchange.get("type") for exchange in exchanges if "type" in exchange
                ]

                # Validate exchange types
                if exchange_types:
                    # If all types are the same, set that as the coupling type
                    if len(set(exchange_types)) == 1:
                        if exchange_types[0] == "strong" or exchange_types[0] == "weak":
                            self.coupling_type = exchange_types[0]
                        else:
                            mylog.rep_error(
                                f"Invalid exchange type: {exchange_types[0]}. Must be 'strong' or 'weak'."
                            )
                            self.coupling_type = None
                    else:
                        # Mixed types, default to weak
                        # mylog.rep_error("Mixed exchange types detected. Defaulting to 'weak'.")
                        self.coupling_type = "weak"

            # --- Parse Acceleration ---
            if "acceleration" in etree:
                acceleration = etree["acceleration"]
                display_standard_values = acceleration.get(
                    "display_standard_values", "false"
                )
                if display_standard_values.lower() not in ["true", "false"]:
                    mylog.rep_error(
                        f"Invalid display_standard_values value: {display_standard_values}. Must be 'true' or 'false'."
                    )
                if display_standard_values.lower() == "true":
                    self.acceleration = {
                        "name": acceleration.get("name", "IQN-ILS"),
                        "initial-relaxation": {
                            "value": acceleration.get("initial-relaxation", {}).get(
                                "value", 0.1
                            ),
                            "enforce": acceleration.get("initial-relaxation", {}).get(
                                "enforce", "false"
                            ),
                        },
                        "preconditioner": {
                            "freeze-after": acceleration.get("preconditioner", {}).get(
                                "freeze-after", -1
                            ),
                            "type": acceleration.get("preconditioner", {}).get(
                                "type", None
                            ),
                        },
                        "filter": {
                            "limit": acceleration.get("filter", {}).get("limit", 1e-16),
                            "type": acceleration.get("filter", {}).get("type", None),
                        },
                        "max-used-iterations": acceleration.get(
                            "max-used-iterations", None
                        ),
                        "time-windows-reused": acceleration.get(
                            "time-windows-reused", None
                        ),
                        "imvj-restart-mode": {
                            "truncation-threshold": acceleration.get(
                                "imvj-restart-mode", {}
                            ).get("truncation-threshold", None),
                            "chunk-size": acceleration.get("imvj-restart-mode", {}).get(
                                "chunk-size", None
                            ),
                            "reused-time-windows-at-restart": acceleration.get(
                                "imvj-restart-mode", {}
                            ).get("reused-time-windows-at-restart", None),
                            "type": acceleration.get("imvj-restart-mode", {}).get(
                                "type", None
                            ),
                        }
                        if any(acceleration.get("imvj-restart-mode", {}).values())
                        else None,
                        "display_standard_values": acceleration.get(
                            "display_standard_values", "false"
                        ),
                    }
                # If display_standard_values is false, set default values to none so they are not displayed
                else:
                    self.acceleration = {
                        "name": acceleration.get("name", "IQN-ILS"),
                        "initial-relaxation": acceleration.get(
                            "initial-relaxation", None
                        ),
                        "preconditioner": {
                            "freeze-after": acceleration.get("preconditioner", {}).get(
                                "freeze-after", None
                            ),
                            "type": acceleration.get("preconditioner", {}).get(
                                "type", None
                            ),
                        }
                        if any(acceleration.get("preconditioner", {}).values())
                        else None,
                        "initial-relaxation": {
                            "value": acceleration.get("initial-relaxation", {}).get(
                                "value", None
                            ),
                            "enforce": acceleration.get("initial-relaxation", {}).get(
                                "enforce", None
                            ),
                        }
                        if any(acceleration.get("initial-relaxation", {}).values())
                        else None,
                        "filter": {
                            "limit": acceleration.get("filter", {}).get("limit", None),
                            "type": acceleration.get("filter", {}).get("type", None),
                        }
                        if any(acceleration.get("filter", {}).values())
                        else None,
                        "max-used-iterations": acceleration.get(
                            "max-used-iterations", None
                        ),
                        "time-windows-reused": acceleration.get(
                            "time-windows-reused", None
                        ),
                        "imvj-restart-mode": {
                            "truncation-threshold": acceleration.get(
                                "imvj-restart-mode", {}
                            ).get("truncation-threshold", None),
                            "chunk-size": acceleration.get("imvj-restart-mode", {}).get(
                                "chunk-size", None
                            ),
                            "reused-time-windows-at-restart": acceleration.get(
                                "imvj-restart-mode", {}
                            ).get("reused-time-windows-at-restart", None),
                            "type": acceleration.get("imvj-restart-mode", {}).get(
                                "type", None
                            ),
                        }
                        if any(acceleration.get("imvj-restart-mode", {}).values())
                        else None,
                        "display_standard_values": acceleration.get(
                            "display_standard_values", "false"
                        ),
                    }

            # --- Parse participants ---
            self.participants = {}
            participants_data = etree["participants"]
            for participant in participants_data:
                # Handle new list of dictionaries format
                if isinstance(participant, dict):
                    name = participant.get("name")
                    solver_info = participant

                    if name is None:
                        mylog.rep_error(
                            f"Participant missing 'name' key: {participant}"
                        )
                        continue

                    solver_name = solver_info.get("solver", name)
                    dimensionality = solver_info.get("dimensionality", 3)

                    new_participant = UI_Participant(
                        name, solver_name, dimensionality=dimensionality
                    )
                    self.participants[new_participant.name] = new_participant
                else:
                    # Unsupported format
                    mylog.rep_error(
                        f"Unsupported participant configuration: {participant}"
                    )
                    continue

            # --- Parse couplings from exchanges ---
            exchanges_list = etree["exchanges"]
            # Save full exchange details
            self.exchanges = exchanges_list.copy()

            # Group exchanges by unique participant pairs
            groups = {}
            for exchange in exchanges_list:
                exchanges = (
                    exchange.get("data-type").lower()
                    if exchange.get("data-type") is not None
                    else "scalar"
                )
                pair = tuple(sorted([exchange["from"], exchange["to"]]))
                groups.setdefault(pair, []).append(exchange)

            self.couplings = []
            for pair, ex_list in groups.items():
                coupling = UI_Coupling()
                p1_name, p2_name = pair
                coupling.participant1 = self.participants[p1_name]
                coupling.participant2 = self.participants[p2_name]

                # Determine coupling type based on exchanged data
                data_names = {ex["data"] for ex in ex_list}
                if any(name.startswith("Force") for name in data_names) and any(
                    name.startswith("Displacement") for name in data_names
                ):
                    coupling.coupling_type = UI_CouplingType.fsi
                elif any(name.startswith("Force") for name in data_names):
                    coupling.coupling_type = UI_CouplingType.f2s
                # elif any("temperature" in name.lower() or "heat" in name.lower() for name in data_names):
                elif any(
                    name.startswith("Temperature") or name.startswith("HeatTransfer")
                    for name in data_names
                ):
                    coupling.coupling_type = UI_CouplingType.cht
                else:
                    # TODO: Handle Velocity, Pressure
                    raise NameError(
                        "Found Velocity, Pressure or an invalid coupling type that is unsupported."
                    )

                # Use the first exchange's patches as boundary interfaces (simple heuristic)
                first_ex = ex_list[0]
                coupling.boundaryC1 = first_ex.get("from-patch", "")
                coupling.boundaryC2 = first_ex.get("to-patch", "")

                self.couplings.append(coupling)
                coupling.participant1.list_of_couplings.append(coupling)
                coupling.participant2.list_of_couplings.append(coupling)
