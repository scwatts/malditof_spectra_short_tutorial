#!/usr/bin/env python3
import argparse
import collections
import csv
import json
import pathlib
import shutil
import sys


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample_sheet_fp', required=True, type=pathlib.Path,
            help='Input sample sheet filepath')
    parser.add_argument('--spectra_dir', required=True, type=pathlib.Path,
            help='Input spectra directory')
    parser.add_argument('--output_dir', required=True, type=pathlib.Path,
            help='Output spectra directory')
    args = parser.parse_args()
    if not args.sample_sheet_fp.exists():
        parser.error(f'Input file {args.sample_sheet_fp} does not exist')
    if not args.spectra_dir.exists():
        parser.error(f'Input file {args.spectra_dir} does not exist')
    if not args.output_dir.exists():
        parser.error(f'Output directory {args.output_dir} does not exist')
    return args


def main():
    # Get command line arguments
    args = get_arguments()

    # Read in sample sheet
    print(f'info: reading sample data', file=sys.stderr)
    with args.sample_sheet_fp.open('r') as fh:
        reader = csv.reader(fh, delimiter='\t')
        header_tokens = next(reader)
        SampleRecord = collections.namedtuple('SampleRecord', header_tokens)
        sample_info = [SampleRecord(*line_tokens) for line_tokens in reader]

    # Read in maldi-tof run data and sample data
    print(f'info: reading malditof data', file=sys.stderr)
    malditof_data = dict()
    run_info_fps = args.spectra_dir.glob('*/runInfo.json')
    for run_info_fp in run_info_fps:
        with run_info_fp.open('r') as fh:
            # Read in data
            data = json.load(fh)
            project_uid = data['ProjectUid']
            # Iterate each sample/analyte
            for analyte_data in data['Analytes']:
                if analyte_data['Context'] != 'id':
                    continue
                analyte_data['ProjectUid'] = project_uid
                malditof_data[analyte_data['AnalyteId']] = analyte_data

    # Get and copy spectra
    output_spectra_dir = args.output_dir / 'spectra'
    output_spectra_dir.mkdir(mode=0o755, exist_ok=True)
    print('info: copying spectra to output directory', file=sys.stderr)
    for i, sample_record in enumerate(sample_info, 1):
        print(f'info: spectrum {i} of {len(sample_info)} copied', end='\r', file=sys.stderr)
        malditof_record = malditof_data[sample_record.sample_id]
        # Copy data
        spectra_path = malditof_record['ProjectUid'] + '/' + malditof_record['SubPath'].replace('\\', '/')
        fp_src = args.spectra_dir / spectra_path
        fp_dst = output_spectra_dir / spectra_path
        if not fp_dst.exists():
            fp_dst.mkdir(mode=0o755, parents=True)
        shutil.copytree(fp_src, fp_dst, dirs_exist_ok=True)
    print(f'info: spectrum {i} of {len(sample_info)} copied', file=sys.stderr)

    # Write out sample data
    print(f'info: writing sample data', file=sys.stderr)
    fields = [
        'sample_id',
        'wgs_species',
        'spectrum_uid',
        'filepath',
    ]
    out_data = list()
    out_record = dict.fromkeys(fields, '-')
    for sample_record in sample_info:
        record = out_record.copy()
        malditof_record = malditof_data[sample_record.sample_id]
        record['sample_id'] = sample_record.sample_id
        record['wgs_species'] = sample_record.wgs_species
        # Field: spectrum_uid
        record['spectrum_uid'] = malditof_record['SpectrumUid']
        # Field: filepath
        subpath = malditof_record['SubPath'].replace('\\', '/')
        parent_dir = malditof_record['ProjectUid']
        record['filepath'] = f'{parent_dir}/{subpath}'
        out_data.append(record)
    out_sample_info_fp = args.output_dir / 'sample_data.tsv'
    with out_sample_info_fp.open('w') as fh:
        print(*fields, sep='\t', file=fh)
        for data in out_data:
            print(*data.values(), sep='\t', file=fh)


if __name__ == '__main__':
    main()
