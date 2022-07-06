"`matflow_cipher.main.py`"

from black import out
from cipher_parse._version import __version__ as cipher_parse_version
from cipher_parse.cipher_input import (
    CIPHERInput,
    MaterialDefinition,
    InterfaceDefinition,
    PhaseTypeDefinition,
)

from matflow_cipher import func_mapper, software_versions


@func_mapper(task="generate_phase_field_input", method="from_random_voronoi")
def generate_phase_field_input_from_random_voronoi(
    materials,
    interfaces,
    num_phases,
    grid_size,
    size,
    components,
    outputs,
    solution_parameters,
    random_seed,
):
    mats = []
    for mat_i in materials:
        if "phase_types" in mat_i:
            mat_i["phase_types"] = [
                PhaseTypeDefinition(**j) for j in mat_i["phase_types"]
            ]
            mat_i = MaterialDefinition(**mat_i)
        mats.append(mat_i)

    interfaces = [InterfaceDefinition(**int_i) for int_i in interfaces]

    inp = CIPHERInput.from_random_voronoi(
        materials=mats,
        interfaces=interfaces,
        num_phases=num_phases,
        grid_size=grid_size,
        size=size,
        components=components,
        outputs=outputs,
        solution_parameters=solution_parameters,
        random_seed=random_seed,
    )
    return {"phase_field_input": inp.to_JSON()}


@software_versions()
def get_versions():
    "Get versions of pertinent software associated with this extension."

    out = {
        "cipher-parse (Python)": {"version": cipher_parse_version},
    }
    return out
