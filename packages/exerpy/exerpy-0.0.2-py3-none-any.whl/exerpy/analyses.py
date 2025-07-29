import json
import logging
import os

import numpy as np
import pandas as pd
from tabulate import tabulate

from .components.component import component_registry
from .components.helpers.cycle_closer import CycleCloser
from .functions import add_chemical_exergy
from .functions import add_total_exergy_flow


class ExergyAnalysis:
    """
    This class performs exergy analysis on energy system models from various simulation tools.
    It parses input data, constructs component objects, calculates exergy flows,
    and provides a comprehensive exergy balance for the overall system and individual components.
    The class supports importing data from TESPy, Aspen, Ebsilon, or directly from JSON files.

    Attributes
    ----------
    Tamb : float
        Ambient temperature in K for reference environment.
    pamb : float
        Ambient pressure in Pa for reference environment.
    _component_data : dict
        Raw component data from the input model.
    _connection_data : dict
        Raw connection data from the input model.
    chemExLib : object, optional
        Chemical exergy library for chemical exergy calculations.
    chemical_exergy_enabled : bool
        Flag indicating if chemical exergy calculations are enabled.
    split_physical_exergy : bool
        Flag indicating if physical exergy is split into thermal and mechanical components.
    components : dict
        Dictionary of component objects constructed from input data.
    connections : dict
        Dictionary of connection data with exergy values.
    E_F : float
        Total fuel exergy for the overall system in W.
    E_P : float
        Total product exergy for the overall system in W.
    E_L : float
        Total loss exergy for the overall system in W.
    E_D : float
        Total exergy destruction for the overall system in W.
    E_F_dict : dict
        Dictionary specifying fuel connections.
    E_P_dict : dict
        Dictionary specifying product connections.
    E_L_dict : dict
        Dictionary specifying loss connections.
    epsilon : float
        Overall exergy efficiency of the system.

    Methods
    -------
    analyse(E_F, E_P, E_L={})
        Performs exergy analysis based on specified fuel, product, and loss definitions.
    from_tespy(model, Tamb=None, pamb=None, chemExLib=None, split_physical_exergy=True)
        Creates an instance from a TESPy network model.
    from_aspen(path, Tamb=None, pamb=None, chemExLib=None, split_physical_exergy=True)
        Creates an instance from an Aspen model file.
    from_ebsilon(path, Tamb=None, pamb=None, chemExLib=None, split_physical_exergy=True)
        Creates an instance from an Ebsilon model file.
    from_json(json_path, Tamb=None, pamb=None, chemExLib=None, split_physical_exergy=True)
        Creates an instance from a JSON file containing system data.
    exergy_results(print_results=True)
        Displays and returns tables of exergy analysis results.
    export_to_json(output_path)
        Exports the model and analysis results to a JSON file.
    _serialize()
    """

    def __init__(self, component_data, connection_data, Tamb, pamb, chemExLib=None, split_physical_exergy=True) -> None:
        """
        Constructor for ExergyAnalysis. It parses the provided simulation file and prepares it for exergy analysis.

        Parameters
        ----------
        component_data : dict
            Data of the components.
        connection_data : dict
            Data of the connections.
        Tamb : float
            Ambient temperature (K).
        pamb : float
            Ambient pressure (Pa).
        chemical_exergy_enabled : bool, optional
            Flag to enable chemical exergy calculations (default is False).
        split_physical_exergy : bool, optional
            Flag to determine if physical exergy should be split into thermal and mechanical exergy (default is False).
        """
        self.Tamb = Tamb
        self.pamb = pamb
        self._component_data = component_data
        self._connection_data = connection_data
        self.chemExLib = chemExLib
        self.chemical_exergy_enabled = self.chemExLib is not None
        self.split_physical_exergy = split_physical_exergy

        # Convert the parsed data into components
        self.components = _construct_components(component_data, connection_data, Tamb)
        self.connections = connection_data

    def analyse(self, E_F, E_P, E_L={}) -> None:
        """
        Run the exergy analysis for the entire system and calculate overall exergy efficiency.

        Parameters
        ----------
        E_F : dict
            Dictionary containing input connections for fuel exergy (e.g., {"inputs": ["1", "2"]}).
        E_P : dict
            Dictionary containing input and output connections for product exergy (e.g., {"inputs": ["E1"], "outputs": ["T1", "T2"]}).
        E_L : dict, optional
            Dictionary containing input and output connections for loss exergy (default is {}).
        """
        # Initialize class attributes for the exergy value of the total system
        self.E_F = 0.0
        self.E_P = 0.0
        self.E_L = 0.0
        self.E_F_dict = E_F
        self.E_P_dict = E_P
        self.E_L_dict = E_L

        for ex_flow in [E_F, E_P, E_L]:
            for connections in ex_flow.values():
                for connection in connections:
                    if connection not in self.connections:
                        msg = (
                            f"The connection {connection} is not part of the "
                            "plant's connections."
                        )
                        raise ValueError(msg)

        # Calculate total fuel exergy (E_F) by summing up all specified input connections
        if "inputs" in E_F:
            self.E_F += sum(
                self.connections[conn]['E']
                for conn in E_F["inputs"]
                if self.connections[conn]['E'] is not None
            )

        if "outputs" in E_F:
            self.E_F -= sum(
                self.connections[conn]['E']
                for conn in E_F["outputs"]
                if self.connections[conn]['E'] is not None
            )

        # Calculate total product exergy (E_P) by summing up all specified input and output connections
        if "inputs" in E_P:
            self.E_P += sum(
                self.connections[conn]['E']
                for conn in E_P["inputs"]
                if self.connections[conn]['E'] is not None
            )
        if "outputs" in E_P:
            self.E_P -= sum(
                self.connections[conn]['E']
                for conn in E_P["outputs"]
                if self.connections[conn]['E'] is not None
            )

        # Calculate total loss exergy (E_L) by summing up all specified input and output connections
        if "inputs" in E_L:
            self.E_L += sum(
                self.connections[conn]['E']
                for conn in E_L["inputs"]
                if self.connections[conn]['E'] is not None
            )
        if "outputs" in E_L:
            self.E_L -= sum(
                self.connections[conn]['E']
                for conn in E_L["outputs"]
                if self.connections[conn]['E'] is not None
            )

        # Calculate overall exergy efficiency epsilon = E_P / E_F
        # E_F == 0 should throw an error because it does not make sense
        self.epsilon = self.E_P / self.E_F if self.E_F != 0 else None

        # The rest is counted as total exergy destruction with all components of the system
        self.E_D = self.E_F - self.E_P - self.E_L

        if self.epsilon is not None:
            eff_str = f"{self.epsilon:.2%}"
        else:
            eff_str = "N/A"
        logging.info(
            f"Overall exergy analysis completed: E_F = {self.E_F:.2f} kW, "
            f"E_P = {self.E_P:.2f} kW, E_L = {self.E_L:.2f} kW, "
            f"Efficiency = {eff_str}"
            )

        # Perform exergy balance for each individual component in the system
        total_component_E_D = 0.0
        for component_name, component in self.components.items():
            if component.__class__.__name__ == "CycleCloser":
                continue
            else:
                # Calculate E_F, E_D, E_P
                component.calc_exergy_balance(self.Tamb, self.pamb, self.split_physical_exergy)
                # Safely calculate y and y* avoiding division by zero
                if self.E_F != 0:
                    component.y = component.E_D / self.E_F
                    component.y_star = component.E_D / self.E_D if component.E_D is not None else None
                else:
                    component.y = None
                    component.y_star = None
                # Sum component destruction if available
                if component.E_D is not None:
                    total_component_E_D += component.E_D

        # Check if the sum of all component exergy destructions matches the overall system exergy destruction
        if not np.isclose(total_component_E_D, self.E_D, rtol=1e-5):
            logging.warning(f"Sum of component exergy destructions ({total_component_E_D:.2f} W) "
                            f"does not match overall system exergy destruction ({self.E_D:.2f} W).")
        else:
            logging.info(f"Exergy destruction check passed: Sum of component E_D matches overall E_D.")

    @classmethod
    def from_tespy(cls, model: str, Tamb=None, pamb=None, chemExLib=None, split_physical_exergy=True):
        """
        Create an instance of the ExergyAnalysis class from a tespy network or
        a tespy network export structure.

        Parameters
        ----------
        model : str | tespy.networks.network.Network
            Path to the tespy Network export or the actual Network instance.
        Tamb : float, optional
            Ambient temperature for analysis, default is None.
        pamb : float, optional
            Ambient pressure for analysis, default is None.
        chemExLib : str, optional
            Name of the library for chemical exergy tables.

        Returns
        -------
        ExergyAnalysis
            Instance of the ExergyAnalysis class.
        """
        from tespy.networks import Network

        from .parser.from_tespy.tespy_config import EXERPY_TESPY_MAPPINGS

        if isinstance(model, str):
            model = Network.from_json(model)
        elif isinstance(model, Network):
            pass
        else:
            msg = (
                "Model parameter must be a path to a valid tespy network "
                "export or a tespy network"
            )
            raise TypeError(msg)

        data = model.to_exerpy(Tamb, pamb, EXERPY_TESPY_MAPPINGS)
        data, Tamb, pamb = _process_json(data, Tamb, pamb, chemExLib, split_physical_exergy)
        return cls(data['components'], data['connections'], Tamb, pamb, chemExLib, split_physical_exergy)

    @classmethod
    def from_aspen(cls, path, Tamb=None, pamb=None, chemExLib=None, split_physical_exergy=True):
        """
        Create an instance of the ExergyAnalysis class from an Aspen model file.

        Parameters
        ----------
        path : str
            Path to the Ebsilon file (.bkp format).
        Tamb : float, optional
            Ambient temperature for analysis, default is None.
        pamb : float, optional
            Ambient pressure for analysis, default is None.
        chemExLib : str, optional
            Name of the chemical exergy library (if any).
        split_physical_exergy : bool, optional
            If True, separates physical exergy into thermal and mechanical components.

        Returns
        -------
        ExergyAnalysis
            An instance of the ExergyAnalysis class with parsed Ebsilon data.
        """

        from .parser.from_aspen import aspen_parser as aspen_parser

        # Check if the file is an Aspen file
        _, file_extension = os.path.splitext(path)

        if file_extension == '.bkp':
            logging.info("Running Ebsilon simulation and generating JSON data.")
            data = aspen_parser.run_aspen(path, split_physical_exergy=split_physical_exergy)
            logging.info("Simulation completed successfully.")

        else:
            # If the file format is not supported
            raise ValueError(
                f"Unsupported file format: {file_extension}. Please provide "
                "an Ebsilon (.bkp) file."
            )

        data, Tamb, pamb = _process_json(
            data, Tamb=Tamb, pamb=pamb, chemExLib=chemExLib, split_physical_exergy=split_physical_exergy,
            required_component_fields=["name", "type"]
        )
        return cls(data["components"], data["connections"], Tamb, pamb, chemExLib, split_physical_exergy)

    @classmethod
    def from_ebsilon(cls, path, Tamb=None, pamb=None, chemExLib=None, split_physical_exergy=True):
        """
        Create an instance of the ExergyAnalysis class from an Ebsilon model file.

        Parameters
        ----------
        path : str
            Path to the Ebsilon file (.ebs format).
        Tamb : float, optional
            Ambient temperature for analysis, default is None.
        pamb : float, optional
            Ambient pressure for analysis, default is None.
        chemExLib : str, optional
            Name of the chemical exergy library (if any).
        split_physical_exergy : bool, optional
            If True, separates physical exergy into thermal and mechanical components.

        Returns
        -------
        ExergyAnalysis
            An instance of the ExergyAnalysis class with parsed Ebsilon data.
        """

        from .parser.from_ebsilon import ebsilon_parser as ebs_parser

        # Check if the file is an Ebsilon file
        _, file_extension = os.path.splitext(path)

        if file_extension == '.ebs':
            logging.info("Running Ebsilon simulation and generating JSON data.")
            data = ebs_parser.run_ebsilon(path, split_physical_exergy=split_physical_exergy)
            logging.info("Simulation completed successfully.")

        else:
            # If the file format is not supported
            raise ValueError(
                f"Unsupported file format: {file_extension}. Please provide "
                "an Ebsilon (.ebs) file."
            )

        data, Tamb, pamb = _process_json(
            data, Tamb=Tamb, pamb=pamb, chemExLib=chemExLib, split_physical_exergy=split_physical_exergy,
            required_component_fields=["name", "type", "type_index"]
        )
        return cls(data["components"], data["connections"], Tamb, pamb, chemExLib, split_physical_exergy)

    @classmethod
    def from_json(cls, json_path: str, Tamb=None, pamb=None, chemExLib=None, split_physical_exergy=True):
        """
        Create an ExergyAnalysis instance from a JSON file.

        Parameters
        ----------
        json_path : str
            Path to JSON file containing component and connection data.
        Tamb : float, optional
            Ambient temperature in K. If None, extracted from JSON.
        pamb : float, optional
            Ambient pressure in Pa. If None, extracted from JSON.
        chemExLib : str, optional
            Name of chemical exergy library to use. Default is None.

        Returns
        -------
        ExergyAnalysis
            Configured instance with data from JSON file.

        Raises
        ------
        FileNotFoundError
            If JSON file does not exist.
        ValueError
            If JSON structure is invalid or missing required data.
        JSONDecodeError
            If JSON file is malformed.
        """
        data = _load_json(json_path)
        data, Tamb, pamb = _process_json(
            data, Tamb=Tamb, pamb=pamb, chemExLib=chemExLib, split_physical_exergy=split_physical_exergy
        )
        return cls(data['components'], data['connections'], Tamb, pamb, chemExLib, split_physical_exergy)

    def exergy_results(self, print_results=True):
        """
        Displays a table of exergy analysis results with columns for E_F, E_P, E_D, and epsilon for each component,
        and additional information for material and non-material connections.

        CycleCloser components are excluded from the component results.

        Parameters
        ----------
        print_results : bool, optional
            If True, prints the results as tables in the console (default is True).

        Returns
        -------
        tuple of pandas.DataFrame
            (df_component_results, df_material_connection_results, df_non_material_connection_results)
            with the exergy analysis results.
        """
        # Define the lambda function for safe multiplication
        convert = lambda x, factor: x * factor if x is not None else None

        # COMPONENTS
        component_results = {
            "Component": [],
            "E_F [kW]": [],
            "E_P [kW]": [],
            "E_D [kW]": [],
            "E_L [kW]": [],
            "ε [%]": [],
            "y [%]": [],
            "y* [%]": []
        }

        # Populate the dictionary with exergy analysis data from each component,
        # excluding CycleCloser components.
        for component_name, component in self.components.items():
            # Exclude components whose class name is "CycleCloser"
            if component.__class__.__name__ == "CycleCloser":
                continue

            component_results["Component"].append(component_name)
            # Convert E_F, E_P, E_D, E_L from W to kW and epsilon to percentage using the lambda
            E_F_kW = convert(component.E_F, 1e-3)
            E_P_kW = convert(component.E_P, 1e-3)
            E_D_kW = convert(component.E_D, 1e-3)
            E_L_kW = convert(getattr(component, 'E_L', None), 1e-3) if getattr(component, 'E_L', None) is not None else 0
            epsilon_percent = convert(component.epsilon, 1e2)

            component_results["E_F [kW]"].append(E_F_kW)
            component_results["E_P [kW]"].append(E_P_kW)
            component_results["E_D [kW]"].append(E_D_kW + E_L_kW)
            component_results["E_L [kW]"].append(0)
            component_results["ε [%]"].append(epsilon_percent)
            component_results["y [%]"].append(convert(component.y, 1e2))
            component_results["y* [%]"].append(convert(component.y_star, 1e2))

        # Convert the component dictionary into a pandas DataFrame
        df_component_results = pd.DataFrame(component_results)

        # Sort the DataFrame by the "Component" column
        df_component_results = df_component_results.sort_values(by="Component")

        # Add the overall results to the components as dummy component "TOT"
        df_component_results.loc["TOT", "E_F [kW]"] = convert(self.E_F, 1e-3)
        df_component_results.loc["TOT", "Component"] = 'TOT'
        df_component_results.loc["TOT", "E_L [kW]"] = convert(self.E_L, 1e-3)
        df_component_results.loc["TOT", "E_P [kW]"] = convert(self.E_P, 1e-3)
        df_component_results.loc["TOT", "E_D [kW]"] = convert(self.E_D, 1e-3)
        df_component_results.loc["TOT", "ε [%]"] = convert(self.epsilon, 1e2)
        # Calculate the total y [%] and y* [%] as the sum of the values for all components
        df_component_results.loc["TOT", "y [%]"] = df_component_results["y [%]"].sum()
        df_component_results.loc["TOT", "y* [%]"] = df_component_results["y* [%]"].sum()

        # MATERIAL CONNECTIONS
        material_connection_results = {
            "Connection": [],
            "m [kg/s]": [],
            "T [°C]": [],
            "p [bar]": [],
            "h [kJ/kg]": [],
            "s [J/kgK]": [],
            "E [kW]": [],
            "e^PH [kJ/kg]": [],
            "e^T [kJ/kg]": [],
            "e^M [kJ/kg]": [],
            "e^CH [kJ/kg]": []
        }

        # NON-MATERIAL CONNECTIONS
        non_material_connection_results = {
            "Connection": [],
            "Kind": [],
            "Energy Flow [kW]": [],
            "Exergy Flow [kW]": []
        }

        # Populate the dictionaries with exergy analysis data for each connection
        for conn_name, conn_data in self.connections.items():
            # Separate material and non-material connections based on fluid type
            kind = conn_data.get("kind", None)

            # Check if the connection is a non-material energy flow type
            if kind in {'power', 'heat'}:
                # Non-material connections: only record energy flow, converted to kW using lambda
                non_material_connection_results["Connection"].append(conn_name)
                non_material_connection_results["Kind"].append(kind)
                non_material_connection_results["Energy Flow [kW]"].append(convert(conn_data.get("energy_flow"), 1e-3))
                non_material_connection_results["Exergy Flow [kW]"].append(convert(conn_data.get("E"), 1e-3))
            elif kind == 'material':
                # Material connections: record full data with conversions using lambda
                material_connection_results["Connection"].append(conn_name)
                material_connection_results["m [kg/s]"].append(conn_data.get('m', None))
                material_connection_results["T [°C]"].append(conn_data.get('T') - 273.15)  # Convert to °C
                material_connection_results["p [bar]"].append(convert(conn_data.get('p'), 1e-5))  # Convert Pa to bar
                material_connection_results["h [kJ/kg]"].append(convert(conn_data.get('h'), 1e-3))  # Convert to kJ/kg
                material_connection_results["s [J/kgK]"].append(conn_data.get('s', None))
                material_connection_results["e^PH [kJ/kg]"].append(convert(conn_data.get('e_PH'), 1e-3))  # Convert to kJ/kg
                material_connection_results["e^T [kJ/kg]"].append(convert(conn_data.get('e_T'), 1e-3))    # Convert to kJ/kg
                material_connection_results["e^M [kJ/kg]"].append(convert(conn_data.get('e_M'), 1e-3))    # Convert to kJ/kg
                material_connection_results["e^CH [kJ/kg]"].append(convert(conn_data.get('e_CH'), 1e-3))  # Convert to kJ/kg
                material_connection_results["E [kW]"].append(convert(conn_data.get("E"), 1e-3))          # Convert to kW

        # Convert the material and non-material connection dictionaries into DataFrames
        df_material_connection_results = pd.DataFrame(material_connection_results)
        df_non_material_connection_results = pd.DataFrame(non_material_connection_results)

        # Sort the DataFrames by the "Connection" column
        df_material_connection_results = df_material_connection_results.sort_values(by="Connection")
        df_non_material_connection_results = df_non_material_connection_results.sort_values(by="Connection")

        if print_results:
            # Print the material connection results DataFrame in the console in a table format
            print("\nMaterial Connection Exergy Analysis Results:")
            print(tabulate(df_material_connection_results.reset_index(drop=True), headers='keys', tablefmt='psql', floatfmt='.3f'))

            # Print the non-material connection results DataFrame in the console in a table format
            print("\nNon-Material Connection Exergy Analysis Results:")
            print(tabulate(df_non_material_connection_results.reset_index(drop=True), headers='keys', tablefmt='psql', floatfmt='.3f'))

            # Print the component results DataFrame in the console in a table format
            print("\nComponent Exergy Analysis Results:")
            print(tabulate(df_component_results.reset_index(drop=True), headers='keys', tablefmt='psql', floatfmt='.3f'))

        return df_component_results, df_material_connection_results, df_non_material_connection_results

    def export_to_json(self, output_path):
        """
        Export the model to a JSON file.
        
        Parameters
        ----------
        output_path : str
            Path where the JSON file will be saved.
        
        Returns
        -------
        None
            The model is saved to the specified path.
        
        Notes
        -----
        This method serializes the model using the internal _serialize method
        and writes the resulting data to a JSON file with indentation.
        """
        data = self._serialize()
        with open(output_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
            logging.info(f"Model exported to JSON file: {output_path}.")

    def _serialize(self):
        """
        Serializes the analysis data into a dictionary for export.
        Returns
        -------
        export : dict
            Dictionary containing serialized data with the following structure:
            - components: Component data
            - connections: Connection data
            - ambient_conditions: Ambient temperature and pressure with units
            - settings: Analysis settings including exergy splitting mode and chemical exergy library
        """
        export = {}
        export["components"] = self._component_data
        export["connections"] = self._connection_data
        export["ambient_conditions"] = {
            "Tamb": self.Tamb,
            "Tamb_unit": "K",
            "pamb": self.pamb,
            "pamb_unit": "Pa"
        }
        export["settings"] = {
            "split_physical_exergy": self.split_physical_exergy,
            "chemExLib": self.chemExLib
        }

        return export


def _construct_components(component_data, connection_data, Tamb):
    """
    Constructs component instances from component and connection data.
    Parameters
    ----------
    component_data : dict
        Dictionary containing component data organized by type.
        Format: {component_type: {component_name: {parameters}}}
    connection_data : dict
        Dictionary containing connection information between components.
        Each connection contains source and target component information.
    Tamb : float
        Ambient temperature, used for determining if a valve is dissipative.
    Returns
    -------
    dict
        Dictionary of instantiated components, with component names as keys.
    Notes
    -----
    Skips components of type 'Splitter'. For valves, automatically determines if they
    are dissipative by comparing inlet and outlet temperatures to ambient temperature.
    """
    components = {}  # Initialize a dictionary to store created components

    # Loop over component types (e.g., 'Combustion Chamber', 'Compressor')
    for component_type, component_instances in component_data.items():
        for component_name, component_information in component_instances.items():
            # Skip components of type 'Splitter'
            if component_type == "Splitter" or component_information.get('type') == "Splitter":
                logging.info(f"Skipping 'Splitter' component during the exergy analysis: {component_name}")
                continue  # Skip this component

            # Fetch the corresponding class from the registry using the component type
            component_class = component_registry.items.get(component_type)

            if component_class is None:
                logging.warning(f"Component type '{component_type}' is not registered.")
                continue

            # Instantiate the component with its attributes
            component = component_class(**component_information)

            # Initialize empty dictionaries for inlets and outlets
            component.inl = {}
            component.outl = {}

            # Assign streams to the components based on connection data
            for conn_id, conn_info in connection_data.items():
                # Assign inlet streams
                if conn_info['target_component'] == component_name:
                    target_connector_idx = conn_info['target_connector']  # Use 0-based indexing
                    component.inl[target_connector_idx] = conn_info  # Assign inlet stream

                # Assign outlet streams
                if conn_info['source_component'] == component_name:
                    source_connector_idx = conn_info['source_connector']  # Use 0-based indexing
                    component.outl[source_connector_idx] = conn_info  # Assign outlet stream

            # --- NEW: Automatically mark Valve components as dissipative ---
            # Here we assume that if a Valve's first inlet and first outlet have temperatures (key "T")
            # above the ambient temperature (Tamb), it is dissipative.
            if component_type == "Valve":
                try:
                    # Grab the temperature from the first inlet and outlet
                    T_in = list(component.inl.values())[0].get("T", None)
                    T_out = list(component.outl.values())[0].get("T", None)
                    if T_in is not None and T_out is not None and T_in > Tamb and T_out > Tamb:
                        component.is_dissipative = True
                    else:
                        component.is_dissipative = False
                except Exception as e:
                    logging.warning(f"Could not evaluate dissipativity for Valve '{component_name}': {e}")
                    component.is_dissipative = False
            else:
                component.is_dissipative = False

            # Store the component in the dictionary
            components[component_name] = component

    return components  # Return the dictionary of created components


def _load_json(json_path):
    """
    Load and validate a JSON file.
    Parameters
    ----------
    json_path : str
        Path to the JSON file to load.
    Returns
    -------
    dict
        The loaded JSON content.
    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.
    ValueError
        If the file does not have a .json extension.
    json.JSONDecodeError
        If the file content is not valid JSON.
    """
    # Check file existence and extension
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"File not found: {json_path}")

    if not json_path.endswith('.json'):
        raise ValueError("File must have .json extension")

    # Load and validate JSON
    with open(json_path, 'r') as file:
        return json.load(file)


