import numpy as np
import ase
from vectra.decompose import decompose
import dataclasses
from ase import units
import rdkit2ase
import networkx as nx

from ase.md.md import MolecularDynamics
from ase.md.nvtberendsen import NVTBerendsen


class DecomposedBerendsenThermostat(NVTBerendsen):
    """Decomposed Berendsen thermostat.

    This thermostat separates the kinetic energy into translational, rotational,
    and vibrational components.

    Parameters
    ----------
    atoms : ase.Atoms
        The Atoms object to be simulated.
    timestep : float
        The integration timestep, in ASE time units.
    temperature_trans : float
        Target temperature for the translational degrees of freedom, in Kelvin.
    temperature_rot : float
        Target temperature for the rotational degrees of freedom, in Kelvin.
    temperature_vib : float
        Target temperature for the vibrational degrees of freedom, in Kelvin.
    tau_trans : float
        Time constant for the translational thermostat, in ASE time units.
    tau_rot : float
        Time constant for the rotational thermostat, in ASE time units.
    tau_vib : float
        Time constant for the vibrational thermostat, in ASE time units.
    suggestions : tuple or list, optional
        Suggestions for molecular decomposition, passed to `rdkit2ase`.
        Default is an empty tuple.
    connectivity : list, optional
        Connectivity information for the atoms. If not provided, it will be
        inferred. Default is None.
    fix_com : bool, optional
        Whether to fix the center of mass of the system. Default is True.

    Example
    -------

    >>> import rdkit2ase
    >>> from ase import units
    >>> from mace.calculators import mace_mp
    >>> import vectra
    >>> water = rdkit2ase.smiles2conformers(smiles="O", numConfs=10)
    >>> box = rdkit2ase.pack(
    ...     data=[water],
    ...     counts=[3],
    ...     density=1000,
    ...     packmol="packmol.jl",
    >>> )
    >>> box.calc = mace_mp()
    >>> md = vectra.DecomposedBerendsenThermostat(
    ...     atoms=box,
    ...     timestep=0.5 * units.fs,
    ...     temperature_rot=5,
    ...     temperature_trans=5,
    ...     temperature_vib=5,
    ...     tau_rot=0.5 * 10 * units.fs,
    ...     tau_trans=0.5 * 10 * units.fs,
    ...     tau_vib=0.5 * 10 * units.fs,
    >>> )
    >>> md.run(100)

    """

    def __init__(
        self,
        atoms: ase.Atoms,
        timestep: float,
        temperature_trans: float,
        temperature_rot: float,
        temperature_vib: float,
        tau_trans: float,
        tau_rot: float,
        tau_vib: float,
        suggestions: tuple | list | None = tuple(),
        connectivity: list | None = None,
        fix_com: bool = True,
    ):
        MolecularDynamics.__init__(self, atoms, timestep)
        self.temperature_trans = temperature_trans
        self.temperature_rot = temperature_rot
        self.temperature_vib = temperature_vib
        self.tau_trans = tau_trans
        self.tau_rot = tau_rot
        self.tau_vib = tau_vib
        self.kB = 1 * units.kB
        if isinstance(suggestions, tuple):
            self.suggestions = list(suggestions)
        else:
            self.suggestions = suggestions
        self.connectivity = connectivity
        self.atoms = atoms
        self.timestep = timestep
        self.fix_com = fix_com

        # print the number and
        graph = rdkit2ase.ase2networkx(atoms, suggestions=self.suggestions)
        for component in nx.connected_components(graph):
            print(f"Found component with {len(component)} atoms")

    @property
    def temperature(self):
        # TODO: weigh the temperatures by the number of degrees of freedom
        return np.mean(
            [
                self.temperature_trans,
                self.temperature_rot,
                self.temperature_vib,
            ]
        )

    def _scale_component(self, comp, ekin, dof, tau, target_temp):
        """Scales a single component of the kinetic energy.

        Parameters
        ----------
        comp : np.ndarray
            The momentum component to be scaled.
        ekin : float
            The kinetic energy of the component.
        dof : int
            The number of degrees of freedom for the component.
        tau : float
            The time constant for the thermostat, in ASE time units.
        target_temp : float
            The target temperature for the component, in Kelvin.

        Returns
        -------
        np.ndarray
            The scaled momentum component.
        float or None
            The old temperature of the component, or None if it could not be
            calculated.
        """
        if dof > 0 and ekin > 1e-12:
            T_old = 2 * ekin / (dof * self.kB)
            factor = np.sqrt(1 + (self.timestep / tau) * (target_temp / T_old - 1))
            comp *= factor
            return comp, T_old
        elif target_temp == 0:
            comp[:] = 0
        return comp, None

    def scale_velocities(self):
        p = self.atoms.get_momenta()
        m = self.atoms.get_masses()

        components = decompose(
            self.atoms,
            p,
            suggestions=self.suggestions,
            connectivity=self.connectivity,
        )
        new_p = np.zeros_like(p)

        trans_temp, rot_temp, vib_temp = [], [], []

        for trans_p, rot_p, vib_p, idx in components:
            m_sub = m[idx][:, None]

            ekin_trans = 0.5 * np.sum(trans_p**2 / m_sub)
            ekin_rot = 0.5 * np.sum(rot_p**2 / m_sub)
            ekin_vib = 0.5 * np.sum(vib_p**2 / m_sub)

            n_atoms = len(idx)
            dof_trans = 3
            # TODO: rot dof could be 2 for linear molecules
            dof_rot = 0 if n_atoms == 1 else (2 if n_atoms == 2 else 3)
            dof_vib = max(0, 3 * n_atoms - dof_trans - dof_rot)

            trans_p, T_trans = self._scale_component(
                trans_p, ekin_trans, dof_trans, self.tau_trans, self.temperature_trans
            )
            if T_trans is not None:
                trans_temp.append(T_trans)

            rot_p, T_rot = self._scale_component(
                rot_p, ekin_rot, dof_rot, self.tau_rot, self.temperature_rot
            )
            if T_rot is not None:
                rot_temp.append(T_rot)

            vib_p, T_vib = self._scale_component(
                vib_p, ekin_vib, dof_vib, self.tau_vib, self.temperature_vib
            )
            if T_vib is not None:
                vib_temp.append(T_vib)

            new_p[idx] = trans_p + rot_p + vib_p

        self.atoms.set_momenta(new_p)

        self.atoms.info["trans_temp"] = np.mean(trans_temp) if trans_temp else 0.0
        self.atoms.info["rot_temp"] = np.mean(rot_temp) if rot_temp else 0.0
        self.atoms.info["vib_temp"] = np.mean(vib_temp) if vib_temp else 0.0


