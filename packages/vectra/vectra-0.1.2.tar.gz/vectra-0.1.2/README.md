# Vectra: Vector Transformations and Thermostats for ASE Atoms and Molecules

Vectra is a Python package designed to provide tools for vector transformations on ASE atoms and molecules, as well as specialized thermostats for molecular dynamics simulations.

## Features

- **Decomposition of Quantities**: Decompose total quantities (e.g., forces, momenta) into translational, rotational, and vibrational components for individual molecules or groups of atoms.
- **Decomposed Berendsen Thermostat**: Apply Berendsen thermostats that operate independently on translational, rotational, and vibrational degrees of freedom.

## Installation

```bash
pip install vectra
```

## Usage

### Decomposing Quantities

Decompose a quantity (like forces or velocities) for a set of atoms into translational, rotational, and vibrational components for each identified molecule.

```python
import ase
import numpy as np
from vectra import decompose
from rdkit2ase import smiles2atoms
from mace.calculators import mace_mp

atoms = smiles2atoms(smiles="O")
atoms.calc = mace_mp() # Any ASE calculator. We are using a uMLIP here.

# Get forces from the calculator
forces = atoms.get_forces()

# Decompose forces
# The 'decompose' function automatically identifies molecules based on connectivity.
decomposed_molecules = decompose(atoms, quantity=forces)

for i, (trans_c, rot_c, vib_c, component_indices) in enumerate(decomposed_molecules):
    print(f"\nMolecule {i+1} (atoms {component_indices}):")
    print("  Translational component:", trans_c)
    print("  Rotational component:", rot_c)
    print("  Vibrational component:", vib_c)
```


### Using Decomposed Berendsen Thermostat

Apply a Berendsen thermostat that can control translational, rotational, and vibrational temperatures independently.

```python
import ase.units
from vectra import DecomposedBerendsenThermostat
from rdkit2ase import smiles2conformers, pack
from mace.calculators import mace_mp

# Create a system with multiple water molecules using smiles2conformers and pack
water = smiles2conformers(smiles="O", num_conformers=1)[0] # Get one conformer
atoms = pack([water], counts=[3], density=1000)

atoms.calc = mace_mp()

md = DecomposedBerendsenThermostat(
    atoms=atoms,
    timestep=0.5, # fs
    temperature_trans=500,
    temperature_rot=400,
    temperature_vib=300,
    tau_trans=0.5 * 100 * ase.units.fs,
    tau_rot=0.5 * 100 * ase.units.fs,
    tau_vib=0.5 * 100 * ase.units.fs,
)

md.run(1000)
```
