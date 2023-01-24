"`matflow_cipher.main.py`"

import json
from pathlib import Path
from textwrap import dedent

from matflow_cipher import input_mapper, output_mapper

import hickle

@input_mapper(
    input_file='inputs.hdf5',
    task='generate_phase_field_input',
    method='from_random_voronoi',
)
def write_generate_phase_field_input_RV_input(
    path,
    materials,
    interfaces,
    num_phases,
    grid_size,
    size,
    components,
    outputs,
    solution_parameters,
    random_seed,
    is_periodic,
):
    kwargs = {
        'materials': materials,
        'interfaces': interfaces,
        'num_phases': num_phases,
        'grid_size': grid_size,
        'size': size,
        'components': components,
        'outputs': outputs,
        'solution_parameters': solution_parameters,
        'random_seed': random_seed,
        'is_periodic': is_periodic,
    }
    hickle.dump(kwargs, path)

@input_mapper(
    input_file='inputs.hdf5',
    task='generate_phase_field_input',
    method='from_random_voronoi_with_orientations',
)
def write_generate_phase_field_input_RV_with_orientations_input(
    path,
    materials,
    interfaces,
    num_phases,
    grid_size,
    size,
    components,
    outputs,
    solution_parameters,
    orientations,
    random_seed,
    is_periodic,
    interface_energy_misorientation_expansion,
):
    kwargs = {
        'materials': materials,
        'interfaces': interfaces,
        'num_phases': num_phases,
        'grid_size': grid_size,
        'size': size,
        'components': components,
        'outputs': outputs,
        'solution_parameters': solution_parameters,
        'orientations': orientations,
        'random_seed': random_seed,
        'is_periodic': is_periodic,
        'interface_energy_misorientation_expansion': interface_energy_misorientation_expansion,
    }
    hickle.dump(kwargs, path)



@input_mapper(
    input_file="generate_phase_field_input_from_random_voronoi.py",
    task="generate_phase_field_input",
    method="from_random_voronoi",
)
def write_generate_phase_field_input_from_random_voronoi_py(path):
    with Path(path).open("wt") as fp:
        fp.write(
            dedent(
                """
            from cipher_parse import (
                CIPHERInput,
                MaterialDefinition,
                InterfaceDefinition,
                PhaseTypeDefinition,
            )
            import sys
            import hickle
            from pathlib import Path

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
                is_periodic,
            ):
                # initialise `MaterialDefinition`, `InterfaceDefinition` and 
                # `PhaseTypeDefinition` objects:
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
                    is_periodic=is_periodic,
                )
                phase_field_input = inp.to_JSON(keep_arrays=True)

                return phase_field_input

            if __name__ == "__main__":
                inputs = hickle.load(sys.argv[1])
                outputs = generate_phase_field_input_from_random_voronoi(**inputs)
                hickle.dump(outputs, "outputs.hdf5")
            """
            )
        )

@input_mapper(
    input_file="generate_phase_field_input_from_random_voronoi_orientations.py",
    task="generate_phase_field_input",
    method="from_random_voronoi_with_orientations",
)
def write_generate_phase_field_input_from_random_voronoi_orientations_py(path):
    with Path(path).open("wt") as fp:
        fp.write(
            dedent(
                """
            import sys
            from pathlib import Path
            
            import hickle
            import numpy as np

            from cipher_parse import (
                CIPHERInput,
                MaterialDefinition,
                InterfaceDefinition,
                PhaseTypeDefinition,
            )
            from cipher_parse.utilities import read_shockley

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
                is_periodic,
                orientations,
                interface_energy_misorientation_expansion,
            ):
                quats = orientations['quaternions']

                # initialise `MaterialDefinition`, `InterfaceDefinition` and 
                # `PhaseTypeDefinition` objects:
                mats = []
                for mat_idx, mat_i in enumerate(materials):
                    if "phase_types" in mat_i:
                        mat_i["phase_types"] = [
                            PhaseTypeDefinition(**j) for j in mat_i["phase_types"]
                        ]
                    else:
                        mat_i["phase_types"] = [PhaseTypeDefinition()]
                    
                    if mat_idx == 0:
                        # add oris to the first defined phase type of the first material:
                        mat_i["phase_types"][0].orientations = quats

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
                    is_periodic=is_periodic,
                )

                if interface_energy_misorientation_expansion:
                    # Calculate misorientations between all phases, and use Read-Shockley to assign
                    # a GB energy for each phase pair; optionally bin phase-pairs together:
                    
                    RS_params = interface_energy_misorientation_expansion['read_shockley']

                    misori = inp.geometry.get_misorientation_matrix()
                    E_GB = read_shockley(misori, **RS_params)

                    num_bins = interface_energy_misorientation_expansion.get('num_bins')
                    if num_bins:
                        bin_edges = np.linspace(0, RS_params['E_max'], num=num_bins)
                    else:
                        bin_edges = None
                        
                    for int_name in interface_energy_misorientation_expansion['interfaces']:
                        inp.apply_interface_property(
                            base_interface_name=int_name,
                            property_name=('energy', 'e0'),
                            property_values=E_GB,
                            additional_metadata={'misorientation': misori},
                            bin_edges=bin_edges,
                        )

                phase_field_input = inp.to_JSON(keep_arrays=True)

                return phase_field_input

            if __name__ == "__main__":
                inputs = hickle.load(sys.argv[1])
                outputs = generate_phase_field_input_from_random_voronoi(**inputs)
                hickle.dump(outputs, "outputs.hdf5")
            """
            )
        )

