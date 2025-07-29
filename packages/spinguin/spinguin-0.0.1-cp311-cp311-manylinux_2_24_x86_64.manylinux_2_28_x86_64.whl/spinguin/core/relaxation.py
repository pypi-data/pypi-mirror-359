"""
This module provides functions for calculating relaxation superoperators.
"""

# Imports
import time
import numpy as np
import scipy.constants as const
import scipy.sparse as sp
from joblib import Parallel, delayed
from scipy.special import eval_legendre
from spinguin.core.superoperators import sop_T_coupled, sop_prod
from spinguin.core.la import \
    eliminate_small, principal_axis_system, \
    cartesian_tensor_to_spherical_tensor, angle_between_vectors, norm_1, \
    auxiliary_matrix_expm, expm, read_shared_sparse, write_shared_sparse
from spinguin.core.basis import idx_to_lq, lq_to_idx, parse_operator_string
from spinguin.core.hide_prints import HidePrints
from typing import Literal

def dd_constant(y1: float, y2: float) -> float:
    """
    Calculates the dipole-dipole coupling constant (excluding the distance).

    Parameters
    ----------
    y1 : float
        Gyromagnetic ratio of the first spin in units of rad/s/T.
    y2 : float
        Gyromagnetic ratio of the second spin in units of rad/s/T.

    Returns
    -------
    dd_const : float
        Dipole-dipole coupling constant in units of rad/s * m^3.
    """

    # Calculate the constant
    dd_const = -const.mu_0 / (4 * np.pi) * y1 * y2 * const.hbar

    return dd_const

def Q_constant(S: float, Q_moment: float) -> float:
    """
    Calculates the nuclear quadrupolar coupling constant in (rad/s) / (V/m^2).
    
    Parameters
    ----------
    S : float
        Spin quantum number.
    Q_moment : float
        Nuclear quadrupole moment (in units of m^2).

    Returns
    -------
    Q_const : float
        Quadrupolar coupling constant.
    """

    # Calculate the quadrupolar coupling constant
    if (S >= 1) and (Q_moment > 0):
        Q_const = -const.e * Q_moment / const.hbar / (2 * S * (2 * S - 1))
    else:
        Q_const = 0
    
    return Q_const

def G0(tensor1: np.ndarray, tensor2: np.ndarray, l: int) -> float:
    """
    Computes the time correlation function at t = 0, G(0), for two
    Cartesian tensors.

    This is the multiplicative factor in front of the exponential
    decay for the isotropic rotational diffusion model.

    Source: Eq. 70 from Hilla & Vaara: Rela2x: Analytic and automatic NMR
    relaxation theory
    https://doi.org/10.1016/j.jmr.2024.107828

    Parameters
    ----------
    tensor1 : ndarray
        Cartesian tensor 1.
    tensor2 : ndarray
        Cartesian tensor 2.
    l : int
        Common rank of the tensors.

    Returns
    -------
    G_0 : float
        Time correlation function evaluated at t = 0.
    """
    # Find the principal axis systems of the tensors
    _, eigvecs1, tensor1_pas = principal_axis_system(tensor1)
    _, eigvecs2, tensor2_pas = principal_axis_system(tensor2)

    # Find the angle between the principal axes
    angle = angle_between_vectors(eigvecs1[0], eigvecs2[0])

    # Write the tensors in the spherical tensor notation
    V1_pas = cartesian_tensor_to_spherical_tensor(tensor1_pas)
    V2_pas = cartesian_tensor_to_spherical_tensor(tensor2_pas)

    # Compute G0
    G_0 = 1 / (2 * l + 1) * eval_legendre(2, np.cos(angle)) * sum(
        [V1_pas[l, q] * np.conj(V2_pas[l, q]) for q in range(-l, l + 1)])

    return G_0

def tau_c_l(tau_c: float, l: int) -> float:
    """
    Calculates the rotational correlation time for a given rank `l`. 
    Applies only for anisotropic rotationally modulated interactions (l > 0).

    Source: Eq. 70 from Hilla & Vaara: Rela2x: Analytic and automatic NMR
    relaxation theory
    https://doi.org/10.1016/j.jmr.2024.107828

    Parameters
    ----------
    tau_c : float
        Rotational correlation time.
    l : int
        Interaction rank.

    Returns
    -------
    t_cl : float
        Rotational correlation time for the given rank. 
    """

    # Calculate the rotational correlation time for anisotropic interactions
    if l != 0:
        t_cl = 6 * tau_c / (l * (l + 1))

    # For isotropic interactions raise an error
    else:
        raise ValueError('Rank l must be different from 0 in tau_c_l.')
    
    return t_cl
    
