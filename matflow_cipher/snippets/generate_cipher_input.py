from matflow.scripting import main_func
from cipher_parse.cipher_input import CIPHERInput
from pathlib import Path
from textwrap import dedent

@main_func
def generate_cipher_input(phase_field_input):
    inp = CIPHERInput.from_JSON(phase_field_input)
    inp.write_yaml('cipher_input.yaml')
    output_lookup = {i: f"out output.{idx}" for idx, i in enumerate(inp.outputs)}

    # MEGA HACK: also write out a Paraview batch script for converting VTU to VTI files:
    # The original VTU fils are more useful for visualisation, and the VTI files are useful
    # for post-processing.
    with Path('vtu2vti.py').open('wt') as fp:
        fp.write(dedent(f"""
            import os

            from paraview.simple import *

            vtu_files = []
            for root, dirs, files in os.walk("."):  # from your argv[1]
                for f in files:
                    if f.endswith(".vtu"):
                        vtu_files.append(f)
            
            for file_i_path in vtu_files:
                file_i_base_name = file_i_path.split(".")[0]
                vtu_data_i = XMLUnstructuredGridReader(
                    FileName=[os.getcwd() + os.path.sep + file_i_path]
                )
                resampleToImage1 = ResampleToImage(Input=vtu_data_i)
                resampleToImage1.SamplingDimensions = {inp.geometry.grid_size.tolist()!r}
                SetActiveSource(resampleToImage1)
                SaveData(file_i_base_name + ".vti", resampleToImage1)
        """))

    # MEGA HACK: also write out a post-processing script here that can be invoked as a 
    # command in the main task:
    with Path('post_processing.py').open('wt') as fp:
        fp.write(dedent(f"""
            import re
            import sys
            import shutil
            from pathlib import Path
            
            import hickle
            import pyvista as pv
            import numpy as np
            from cipher_parse.cipher_output import parse_cipher_stdout
            from cipher_parse.utilities import get_evenly_spaced_subset

            max_viz_files = int(sys.argv[1])

            path = Path('').resolve()
            vti_file_list = sorted(
                [i for i in path.glob('*.vti')],
                key=lambda x: int(re.search(r"\d+", x.name).group())
            )
            vtu_file_list = sorted(
                [i for i in path.glob('*.vtu')],
                key=lambda x: int(re.search(r"\d+", x.name).group())
            )
            data = []
            output_lookup = {output_lookup!r}
            for file_i in vti_file_list:
                mesh = pv.get_reader(file_i).read()

                requested_outputs = {{}}
                for name in output_lookup:
                    requested_outputs[name] = mesh.get_array(output_lookup[name]).reshape(
                        mesh.dimensions, order='F')
                
                grain_map = requested_outputs['phaseid']
                uniq, counts = np.unique(grain_map.astype(int), return_counts=True)
                num_voxels_per_grain = dict(zip(uniq, counts))
                grain_diameter = {{
                    grain_ID: (6 * vox_count / np.pi) ** (1/3)
                    for grain_ID, vox_count in num_voxels_per_grain.items()
                }}
                data.append({{
                    'dimensions': mesh.dimensions,
                    'spacing': mesh.spacing,
                    'number_of_cells': mesh.number_of_cells,
                    'number_of_points': mesh.number_of_points,
                    'num_voxels_per_grain': num_voxels_per_grain,
                    'grain_diameter': grain_diameter,
                    **requested_outputs,
                }})

            stdout_dat = parse_cipher_stdout('stdout.log')
            outputs = {{
                'vti_file_list': [str(i) for i in vti_file_list],
                'vtu_file_list': [str(i) for i in vtu_file_list],
                'data': data,
                'stdout': stdout_dat,
                'time': [stdout_dat['outputs'][i.name] for i in vtu_file_list],
            }}
            hickle.dump(outputs, "post_proc_outputs.hdf5")

            viz_dir = Path("original_viz")
            viz_dir.mkdir()
            vtu_orig_file_list = []
            for viz_file_i in vtu_file_list:
                dst_i = viz_dir.joinpath(viz_file_i.name).with_suffix('.viz' + viz_file_i.suffix)
                shutil.move(viz_file_i, dst_i)
                vtu_orig_file_list.append(dst_i)

            for viz_file_i in vti_file_list:
                dst_i = viz_dir.joinpath(viz_file_i.name).with_suffix('.viz' + viz_file_i.suffix)
                shutil.move(viz_file_i, dst_i)

            viz_files_idx = get_evenly_spaced_subset(vtu_file_list, max_viz_files)        
            print(f'viz_files_idx: {{viz_files_idx}}')

            print(f'vtu_orig_file_list: {{vtu_orig_file_list}}')

            for i in viz_files_idx:
                viz_file_i = vtu_orig_file_list[i]
                dst_i = Path('').joinpath(viz_file_i.name).with_suffix('').with_suffix('.vtu')
                print(f"viz_file_i: {{viz_file_i}}")
                print(f"dst_i: {{dst_i}}")
                shutil.copy(viz_file_i, dst_i)
                

        """))