def _process_json(data, Tamb=None, pamb=None, chemExLib=None, split_physical_exergy=True, required_component_fields=['name']):
    """Process JSON data to prepare it for exergy analysis.
    This function validates the data structure, ensures all required fields are present,
    and enriches the data with chemical exergy and total exergy flow calculations.
    Parameters
    ----------
    data : dict
        Dictionary containing system data with components, connections and ambient conditions
    Tamb : float, optional
        Ambient temperature in K, overrides the value in data if provided
    pamb : float, optional
        Ambient pressure in Pa, overrides the value in data if provided
    chemExLib : dict, optional
        Chemical exergy library for reference values
    split_physical_exergy : bool, default=True
        Whether to split physical exergy into thermal and mechanical parts
    required_component_fields : list, default=['name']
        List of fields that must be present in each component
    Returns
    -------
    tuple
        (processed_data, ambient_temperature, ambient_pressure)
    Raises
    ------
    ValueError
        If required sections or fields are missing, or if data structure is invalid
    """
    # Validate required sections
    required_sections = ['components', 'connections', 'ambient_conditions']
    missing_sections = [s for s in required_sections if s not in data]
    if missing_sections:
        raise ValueError(f"Missing required sections: {missing_sections}")

    # Check for mass_composition in material streams if chemical exergy is requested
    if chemExLib:
        for conn_name, conn_data in data['connections'].items():
            if conn_data.get('kind') == 'material' and 'mass_composition' not in conn_data:
                raise ValueError(f"Material stream '{conn_name}' missing mass_composition")

    # Extract or use provided ambient conditions
    Tamb = Tamb or data['ambient_conditions'].get('Tamb')
    pamb = pamb or data['ambient_conditions'].get('pamb')

    if Tamb is None or pamb is None:
        raise ValueError("Ambient conditions (Tamb, pamb) must be provided either in JSON or as parameters")

    # Validate component data structure
    if not isinstance(data['components'], dict):
        raise ValueError("Components section must be a dictionary")

    for comp_type, components in data['components'].items():
        if not isinstance(components, dict):
            raise ValueError(f"Component type '{comp_type}' must contain dictionary of components")

        for comp_name, comp_data in components.items():
            missing_fields = [f for f in required_component_fields if f not in comp_data]
            if missing_fields:
                raise ValueError(f"Component '{comp_name}' missing required fields: {missing_fields}")

    # Validate connection data structure
    for conn_name, conn_data in data['connections'].items():
        required_conn_fields = ['kind', 'source_component', 'target_component']
        missing_fields = [f for f in required_conn_fields if f not in conn_data]
        if missing_fields:
            raise ValueError(f"Connection '{conn_name}' missing required fields: {missing_fields}")

    # Add chemical exergy if library provided
    if chemExLib:
        data = add_chemical_exergy(data, Tamb, pamb, chemExLib)
        logging.info("Added chemical exergy values")
    else:
        logging.warning("You haven't provided a chemical exergy library. Chemical exergy values will not be added.")

    # Calculate total exergy flows
    data = add_total_exergy_flow(data, split_physical_exergy)
    logging.info("Added total exergy flows")

    return data, Tamb, pamb


