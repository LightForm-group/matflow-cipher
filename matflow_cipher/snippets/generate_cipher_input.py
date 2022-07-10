from matflow.scripting import main_func
from cipher_parse.cipher_input import CIPHERInput
from pathlib import Path
from textwrap import dedent

@main_func
def generate_cipher_input(phase_field_input):
    inp = CIPHERInput.from_JSON(phase_field_input)
    inp.write_yaml('cipher_input.yaml')

    # MEGA HACK: also write out a post-processing script here that can be invoked as a 
    # command in the main task:
    with Path('post_processing.py').open('wt') as fp:
        fp.write(dedent("""
            import hickle
            from pathlib import Path
            import pyvista as pv

            from cipher_parse.cipher_input import CIPHERInput

            path = Path('').resolve()
            print(path)

            file_list = [str(i) for i in path.glob('*.vtu')]
            data = []
            for file_i in file_list:
                mesh = pv.get_reader(file_i).read()
                data.append({
                    'number_of_cells': mesh.number_of_cells,
                    'number_of_points': mesh.number_of_points,
                })

            outputs = {
                'file_list': file_list,
                'data': data,
            }
            hickle.dump(outputs, "post_proc_outputs.hdf5")
            
        """))
