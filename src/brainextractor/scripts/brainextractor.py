#!/usr/bin/env python3

import os
from pathlib import Path
import argparse
import SimpleITK as sitk
from brainextractor.main import BrainExtractor


def main():
    # create command line parser
    parser = argparse.ArgumentParser(
        description="A Reimplementation of FSL's Brain Extraction Tool",
        epilog="Author: Andrew Van, vanandrew@wustl.edu, 12/15/2020",
    )
    parser.add_argument("input_img", help="Input image to brain extract")
    parser.add_argument("output_img", help="Output image to write out")
    parser.add_argument("-w", "--write_surface_deform", help="Path to write out surface files at each deformation step", type=Path, default=None, required=False)
    parser.add_argument(
        "-f",
        "--fractional_threshold",
        type=float,
        default=0.5,
        help="Main threshold parameter for controlling brain/background (Default: 0.5)",
    )
    parser.add_argument(
        "-n", "--iterations", type=int, default=1000, help="Number of iterations to run (Default: 1000)"
    )
    parser.add_argument(
        "-t",
        "--histogram_threshold",
        nargs=2,
        type=float,
        default=[0.02, 0.98],
        help="Sets min/max of histogram (Default: 0.02, 0.98)",
    )
    parser.add_argument(
        "-d",
        "--search_distance",
        nargs=2,
        type=float,
        default=[20.0, 10.0],
        help="Sets search distance for max/min of image along vertex normals (Default: 20.0, 10.0)",
    )
    parser.add_argument(
        "-r",
        "--radius_of_curvatures",
        nargs=2,
        type=float,
        default=[3.33, 10.0],
        help="Sets min/max radius of curvature for surface (Default: 3.33, 10.0)",
    )

    # parse arguments
    args = parser.parse_args()

    # load input image
    input_img = os.path.abspath(args.input_img)
    img = sitk.ReadImage(input_img)

    # create brain extractor
    bet = BrainExtractor(
        img=img,
        t02t=args.histogram_threshold[0],
        t98t=args.histogram_threshold[1],
        bt=args.fractional_threshold,
        d1=args.search_distance[0],
        d2=args.search_distance[1],
        rmin=args.radius_of_curvatures[0],
        rmax=args.radius_of_curvatures[1],
    )

    # create output path for surface files if defined
    deformation_path = args.write_surface_deform
    if deformation_path:
        if not deformation_path.parent.exists():
            deformation_path.mkdir(parents=True, exist_ok=True)

    # run brain extractor
    bet.run(iterations=args.iterations, deformation_path=deformation_path if args.write_surface_deform else None)

    # make dirs to output directory as needed
    output_img = os.path.abspath(args.output_img)
    os.makedirs(os.path.dirname(output_img), exist_ok=True)

    # write mask to file
    print("Saving mask...")
    bet.save_mask(output_img)
    print("Mask saved.")