class ExergoeconomicAnalysis:
    """"
    This class performs exergoeconomic analysis on a previously completed exergy analysis.
    It takes the results from an ExergyAnalysis instance and builds upon them
    to conduct a complete exergoeconomic analysis. It constructs and solves a system
    of linear equations to determine the costs (both total and specific) associated
    with each exergy stream in the system, and calculates various exergoeconomic indicators
    for each component.

    Attributes
    ----------
    exergy_analysis : ExergyAnalysis
        The exergy analysis instance used as the basis for calculations.
    connections : dict
        Dictionary of all energy/material connections in the system.
    components : dict
        Dictionary of all components in the system.
    chemical_exergy_enabled : bool
        Flag indicating if chemical exergy is considered in calculations.
    E_F_dict : dict
        Dictionary mapping fuel streams to components.
    E_P_dict : dict
        Dictionary mapping product streams to components.
    E_L_dict : dict
        Dictionary mapping loss streams to components.
    num_variables : int
        Number of cost variables in the exergoeconomic equations.
    variables : dict
        Dictionary mapping variable indices to variable names.
    equations : dict
        Dictionary mapping equation indices to equation types.
    currency : str
        Currency symbol used in cost reporting.
    system_costs : dict
        Dictionary of system-level costs after analysis.

    Methods
    -------
    initialize_cost_variables()
        Defines and indexes all cost variables in the system.
    assign_user_costs(Exe_Eco_Costs)
        Assigns user-defined costs to components and input streams.
    construct_matrix(Tamb)
        Constructs the linear equation system for exergoeconomic analysis.
    solve_exergoeconomic_analysis(Tamb)
        Solves the cost equations and assigns results to connections and components.
    run(Exe_Eco_Costs, Tamb)
        Executes the complete exergoeconomic analysis workflow.
    exergoeconomic_results(print_results=True)
        Displays and returns tables of exergoeconomic analysis results.
    """

    def __init__(self, exergy_analysis_instance, currency="EUR"):
        """
        Initialize an economic analysis for an exergy analysis.

        Parameters
        ----------
        exergy_analysis_instance : ExergyAnalysis
            Instance of ExergyAnalysis that has already performed exergy calculations.
        currency : str, optional
            Currency symbol for cost calculations, by default "EUR".

        Notes
        -----
        This class inherits all exergy analysis results from the provided instance
        and prepares data structures for economic equations and cost variables.
        """
        self.exergy_analysis = exergy_analysis_instance
        self.connections = exergy_analysis_instance.connections
        self.components = exergy_analysis_instance.components
        self.chemical_exergy_enabled = exergy_analysis_instance.chemical_exergy_enabled
        self.E_F_dict = exergy_analysis_instance.E_F_dict
        self.E_P_dict = exergy_analysis_instance.E_P_dict
        self.E_L_dict = exergy_analysis_instance.E_L_dict
        self.num_variables = 0  # Track number of equations (or cost variables) for the matrix
        self.variables = {}  # New dictionary to map variable indices to names
        self.equations = {}  # New dictionary to map equation indices to kind of equation
        self.currency = currency  # EUR is default currency for cost calculations

    def initialize_cost_variables(self):
        """
        Initialize cost variables for the exergoeconomic analysis.

        This method assigns unique indices to each cost variable in the matrix system
        and populates a dictionary mapping these indices to variable names.
        
        For material streams, separate indices are assigned for thermal, mechanical,
        and chemical exergy components when chemical exergy is enabled (otherwise only
        thermal and mechanical). For non-material streams (heat, power), a single index
        is assigned for the total exergy cost.
        
        Notes
        -----
        The assigned indices are used for constructing the cost balance equations
        in the matrix system that will be solved to find all cost variables.
        """
        col_number = 0
        valid_components = {comp.name for comp in self.components.values()}

        # Process each connection (stream) which is part of the system (has a valid source or target)
        for name, conn in self.connections.items():
            conn["name"] = name  # Add the connection name to the dictionary
            is_part_of_the_system = (conn.get("source_component") in valid_components) or \
                                    (conn.get("target_component") in valid_components)
            if not is_part_of_the_system:
                continue
            else:
                kind = conn.get("kind", "material")
                # For material streams, assign indices based on the flag.
                if kind == "material":
                    if self.exergy_analysis.chemical_exergy_enabled:
                        conn["CostVar_index"] = {
                            "T": col_number,
                            "M": col_number + 1,
                            "CH": col_number + 2
                        }
                        self.variables[str(col_number)]     = f"C_{name}_T"
                        self.variables[str(col_number + 1)] = f"C_{name}_M"
                        self.variables[str(col_number + 2)] = f"C_{name}_CH"
                        col_number += 3
                    else:
                        conn["CostVar_index"] = {
                            "T": col_number,
                            "M": col_number + 1
                        }
                        self.variables[str(col_number)]     = f"C_{name}_T"
                        self.variables[str(col_number + 1)] = f"C_{name}_M"
                        col_number += 2
                    # Check if this connection's target is a dissipative component.
                    target = conn.get("target_component")
                    if target in valid_components:
                        comp = self.exergy_analysis.components.get(target)
                        if comp is not None and getattr(comp, "is_dissipative", False):
                            # Add an extra index for the dissipative cost difference.
                            conn["CostVar_index"]["dissipative"] = col_number
                            self.variables[str(col_number)] = "dissipative"
                            col_number += 1
                # For non-material streams (e.g., heat, power), assign one index.
                elif kind in ("heat", "power"):
                    conn["CostVar_index"] = {"exergy": col_number}
                    self.variables[str(col_number)] = f"C_{name}_TOT"
                    col_number += 1

        # Store the total number of cost variables for later use.
        self.num_variables = col_number

    def assign_user_costs(self, Exe_Eco_Costs):
        """
        Assign component and connection costs from user input dictionary.

        Parameters
        ----------
        Exe_Eco_Costs : dict
            Dictionary containing cost assignments for components and connections.
            Format for components: "<component_name>_Z": cost_value [currency/h]
            Format for connections: "<connection_name>_c": cost_value [currency/GJ]

        Raises
        ------
        ValueError
            If a component cost is missing or if a required input connection cost is not provided.

        Notes
        -----
        Component costs are converted from [currency/h] to [currency/s].
        Connection costs are converted from [currency/GJ] to [currency/J].
        Material connections receive c_T, c_M, c_CH cost breakdowns.
        Heat and power connections receive only c_TOT values.
        """
        # --- Component Costs ---
        for comp_name, comp in self.components.items():
            if isinstance(comp, CycleCloser):
                continue
            else:
                cost_key = f"{comp_name}_Z"
                if cost_key in Exe_Eco_Costs:
                    comp.Z_costs = Exe_Eco_Costs[cost_key] / 3600  # Convert currency/h to currency/s
                else:
                    raise ValueError(f"Cost for component '{comp_name}' is mandatory but not provided in Exe_Eco_Costs.")

        # --- Connection Costs ---
        accepted_kinds = {"material", "heat", "power"}
        for conn_name, conn in self.connections.items():
            kind = conn.get("kind", "material")

            # Only consider valid connection types
            if kind not in accepted_kinds:
                continue

            cost_key = f"{conn_name}_c"

            # Check if the connection is an input (but also not an output)
            is_input = not conn.get("source_component") and conn.get("target_component")

            # For input connections (except for power connections) a cost is mandatory.
            if is_input and kind != "power" and cost_key not in Exe_Eco_Costs:
                raise ValueError(f"Cost for input connection '{conn_name}' is mandatory but not provided in Exe_Eco_Costs.")

            # Assign cost if provided.
            if cost_key in Exe_Eco_Costs:
                # Convert cost from currency/GJ to currency/J.
                c_TOT = Exe_Eco_Costs[cost_key] * 1e-9
                conn["c_TOT"] = c_TOT

                if kind == "material":
                    # Compute C_TOT based on exergy terms and mass flow.
                    conn["C_TOT"] = c_TOT * conn.get("E", 0)

                    # Assign cost breakdown for material streams.
                    if self.chemical_exergy_enabled:
                        exergy_terms = {"T": "e_T", "M": "e_M", "CH": "e_CH"}
                    else:
                        exergy_terms = {"T": "e_T", "M": "e_M"}
                    for label, exergy_key in exergy_terms.items():
                        conn[f"c_{label}"] = c_TOT
                        conn[f"C_{label}"] = c_TOT * conn.get(exergy_key, 0) * conn.get("m", 0)

                elif kind in {"heat", "power"}:
                    # Ensure energy flow "E" is present before computing cost.
                    if "E" not in conn:
                        raise ValueError(f"Energy flow 'E' is missing for {kind} connection '{conn_name}'.")

                    # Assign only the total cost for heat and power streams.
                    conn["C_TOT"] = c_TOT * conn["E"]


    def construct_matrix(self, Tamb):
        """
        Construct the exergoeconomic cost matrix and vector.
        
        Parameters
        ----------
        Tamb : float
            Ambient temperature in Kelvin.
            
        Returns
        -------
        tuple
            A tuple containing:
            - A: numpy.ndarray - The coefficient matrix for the linear equation system
            - b: numpy.ndarray - The right-hand side vector for the linear equation system
            
        Notes
        -----
        This method constructs a system of linear equations that includes:
        1. Cost balance equations for each productive component
        2. Equations for inlet streams to fix their costs based on provided values
        3. Auxiliary equations for power flows
        4. Custom auxiliary equations from each component
        5. Special equations for dissipative components
        """
        num_vars = self.num_variables
        A = np.zeros((num_vars, num_vars))
        b = np.zeros(num_vars)
        counter = 0

        # Filter out CycleCloser instances, keeping the component objects.
        valid_components = [comp for comp in self.components.values() if not isinstance(comp, CycleCloser)]
        # Create a set of valid component names for cost balance comparisons.
        valid_component_names = {comp.name for comp in valid_components}

        # 1. Cost balance equations for productive components.
        for comp in valid_components:
            if not getattr(comp, "is_dissipative", False):
            # Assign the row index for the cost balance equation to this component.
                comp.exergy_cost_line = counter
                for conn in self.connections.values():
                    # Check if the connection is linked to a valid component.
                    # If the connection's target is the component, it is an inlet (add +1).
                    if conn.get("target_component") == comp.name:
                        for key, col in conn["CostVar_index"].items():
                            A[counter, col] = 1  # Incoming costs
                    # If the connection's source is the component, it is an outlet (subtract -1).
                    elif conn.get("source_component") == comp.name:
                        for key, col in conn["CostVar_index"].items():
                            A[counter, col] = -1  # Outgoing costs
                    self.equations[counter] = f"Z_costs_{comp.name}"  # Store the equation name

            # For productive components: C_in - C_out = -Z_costs.
            if getattr(comp, "is_dissipative", False):
                continue
            else:
                b[counter] = -getattr(comp, "Z_costs", 1)
                counter += 1

        # 2. Inlet stream equations.
        # Gather all power connections.
        power_conns = [conn for conn in self.connections.values() if conn.get("kind") == "power"]
        # Set the flag: if any power connection has NO target component, then there is an outlet.
        has_power_outlet = any(conn.get("target_component") is None for conn in power_conns)

        for name, conn in self.connections.items():
            # A connection is treated as an inlet if its source_component is missing or not part of the system
            # and its target_component is among the valid components.
            if (conn.get("source_component") is None or conn.get("source_component") not in self.components) \
                    and (conn.get("target_component") in valid_component_names):
                kind = conn.get("kind", "material")
                if kind == "material":
                    if self.chemical_exergy_enabled:
                        exergy_terms = ["T", "M", "CH"]
                    else:
                        exergy_terms = ["T", "M"]
                    for label in exergy_terms:
                        idx = conn["CostVar_index"][label]
                        A[counter, idx] = 1  # Fix the cost variable.
                        b[counter] = conn.get(f"C_{label}", conn.get("C_TOT", 0))
                        self.equations[counter] = f"boundary_stream_costs_{name}_{label}"
                        counter += 1
                elif kind == "heat":
                    idx = conn["CostVar_index"]["exergy"]
                    A[counter, idx] = 1
                    b[counter] = conn.get("C_TOT", 0)
                    self.equations[counter] = f"boundary_stream_costs_{name}_TOT"
                    counter += 1
                elif kind == "power":
                    if not has_power_outlet:
                        # Skip this connection if the user did not define a cost (i.e. C_TOT is missing or zero).
                        if not conn.get("C_TOT"):
                            continue
                        idx = conn["CostVar_index"]["exergy"]
                        A[counter, idx] = 1
                        b[counter] = conn.get("C_TOT", 0)
                        self.equations[counter] = f"boundary_stream_costs_{name}_TOT"
                        counter += 1
                    else:
                        continue

        # 3. Auxiliary equations for the equality of the specific costs
        # of all power flows at the input or output of the system.
        power_conns = [conn for conn in self.connections.values()
                    if conn.get("kind") == "power" and
                    (conn.get("source_component") not in valid_component_names or conn.get("target_component") not in valid_component_names) and not
                    (conn.get("source_component") not in valid_component_names and conn.get("target_component") not in valid_component_names)]

        # Only add auxiliary equations if there is more than one power connection.
        if len(power_conns) > 1:
            # Choose the first connection as reference.
            ref = power_conns[0]
            ref_idx = ref["CostVar_index"]["exergy"]
            for conn in power_conns[1:]:
                cur_idx = conn["CostVar_index"]["exergy"]
                A[counter, ref_idx] = 1 / ref["E"] if ref["E"] != 0 else 1
                A[counter, cur_idx] = -1 / conn["E"] if conn["E"] != 0 else -1
                b[counter] = 0
                self.equations[counter] = f"aux_power_eq_{ref['name']}_{conn['name']}"
                counter += 1

        # 4. Auxiliary equations.
        # These equations are needed because we have more variables than components.
        # For each productive component call its auxiliary equation routine, if available.
        for comp in self.components.values():
            if getattr(comp, "is_dissipative", False):
                continue
            else:
                if hasattr(comp, "aux_eqs") and callable(comp.aux_eqs):
                    # The aux_eqs function should accept the current matrix, vector, counter, and Tamb,
                    # and return the updated (A, b, counter).
                    A, b, counter, self.equations = comp.aux_eqs(A, b, counter, Tamb, self.equations, self.chemical_exergy_enabled)
                else:
                    # If no auxiliary equations are provided.
                    logging.warning(f"No auxiliary equations provided for component '{comp.name}'.")

        # 5. Dissipative components:
        # Now, for each dissipative component, call its dis_eqs() method.
        # This will build an equation that integrates the dissipative cost difference (C_diff)
        # into the overall cost balance (i.e. it charges the component’s Z_costs accordingly).
        for comp in self.components.values():
            if getattr(comp, "is_dissipative", False):
                if hasattr(comp, "dis_eqs") and callable(comp.dis_eqs):
                    # Let the component provide its own modifications for the cost matrix.
                    A, b, counter, self.equations = comp.dis_eqs(A, b, counter, Tamb, self.equations, self.chemical_exergy_enabled, list(self.components.values()))

        return A, b


    def solve_exergoeconomic_analysis(self, Tamb):
        """
        Solve the exergoeconomic cost balance equations and assign the results to connections and components.
        
        Parameters
        ----------
        Tamb : float
            Ambient temperature in Kelvin.
            
        Returns
        -------
        tuple
            (exergy_cost_matrix, exergy_cost_vector) - The coefficient matrix and right-hand side vector used 
            in the linear equation system.
            
        Raises
        ------
        ValueError
            If the exergoeconomic system is singular or if the cost balance is not satisfied.
            
        Notes
        -----
        This method performs the following steps:
        1. Constructs the exergoeconomic cost matrix
        2. Solves the system of linear equations
        3. Assigns cost solutions to connections
        4. Calculates component exergoeconomic indicators
        5. Distributes loss stream costs to product streams
        6. Computes system-level cost variables
        """
        # Step 1: Construct the cost matrix
        exergy_cost_matrix, exergy_cost_vector = self.construct_matrix(Tamb)

        # Step 2: Solve the system of equations
        try:
            C_solution = np.linalg.solve(exergy_cost_matrix, exergy_cost_vector)
        except np.linalg.LinAlgError:
            raise ValueError(f"Exergoeconomic system is singular and cannot be solved. "
                             f"Provided equations: {len(self.equations)}, variables in system: {len(self.variables)}")

        # Step 3: Assign solutions to connections
        for conn_name, conn in self.connections.items():
            is_part_of_the_system = conn.get("source_component") or conn.get("target_component")
            if not is_part_of_the_system:
                continue
            else:
                kind = conn.get("kind")
                if kind == "material":
                    # Retrieve mass flow and specific exergy values
                    m_val = conn.get("m", 1)         # mass flow [kg/s]
                    e_T = conn.get("e_T", 0)         # thermal specific exergy [kJ/kg]
                    e_M = conn.get("e_M", 0)         # mechanical specific exergy [kJ/kg]
                    E_T = m_val * e_T                # thermal exergy flow [kW]
                    E_M = m_val * e_M                # mechanical exergy flow [kW]

                    conn["C_T"] = C_solution[conn["CostVar_index"]["T"]]
                    conn["c_T"] = conn["C_T"] / E_T if E_T != 0 else np.nan

                    conn["C_M"] = C_solution[conn["CostVar_index"]["M"]]
                    conn["c_M"] = conn["C_M"] / E_M if E_M != 0 else np.nan

                    conn["C_PH"] = conn["C_T"] + conn["C_M"]
                    conn["c_PH"] = conn["C_PH"] / (E_T + E_M) if (E_T + E_M) != 0 else np.nan

                    if self.chemical_exergy_enabled:
                        e_CH = conn.get("e_CH", 0)   # chemical specific exergy [kJ/kg]
                        E_CH = m_val * e_CH         # chemical exergy flow [kW]
                        conn["C_CH"] = C_solution[conn["CostVar_index"]["CH"]]
                        conn["c_CH"] = conn["C_CH"] / E_CH if E_CH != 0 else np.nan
                        conn["C_TOT"] = conn["C_T"] + conn["C_M"] + conn["C_CH"]
                        total_E = E_T + E_M + E_CH
                        conn["c_TOT"] = conn["C_TOT"] / total_E if total_E != 0 else np.nan
                    else:
                        conn["C_TOT"] = conn["C_T"] + conn["C_M"]
                        total_E = E_T + E_M
                        conn["c_TOT"] = conn["C_TOT"] / total_E if total_E != 0 else np.nan
                elif kind in {"heat", "power"}:
                    conn["C_TOT"] = C_solution[conn["CostVar_index"]["exergy"]]
                    conn["c_TOT"] = conn["C_TOT"] / conn.get("E", 1)

        # Step 4: Assign C_P, C_F, C_D, and f values to components
        for comp in self.exergy_analysis.components.values():
            if hasattr(comp, "exergoeconomic_balance") and callable(comp.exergoeconomic_balance):
                comp.exergoeconomic_balance(self.exergy_analysis.Tamb)

        # Step 5: Distribute the cost of loss streams to the product streams.
        # For each loss stream (provided in E_L_dict), its C_TOT is distributed among the product streams (in E_P_dict)
        # in proportion to their exergy (E). After the distribution the loss stream's C_TOT is set to zero.
        loss_streams = self.E_L_dict.get("inputs", [])
        product_streams = self.E_P_dict.get("inputs", [])
        for loss_name in loss_streams:
            loss_conn = self.connections.get(loss_name)
            if loss_conn is None:
                continue
            loss_cost = loss_conn.get("C_TOT", 0)
            # If there is no cost assigned to this loss stream, skip it.
            if not loss_cost:
                continue
            # Calculate the total exergy of the product streams.
            total_E = 0
            for prod_name in product_streams:
                prod_conn = self.connections.get(prod_name)
                if prod_conn is None:
                    continue
                total_E += prod_conn.get("E", 0)
            # Avoid division by zero.
            if total_E == 0:
                continue
            # Distribute the loss cost to each product stream proportionally to its exergy.
            for prod_name in product_streams:
                prod_conn = self.connections.get(prod_name)
                if prod_conn is None:
                    continue
                prod_E = prod_conn.get("E", 0)
                share = loss_cost * (prod_E / total_E)
                prod_conn["C_TOT"] = prod_conn.get("C_TOT", 0) + share
                prod_conn["c_TOT"] = prod_conn["C_TOT"] / prod_conn.get("E", 1)
            # The cost of the loss streams are not set to zero to show
            # them in the table, but they are attributed to the product streams.

        # Step 6: Compute system-level cost variables using the E_F and E_P dictionaries.
        # Compute total fuel cost (C_F_total) from fuel streams.
        C_F_total = 0.0
        for conn_name in self.E_F_dict.get("inputs", []):
            conn = self.connections.get(conn_name, {})
            C_F_total += conn.get("C_TOT", 0)
        for conn_name in self.E_F_dict.get("outputs", []):
            conn = self.connections.get(conn_name, {})
            C_F_total -= conn.get("C_TOT", 0)

        # Compute total product cost (C_P_total) from product streams.
        C_P_total = 0.0
        for conn_name in self.E_P_dict.get("inputs", []):
            conn = self.connections.get(conn_name, {})
            C_P_total += conn.get("C_TOT", 0)
        for conn_name in self.E_P_dict.get("outputs", []):
            conn = self.connections.get(conn_name, {})
            C_P_total -= conn.get("C_TOT", 0)

        # The total loss cost is assigned to the product already, so we don't need to consider it here.

        # Compute the sum of all Z costs (Z_total) from all components except CycleCloser.
        Z_total = 0.0
        for comp in self.exergy_analysis.components.values():
            # Sum Z_costs from all non-CycleCloser components, converting from currency/s to currency/h.
            if comp.__class__.__name__ != "CycleCloser":
                Z_total += getattr(comp, "Z_costs", 0)

        # convert the costs to currency/h
        C_F_total *= 3600
        C_P_total *= 3600
        Z_total *= 3600

        # Store the system-level costs in the exergy analysis instance.
        self.system_costs = {
            "C_F": float(C_F_total),
            "C_P": float(C_P_total),
            "Z": float(Z_total)
        }

        # Check cost balance and raise error if violated
        if abs(self.system_costs["C_P"] - self.system_costs["C_F"] - self.system_costs["Z"]) > 1e-4:
            raise ValueError(
                f"Exergoeconomic cost balance not satisfied: C_P ({self.system_costs['C_P']:.6f}) ≠ "
                f"C_F ({self.system_costs['C_F']:.6f}) + Z ({self.system_costs['Z']:.6f})"
            )

        return exergy_cost_matrix, exergy_cost_vector

    def run(self, Exe_Eco_Costs, Tamb):
        """
        Execute the full exergoeconomic analysis.
        
        Parameters
        ----------
        Exe_Eco_Costs : dict
            Dictionary containing cost assignments for components and connections.
            Format for components: "<component_name>_Z": cost_value [currency/h]
            Format for connections: "<connection_name>_c": cost_value [currency/GJ]
        Tamb : float
            Ambient temperature in Kelvin.
            
        Notes
        -----
        This method performs the complete exergoeconomic analysis by:
        1. Initializing cost variables for all components and streams
        2. Assigning user-defined costs to components and boundary streams
        3. Solving the system of exergoeconomic equations
        """
        self.initialize_cost_variables()
        self.assign_user_costs(Exe_Eco_Costs)
        self.solve_exergoeconomic_analysis(Tamb)
        logging.info(f"Exergoeconomic analysis completed successfully.")


    def exergoeconomic_results(self, print_results=True):
        """
        Displays tables of exergoeconomic analysis results with columns for costs and economic parameters for each component,
        and additional cost information for material and non-material connections.

        Parameters
        ----------
        print_results : bool, optional
            If True, prints the results as tables in the console (default is True).

        Returns
        -------
        tuple of pandas.DataFrame
            (df_component_results, df_material_connection_results_part1, df_material_connection_results_part2, df_non_material_connection_results)
            with the exergoeconomic analysis results.
        """
        # Retrieve the base exergy results without printing them
        df_comp, df_mat, df_non_mat = self.exergy_analysis.exergy_results(print_results=False)

        # -------------------------
        # Add new cost columns to the component results table.
        # We assume that each component (except CycleCloser, which is already excluded)
        # has attributes: C_F, C_P, C_D, and Z_cost (all in currency/s), which we convert to currency/h.
        C_F_list = []
        C_P_list = []
        C_D_list = []
        Z_cost_list = []
        r_list = []
        f_list = []

        # Iterate over the component DataFrame rows. The "Component" column contains the key.
        for idx, row in df_comp.iterrows():
            comp_name = row["Component"]
            if comp_name != "TOT":
                comp = self.components.get(comp_name, None)
                if comp is not None:
                    C_F_list.append(getattr(comp, "C_F", 0) * 3600)
                    C_P_list.append(getattr(comp, "C_P", 0) * 3600)
                    C_D_list.append(getattr(comp, "C_D", 0) * 3600)
                    Z_cost_list.append(getattr(comp, "Z_costs", 0) * 3600)
                    f_list.append(getattr(comp, "f", 0) * 100)
                    r_list.append(getattr(comp, "r", 0) * 100)
                else:
                    C_F_list.append(np.nan)
                    C_P_list.append(np.nan)
                    C_D_list.append(np.nan)
                    Z_cost_list.append(np.nan)
                    f_list.append(np.nan)
                    r_list.append(np.nan)
            else:
                # We'll update the TOT row using system-level values later.
                C_F_list.append(np.nan)
                C_P_list.append(np.nan)
                C_D_list.append(np.nan)
                Z_cost_list.append(np.nan)
                f_list.append(np.nan)
                r_list.append(np.nan)

        # Add the new columns to the component DataFrame.
        df_comp[f"C_F [{self.currency}/h]"] = C_F_list
        df_comp[f"C_P [{self.currency}/h]"] = C_P_list
        df_comp[f"C_D [{self.currency}/h]"] = C_D_list
        df_comp[f"Z [{self.currency}/h]"] = Z_cost_list
        df_comp[f"C_D+Z [{self.currency}/h]"] = df_comp[f"C_D [{self.currency}/h]"] + df_comp[f"Z [{self.currency}/h]"]
        df_comp[f"f [%]"] = f_list
        df_comp[f"r [%]"] = r_list

        # Update the TOT row with system-level values using .loc.
        df_comp.loc["TOT", f"C_F [{self.currency}/h]"] = self.system_costs.get("C_F", np.nan)
        df_comp.loc["TOT", f"C_P [{self.currency}/h]"] = self.system_costs.get("C_P", np.nan)
        df_comp.loc["TOT", f"Z [{self.currency}/h]"]   = self.system_costs.get("Z", np.nan)
        df_comp.loc["TOT", f"C_D+Z [{self.currency}/h]"] = (
            df_comp.loc["TOT", f"C_D [{self.currency}/h]"] +
            df_comp.loc["TOT", f"Z [{self.currency}/h]"]
        )

        df_comp[f"c_F [{self.currency}/GJ]"] = df_comp[f"C_F [{self.currency}/h]"] / df_comp["E_F [kW]"] * 1e6 / 3600
        df_comp[f"c_P [{self.currency}/GJ]"] = df_comp[f"C_P [{self.currency}/h]"] / df_comp["E_P [kW]"] * 1e6 / 3600

        df_comp.loc["TOT", f"C_D [{self.currency}/h]"] = df_comp.loc["TOT", f"c_F [{self.currency}/GJ]"] * df_comp.loc["TOT", f"E_D [kW]"] / 1e6 * 3600
        df_comp.loc["TOT", f"C_D+Z [{self.currency}/h]"] = df_comp.loc["TOT", f"C_D [{self.currency}/h]"] + df_comp.loc["TOT", f"Z [{self.currency}/h]"]
        df_comp.loc["TOT", f"f [%]"] = df_comp.loc["TOT", f"Z [{self.currency}/h]"] / df_comp.loc["TOT", f"C_D+Z [{self.currency}/h]"] * 100
        df_comp.loc["TOT", f"r [%]"] = ((df_comp.loc["TOT", f"c_P [{self.currency}/GJ]"] - df_comp.loc["TOT", f"c_F [{self.currency}/GJ]"]) /
                                         df_comp.loc["TOT", f"c_F [{self.currency}/GJ]"]) * 100

        # -------------------------
        # Add cost columns to material connections.
        # -------------------------
        # Uppercase cost columns (in currency/h)
        C_T_list = []
        C_M_list = []
        C_CH_list = []
        C_TOT_list = []
        # Lowercase cost columns (in GJ/{currency})
        c_T_list = []
        c_M_list = []
        c_CH_list = []
        c_TOT_list = []

        for idx, row in df_mat.iterrows():
            conn_name = row['Connection']
            conn_data = self.connections.get(conn_name, {})
            kind = conn_data.get("kind", None)
            if kind == "material":
                C_T = conn_data.get("C_T", None)
                C_M = conn_data.get("C_M", None)
                C_CH = conn_data.get("C_CH", None)
                C_TOT = conn_data.get("C_TOT", None)
                c_T = conn_data.get("c_T", None)
                c_M = conn_data.get("c_M", None)
                c_CH = conn_data.get("c_CH", None)
                c_TOT = conn_data.get("c_TOT", None)
                C_T_list.append(C_T * 3600 if C_T is not None else None)
                C_M_list.append(C_M * 3600 if C_M is not None else None)
                C_CH_list.append(C_CH * 3600 if C_CH is not None else None)
                C_TOT_list.append(C_TOT * 3600 if C_TOT is not None else None)
                c_T_list.append(c_T * 1e9 if c_T is not None else None)
                c_M_list.append(c_M * 1e9 if c_M is not None else None)
                c_CH_list.append(c_CH * 1e9 if c_CH is not None else None)
                c_TOT_list.append(c_TOT * 1e9 if c_TOT is not None else None)
            elif kind in {"heat", "power"}:
                # For non-material streams in the material table, only C^TOT is defined.
                C_T_list.append(np.nan)
                C_M_list.append(np.nan)
                C_CH_list.append(np.nan)
                c_T_list.append(np.nan)
                c_M_list.append(np.nan)
                c_CH_list.append(np.nan)
                C_TOT = conn_data.get("C_TOT", None)
                C_TOT_list.append(C_TOT * 3600 if C_TOT is not None else None)
                c_TOT = conn_data.get("C_TOT", None)
                c_TOT_list.append(c_TOT * 1e9 if c_TOT is not None else None)
            else:
                C_T_list.append(np.nan)
                C_M_list.append(np.nan)
                C_CH_list.append(np.nan)
                C_TOT_list.append(np.nan)
                c_T_list.append(np.nan)
                c_M_list.append(np.nan)
                c_CH_list.append(np.nan)
                c_TOT_list.append(np.nan)

        df_mat[f"C^T [{self.currency}/h]"] = C_T_list
        df_mat[f"C^M [{self.currency}/h]"] = C_M_list
        df_mat[f"C^CH [{self.currency}/h]"] = C_CH_list
        df_mat[f"C^TOT [{self.currency}/h]"] = C_TOT_list
        df_mat[f"c^T [GJ/{self.currency}]"] = c_T_list
        df_mat[f"c^M [GJ/{self.currency}]"] = c_M_list
        df_mat[f"c^CH [GJ/{self.currency}]"] = c_CH_list
        df_mat[f"c^TOT [GJ/{self.currency}]"] = c_TOT_list

        # -------------------------
        # Add cost columns to non-material connections.
        # -------------------------
        C_TOT_non_mat = []
        c_TOT_non_mat = []
        for idx, row in df_non_mat.iterrows():
            conn_name = row["Connection"]
            conn_data = self.connections.get(conn_name, {})
            C_TOT = conn_data.get("C_TOT", None)
            C_TOT_non_mat.append(C_TOT * 3600 if C_TOT is not None else None)
            c_TOT = conn_data.get("c_TOT", None)
            c_TOT_non_mat.append(c_TOT * 1e9 if c_TOT is not None else None)
        df_non_mat[f"C^TOT [{self.currency}/h]"] = C_TOT_non_mat
        df_non_mat[f"c^TOT [GJ/{self.currency}]"] = c_TOT_non_mat

        # -------------------------
        # Split the material connections into two tables according to your specifications.
        # -------------------------
        # df_mat1: Columns from mass flow until e^CH.
        df_mat1 = df_mat[[
            "Connection",
            "m [kg/s]",
            "T [°C]",
            "p [bar]",
            "h [kJ/kg]",
            "s [J/kgK]",
            "E [kW]",
            "e^PH [kJ/kg]",
            "e^T [kJ/kg]",
            "e^M [kJ/kg]",
            "e^CH [kJ/kg]"
        ]].copy()

        # df_mat2: Columns from E onward, plus the uppercase and lowercase cost columns.
        df_mat2 = df_mat[[
            "Connection",
            "E [kW]",
            "e^PH [kJ/kg]",
            "e^T [kJ/kg]",
            "e^M [kJ/kg]",
            "e^CH [kJ/kg]",
            f"C^T [{self.currency}/h]",
            f"C^M [{self.currency}/h]",
            f"C^CH [{self.currency}/h]",
            f"C^TOT [{self.currency}/h]",
            f"c^T [GJ/{self.currency}]",
            f"c^M [GJ/{self.currency}]",
            f"c^CH [GJ/{self.currency}]",
            f"c^TOT [GJ/{self.currency}]"
        ]].copy()

        # Remove any columns that contain only NaN values from df_mat1, df_mat2, and df_non_mat.
        df_mat1.dropna(axis=1, how='all', inplace=True)
        df_mat2.dropna(axis=1, how='all', inplace=True)
        df_non_mat.dropna(axis=1, how='all', inplace=True)

        # -------------------------
        # Print the four tables if requested.
        # -------------------------
        if print_results:
            print("\nExergoeconomic Analysis - Component Results:")
            print(tabulate(df_comp.reset_index(drop=True), headers="keys", tablefmt="psql", floatfmt=".3f"))
            print("\nExergoeconomic Analysis - Material Connection Results (exergy data):")
            print(tabulate(df_mat1.reset_index(drop=True), headers="keys", tablefmt="psql", floatfmt=".3f"))
            print("\nExergoeconomic Analysis - Material Connection Results (cost data):")
            print(tabulate(df_mat2.reset_index(drop=True), headers="keys", tablefmt="psql", floatfmt=".3f"))
            print("\nExergoeconomic Analysis - Non-Material Connection Results:")
            print(tabulate(df_non_mat.reset_index(drop=True), headers="keys", tablefmt="psql", floatfmt=".3f"))

        return df_comp, df_mat1, df_mat2, df_non_mat


