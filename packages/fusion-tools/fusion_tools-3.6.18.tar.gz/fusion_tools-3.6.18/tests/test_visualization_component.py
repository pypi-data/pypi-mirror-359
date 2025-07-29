"""
Testing new Visualization structure

"""

import os
import sys
sys.path.append('./src/')

from fusion_tools.visualization import Visualization
from fusion_tools.components import SlideMap, OverlayOptions, PropertyViewer, PropertyPlotter, GlobalPropertyPlotter
from fusion_tools.handler.dsa_handler import DSAHandler
from fusion_tools.utils.shapes import load_visium

def main():
 
    base_dir = 'C:\\Users\\samuelborder\\Desktop\\HIVE_Stuff\\FUSION\\Test Upload\\'
    local_slide_list = [
        base_dir+'XY01_IU-21-015F_001.svs',
        base_dir+'XY01_IU-21-015F.svs',
        base_dir+'new Visium\\V12U21-010_XY02_21-0069.tif',
        base_dir+'New Visium Format\\A1\\spatial\\tissue_hires_image.tif'
    ]

    local_annotations_list = [
        base_dir+'XY01_IU-21-015F_001.xml',
        None,
        base_dir+'new Visium\\V12U21-010_XY02_21-0069.h5ad',
        load_visium(
            base_dir+'New Visium Format\\A1\\spatial\\tissue_positions.csv',
            scale_factor=base_dir+'New Visium Format\\A1\\spatial\\scalefactors_json.json')
    ]

    dsa_handler = DSAHandler(
        girderApiUrl = 'http://ec2-3-230-122-132.compute-1.amazonaws.com:8080/api/v1'
    )

    dsa_items_list = [
        '64f545082d82d04be3e39ee1',
        '64f54be52d82d04be3e39f65'
    ]

    dsa_tileservers = [dsa_handler.get_tile_server(i) for i in dsa_items_list]
    
    vis_sess = Visualization(
        local_slides = local_slide_list,
        local_annotations = local_annotations_list,
        tileservers = dsa_tileservers,
        linkage = 'row',
        components = [
            [
                SlideMap(
                    cache = True
                ),
                [
                    OverlayOptions(ignore_list = ['_id','_index','barcode']),
                    PropertyViewer(ignore_list = ['_id','_index','barcode']),
                    PropertyPlotter(ignore_list = ['_id','_index','barcode']),
                    GlobalPropertyPlotter()
                ],            
            ]
        ],
        app_options={
            'port': 8050,
        }
    )

    vis_sess.start()



if __name__=='__main__':
    main()