@dataclasses.dataclass
class DecomposedBerendsenThermostatDC:
    """
    Dataclass representing the decomposed Berendsen thermostat parameters.

    Parameters
    ----------
    timestep : float
        The integration timestep for the thermostat in femtoseconds.
    temperature_trans : float
        Target translational temperature (in Kelvin).
    temperature_rot : float
        Target rotational temperature (in Kelvin).
    temperature_vib : float
        Target vibrational temperature (in Kelvin).
    fix_com : bool, optional
        If True, the center of mass is fixed during the simulation (default is True).
    tau_trans : float
        Coupling time constant for translational degrees of freedom (in femtoseconds).
    tau_rot : float
        Coupling time constant for rotational degrees of freedom (in femtoseconds).
    tau_vib : float
        Coupling time constant for vibrational degrees of freedom (in femtoseconds).
    suggestions : tuple or list or None, optional
        Optional suggestions for thermostat configuration (default is empty tuple).
    connectivity : list or None, optional
        Optional connectivity information for the system (default is None).
    """

    time_step: float
    temperature_trans: float
    temperature_rot: float
    temperature_vib: float
    tau_trans: float
    tau_rot: float
    tau_vib: float
    suggestions: tuple | list | None = tuple()
    connectivity: list | None = None
    fix_com: bool = True

    @property
    def temperature(self):
        return 0

    def get_thermostat(self, atoms: ase.Atoms) -> DecomposedBerendsenThermostat:
        return DecomposedBerendsenThermostat(
            atoms=atoms,
            timestep=self.time_step * units.fs,
            temperature_trans=self.temperature_trans,
            temperature_rot=self.temperature_rot,
            temperature_vib=self.temperature_vib,
            tau_trans=self.tau_trans * units.fs,
            tau_rot=self.tau_rot * units.fs,
            tau_vib=self.tau_vib * units.fs,
            suggestions=self.suggestions,
            connectivity=self.connectivity,
            fix_com=self.fix_com,
        )