def dd_coupling_tensors(xyz: np.ndarray, gammas: np.ndarray) -> np.ndarray:
    """
    Calculates the dipole-dipole coupling tensor between all nuclei
    in the spin system.

    Parameters
    ----------
    xyz : ndarray
        A 2-dimensional array specifying the cartesian coordinates in
        the XYZ format for each nucleus in the spin system. Must be
        given in the units of Å.
    gammas : ndarray
        A 1-dimensional array specifying the gyromagnetic ratios for
        each nucleus in the spin system. Must be given in the units
        of rad/s/T.

    Returns
    -------
    dd_tensors : ndarray
        Array of dimensions (N, N, 3, 3) containing the 3x3 tensors
        between all nuclei.
    """

    # Deduce the number of spins in the system
    nspins = gammas.shape[0]

    # Convert the molecular coordinates to SI units
    xyz = xyz * 1e-10

    # Get the connector and distance arrays
    connectors = xyz[:, np.newaxis] - xyz
    distances = np.linalg.norm(connectors, axis=2)

    # Initialize the array of tensors
    dd_tensors = np.zeros((nspins, nspins, 3, 3))

    # Go through each spin pair
    for i in range(nspins):
        for j in range(nspins):

            # Only the lower triangular part is computed
            if i > j:
                rr = np.outer(connectors[i, j], connectors[i, j])
                dd_tensors[i, j] = dd_constant(gammas[i], gammas[j]) * \
                                   (3 * rr - distances[i, j]**2 * np.eye(3)) / \
                                   distances[i, j]**5

    return dd_tensors

def shielding_intr_tensors(shielding: np.ndarray,
                           gammas: np.ndarray, B: float) -> np.ndarray:
    """
    Calculates the shielding interaction tensors for a spin system.

    Parameters
    ----------
    shielding : ndarray
        A 3-dimensional array specifying the nuclear shielding tensors for each
        nucleus. The tensors must be given in the units of ppm.
    gammas : ndarray
        A 1-dimensional array specifying the gyromagnetic ratios for
        each nucleus in the spin system. Must be given in the units
        of rad/s/T.
    B : float
        External magnetic field in units of T.

    Returns
    -------
    shielding_tensors: ndarray
        Array of shielding tensors.
    """

    # Convert from ppm to dimensionless
    shielding_tensors = shielding * 1e-6

    # Create Larmor frequencies ("shielding constants" for relaxation)
    # TODO: Check the sign of the Larmor frequency (Perttu?)
    w0s = -gammas * B

    # Multiply with the Larmor frequencies
    for i, val in enumerate(w0s):
        shielding_tensors[i] *= val

    return shielding_tensors

# TODO: Check the sign (Perttu?)
def Q_intr_tensors(efg: np.ndarray,
                   spins: np.ndarray,
                   quad: np.ndarray) -> np.ndarray:
    """
    Calculates the quadrupolar interaction tensors for a spin system.

    Parameters
    ----------
    efg : ndarray
        A 3-dimensional array specifying the electric field gradient tensors.
        Must be given in atomic units.
    spins : ndarray
        A 1-dimensional array specifying the spin quantum numbers for each
        spin.
    quad : ndarray
        A 1-dimensional array specifying the quadrupolar moments. Must be given
        in the units of m^2.
        
    Returns
    -------
    Q_tensors: ndarray
        Quadrupolar interaction tensors.
    """

    # Convert from a.u. to V/m^2
    Q_tensors = -9.7173624292e21 * efg

    # Create quadrupolar coupling constants
    Q_constants = [Q_constant(S, Q) for S, Q in zip(spins, quad)]

    # Multiply the tensors with the quadrupolar coupling constants
    for i, val in enumerate(Q_constants):
        Q_tensors[i] *= val

    return Q_tensors