@input_mapper(
    input_file='inputs.hdf5',
    task='generate_phase_field_input',
    method='from_volume_element',
)
def write_generate_phase_field_input_VE_input(
    path,
    volume_element,
    materials,
    interfaces,
    phase_type_map,
    size,
    components,
    outputs,
    solution_parameters,
    random_seed,
    interface_energy_misorientation_expansion,
):
    kwargs = {
        'volume_element': volume_element,
        'materials': materials,
        'interfaces': interfaces,
        'phase_type_map': phase_type_map,
        'size': size,
        'components': components,
        'outputs': outputs,
        'solution_parameters': solution_parameters,
        'random_seed': random_seed,
        'interface_energy_misorientation_expansion': interface_energy_misorientation_expansion,
    }
    hickle.dump(kwargs, path)

@input_mapper(
    input_file="generate_phase_field_input_from_volume_element.py",
    task="generate_phase_field_input",
    method="from_volume_element",
)
def write_generate_phase_field_input_from_volume_element_py(path):
    with Path(path).open("wt") as fp:
        fp.write(
            dedent(
                """
            import sys
            
            import numpy as np
            import hickle

            from cipher_parse import (
                CIPHERInput,
                CIPHERGeometry,
                MaterialDefinition,
                InterfaceDefinition,
                PhaseTypeDefinition,
            )
            from cipher_parse.utilities import read_shockley

            def generate_phase_field_input_from_volume_element(
                volume_element,
                materials,
                interfaces,
                phase_type_map,
                size,
                components,
                outputs,
                solution_parameters,
                random_seed,
                interface_energy_misorientation_expansion,
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

                geom = volume_element_to_cipher_geometry(
                    volume_element=volume_element, 
                    cipher_materials=mats,
                    cipher_interfaces=interfaces,
                    phase_type_map=phase_type_map,
                    size=size,
                    random_seed=random_seed,
                )

                inp = CIPHERInput(
                    geometry=geom,
                    components=components,
                    outputs=outputs,
                    solution_parameters=solution_parameters,
                )
                if interface_energy_misorientation_expansion:
                    # Calculate misorientations between all phases, and use Read-Shockley to assign
                    # a GB energy for each phase pair; optionally bin phase-pairs togetherL
                    
                    RS_params = interface_energy_misorientation_expansion['read_shockley']

                    misori = inp.geometry.get_misorientation_matrix()
                    E_GB = read_shockley(misori, **RS_params)

                    num_bins = interface_energy_misorientation_expansion.get('num_bins')
                    if num_bins:
                        bin_edges = np.linspace(0, RS_params['E_max'], num=num_bins)
                    else:
                        bin_edges = None
                        
                    for int_name in interface_energy_misorientation_expansion['interfaces']:
                        inp.apply_interface_property(
                            base_interface_name=int_name,
                            property_name=('energy', 'e0'),
                            property_values=E_GB,
                            additional_metadata={'misorientation': misori},
                            bin_edges=bin_edges,
                        )

                phase_field_input = inp.to_JSON(keep_arrays=True)
                
                return phase_field_input

            def volume_element_to_cipher_geometry(
                volume_element,
                cipher_materials,
                cipher_interfaces,
                phase_type_map=None,
                size=None,
                random_seed=None
            ):

                uq, inv = np.unique(volume_element['constituent_phase_label'], return_inverse=True)
                cipher_phases = {i: np.where(inv == idx)[0] for idx, i in enumerate(uq)}
                orientations = volume_element['orientations']['quaternions']
                for mat_name_i in cipher_phases:
                    phases_set = False
                    if phase_type_map:
                        phase_type_name = phase_type_map[mat_name_i]
                    else:
                        phase_type_name = mat_name_i
                    for mat in cipher_materials:
                        for phase_type_i in mat.phase_types:
                            if phase_type_i.name == phase_type_name:
                                phase_i_idx = cipher_phases[mat_name_i]
                                phase_type_i.phases = phase_i_idx
                                phase_type_i.orientations = orientations[phase_i_idx]
                                phases_set = True
                                break
                        if phases_set:
                            break

                    if not phases_set:
                        raise ValueError(
                            f"No defined material/phase-type for Dream3D phase {mat_name_i!r}"
                        )

                geom = CIPHERGeometry(
                    voxel_phase=volume_element['element_material_idx'],
                    size=volume_element['size'] if size is None else size,
                    materials=cipher_materials,
                    interfaces=cipher_interfaces,
                    random_seed=random_seed,
                )
                return geom
            
            if __name__ == "__main__":
                inputs = hickle.load(sys.argv[1])
                outputs = generate_phase_field_input_from_volume_element(**inputs)
                hickle.dump(outputs, "outputs.hdf5")

            """
            )
        )


