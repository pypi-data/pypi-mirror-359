from precicecasegenerate.controller_utils.myutils.UT_PCErrorLogging import (
    UT_PCErrorLogging,
)
from enum import Enum


class QuantityCouple(object):
    """the quantity that is coupled"""

    def __init__(self):
        self.name = "None"  # the name of the quantity as it is called physically
        self.instance_name = "None"  # this will be the solver name "-" quantity name, example: "InnerSolver-Pressure"
        self.unit = "None"  # unit of the quantity
        self.BC = -1  # boundary code for the coupling
        self.relative_tolerance = 1e-4  # the relative convergence for coupling
        self.list_of_solvers = (
            {}
        )  # list of solvers that use this quantity (either read or write)
        self.source_solver = (
            None  # the origin of this quantity the solver how creates it
        )
        self.source_mesh_name = "None"  # the source mesh name
        self.mapping_string = "ERROR"  # conservative or consistent
        self.dim = 3  # the dimension of the quantity
        self.is_consistent = (
            True  # True if this quantity is consistent False if it is conservative
        )
        pass


def get_quantity_object(name: str, bc: str, instance_name: str):
    """Function to create coupling quantity"""
    ret = None
    if name.startswith("Force"):
        ret = Force()
    if name.startswith("Displacement"):
        ret = Displacement()
    if name.startswith("Velocity"):
        ret = Velocity()
    if name.startswith("Pressure"):
        ret = Pressure()
    if name.startswith("Temperature"):
        ret = Temperature()
    if name.startswith("HeatTransfer"):
        ret = HeatTransfer()
    if ret is None:
        # TODO: report error
        return QuantityCouple()
    else:
        # set the boundary code at the source solver
        ret.BC = bc
        # the instance name is like "InnerSolver-Pressure" (a combination of solver name and quantity name)
        # print(" Instance Name = ",instance_name)
        ret.instance_name = instance_name
        return ret


class Force(QuantityCouple):
    """Forces"""

    def __init__(self):
        super().__init__()
        self.name = "Force"
        self.unit = "N"
        self.mapping_string = "conservative"
        self.is_consistent = False
        pass


class Displacement(QuantityCouple):
    """Displacements"""

    def __init__(self):
        super().__init__()
        self.name = "Displacement"
        self.unit = "m"
        self.mapping_string = "consistent"
        pass


class Velocity(QuantityCouple):
    """Velocities"""

    def __init__(self):
        super().__init__()
        self.name = "Velocity"
        self.unit = "m/s"
        self.mapping_string = "consistent"
        pass


class Pressure(QuantityCouple):
    """Pressures"""

    def __init__(self):
        super().__init__()
        self.name = "Pressure"
        self.unit = "N/m^2"
        self.mapping_string = "consistent"
        self.dim = 1
        pass


class Temperature(QuantityCouple):
    """temperature"""

    def __init__(self):
        super().__init__()
        self.name = "Temperature"
        self.unit = "C"
        self.mapping_string = "consistent"
        self.dim = 1
        pass


class HeatTransfer(QuantityCouple):
    """heat transfer"""

    def __init__(self):
        super().__init__()
        self.name = "HeatTransfer"
        self.unit = "?"
        self.mapping_string = "consistent"
        self.dim = 1
        pass
