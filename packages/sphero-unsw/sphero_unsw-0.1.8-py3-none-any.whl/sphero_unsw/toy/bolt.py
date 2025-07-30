"""
This module implements extended functionality of spherov2.scanner for Sphero BOLT+ to support Sphero BOLT+ robot.

# ====================================================================
# Authors: Kathryn Kasmarik, Reda Ghanem
# Version 0.1.8
# School of Systems and Computing, UNSW Canberra
# ==================================================================== 

"""


# ------------------------------------------------------------------------- #
# [1] Import necessary libraries
# ------------------------------------------------------------------------- #

# Import all necessary classes and functions from spherov2
from sphero_unsw.scanner import *
# Import BOLT as BASEBOLT from spherov2.toy.bolt
from spherov2.toy.bolt import BOLT as BASEBOLT



class BOLT(BASEBOLT):
    """
    This class extends the BOLTPLUS class to support Sphero BOLT+ robot.
    It inherits all functionalities from BOLTPLUS and can be used to
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the BOLT class with the same parameters as BOLTPLUS.
        """
        super().__init__(*args, **kwargs)

    # Additional methods specific to BOLT can be added here if needed.
    # For now, it inherits all functionalities from BOLTPLUS.