def process_interactions(intrs: dict, zero_value: float) -> dict:
    """
    Processes all incoherent interactions and organizes them by rank. 
    Disregards interactions below a specified threshold.

    Parameters
    ----------
    intrs : dict
        A dictionary where the keys represent the interaction type, and the
        values contain the interaction tensors and the ranks.
    zero_value : float
        If the eigenvalues of the interaction tensor, estimated using the
        1-norm, are smaller than this threshold, the interaction is ignored.

    Returns
    -------
    interactions : dict
        A dictionary where the interactions are organized by rank. The values
        contain all interactions with meaningful strength. The interactions are
        tuples in the format ("interaction", spin_1, spin_2, tensor).
    """

    # Initialize the lists of interaction descriptions for different ranks
    interactions = {
        1: [],
        2: []
    }

    # Iterate through the interactions
    for interaction, properties in intrs.items():

        # Extract the properties
        tensors = properties[0]
        ranks = properties[1]

        # Iterate through the ranks
        for rank in ranks:

            # Process single-spin interactions
            if interaction in ["CSA", "Q"]:
                for spin_1 in range(tensors.shape[0]):
                    if norm_1(tensors[spin_1], ord='row') > zero_value:
                        interactions[rank].append(
                            (interaction, spin_1, None, tensors[spin_1]))

            # Process two-spin interactions
            if interaction == "DD":
                for spin_1 in range(tensors.shape[0]):
                    for spin_2 in range(tensors.shape[1]):
                        if norm_1(
                            tensors[spin_1, spin_2], ord='row') > zero_value:
                            interactions[rank].append(
                                (interaction, spin_1, spin_2, 
                                 tensors[spin_1, spin_2]))

    return interactions

def get_sop_T(basis: np.ndarray,
              spins: np.ndarray,
              l: int,
              q: int,
              interaction_type: Literal["CSA", "Q", "DD"],
              spin_1: int,
              spin_2: int = None,
              sparse: bool=True) -> np.ndarray | sp.csc_array:
    """
    Helper function for the relaxation module. Calculates the coupled product 
    superoperators for different interaction types.

    Parameters
    ----------
    basis : ndarray
        A 2-dimensional array containing the basis set that contains sequences
        of integers describing the Kronecker products of irreducible spherical
        tensors.
    spins : ndarray
        A 1-dimensional array specifying the spin quantum numbers for each spin
        in the system.
    l : int
        Operator rank.
    q : int
        Operator projection.
    interaction_type : {'CSA', 'Q', 'DD'}
        Describes the interaction type. Possible options are "CSA", "Q", and
        "DD", which stand for chemical shift anisotropy, quadrupolar coupling,
        and dipole-dipole coupling, respectively.
    spin_1 : int
        Index of the first spin.
    spin_2 : int, optional
        Index of the second spin. Leave empty for single-spin interactions
        (e.g., CSA).
    sparse : bool, default=True
        Specifies whether to return the superoperator as a sparse or dense
        array.

    Returns
    -------
    sop : ndarray or csc_array
        Coupled spherical tensor superoperator of rank `l` and projection `q`.
    """

    # Single-spin linear interaction
    if interaction_type == "CSA":
        sop = sop_T_coupled(basis, spins, l, q, spin_1, sparse=sparse)

    # Single-spin quadratic interaction
    elif interaction_type == "Q":
        nspins = spins.shape[0]
        op_def = np.zeros(nspins, dtype=int)
        op_def[spin_1] = lq_to_idx(l, q)
        sop = sop_prod(op_def, basis, spins, 'comm', sparse)

    # Two-spin bilinear interaction
    elif interaction_type == "DD":
        sop = sop_T_coupled(basis, spins, l, q, spin_1, spin_2, sparse)

    # Raise an error for invalid interaction types
    else:
        raise ValueError(f"Invalid interaction type '{interaction_type}' for "
                         "relaxation superoperator. Possible options are " 
                         "'CSA', 'Q', and 'DD'.")

    return sop

