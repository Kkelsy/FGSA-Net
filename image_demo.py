# Copyright (c) OpenMMLab. All rights reserved.
from argparse import ArgumentParser

import mmcv

import mmcv_custom   # noqa: F401,F403
import mmseg_custom   # noqa: F401,F403
from mmseg.apis import inference_segmentor, init_segmentor, show_result_pyplot
from mmseg.core.evaluation import get_palette
from mmcv.runner import load_checkpoint
from mmseg.core import get_classes
import cv2
import os.path as osp
import os

def main():
    parser = ArgumentParser()
    parser.add_argument('config', help='Config file')
    parser.add_argument('checkpoint', help='Checkpoint file')
    parser.add_argument('img', help='Image file')
    parser.add_argument('--out', type=str, default="result_imgs", help='out dir')
    parser.add_argument(
        '--device', default='cuda:0', help='Device used for inference')
    parser.add_argument(
        '--palette',
        default='cityscapes',
        help='Color palette used for segmentation map')
    parser.add_argument(
        '--opacity',
        type=float,
        default=0.5,
        help='Opacity of painted segmentation map. In (0, 1] range.')
    args = parser.parse_args()

    # build the model from a config file and a checkpoint file
    
    model = init_segmentor(args.config, checkpoint=None, device=args.device)
    checkpoint = load_checkpoint(model, args.checkpoint, map_location='cpu')[0]
    if 'CLASSES' in checkpoint.get('meta', {}):
        model.CLASSES = checkpoint['meta']['CLASSES']
    else:
        model.CLASSES = get_classes(args.palette)

    img_dir = os.listdir(args.img)   
    for filename in img_dir:
        img_path = args.img + '/' + filename 
        # test a single image
        result = inference_segmentor(model, img_path)
        # show the results
        if hasattr(model, 'module'):
            model = model.module

        img = model.show_result(img_path, result,
                                palette=get_palette(args.palette),
                                show=False, opacity=args.opacity)
        mmcv.mkdir_or_exist(args.out)
        out_path = osp.join(args.out, osp.basename(img_path))
        cv2.imwrite(out_path, img)
    print(f"Result is save at {out_path}")

if __name__ == '__main__':
    main()