@output_mapper(
    output_name='phase_field_input',
    task='generate_phase_field_input',
    method='from_random_voronoi',
)
@output_mapper(
    output_name='phase_field_input',
    task='generate_phase_field_input',
    method='from_random_voronoi_with_orientations',
)
@output_mapper(
    output_name='phase_field_input',
    task='generate_phase_field_input',
    method='from_volume_element',
)
@output_mapper(
    output_name='phase_field_output',
    task='simulate_grain_growth',
    method='phase_field',
)
def read_phase_field_input(path):
    return hickle.load(path)

@input_mapper(
    input_file="cipher_output_parse_args.json",
    task="simulate_grain_growth",
    method="phase_field",
)
def write_cipher_output_parse_args_json(path, num_VTU_files, VTU_files_time_interval, derive_outputs, save_outputs, delete_VTIs, delete_VTUs):
    if num_VTU_files is not None and VTU_files_time_interval is not None:
        num_VTU_files = None
    with Path(path).open("wt") as fp:
        args = {
            'num_VTU_files': num_VTU_files,
            'VTU_files_time_interval': VTU_files_time_interval,
            'derive_outputs': derive_outputs,
            'save_outputs': save_outputs,
            'delete_VTIs': delete_VTIs,
            'delete_VTUs': delete_VTUs,
        }
        json.dump(args, fp)

@input_mapper(
    input_file="write_cipher_input.py",
    task="simulate_grain_growth",
    method="phase_field",
)
def write_cipher_input_py(path):
    with Path(path).open("wt") as fp:
        fp.write(
            dedent(
                """
                import hickle
                from cipher_parse import CIPHERInput

                if __name__ == "__main__":
                    inp = CIPHERInput.from_JSON(hickle.load('inputs.hdf5')['phase_field_input'])
                    inp.write_yaml('cipher_input.yaml')
                    inp.geometry.write_VTK('initial.vti')

            """
            )
        )

@input_mapper(
    input_file="cipher_output_parse.py",
    task="simulate_grain_growth",
    method="phase_field",
)
def write_cipher_output_parse_py(path):
    with Path(path).open("wt") as fp:
        fp.write(
            dedent(
                """
                import hickle
                import json
                from pathlib import Path

                from cipher_parse import CIPHEROutput

                if __name__ == "__main__":

                    with Path('cipher_output_parse_args.json').open('rt') as fp:
                        args = json.load(fp)

                    out = CIPHEROutput.parse(directory='.', options=args)
                    out_js = out.to_JSON(keep_arrays=True)
                    hickle.dump(out_js, 'post_proc_outputs.hdf5')

            """
            )
        )

@input_mapper(input_file='inputs.hdf5', task='simulate_grain_growth', method='phase_field')
def write_simulate_grain_growth_phase_field_input(path, phase_field_input):
    kwargs = {'phase_field_input': phase_field_input}
    hickle.dump(kwargs, path)

