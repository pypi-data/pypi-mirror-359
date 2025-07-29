from cmath import phase
from functools import total_ordering

import numpy as np
import xarray as xr
from enum import Enum

import dartsflash.libflash as df
from dartsflash.libflash import FlashParams, EoS
from dartsflash.components import CompData, ConcentrationUnits as cu


NA = 6.02214076e23  # Avogadro's number [mol-1]
kB = 1.380649e-23  # Boltzmann constant [J/K]
R = NA * kB  # Gas constant [J/mol.K]


class DARTSFlash:
    f: df.Flash = None

    @total_ordering
    class FlashType(Enum):
        NegativeFlash = -1
        PTFlash = 0
        PHFlash = 1
        PSFlash = 2
        def __lt__(self, other):
            if self.__class__ is other.__class__:
                return self.value < other.value
            return NotImplemented

    get_vars = {FlashType.NegativeFlash: ["pressure", "temperature"],
                FlashType.PTFlash: ["pressure", "temperature"],
                FlashType.PHFlash: ["pressure", "enthalpy"],
                FlashType.PSFlash: ["pressure", "entropy"]
                }

    get_eos = {
        "IG": lambda comp_data: df.IdealGas(comp_data),
        "IAPWS": lambda comp_data, iapws_ideal=True: df.IAPWS95(comp_data, iapws_ideal),
        "IAPWSIce": lambda comp_data, iapws_ideal=True: df.IAPWSIce(comp_data, iapws_ideal),
        "PR": lambda comp_data: df.CubicEoS(comp_data, df.CubicEoS.PR),
        "SRK": lambda comp_data: df.CubicEoS(comp_data, df.CubicEoS.SRK),
        "Aq": lambda comp_data: df.AQEoS(comp_data, {df.AQEoS.water: df.AQEoS.Jager2003,
                                                     df.AQEoS.solute: df.AQEoS.Ziabakhsh2012,
                                                     df.AQEoS.ion: df.AQEoS.Jager2003}),
        "Ballard": lambda comp_data, hydrate_type="sI": df.Ballard(comp_data, hydrate_type),
    }

    def __init__(self, comp_data: CompData, mixture_name: str = None):
        """
        Constructor for DARTSFlash class. Provide CompData object and optional mixture name

        :param comp_data: CompData object
        :param mixture_name: Name of mixture, optional
        """
        self.comp_data = comp_data
        self.flash_params = FlashParams(comp_data)

        self.components = comp_data.components
        self.ions = comp_data.ions
        self.nc = comp_data.nc
        self.ni = comp_data.ni
        self.ns = comp_data.ns
        self.nv = self.ns + 2  # NC + 2 state specifications

        self.filename = "-".join(comp for comp in self.components) if mixture_name is None else mixture_name
        self.mixture_name = "-".join(label for label in comp_data.comp_labels[:self.nc]) if mixture_name is None else mixture_name

        self.eos = {}

    def add_eos(self, eos_name: str, eos: EoS, initial_guesses: list = None, eos_range: dict = None,
                stability_tol: float = 1e-20, switch_tol: float = 1e-20, line_tol: float = 1e-8, max_iter: int = 500,
                line_iter: int = 10, root_flag: EoS.RootFlag = EoS.STABLE, preferred_roots: list = None,
                root_order: list = None, rich_phase_order: list = None, use_gmix: bool = False, active_components: list = None):
        """
        Method to add EoS object and set EoS-specific parameters

        :param eos_name: Map key for EoS object
        :type eos_name: str
        :param eos: Equation of state
        :type eos: EoS
        :param initial_guesses: Set of initial guesses for EoS
        :type initial_guesses: list
        :param eos_range: Composition range of applicability of EoS
        :type eos_range: dict
        :param stability_tol: Stability test objective function convergence criterion
        :type stability_tol: float
        :param switch_tol: Switch to Newton criterion
        :type switch_tol: float
        :param line_tol: Line-search iteration tolerance
        :type line_tol: float
        :param max_iter: Maximum number of stability test iterations
        :type max_iter: int
        :param line_iter: Maximum number of stability line-search iterations
        :type line_iter: int
        :param root_flag: EoS.RootFlag enum for roots to be selected in stability test. 0) STABLE, 1) MIN, 2) MAX
        :type root_flag: EoS.RootFlag
        :param use_gmix: Flag to use minimum of gmix for phase split rather than stationary point
        :type use_gmix: bool
        :param preferred_roots:
        :type preferred_roots: list
        """
        eos_range = eos_range if eos_range is not None else {}
        for i, zrange in eos_range.items():
            eos.set_eos_range(i, zrange)
        
        if preferred_roots is not None:
            preferred_roots = [preferred_roots] if not isinstance(preferred_roots, (list, np.ndarray)) else preferred_roots
            for preferred_root in preferred_roots:
                i, x, flag = preferred_root
                eos.set_preferred_roots(i, x, flag)

        self.eos[eos_name] = eos
        self.flash_params.add_eos(eos_name, eos)

        params = self.flash_params.eos_params[eos_name]
        params.initial_guesses = initial_guesses if initial_guesses is not None else []
        params.stability_tol = stability_tol
        params.stability_switch_tol = switch_tol
        params.stability_line_tol = line_tol
        params.stability_max_iter = max_iter
        params.stability_line_iter = line_iter

        params.root_flag = root_flag
        params.root_order = root_order if root_order is not None else [EoS.STABLE]
        params.rich_phase_order = rich_phase_order if rich_phase_order is not None else []
        params.use_gmix = use_gmix

        if active_components is not None:
            params.set_active_components(active_components)

    def init_flash(self, flash_type: FlashType, eos_order: list, min_z: float = 1e-13, y_pure: float = 0.9,
                   tpd_tol: float = 1e-8, tpd_1p_tol: float = 1e-4, tpd_close_to_boundary: float = 1e-3, comp_tol: float = 1e-4,
                   rr2_tol: float = 1e-12, rrn_tol: float = 1e-14, rr_max_iter: int = 100, rr_line_iter: int = 10,
                   split_tol: float = 1e-15, split_switch_tol: float = 1e-15, split_line_tol: float = 1e-8, split_negative_flash_tol: float = 1e-4,
                   split_max_iter: int = 500, split_line_iter = 100, split_negative_flash_iter = 500,
                   split_variables: FlashParams.SplitVars = FlashParams.SplitVars.lnK,
                   stability_variables: FlashParams.StabilityVars = FlashParams.StabilityVars.alpha,
                   T_min: float = 100., T_max: float = 1000., T_init: float = 300., X_tol: float = 1e-3, T_tol: float = 1e-8,
                   verbose: bool = False, nf_initial_guess: list = None):
        """
        Method to specify flash parameters and initialize an instance of Flash accordingly

        :param flash_type: DARTSFlash.FlashType, NegativeFlash (PT), PTFlash, PHFlash or PSFlash
        :param eos_order: List of EoS names to be used inside the flash
        :param min_z: Minimum z value
        :param y_pure: Composition for 'pure' component initial guess
        :param tpd_tol: Tolerance for tpd function
        :param tpd_1p_tol: Tolerance for tpd 1p function
        :param tpd_close_to_boundary: Tolerance for tpd close to boundary
        :param comp_tol: Tolerance for composition comparison
        :param rr2_tol: Tolerance for two-phase Rachford-Rice algorithm
        :param rrn_tol: Tolerance for multiphase Rachford-Rice algorithm
        :param rr_max_iter: Maximum number of Rachford-Rice iterations
        :param rr_line_iter: Maximum number of Rachford-Rice line search iterations
        :param split_tol: Tolerance for phase split algorithm
        :param split_switch_tol: Tolerance for phase split switch to Newton iterations
        :param split_line_tol: Tolerance for phase split line search iterations
        :param split_negative_flash_tol: Tolerance for phase split negative flash iterations
        :param split_max_iter: Maximum number of phase split iterations
        :param split_line_iter: Maximum number of phase split line search iterations
        :param split_negative_flash_iter: Maximum number of phase split negative flash iterations
        :param split_variables: Phase split variables, default is FlashParams.SplitVars.nik
        :param stability_variables: Stability variables, default is FlashParams.StabilityVars.Y
        :param T_min: Minimum temperature for PXFlash root finding
        :param T_max: Maximum temperature for PXFlash root finding
        :param T_init: Initial temperature for PXFlash root finding
        :param X_tol: Tolerance for PXFlash specification equation (X-Xspec = 0)
        :param T_tol: Tolerance for PXFlash temperature bounds difference
        :param verbose: Flag to enable verbose mode
        :param nf_initial_guess: List of InitialGuess K-values, only required for NegativeFlash evaluation
        """
        # Define EoS and np_max for length of output
        self.flash_params.eos_order = eos_order
        self.np_max = 0
        for j, eosname in enumerate(eos_order):
            params = self.flash_params.eos_params[eosname]
            self.np_max += len(params.root_order)  # V/L
            if params.rich_phase_order:
                self.np_max += len(params.rich_phase_order) - 1  # Rich liquids

        # Set flash-related parameters in FlashParams object
        self.flash_params.min_z = min_z
        self.flash_params.y_pure = y_pure
        self.flash_params.tpd_tol = tpd_tol
        self.flash_params.tpd_1p_tol = tpd_1p_tol
        self.flash_params.tpd_close_to_boundary = tpd_close_to_boundary
        self.flash_params.comp_tol = comp_tol
        self.flash_params.rr2_tol = rr2_tol
        self.flash_params.rrn_tol = rrn_tol
        self.flash_params.rr_max_iter = rr_max_iter
        # self.flash_params.rr_line_iter = rr_line_iter

        self.flash_params.split_tol = split_tol
        self.flash_params.split_switch_tol = split_switch_tol
        self.flash_params.split_line_tol = split_line_tol
        # self.flash_params.split_negative_flash_tol = split_negative_flash_tol
        self.flash_params.split_max_iter = split_max_iter
        self.flash_params.split_line_iter = split_line_iter
        self.flash_params.split_negative_flash_iter = split_negative_flash_iter

        self.flash_params.split_variables = split_variables
        self.flash_params.stability_variables = stability_variables

        self.flash_params.T_min = T_min
        self.flash_params.T_max = T_max
        self.flash_params.T_init = T_init
        self.flash_params.phflash_Htol = X_tol
        self.flash_params.phflash_Ttol = T_tol

        self.flash_params.verbose = verbose

        # Initialize flash object
        self.flash_type = flash_type
        self.state_vars = self.get_vars[flash_type]
        if flash_type == DARTSFlash.FlashType.NegativeFlash:
            self.f = df.NegativeFlash(self.flash_params, eos_order, nf_initial_guess)
        elif flash_type == DARTSFlash.FlashType.PTFlash:
            self.f = df.Flash(self.flash_params)
        elif flash_type == DARTSFlash.FlashType.PHFlash:
            from dartsflash.libflash import PXFlash
            self.f = PXFlash(self.flash_params, PXFlash.ENTHALPY)
        else:  # flash_type == DARTSFlash.FlashType.PSFlash:
            from dartsflash.libflash import PXFlash
            self.f = PXFlash(self.flash_params, PXFlash.ENTROPY)

    def get_ranges(self, prange: list, trange: list, composition: list = None):
        """
        Method to calculate ranges of state variable that correspond to specified P-T-z conditions
        """
        if self.flash_type <= DARTSFlash.FlashType.PTFlash:
            return trange
        else:
            x = []
            for eosname in self.flash_params.eos_order:
                if self.flash_type == DARTSFlash.FlashType.PHFlash:
                    x += [self.eos[eosname].H(prange[i], trange[j], composition) * R for i in range(2) for j in range(2)]
                else:
                    x += [self.eos[eosname].S(prange[i], trange[j], composition) * R for i in range(2) for j in range(2)]
            return [np.amin(x), np.amax(x)]

    def evaluate(self, state_spec_1: float, state_spec_2: float, composition: np.ndarray, evaluate_PT: bool = False):
        """
        Method to evaluate PX-flash or PT-flash at a single state. This method is

        :param state_spec_1: First state specification values (P)
        :type state_spec_1: float
        :param state_spec_2: Second state specification values (T, H, S)
        :type state_spec_2: float
        :param composition: Feed composition
        :type composition: np.ndarray
        :param evaluate_PT: Flag to evaluate PT-flash in case it is necessary from PX-flash object
        :type evaluate_PT: bool
        """
        if evaluate_PT:
            return self.f.evaluate_PT(state_spec_1, state_spec_2, composition)
        else:
            return self.f.evaluate(state_spec_1, state_spec_2, composition)

    def evaluate_PT(self, pressure: float, temperature: float, composition: np.ndarray, evaluate_PT: bool = False):
        """
        Method to evaluate PT-flash at a single state evaluate PT-flash in case it is necessary in PX-formulation

        :param pressure: Pressure [bar]
        :param temperature: Temperature [K]
        :param composition: Feed composition
        :type composition: np.ndarray
        """
        return self.f.evaluate_PT(pressure, temperature, composition)

    def get_flash_results(self, derivs: bool = False):
        """
        Method to get access to FlashResults object

        :param derivs: Flag to evaluate derivatives of the flash
        :type derivs: bool
        """
        return self.f.get_flash_results(derivs=derivs)

    def get_state(self, state_variables, variable_idxs, idxs, mole_fractions, comp_in_dims,
                  concentrations: dict = None, concentration_unit: cu = cu.MOLALITY):
        # Get state
        j = 0
        state = np.empty(self.nv)
        for ith_var, ith_idx in enumerate(variable_idxs):
            if hasattr(state_variables[ith_var], "__len__"):
                state[ith_idx] = state_variables[ith_var][idxs[j]]
                j += 1
            else:
                state[ith_idx] = state_variables[ith_var]

        # If mole fractions, normalize mole numbers
        if mole_fractions:
            sum_zc = np.sum(state[comp_in_dims])
            if sum_zc > 1.+1e-10:
                return None
            else:
                for ith_comp in range(self.nc):
                    if (ith_comp + 2) not in comp_in_dims:
                        state[ith_comp + 2] *= (1. - sum_zc)

        # Calculate composition with concentrations
        if concentrations is not None:
            state[2:] = self.comp_data.calculate_concentrations(state[2:self.nc+2], mole_fractions, concentrations=concentrations,
                                                                concentration_unit=concentration_unit)
        else:
            assert self.ni == 0, "Ions specified but no concentrations"

        return state

    def evaluate_full_space(self, state_spec: dict, compositions: dict, evaluate, output_arrays: dict, output_type: dict,
                            mole_fractions: bool = True, concentrations: dict = None, concentration_unit: cu = cu.MOLALITY,
                            print_state: str = None):
        """
        This is a loop over all specified states to which each DARTSFlash subroutine can be passed

        :param state_spec: Dictionary containing state specification
        :param compositions: Dictionary containing variable dimensions
        :param mole_fractions: Switch for mole fractions in state
        :param evaluate: Callable with set of methods to evaluate
        :param output_arrays: Dictionary of array shapes to evaluate()
        :param output_type: Dictionary of output types to evaluate()
        :param concentrations: Dictionary of concentrations
        :param concentration_unit: Unit for concentration. 0/MOLALITY) molality (mol/kg H2O), 1/WEIGHT) Weight fraction (-)
        :param print_state: Switch for printing state and progress
        """
        assert self.flash_params.eos_params is not {}, "No EoS(Params) object has been defined"
        assert "pressure" in state_spec.keys() or "volume" in state_spec.keys(), \
            "Invalid state specification, should be either pressure- (PT/PH/PS) or volume-based (VT/VU/VS)"
        state = {spec: np.array([state_spec[spec]], copy=True) if not hasattr(state_spec[spec], "__len__")
                    else np.array(state_spec[spec], copy=True) for spec in state_spec.keys()}

        # Find dimensions and constants
        dimensions = {}
        constants = {}
        for var, dim in dict(list(state.items()) + list(compositions.items())).items():
            if isinstance(dim, (list, np.ndarray)):
                dimensions[var] = dim
            else:
                constants[var] = dim

        # Determine order of dimensions. State spec should be in right order for function call (P,X,n) or (V,X,n)
        dims_order = [comp for comp in self.components if comp in dimensions.keys()]
        ls = list(state.keys())
        first_spec = "pressure" if "pressure" in ls else "volume"
        second_spec = ls[0] if ls[1] == first_spec else ls[1]
        dims_order += [first_spec, second_spec]

        # Create xarray DataArray to store results
        array_shape = [dimensions[var].size for var in dims_order]
        n_dims = [i for i, dim in enumerate(dims_order)]
        n_points = np.prod(array_shape)

        # Know where to find state variables/constants
        state_variables = [dimensions[var] for var in dims_order] + [constant for var, constant in constants.items()]
        comp_in_dims = [i + 2 for i, comp in enumerate(self.components) if comp in dimensions.keys()]
        variable_idxs = [([first_spec, second_spec] + self.components).index(var)
                         for i, var in enumerate(dims_order + list(constants.keys()))]

        # Create data dict and coords for xarray DataArray to store results
        data = {prop: (dims_order + [prop + '_array'] if array_len > 1 else dims_order,
                       np.full(tuple(array_shape + [array_len] if array_len > 1 else array_shape),
                               (np.nan if output_type[prop] is float else 0)).astype(output_type[prop]))
                for prop, array_len in output_arrays.items()}
        coords = {dimension: xrange for dimension, xrange in dimensions.items()}

        # Loop over dimensions to create state and evaluate function
        idxs = np.array([0 for i in n_dims])
        for point in range(n_points):
            # Get state
            state = self.get_state(state_variables=state_variables, variable_idxs=variable_idxs, idxs=idxs,
                                   mole_fractions=mole_fractions, comp_in_dims=comp_in_dims,
                                   concentrations=concentrations, concentration_unit=concentration_unit)
            if print_state is not None and state is not None:
                print("\r" + print_state + " progress: {}/{}".format(point+1, n_points), "idxs:", idxs, "state:", [float("%.4f" % i) for i in state], end='')

            # Evaluate method_to_evaluate(state)
            if state is not None:
                output_data = evaluate(state)
                for prop, method in output_data.items():
                    method_output = method()
                    if isinstance(data[prop][1][tuple(idxs)], (list, np.ndarray)):
                        try:
                            data[prop][1][tuple(idxs)][:len(method_output)] = method_output
                        except ValueError as e:
                            print(e.args[0], method_output)
                            data[prop][1][tuple(idxs)][:] = np.nan if data[prop][1].dtype is float else 0
                    else:
                        data[prop][1][tuple(idxs)] = method_output[0] if hasattr(method_output, "__len__") else method_output

            # Increment idxs
            idxs[0] += 1
            for i in n_dims[1:]:
                if idxs[i-1] == array_shape[i-1]:
                    idxs[i-1] = 0
                    idxs[i] += 1
                else:
                    break

        if print_state is not None:
            print("\r" + print_state + " progress: finished")

        # Save data
        results = xr.Dataset(coords=coords)
        for var_name in data.keys():
            results[var_name] = (data[var_name][0], data[var_name][1])

        return results

    def evaluate_flash_1c(self, state_spec: dict, print_state: str = None):
        """
        Method to evaluate single-component flash

        :param state_spec: Dictionary containing state specification
        :param print_state: Switch for printing state and progress
        """
        output_arrays = {'pres': 1, 'temp': 1, 'nu': self.np_max, 'np': 1, 'eos_idx': self.np_max, 'root_type': self.np_max}
        output_type = {'pres': float, 'temp': float, 'nu': float, 'np': int, 'eos_idx': int, 'root_type': int}

        def evaluate(state):
            error = self.f.evaluate(state[0], state[1])
            flash_results = self.f.get_flash_results()
            if error:
                print("Error in Flash", state)
                flash_results.print_results()

            output_data = {"pres": lambda results=flash_results: results.pressure,
                           "temp": lambda results=flash_results: results.temperature,
                           "nu": lambda results=flash_results: results.nu if not np.isnan(results.temperature) else np.empty(self.np_max) * np.nan,
                           "np": lambda results=flash_results: results.np,
                           "eos_idx": lambda results=flash_results: results.eos_idx,
                           "root_type": lambda results=flash_results: results.root_type
                           }
            return output_data

        return self.evaluate_full_space(state_spec=state_spec, compositions={self.components[0]: 1.}, evaluate=evaluate,
                                        output_arrays=output_arrays, output_type=output_type, print_state=print_state)

    def evaluate_flash(self, state_spec: dict, compositions: dict, mole_fractions: bool,
                       concentrations: dict = None, concentration_unit: cu = cu.MOLALITY, print_state: str = None):
        """
        Method to evaluate multi-component flash

        :param state_spec: Dictionary containing state specification
        :param compositions: Dictionary containing variable dimensions
        :param mole_fractions: Switch for mole fractions in state
        :param concentrations: Dictionary of concentrations
        :param concentration_unit: Unit for concentration. 0/MOLALITY) molality (mol/kg H2O), 1/WEIGHT) Weight fraction (-)
        :param print_state: Switch for printing state and progress
        """
        output_arrays = {'pres': 1, 'temp': 1, 'nu': self.np_max, 'np': 1, 'X': self.np_max * self.ns,
                         'eos_idx': self.np_max, 'root_type': self.np_max}
        output_type = {'pres': float, 'temp': float, 'nu': float, 'X': float, 'np': int, 'eos_idx': int, 'root_type': int}

        def evaluate(state):
            error = self.f.evaluate(state[0], state[1], state[2:])
            flash_results = self.f.get_flash_results()
            if error:
                print("Error in Flash", state)
                flash_results.print_results()

            output_data = {"pres": lambda results=flash_results: results.pressure,
                           "temp": lambda results=flash_results: results.temperature,
                           "nu": lambda results=flash_results: results.nu,
                           "np": lambda results=flash_results: results.np,
                           "X": lambda results=flash_results: results.X,
                           "eos_idx": lambda results=flash_results: results.eos_idx,
                           "root_type": lambda results=flash_results: results.root_type
                           }
            return output_data

        return self.evaluate_full_space(state_spec=state_spec, compositions=compositions, mole_fractions=mole_fractions,
                                        evaluate=evaluate, output_arrays=output_arrays, output_type=output_type,
                                        concentrations=concentrations, concentration_unit=concentration_unit,
                                        print_state=print_state)

    def evaluate_phase_properties_1p(self, state_spec: dict, compositions: dict, mole_fractions: bool, properties_to_evaluate: dict,
                                     concentrations: dict = None, concentration_unit: cu = cu.MOLALITY, print_state: str = None):
        """
        Method to evaluate single phase properties: rho, Cp, etc.

        :param state_spec: Dictionary containing state specification
        :param compositions: Dictionary containing variable dimensions
        :param mole_fractions: Switch for mole fractions in state
        :param properties_to_evaluate: List of properties to evaluate
        :param concentrations: Dictionary of concentrations
        :param concentration_unit: Unit for concentration. 0/MOLALITY) molality (mol/kg H2O), 1/WEIGHT) Weight fraction (-)
        :param print_state: Switch for printing state and progress
        """
        # Assign array length and data type of properties
        pt = "pressure" in state_spec.keys()
        properties_to_evaluate = properties_to_evaluate if properties_to_evaluate is not None else {}
        output_arrays = {}
        output_type = {}
        for prop_name, prop in properties_to_evaluate.items():
            output_sample = prop(0., 0., np.ones(self.ns), 0, pt)
            output_sample = [output_sample] if not hasattr(output_sample, '__len__') else output_sample
            output_arrays[prop_name] = len(output_sample)
            output_type[prop_name] = type(output_sample[0]) if isinstance(output_sample[0], bool) else \
                (int if (float(output_sample[0]).is_integer()) else float)

        def evaluate(state):
            methods = {}

            for prop_name, prop in properties_to_evaluate.items():
                result = prop(state[0], state[1], state[2:], 0, pt)
                methods[prop_name] = lambda res=result: res

            return methods

        return self.evaluate_full_space(state_spec=state_spec, compositions=compositions, mole_fractions=mole_fractions,
                                        evaluate=evaluate, output_arrays=output_arrays, output_type=output_type,
                                        concentrations=concentrations, concentration_unit=concentration_unit,
                                        print_state=print_state)

    def evaluate_phase_properties_np(self, state_spec: dict, compositions: dict, state_variables: list, flash_results: xr.Dataset,
                                     properties_to_evaluate: list = None, print_state: str = None):
        """
        Method to evaluate phase properties at multiphase equilibrium: rho, Cp, etc.

        :param state_spec: Dictionary containing state specification
        :param compositions: Dictionary containing variable dimensions
        :param state_variables: List of state variable names to find index in flash results
        :param flash_results: Dataset of flash results
        :param properties_to_evaluate: Dict of properties to evaluate [prop_name, EoS.Property]
        :param print_state: Switch for printing state and progress
        """
        # Assign array length and data type of properties
        pt = "pressure" in state_spec.keys()
        properties_to_evaluate = properties_to_evaluate if properties_to_evaluate is not None else {}
        output_arrays = {}
        output_type = {}
        for prop_name, prop in properties_to_evaluate.items():
            output_sample = prop(0, 0, np.ones(self.ns), 0, pt)
            output_sample = [output_sample] if not hasattr(output_sample, '__len__') else output_sample
            output_arrays[prop_name] = len(output_sample) * self.np_max
            output_type[prop_name] = type(output_sample[0]) if isinstance(output_sample[0], bool) else \
                (int if (float(output_sample[0]).is_integer()) else float)

        def evaluate(state):
            methods = {}
            flash_params = self.flash_params

            # Retrieve flash results at current state: p, T, X, eos_idxs, roots
            flash_result = flash_results.loc[{state_var: state[i] for i, state_var in enumerate(state_variables[:-1])
                                              if state_var in flash_results.dims}]
            eos_idxs = flash_result.eos_idx.values
            nu = flash_result.nu.values
            X = flash_result.X.values
            roots = flash_result.root_type.values

            # Loop over properties to evaluate
            for prop_name in properties_to_evaluate.keys():
                result = np.array([])
                for eos_idx in eos_idxs:
                    eos = self.eos[flash_params.eos_order[eos_idx]]
                    result = np.append(result, eval("eos." + prop_name + "(state[0], state[1], X)"))
                methods[prop_name] = lambda res=result: res

            return methods

        return self.evaluate_full_space(state_spec=state_spec, compositions=compositions, mole_fractions=True,
                                        evaluate=evaluate, output_arrays=output_arrays, output_type=output_type,
                                        print_state=print_state)

    def evaluate_properties_1p(self, state_spec: dict, compositions: dict, mole_fractions: bool,
                               properties_to_evaluate: dict, mix: bool = False,
                               concentrations: dict = None, concentration_unit: cu = cu.MOLALITY, print_state: str = None):
        """
        Method to evaluate single phase thermodynamic properties: S, G, H, A, U

        :param state_spec: Dictionary containing state specification
        :param compositions: Dictionary containing variable dimensions
        :param mole_fractions: Switch for mole fractions in state
        :param properties_to_evaluate: List of properties to evaluate [prop_name, EoS.Property]
        :param mix: Bool to switch to mixing properties, default is False
        :param concentrations: Dictionary of concentrations
        :param concentration_unit: Unit for concentration. 0/MOLALITY) molality (mol/kg H2O), 1/WEIGHT) Weight fraction (-)
        :param print_state: Switch for printing state and progress
        """
        # Assign array length and data type of properties
        pt = "pressure" in state_spec.keys()
        properties_to_evaluate = properties_to_evaluate if properties_to_evaluate is not None else {}
        output_arrays = {}
        output_type = {}
        eos_idxs = np.array([i for i, eos in enumerate(self.eos.keys())])
        roots = np.zeros(len(self.eos))

        for prop_name, prop in properties_to_evaluate.items():
            assert isinstance(prop, EoS.Property)
            output_arrays[prop_name] = len(self.eos)
            output_type[prop_name] = float

        def evaluate(state):
            methods = {}

            for prop_name, prop in properties_to_evaluate.items():
                result = self.flash_params.prop_1p(prop, state[0], state[1], state[2:], eos_idxs, roots)

                if mix:
                    # Calculate pure component properties M(zi=1)
                    pure = self.flash_params.prop_pure(prop, state[0], state[1])

                    # Calculate property of mixing: Mj - xij M(zi=1)
                    methods[prop_name] = lambda res=result, pu=pure: res - np.sum(pu * state[2:])
                else:
                    methods[prop_name] = lambda res=result: res

            return methods

        return self.evaluate_full_space(state_spec=state_spec, compositions=compositions, mole_fractions=mole_fractions,
                                        evaluate=evaluate, output_arrays=output_arrays, output_type=output_type,
                                        concentrations=concentrations, concentration_unit=concentration_unit,
                                        print_state=print_state)

    def evaluate_properties_np(self, state_spec: dict, compositions: dict, state_variables: list, flash_results: xr.Dataset,
                               properties_to_evaluate: dict = None, phase_idxs: list = None,
                               total_properties_to_evaluate: dict = None, mix: bool = False, print_state: str = None):
        """
        Method to evaluate phase thermodynamic properties at multiphase equilibrium: S, G, H, A, U

        :param state_spec: Dictionary containing state specification
        :param compositions: Dictionary containing variable dimensions
        :param state_variables: List of state variable names to find index in flash results
        :param flash_results: Dataset of flash results
        :param properties_to_evaluate: Dict of properties to evaluate [prop_name, EoS.Property]
        :param phase_idxs: List of idxs of phases to evaluate property of
        :param total_properties_to_evaluate: Dict of total properties to evaluate [prop_name, EoS.Property]
        :param mix: Bool to switch to mixing properties, default is False
        :param print_state: Switch for printing state and progress
        """
        # Assign array length and data type of phase properties
        properties_to_evaluate = properties_to_evaluate if properties_to_evaluate is not None else {}
        phase_idxs = phase_idxs if phase_idxs is not None else [j for j in range(self.np_max)]
        output_arrays = {}
        output_type = {}
        for prop_name, prop in properties_to_evaluate.items():
            output_arrays[prop_name] = len(phase_idxs)
            output_type[prop_name] = float

        # Assign array length of total properties at equilibrium
        total_properties_to_evaluate = total_properties_to_evaluate if total_properties_to_evaluate is not None else {}
        for prop_name, prop in total_properties_to_evaluate.items():
            output_arrays[prop_name + "_total"] = 1
            output_type[prop_name + "_total"] = float

        def evaluate(state):
            methods = {}

            # Retrieve flash results at current state: p, T, X, eos_idxs, roots
            flash_result = flash_results.loc[{state_var: state[i] for i, state_var in enumerate(state_variables[:-1])
                                              if state_var in flash_results.dims}]
            eos_idxs = flash_result.eos_idx.values
            pres = flash_result.pres.values
            temp = flash_result.temp.values
            nu = flash_result.nu.values
            X = flash_result.X.values
            roots = flash_result.root_type.values

            # Loop over properties to evaluate
            for prop_name, prop in properties_to_evaluate.items():
                result = self.flash_params.prop_np(prop, pres, temp, X, eos_idxs, roots)

                if mix:
                    # Calculate pure component properties M(zi=1)
                    pure = self.flash_params.prop_pure(prop, pres, temp)
                    methods[prop_name] = lambda res=result, pu=pure: [res[j] - np.nansum(pu * X[j * self.ns:(j + 1) * self.ns])
                                                                      if not np.isnan(res[j]) else np.nan for j in phase_idxs]
                else:
                    methods[prop_name] = lambda res=result: res

            # Loop over total properties to evaluate
            for prop_name, prop in total_properties_to_evaluate.items():
                # Calculate equilibrium phase properties Mj
                result = self.flash_params.prop_np(prop, pres, temp, X, eos_idxs, roots)

                if mix:
                    # Calculate pure component properties M(zi=1)
                    pure = self.flash_params.prop_pure(prop, pres, temp)

                    # Calculate total property of mixing: nuj * (Mj - xij M(zi=1))
                    methods[prop_name + "_total"] = lambda nu_=nu, res=result, pu=pure: (
                        np.nansum(nu_ * np.array([res[j] - np.nansum(pu * X[j * self.ns:(j + 1) * self.ns])
                                                  if not np.isnan(res[j]) else np.nan for j in phase_idxs]))
                    )
                else:
                    methods[prop_name + "_total"] = lambda nu_=nu, res=result: np.nansum(nu_ * res)

            return methods

        return self.evaluate_full_space(state_spec=state_spec, compositions=compositions, mole_fractions=True,
                                        evaluate=evaluate, output_arrays=output_arrays, output_type=output_type,
                                        print_state=print_state)

    def evaluate_stationary_points(self, state_spec: dict, compositions: dict, mole_fractions: bool,
                                   concentrations: dict = None, concentration_unit: cu = cu.MOLALITY, print_state: str = None):
        """
        Method to evaluate stationary points

        :param state_spec: Dictionary containing state specification
        :param compositions: Dictionary containing variable dimensions
        :param mole_fractions: Switch for mole fractions in state
        :param concentrations: Dictionary of concentrations
        :param concentration_unit: Unit for concentration. 0/MOLALITY) molality (mol/kg H2O), 1/WEIGHT) Weight fraction (-)
        :param print_state: Switch for printing state and progress
        """
        max_tpd = self.np_max + 1
        output_arrays = {'y': max_tpd * self.nc, 'tpd': max_tpd, 'tot_sp': 1, 'neg_sp': 1, 'eos_idx': max_tpd, 'root_type': max_tpd}
        output_type = {'y': float, 'tpd': float, 'tot_sp': int, 'neg_sp': int, 'eos_idx': int, 'root_type': int}

        def evaluate(state):
            stationary_points = self.f.find_stationary_points(state[0], state[1], state[2:])
            output_data = {"y": lambda spts=stationary_points: np.array([sp.y for sp in spts]).flatten(),
                           "tpd": lambda spts=stationary_points: np.array([sp.tpd for sp in spts]),
                           "tot_sp": lambda spts=stationary_points: len(spts),
                           "neg_sp": lambda spts=stationary_points: np.sum([sp.tpd < -1e-8 for sp in spts]),
                           "eos_idx": lambda spts=stationary_points: np.array([sp.eos_idx for sp in spts]),
                           "root_type": lambda spts=stationary_points: np.array([sp.root_type for sp in spts]),
            }
            return output_data

        return self.evaluate_full_space(state_spec=state_spec, compositions=compositions, mole_fractions=mole_fractions,
                                        evaluate=evaluate, output_arrays=output_arrays, output_type=output_type,
                                        concentrations=concentrations, concentration_unit=concentration_unit,
                                        print_state=print_state)

    def output_to_file(self, data: xr.Dataset, csv_filename: str = None, h5_filename: str = None):
        """
        Method to write xarray.Dataset to .csv and/or .h5 format

        :param data: Xarray Dataset
        :param csv_filename: Filename to write to .csv format
        :param h5_filename: Filename to write to .h5 format
        """
        if csv_filename is not None:
            df = data.to_dataframe()
            csv_filename = csv_filename + '.csv' if not csv_filename[:-4] == '.csv' else csv_filename
            df.to_csv(csv_filename)

        if h5_filename is not None:
            h5_filename = h5_filename + '.h5' if not h5_filename[:-3] == '.h5' else h5_filename
            data.to_netcdf(h5_filename, engine='h5netcdf')