def sop_R_redfield_term(
        l: int, q: int,
        type_r: str, spin_r1: int, spin_r2: int, tensor_r: np.ndarray,
        top_l_shared: dict, top_r_shared: dict, bottom_r_shared: dict,
        t_max: float, aux_zero: float, relaxation_zero: float,
        sop_Ts: dict, interactions: dict
) -> tuple[int, int, str, int, int, sp.csc_array]:
    """
    Helper function for the Redfield relaxation theory. This function calculates
    one term of the relaxation superoperator and enables the use of parallel
    computation.

    NOTE: This function returns some of the input parameters to display the
    progress in the computation of the total Redfield relaxation superoperator.

    Parameters
    ----------
    l : int
        Operator rank.
    q : int
        Operator projection.
    type_r : str
        Interaction type. Possible options are "CSA", "Q", and "DD".
    spin_r1 : int
        Index of the first spin in the interaction.
    spin_r2 : int
        Index of the second spin in the interaction. Leave empty for single-spin
        interactions (e.g., CSA).
    tensor_r : np.ndarray
        Interaction tensor for the right-hand interaction.
    top_l_shared : dict
        Dictionary containing the shared top left block of the auxiliary matrix.
    top_r_shared : dict
        Dictionary containing the shared top right block of the auxiliary
        matrix.
    bottom_r_shared : dict
        Dictionary containing the shared bottom right block of the auxiliary
        matrix.
    t_max : float
        Integration limit for the auxiliary matrix method.
    aux_zero : float
        Threshold for the convergence of the Taylor series when exponentiating
        the auxiliary matrix.
    relaxation_zero : float
        Values below this threshold are disregarded in the construction of the
        relaxation superoperator term.
    sop_Ts : dict
        Dictionary containing the shared coupled T superoperators for different
        interactions.
    interactions : dict
        Dictionary containing the interactions organized by rank.

    Returns
    -------
    l : int
        Operator rank.
    q : int
        Operator projection.
    type_r : str
        Interaction type.
    spin_r1 : int
        Index of the first spin.
    spin_r2 : int
        Index of the second spin.
    sop_R_term : csc_array
        Relaxation superoperator term for the given interaction.
    """
    # Create an empty list for the SharedMemory objects
    shms = []

    # Convert the shared arrays back to CSC arrays
    top_l, top_l_shm = read_shared_sparse(top_l_shared)
    top_r, top_r_shm = read_shared_sparse(top_r_shared)
    bottom_r, bottom_r_shm = read_shared_sparse(bottom_r_shared)
    dim = top_r.shape[0]

    # Store the SharedMemories
    shms.extend(top_l_shm)
    shms.extend(top_r_shm)
    shms.extend(bottom_r_shm)
    
    # Calculate the Redfield integral using the auxiliary matrix method
    aux_expm = auxiliary_matrix_expm(top_l, top_r, bottom_r, t_max, aux_zero)

    # Extract top left and top right blocks
    aux_top_l = aux_expm[:dim, :dim]
    aux_top_r = aux_expm[:dim, dim:]

    # Extract the Redfield integral
    integral = aux_top_l.conj().T @ aux_top_r

    # Initialize the left coupled T superoperator
    sop_T_l = sp.csc_array((dim, dim), dtype=complex)

    # Iterate over the LEFT interactions
    for interaction_l in interactions[l]:

        # Extract the interaction information
        type_l = interaction_l[0]
        spin_l1 = interaction_l[1]
        spin_l2 = interaction_l[2]
        tensor_l = interaction_l[3]

        # Compute G0
        G_0 = G0(tensor_l, tensor_r, l)

        # Add current term to the left operator
        sop_T, sop_T_shm = \
            read_shared_sparse(sop_Ts[(l, q, type_l, spin_l1, spin_l2)])
        sop_T_l += G_0 * sop_T
        shms.extend(sop_T_shm)

    # Handle negative q values by spherical tensor properties
    if q == 0:
        sop_R_term = sop_T_l.conj().T @ integral
    else:
        sop_R_term = sop_T_l.conj().T @ integral + sop_T_l @ integral.conj().T

    # Eliminate small values
    eliminate_small(sop_R_term, relaxation_zero)
    
    # Close the SharedMemory objects
    for shm in shms:
        shm.close()

    return l, q, type_r, spin_r1, spin_r2, sop_R_term