class EconomicAnalysis:
    """
    Perform economic analysis of a power plant using the total revenue requirement method.

    Parameters
    ----------
    pars : dict
        Dictionary containing the following keys:
        - tau: Full load hours of the plant (hours/year)
        - i_eff: Effective rate of return (yearly based)
        - n: Lifetime of the plant (years)
        - r_n: Nominal escalation rate (yearly based)

    Attributes
    ----------
    tau : float
        Full load hours of the plant (hours/year).
    i_eff : float
        Effective rate of return (yearly based).
    n : int
        Lifetime of the plant (years).
    r_n : float
        Nominal escalation rate (yearly based).
    """

    def __init__(self, pars):
        """
        Initialize the EconomicAnalysis with plant parameters provided in a dictionary.
        
        Parameters
        ----------
        pars : dict
            Dictionary containing the following keys:
            - tau: Full load hours of the plant (hours/year)
            - i_eff: Effective rate of return (yearly based)
            - n: Lifetime of the plant (years)
            - r_n: Nominal escalation rate (yearly based)
        """
        self.tau = pars['tau']
        self.i_eff = pars['i_eff']
        self.n = pars['n']
        self.r_n = pars['r_n']

    def compute_crf(self):
        """
        Compute the Capital Recovery Factor (CRF) using the effective rate of return.
        
        Returns
        -------
        float
            The capital recovery factor.

        Notes
        -----
        CRF = i_eff * (1 + i_eff)**n / ((1 + i_eff)**n - 1)
        """
        return self.i_eff * (1 + self.i_eff)**self.n / ((1 + self.i_eff)**self.n - 1)

    def compute_celf(self):
        """
        Compute the Cost Escalation Levelization Factor (CELF) for repeating expenditures.
        
        Returns
        -------
        float
            The cost escalation levelization factor.

        Notes
        -----
        k = (1 + r_n) / (1 + i_eff)
        CELF = ((1 - k**n) / (1 - k)) * CRF
        """
        k = (1 + self.r_n) / (1 + self.i_eff)
        return (1 - k**self.n) / (1 - k) * self.compute_crf()

    def compute_levelized_investment_cost(self, total_PEC):
        """
        Compute the levelized investment cost (annualized investment cost).
        
        Parameters
        ----------
        total_PEC : float
            Total purchasing equipment cost (PEC) across all components.
            
        Returns
        -------
        float
            Levelized investment cost (currency/year).
        """
        return total_PEC * self.compute_crf()

    def compute_component_costs(self, PEC_list, OMC_relative):
        """
        Compute the cost rates for each component.
        
        Parameters
        ----------
        PEC_list : list of float
            The purchasing equipment cost (PEC) of each component (in currency).
        OMC_relative : list of float
            For each component, the first-year OM cost as a fraction of its PEC.
            
        Returns
        -------
        tuple
            (Z_CC, Z_OM, Z_total) where:
            - Z_CC: List of investment cost rates per component (currency/hour)
            - Z_OM: List of operating and maintenance cost rates per component (currency/hour)
            - Z_total: List of total cost rates per component (currency/hour)
        """
        total_PEC = sum(PEC_list)
        # Levelize total investment cost and allocate proportionally.
        levelized_investment_cost = self.compute_levelized_investment_cost(total_PEC)
        Z_CC = [(levelized_investment_cost * pec / total_PEC) / self.tau for pec in PEC_list]

        # Compute first-year OMC for each component as a fraction of PEC.
        first_year_OMC = [frac * pec for frac, pec in zip(OMC_relative, PEC_list)]
        total_first_year_OMC = sum(first_year_OMC)

        # Levelize the total operating and maintenance cost.
        celf_value = self.compute_celf()
        levelized_om_cost = total_first_year_OMC * celf_value

        # Allocate the levelized OM cost to each component in proportion to its PEC.
        Z_OM = [(levelized_om_cost * pec / total_PEC) / self.tau for pec in PEC_list]

        # Total cost rate per component.
        Z_total = [zcc + zom for zcc, zom in zip(Z_CC, Z_OM)]
        return Z_CC, Z_OM, Z_total