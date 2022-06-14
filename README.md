# Subline Frequency Setting for autonomous minibusses under demand uncertainty

This repository is meant for publishing some of the code related to the **subline frequency setting problem for autonomous minibusses**.

Currently, this repository contains the following scripts:

1. `DWS_14stops.py` script contains the deterministic subline frequency settings model introduced in the paper **Subline Frequency Setting for autonomous minibusses under demand uncertainty**, which is currently under scientific review. This script contains all necessary functions to calculate the solution of the mathematical program. 

2. `DNS_14stops.py` script contains the deterministic frequency settings model that does not consider sublines.

3. `SWS_14stops.py` script contains the stochastic frequency settings model that considers sublines.

In addition, this repository contains the Data_input folder with the following data files:

1. `demand_14stops_leftskewed.txt` the average demand used in the deterministic models of section 5.4.1. of the paper.
2. `demand_14stops_bothterminals.txt` the average demand used in the deterministic models of section 5.4.2. of the paper.
3. `demand_14stops_skewedcenter.txt` the average demand used in the deterministic models of section 5.4.3. of the paper.
4. `demand_14stops_constant.txt` the average demand used in the deterministic models of section 5.4.4. of the paper.
5. `data_input_14stops.xlsx` the file with the 100 demand scenarios used in the stochastic model of sections 5.4.1.-5.4.4. of the paper. Sheet slt_fr corresponds to the left skewed demand scenario (section 5.4.1), sheet sbt_fr to the skewed demand in both terminals (section 5.4.2), sheet sc_fr to the skewed demand in the center (section 5.4.3), and sheet constant_fr to the balanced demand scenario (section 5.4.4).

# Referencing

In case you use this code for scientific purposes, it is appreciated if you provide a citation to the paper:

**K. Gkiotsalitis, M. Schmidt, and E. van der Hurk.** Subline Frequency Setting for autonomous minibusses under demand uncertainty, Transportation Research Part C: Emerging Technologies, https://doi.org/10.1016/j.trc.2021.103492.

# License

MIT License

# Dependencies

The scripts are written in Python. Running or modifying these script requires an installed version of **Python**. 

The mathematical programs are solved with Gurobi. Running or modifying the scripts requires an installed version of **Gurobi**.