def sop_R_redfield(basis: np.ndarray,
                   sop_H: sp.csc_array,
                   tau_c: float,
                   spins: np.ndarray,
                   B: float = None,
                   gammas: np.ndarray = None,
                   quad: np.ndarray = None,
                   xyz: np.ndarray = None,
                   shielding: np.ndarray = None,
                   efg: np.ndarray = None,
                   include_antisymmetric: bool=False,
                   include_dynamic_frequency_shift: bool=False,
                   relative_error: float=1e-6,
                   interaction_zero: float=1e-9,
                   aux_zero: float=1e-18,
                   relaxation_zero: float=1e-12,
                   parallel_dim: int=1000,
                   sparse: bool=True) -> np.ndarray | sp.csc_array:
    """
    Calculates the relaxation superoperator using Redfield relaxation theory.

    Sources:
    
    Eq. 54 from Hilla & Vaara: Rela2x: Analytic and automatic NMR relaxation
    theory
    https://doi.org/10.1016/j.jmr.2024.107828

    Eq. 24 and 25 from Goodwin & Kuprov: Auxiliary matrix formalism for
    interaction representation transformations, optimal control, and spin
    relaxation theories
    https://doi.org/10.1063/1.4928978

    Parameters
    ----------
    basis : ndarray
        A 2-dimensional array containing the basis set that contains sequences
        of integers describing the Kronecker products of irreducible spherical
        tensors.
    sop_H : ndarray or csc_array
        Coherent part of the Hamiltonian superoperator.
    tau_c : float
        Rotational correlation time in seconds.
    spins : ndarray
        A 1-dimensional array specifying the spin quantum numbers of the system.
    B : float
        External magnetic field in Tesla.
    gammas : ndarray, default=None
        A 1-dimensional array specifying the gyromagnetic ratios for each spin.
        Must be defined in the units of rad/s/T.
    quad : ndarray, default=None
        A 1-dimensional array specifying the quadrupolar moments for each spin.
        Must be defined in the units of m^2.
    xyz : ndarray, default=None
        A 2-dimensional array where the rows contain the Cartesian coordinates
        for each spin in the units of Å.
    shielding : ndarray, default=None
        A 3-dimensional array where the shielding tensors are specified for each
        spin in the units of Å.
    efg : ndarray, default=None
        A 3-dimensional array where the electric field gradient tensors are
        specified for each spin in the units of Å.
    include_antisymmetric : bool, default=False
        Specifies whether the antisymmetric component of the CSA is included.
        This is usually very small and can be neglected.
    include_dynamic_frequency_shift : bool, default=False
        Specifies whether the dynamic frequency shifts are included. This
        corresponds to the imaginary part of the relaxation superoperator that
        causes small shifts to the resonance frequencies. This effect is usually
        very small and can be neglected.
    relative_error : float=1e-6
        Relative error for the Redfield integral that is calculated using
        auxiliary matrix method. Smaller values correspond to more accurate
        integrals.
    interaction_zero : float=1e-9
        If the eigenvalues of the interaction tensor, estimated using the
        1-norm, are smaller than this threshold, the interaction is ignored.
    aux_zero : float=1e-18
        This threshold is used to estimate the convergence of the Taylor series
        when exponentiating the auxiliary matrix, and also to eliminate small
        values from the arrays in the matrix exponential squaring step.
    relaxation_zero : float=1e-12
        Smaller values than this threshold are eliminated from the relaxation
        superoperator before returning the array.
    parallel_dim : int=1000
        If the basis set dimension is larger than this value, the Redfield
        integrals are calculated in parallel. Otherwise, the integrals are
        calculated in serial.
    sparse : bool=True
        Specifies whether to calculate the relaxation superoperator as sparse or
        dense array.

    Returns
    -------
    sop_R : ndarray or csc_array
        Relaxation superoperator.
    """

    time_start = time.time()
    print('Constructing relaxation superoperator using Redfield theory...')

    # Obtain the basis set dimension
    dim = basis.shape[0]

    # Initialize a list to hold all SharedMemories
    shms = []

    # Initialize a dictionary for incoherent interactions
    interactions = {}

    # Process dipole-dipole couplings
    if xyz is not None:
        dd_tensors = dd_coupling_tensors(xyz, gammas)
        dd_ranks = [2]
        interactions['DD'] = (dd_tensors, dd_ranks)

    # Process nuclear shielding
    if shielding is not None:
        sh_tensors = shielding_intr_tensors(shielding, gammas, B)
        if include_antisymmetric:
            sh_ranks = [1, 2]
        else:
            sh_ranks = [2]
        interactions['CSA'] = (sh_tensors, sh_ranks)

    # Process quadrupolar coupling
    if efg is not None:
        q_tensors = Q_intr_tensors(efg, spins, quad)
        q_ranks = [2]
        interactions['Q'] = (q_tensors, q_ranks)

    # Process the interactions
    interactions = process_interactions(interactions, interaction_zero)

    # Initialize the relaxation superoperator
    sop_R = sp.csc_array((dim, dim), dtype=complex)

    # Define the integration limit for the auxiliary matrix method
    t_max = np.log(1 / relative_error) * tau_c

    # Top left array of auxiliary matrix
    top_left = 1j * sop_H
    top_left, top_left_shm = write_shared_sparse(top_left)
    shms.extend(top_left_shm)

    # FIRST LOOP
    # -- PRECOMPUTE THE COUPLED T SUPEROPERATORS
    # -- CREATE THE LIST OF TASKS
    print("Building superoperators...")
    sop_Ts = {}
    tasks = []
    
    # Iterate over the ranks
    for l in [1, 2]:

        # Diagonal matrix of correlation time
        tau_c_diagonal_l = 1 / tau_c_l(tau_c, l) * \
                            sp.eye_array(sop_H.shape[0], format='csc')

        # Bottom right array of auxiliary matrix
        bottom_right = 1j * sop_H - tau_c_diagonal_l
        bottom_right, bottom_right_shm = write_shared_sparse(bottom_right)
        shms.extend(bottom_right_shm)

        # Iterate over the projections (negative q values are handled by 
        # spherical tensor properties)
        for q in range(0, l + 1):

            # Iterate over the interactions
            for interaction in interactions[l]:

                # Extract the interaction information
                itype = interaction[0]
                spin1 = interaction[1]
                spin2 = interaction[2]
                tensor = interaction[3]

                # Show current status
                if spin2 is None:
                    print(f"l: {l}, q: {q} - {itype} for spin {spin1}")
                else:
                    print(f"l: {l}, q: {q} - {itype} for spins {spin1}-{spin2}")

                # Compute a shared version of the coupled T superoperator
                sop_T, sop_T_shm = write_shared_sparse(get_sop_T(
                    basis, spins, l, q, itype, spin1, spin2, sparse))
                sop_Ts[(l, q, itype, spin1, spin2)] = sop_T
                shms.extend(sop_T_shm)

                # Add to the list of tasks
                tasks.append((
                    l, q,                               # Rank and projection
                    itype, spin1, spin2, tensor,        # Right interaction
                    top_left, sop_T, bottom_right,      # Aux matrix components
                    t_max, aux_zero, relaxation_zero,   # Numerical parameters
                    sop_Ts, interactions                # Left interaction
                ))

    print("Superoperators built.")

    # SECOND LOOP -- Iterate over the tasks in parallel
    if dim > parallel_dim:
        print("Performing the Redfield integrals in parallel...")

        # Create the parallel tasks
        parallel = Parallel(n_jobs=-1, return_as="generator_unordered")
        output_generator = parallel(
            delayed(sop_R_redfield_term)(*task) for task in tasks
        )

        # Process the results from parallel processing
        for result in output_generator:

            # Parse the result and add term to total relaxation superoperator
            l, q, itype, spin1, spin2, sop_R_term = result
            sop_R += sop_R_term

            # Show current status
            if spin2 is None:
                print(f"l: {l}, q: {q} - {itype} for spin {spin1}")
            else:
                print(f"l: {l}, q: {q} - {itype} for spins {spin1}-{spin2}")

    # SECOND LOOP -- Iterate over the tasks in serial
    else:
        print("Performing the Redfield integrals in serial...")

        # Process the tasks in serial
        for task in tasks:

            # Parse the result and add term to total relaxation superoperator
            l, q, itype, spin1, spin2, sop_R_term = sop_R_redfield_term(*task)
            sop_R += sop_R_term

            # Show current status
            if spin2 is None:
                print(f"l: {l}, q: {q} - {itype} for spin {spin1}")
            else:
                print(f"l: {l}, q: {q} - {itype} for spins {spin1}-{spin2}")

    # Clear the shared memories
    for shm in shms:
        shm.close()
        shm.unlink()
    
    print("Redfield integrals completed.")

    # Return only real values unless dynamic frequency shifts are requested
    if not include_dynamic_frequency_shift:
        print("Removing the dynamic frequency shifts...")
        sop_R = sop_R.real
        print("Dynamic frequency shifts removed.")
    
    # Eliminate small values
    print("Eliminating small values from the relaxation superoperator...")
    eliminate_small(sop_R, relaxation_zero)
    print("Small values eliminated.")
    
    print("Redfield relaxation superoperator constructed in "
          f"{time.time() - time_start:.4f} seconds.")
    print()

    return sop_R

