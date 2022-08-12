from matflow.scripting import main_func
from cipher_parse.cipher_input import CIPHERInput
from pathlib import Path
from textwrap import dedent

@main_func
def generate_cipher_input(phase_field_input):
    inp = CIPHERInput.from_JSON(phase_field_input)
    inp.write_yaml('cipher_input.yaml')

    # MEGA HACK: also write out a Paraview batch script for converting VTU to VTI files:
    with Path('vtu2vti.py').open('wt') as fp:
        fp.write(dedent("""
            import os

            vtu_files = []
            for root, dirs, files in os.walk("."):  # from your argv[1]
                for f in files:
                    if f.endswith(".vtu"):
                        vtu_files.append(f)

            print(vtu_files)

            # state file generated using paraview version 5.5.2

            # ----------------------------------------------------------------
            # setup views used in the visualization
            # ----------------------------------------------------------------

            # trace generated using paraview version 5.5.2

            #### import the simple module from the paraview
            from paraview.simple import *

            #### disable automatic camera reset on 'Show'
            paraview.simple._DisableFirstRenderCameraReset()

            # get the material library
            materialLibrary1 = GetMaterialLibrary()

            # Create a new 'Render View'
            renderView1 = CreateView("RenderView")
            renderView1.ViewSize = [1546, 714]
            renderView1.AnnotationColor = [0.0, 0.0, 0.0]
            renderView1.AxesGrid = "GridAxes3DActor"
            renderView1.OrientationAxesLabelColor = [0.0, 0.0, 0.0]
            renderView1.CenterOfRotation = [50.0, 50.0, 50.0]
            renderView1.StereoType = 0
            renderView1.CameraPosition = [50.0, 50.0, 384.60652149512316]
            renderView1.CameraFocalPoint = [50.0, 50.0, 50.0]
            renderView1.CameraParallelScale = 86.60254037844386
            renderView1.Background = [0.32, 0.34, 0.43]
            renderView1.OSPRayMaterialLibrary = materialLibrary1

            # init the 'GridAxes3DActor' selected for 'AxesGrid'
            renderView1.AxesGrid.XTitleColor = [0.0, 0.0, 0.0]
            renderView1.AxesGrid.XTitleFontFile = ""
            renderView1.AxesGrid.YTitleColor = [0.0, 0.0, 0.0]
            renderView1.AxesGrid.YTitleFontFile = ""
            renderView1.AxesGrid.ZTitleColor = [0.0, 0.0, 0.0]
            renderView1.AxesGrid.ZTitleFontFile = ""
            renderView1.AxesGrid.XLabelColor = [0.0, 0.0, 0.0]
            renderView1.AxesGrid.XLabelFontFile = ""
            renderView1.AxesGrid.YLabelColor = [0.0, 0.0, 0.0]
            renderView1.AxesGrid.YLabelFontFile = ""
            renderView1.AxesGrid.ZLabelColor = [0.0, 0.0, 0.0]
            renderView1.AxesGrid.ZLabelFontFile = ""

            # ----------------------------------------------------------------
            # restore active view
            SetActiveView(renderView1)
            # ----------------------------------------------------------------

            # ----------------------------------------------------------------
            # setup the data processing pipelines
            # ----------------------------------------------------------------

            for file_i_path in vtu_files:

                file_i_base_name = file_i_path.split(".")[0]

                # create a new 'XML Unstructured Grid Reader'
                vtu_data_i = XMLUnstructuredGridReader(
                    FileName=[os.getcwd() + os.path.sep + file_i_path]
                )
                vtu_data_i.CellArrayStatus = ["Rank", "out output"]

                # create a new 'Resample To Image'
                resampleToImage1 = ResampleToImage(Input=vtu_data_i)
                resampleToImage1.SamplingDimensions = [100, 100, 100]
                resampleToImage1.SamplingBounds = [0.0, 100.0, 0.0, 100.0, 0.0, 100.0]

                # ----------------------------------------------------------------
                # setup the visualization in view 'renderView1'
                # ----------------------------------------------------------------

                # show data from resampleToImage1
                resampleToImage1Display = Show(resampleToImage1, renderView1)

                # trace defaults for the display properties.
                resampleToImage1Display.Representation = "Outline"
                resampleToImage1Display.ColorArrayName = [None, ""]
                resampleToImage1Display.OSPRayScaleArray = "Rank"
                resampleToImage1Display.OSPRayScaleFunction = "PiecewiseFunction"
                resampleToImage1Display.SelectOrientationVectors = "None"
                resampleToImage1Display.ScaleFactor = 10.0
                resampleToImage1Display.SelectScaleArray = "None"
                resampleToImage1Display.GlyphType = "Arrow"
                resampleToImage1Display.GlyphTableIndexArray = "None"
                resampleToImage1Display.GaussianRadius = 0.5
                resampleToImage1Display.SetScaleArray = ["POINTS", "Rank"]
                resampleToImage1Display.ScaleTransferFunction = "PiecewiseFunction"
                resampleToImage1Display.OpacityArray = ["POINTS", "Rank"]
                resampleToImage1Display.OpacityTransferFunction = "PiecewiseFunction"
                resampleToImage1Display.DataAxesGrid = "GridAxesRepresentation"
                resampleToImage1Display.SelectionCellLabelFontFile = ""
                resampleToImage1Display.SelectionPointLabelFontFile = ""
                resampleToImage1Display.PolarAxes = "PolarAxesRepresentation"
                resampleToImage1Display.ScalarOpacityUnitDistance = 1.3638195335188013
                resampleToImage1Display.Slice = 63

                # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
                resampleToImage1Display.ScaleTransferFunction.Points = [
                    0.0,
                    0.0,
                    0.5,
                    0.0,
                    15.0,
                    1.0,
                    0.5,
                    0.0,
                ]

                # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
                resampleToImage1Display.OpacityTransferFunction.Points = [
                    0.0,
                    0.0,
                    0.5,
                    0.0,
                    15.0,
                    1.0,
                    0.5,
                    0.0,
                ]

                # init the 'GridAxesRepresentation' selected for 'DataAxesGrid'
                resampleToImage1Display.DataAxesGrid.XTitleColor = [0.0, 0.0, 0.0]
                resampleToImage1Display.DataAxesGrid.XTitleFontFile = ""
                resampleToImage1Display.DataAxesGrid.YTitleColor = [0.0, 0.0, 0.0]
                resampleToImage1Display.DataAxesGrid.YTitleFontFile = ""
                resampleToImage1Display.DataAxesGrid.ZTitleColor = [0.0, 0.0, 0.0]
                resampleToImage1Display.DataAxesGrid.ZTitleFontFile = ""
                resampleToImage1Display.DataAxesGrid.XLabelColor = [0.0, 0.0, 0.0]
                resampleToImage1Display.DataAxesGrid.XLabelFontFile = ""
                resampleToImage1Display.DataAxesGrid.YLabelColor = [0.0, 0.0, 0.0]
                resampleToImage1Display.DataAxesGrid.YLabelFontFile = ""
                resampleToImage1Display.DataAxesGrid.ZLabelColor = [0.0, 0.0, 0.0]
                resampleToImage1Display.DataAxesGrid.ZLabelFontFile = ""

                # init the 'PolarAxesRepresentation' selected for 'PolarAxes'
                resampleToImage1Display.PolarAxes.PolarAxisTitleColor = [0.0, 0.0, 0.0]
                resampleToImage1Display.PolarAxes.PolarAxisTitleFontFile = ""
                resampleToImage1Display.PolarAxes.PolarAxisLabelColor = [0.0, 0.0, 0.0]
                resampleToImage1Display.PolarAxes.PolarAxisLabelFontFile = ""
                resampleToImage1Display.PolarAxes.LastRadialAxisTextColor = [0.0, 0.0, 0.0]
                resampleToImage1Display.PolarAxes.LastRadialAxisTextFontFile = ""
                resampleToImage1Display.PolarAxes.SecondaryRadialAxesTextColor = [0.0, 0.0, 0.0]
                resampleToImage1Display.PolarAxes.SecondaryRadialAxesTextFontFile = ""

                # ----------------------------------------------------------------
                # finally, restore active source
                SetActiveSource(resampleToImage1)
                # ----------------------------------------------------------------

                SaveData(file_i_base_name + ".vti", resampleToImage1)
        """))

    # MEGA HACK: also write out a post-processing script here that can be invoked as a 
    # command in the main task:
    with Path('post_processing.py').open('wt') as fp:
        fp.write(dedent("""
            import re
            from pathlib import Path
            
            import hickle
            import pyvista as pv
            import numpy as np
            from skimage.measure import label, regionprops
            from cipher_parse.cipher_input import CIPHERInput

            path = Path('').resolve()
            file_list = sorted(
                [i for i in path.glob('*.vti')],
                key=lambda x: int(re.search(r"\d+", x.name).group())
            )
            data = []
            for file_i in file_list:
                mesh = pv.get_reader(file_i).read()

                grain_map = mesh.get_array('out output')[:, 0].reshape(mesh.dimensions, order='F')
                grain_label = label(grain_map)
                regions = regionprops(grain_label)
                EDAs = np.array([i.equivalent_diameter_area for i in regions])
                centroids = np.array([i.centroid for i in regions])

                mid_point = np.array(mesh.dimensions) * np.array(mesh.spacing) / 2
                central_grain_id = np.argmin(np.sum((centroids - mid_point) ** 2, axis=1))
                central_grain_size = EDAs[central_grain_id]
                num_grains = centroids.shape[0]
                non_central_grain_idx = np.ones(num_grains)
                non_central_grain_idx[central_grain_id] = 0
                non_central_grain_sizes = EDAs[non_central_grain_idx.astype(bool)]

                data.append({
                    'dimensions': mesh.dimensions,
                    'spacing': mesh.spacing,
                    'number_of_cells': mesh.number_of_cells,
                    'number_of_points': mesh.number_of_points,
                    'grain_EDAs': EDAs,
                    'grain_centroids': centroids,
                    'num_grains': num_grains,
                    'central_grain_ID': central_grain_id,
                    'central_grain_size': central_grain_size,
                    'non_central_grain_sizes': non_central_grain_sizes,
                })

            nucleus_size = [i['central_grain_size'] for i in data]
            mean_sub_grain_size = [np.mean(i['grain_EDAs']) for i in data]

            outputs = {
                'file_list': [str(i) for i in file_list],
                'data': data,
                'nucleus_size': nucleus_size,
                'mean_sub_grain_size': mean_sub_grain_size, 
            }
            hickle.dump(outputs, "post_proc_outputs.hdf5")
            
        """))
