from precicecasegenerate.controller_utils.myutils.UT_PCErrorLogging import (
    UT_PCErrorLogging,
)


class UI_SimulationInfo(object):
    """
    This class contains information on the user input level regarding the
    general simulation information
    """

    def __init__(self):
        """The constructor."""
        self.steady = False
        self.NrTimeStep = -1
        self.Dt = 1e-3
        self.max_iterations = 50
        self.accuracy = "medium"
        self.mode = "on"
        self.sync_mode = "fundamental"
        self.display_standard_values = "false"
        self.coupling = "parallel"
        pass

    def init_from_yaml(self, etree, mylog: UT_PCErrorLogging):
        """Method to initialize fields from a parsed YAML file node"""
        # catch exceptions if these items are not in the list
        try:
            self.steady = etree.get("steady-state")
            self.NrTimeStep = etree.get("timesteps")
            self.Dt = etree.get("time-window-size")
            self.display_standard_values = etree.get("display_standard_values", "false")
            self.max_iterations = etree.get("max-iterations")
            self.accuracy = etree.get("accuracy")
            self.sync_mode = etree.get("synchronize")
            self.mode = etree.get("mode")
            self.coupling = etree.get("coupling")
        except:
            mylog.rep_error("Error in YAML initialization of the Simulator info.")
        pass