def sop_R_random_field():
    """
    TODO PERTTU?
    """

def sop_R_phenomenological(basis: np.ndarray,
                           R1: np.ndarray,
                           R2: np.ndarray,
                           sparse: bool=True) -> np.ndarray | sp.csc_array:
    """
    Constructs the relaxation superoperator from given `R1` and `R2` values
    for each spin.

    Parameters
    ----------
    basis : ndarray
        A 2-dimensional array containing the basis set that contains sequences
        of integers describing the Kronecker products of irreducible spherical
        tensors.
    R1 : ndarray
        A one dimensional array containing the longitudinal relaxation rates
        in 1/s for each spin. For example: `np.array([1.0, 2.0, 2.5])`
    R2 : ndarray
        A one dimensional array containing the transverse relaxation rates
        in 1/s for each spin. For example: `np.array([2.0, 4.0, 5.0])`
    sparse : bool, default=True
        Specifies whether to construct the relaxation superoperator as sparse or
        dense array.

    Returns
    -------
    sop_R : ndarray or csc_array
        Relaxation superoperator.
    """

    time_start = time.time()
    print('Constructing the phenomenological relaxation superoperator...')

    # Obtain the basis dimension
    dim = basis.shape[0]

    # Create an empty array for the relaxation superoperator
    if sparse:
        sop_R = sp.lil_array((dim, dim))
    else:
        sop_R = np.zeros((dim, dim))

    # Loop over the basis set
    for idx, state in enumerate(basis):

        # Initialize the relaxation rate for the current state
        R_state = 0
        
        # Loop over the state
        for spin, operator in enumerate(state):

            # Continue only if the operator is not the unit state
            if operator != 0:

                # Get the projection of the state
                _, q = idx_to_lq(operator)
            
                # Check if the current spin has a longitudinal state
                if q == 0:
                    
                    # Add to the relaxation rate
                    R_state += R1[spin]

                # Otherwise, the state must be transverse
                else:

                    # Add to the relaxation rate
                    R_state += R2[spin]

        # Add to the relaxation matrix
        sop_R[idx, idx] = R_state

    # Convert to CSC array if using sparse
    if sparse:
        sop_R = sop_R.tocsc()

    print("Phenomenological relaxation superoperator constructed in "
          f"{time.time() - time_start:.4f} seconds.")
    print()

    return sop_R

