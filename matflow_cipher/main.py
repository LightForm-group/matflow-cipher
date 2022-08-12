"`matflow_cipher.main.py`"

from matflow.scripting import get_wrapper_script

from matflow_cipher import input_mapper, output_mapper, sources_mapper

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
    }
    hickle.dump(kwargs, path)

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


@sources_mapper(
    task='generate_phase_field_input',
    method='from_random_voronoi',
    script='generate_phase_field_input_from_random_voronoi',
)
def generate_phase_field_input_from_random_voronoi():

    script_name = 'generate_phase_field_input_from_random_voronoi.py'
    snippets = [{'name': 'generate_phase_field_input_from_random_voronoi.py'}]
    outputs = ['phase_field_input']
    out = {
        'script': {
            'content': get_wrapper_script(__package__, script_name, snippets, outputs),
            'filename': script_name,
        }
    }
    return out

@sources_mapper(
    task='generate_phase_field_input',
    method='from_volume_element',
    script='generate_phase_field_input_from_volume_element',
)
def generate_phase_field_input_from_random_voronoi():

    script_name = 'generate_phase_field_input_from_volume_element.py'
    snippets = [{'name': 'generate_phase_field_input_from_volume_element.py'}]
    outputs = ['phase_field_input']
    out = {
        'script': {
            'content': get_wrapper_script(__package__, script_name, snippets, outputs),
            'filename': script_name,
        }
    }
    return out    

@output_mapper(
    output_name='phase_field_input',
    task='generate_phase_field_input',
    method='from_random_voronoi',
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

@input_mapper(input_file='inputs.hdf5', task='simulate_grain_growth', method='phase_field')
def write_simulate_grain_growth_phase_field_input(path, phase_field_input):
    kwargs = {'phase_field_input': phase_field_input}
    hickle.dump(kwargs, path)


@sources_mapper(
    task='simulate_grain_growth',
    method='phase_field',
    script='generate_cipher_input',
)
def generate_cipher_input():

    script_name = 'generate_cipher_input.py'
    snippets = [{'name': 'generate_cipher_input.py'}]
    outputs = []
    out = {
        'script': {
            'content': get_wrapper_script(__package__, script_name, snippets, outputs),
            'filename': script_name,
        }
    }
    return out
