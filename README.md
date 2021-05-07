# Subline Frequency Setting for autonomous minibusses under demand uncertainty

This repository is meant for publishing some of the code related to the **subline frequency setting problem for autonomous minibusses**.

Currently, this repository contains the following scripts:

1. `DWS_14stops.py` script contains the deterministic subline frequency settings model introduced in the paper **Subline Frequency Setting for autonomous minibusses under demand uncertainty**, which is currently under scientific review. This script contains all necessary functions to calculate the solution of the mathematical program. 

2. `DNS_14stops.py` script contains the deterministic frequency settings model that does not consider sublines.

3. `SWS_14stops.py` script contains the stochastic frequency settings model that considers sublines.

In addition, this repository contains the following data files:

1. 

# Referencing

In case you use this code for scientific purposes, it is appreciated if you provide a citation to the paper:

**K. Gkiotsalitis, M. Schmidt, and E. van der Hurk.** Subline Frequency Setting for autonomous minibusses under demand uncertainty, under revision.

# License

MIT License

# Dependencies

The scripts are written in Python. Running or modifying these script requires an installed version of **Python**. 

The mathematical programs are solved with Gurobi. Running or modifying the scripts requires an installed version of **Gurobi**.