def sop_R_sr2k(basis: np.ndarray,
               spins: np.ndarray,
               gammas: np.ndarray,
               chemical_shifts: np.ndarray,
               J_couplings: np.ndarray,
               sop_R: sp.csc_array,
               B: float,
               sparse: bool=True) -> np.ndarray | sp.csc_array:
    """
    Calculates the scalar relaxation of the second kind (SR2K) based on 
    Abragam's formula.

    Parameters
    ----------
    basis : ndarray
        A 2-dimensional array containing the basis set that contains sequences
        of integers describing the Kronecker products of irreducible spherical
        tensors.
    spins : ndarray
        A 1-dimensional array specifying the spin quantum numbers for each spin
        in the system.
    gammas : ndarray
        A 1-dimensional array specifying the gyromagnetic ratios for
        each nucleus in the spin system. Must be given in the units
        of rad/s/T.
    chemical_shifts : ndarray
        A 1-dimensional array containing the chemical shifts of each spin in the
        units of ppm.
    J_couplings : ndarray
        A 2-dimensional array containing the scalar J-couplings between each
        spin in the units of Hz. Only the bottom triangle is considered.
    sop_R : ndarray or csc_array
        Relaxation superoperator without scalar relaxation of the second kind.
    B : float
        Magnetic field in units of T.
    sparse: bool, default=True
        Specifies whether to return the relaxation superoperator as dense or
        sparse array.

    Returns
    -------
    sop_R : ndarray or csc_array
        Relaxation superoperator containing the contribution from scalar
        relaxation of the second kind.
    """

    print("Processing scalar relaxation of the second kind...")
    time_start = time.time()

    # Obtain the number of spins
    nspins = spins.shape[0]

    # Make a dictionary of the basis for fast lookup
    basis_lookup = {tuple(row): idx for idx, row in enumerate(basis)}

    # Initialize arrays for the relaxation rates
    R1 = np.zeros(nspins)
    R2 = np.zeros(nspins)

    # Obtain indices of quadrupolar nuclei in the system
    quadrupolar = []
    for i, spin in enumerate(spins):
        if spin > 0.5:
            quadrupolar.append(i)
    
    # Loop over the quadrupolar nuclei
    for quad in quadrupolar:

        # Find the operator definitions of the longitudinal and transverse
        # states
        op_def_z, _ = parse_operator_string(f"I(z, {quad})", nspins)
        op_def_p, _ = parse_operator_string(f"I(+, {quad})", nspins)

        # Convert operator definitions to tuple for searching the basis
        op_def_z = tuple(op_def_z[0])
        op_def_p = tuple(op_def_p[0])

        # Find the indices of the longitudinal and transverse states
        idx_long = basis_lookup[op_def_z]
        idx_trans = basis_lookup[op_def_p]

        # Find the relaxation times of the quadrupolar nucleus
        T1 = 1 / sop_R[idx_long, idx_long]
        T2 = 1 / sop_R[idx_trans, idx_trans]

        # Convert to real values
        T1 = np.real(T1)
        T2 = np.real(T2)

        # Find the Larmor frequency of the quadrupolar nucleus
        omega_quad = gammas[quad] * B * (1 + chemical_shifts[quad] * 1e-6)

        # Find the spin quantum number of the quadrupolar nucleus
        S = spins[quad]

        # Loop over all spins
        for target, gamma in enumerate(gammas):

            # Proceed only if the gyromagnetic ratios are different
            if not gammas[quad] == gamma:

                # Find the Larmor frequency of the target spin
                omega_target = gammas[target] * B * \
                               (1 + chemical_shifts[target] * 1e-6)

                # Find the scalar coupling between spins in rad/s
                J = 2 * np.pi * J_couplings[quad][target]

                # Calculate the relaxation rates
                R1[target] += ((J**2) * S * (S + 1)) / 3 * \
                    (2 * T2) / (1 + (omega_target - omega_quad)**2 * T2**2)
                R2[target] += ((J**2) * S * (S + 1)) / 3 * \
                    (T1 + (T2 / (1 + (omega_target - omega_quad)**2 * T2**2)))

    # Get relaxation superoperator corresponding to SR2K
    with HidePrints():
        sop_R = sop_R_phenomenological(basis, R1, R2, sparse)

    print(f"SR2K superoperator constructed in {time.time() - time_start:.4f} "
          "seconds.")
    print()
    
    return sop_R

def ldb_thermalization(R: np.ndarray | sp.csc_array,
                       H_left: np.ndarray |sp.csc_array,
                       T: float,
                       zero_value: float=1e-18) -> np.ndarray | sp.csc_array:
    """
    Applies the Levitt-Di Bari thermalization to the relaxation superoperator.

    Parameters
    ----------
    R : ndarray or csc_array
        Relaxation superoperator to be thermalized.
    H_left : ndarray or csc_array
        Left-side coherent Hamiltonian superoperator.
    T : float
        Temperature of the spin bath in Kelvin.
    zero_value : float, default=1e-18
        This threshold is used to estimate the convergence in the matrix
        exponential and to eliminate small values from the array.
    
    Returns
    -------
    R : ndarray or csc_array
        Thermalized relaxation superoperator.
    """
    print("Applying thermalization to the relaxation superoperator...")
    time_start = time.time()

    # Get the matrix exponential corresponding to the Boltzmann distribution
    with HidePrints():
        P = expm(const.hbar / (const.k * T) * H_left, zero_value)

    # Calculate the thermalized relaxation superoperator
    R = R @ P

    print(f"Thermalization applied in {time.time() - time_start:.4f} seconds.")
    print()

    return R