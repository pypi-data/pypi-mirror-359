# burdenr/cli.py

import click
import os
import time
import pandas as pd
import logging
import multiprocessing as mp
from burdenr.tools.handle_data import chunk_handle
from burdenr.tools.callrisk import *
import gzip
import tempfile
import click

@click.command()
@click.option(
    '-f', '--infile',
    required=True,
    type=click.Path(exists=True),
    help='Input file path. Supports VCF (.vcf, .vcf.gz) or genotype frequency file (gt_freq_info.tsv, gt_freq_info.tsv.gz).'
)
@click.option(
    '-w', '--work-dir',
    default='./workdir',
    show_default=True,
    type=click.Path(file_okay=False),
    help='Working directory where output files will be saved. Default: ./workdir'
)
@click.option(
    '-A', 'popA',
    required=True,
    help='Name of population A (target population).'
)
@click.option(
    '-B', 'popB',
    required=True,
    help='Name of population B (target population).'
)
@click.option(
    '-C', 'popC',
    required=False,
    help='Name of population C (outgroup population), optional.'
)
@click.option(
    '-G', '--group-info',
    required=True,
    type=click.Path(exists=True),
    help='Path to the sample group file (tab-separated, columns: Group\\tSample).'
)
@click.option(
    '--freq',
    type=float,
    default=None,
    help='Allele frequency threshold for filtering variants. Variants with frequencies above this value in either population will be excluded. Default is no frequency filtering.'
)
@click.option(
    '--fix-sites',
    type=int,
    default=None,
    help='Number of fixed sites to use in jackknife resampling. Defaults to one-fifth of total sites if not specified.'
)
@click.option(
    '--boostrap_n',
    type=int,
    default=100,
    show_default=True,
    help='Number of boostrap to calcualte the risk'
)
@click.option(
    '--n-cores',
    type=int,
    default=4,
    show_default=True,
    help='Number of CPU cores to use for multiprocessing.'
)
@click.option(
    '--log',
    'log_level',
    default='INFO',
    type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']),
    show_default=True,
    help='Logging verbosity level.'
)


def main(infile, work_dir, popA, popB, popC, group_info, freq, fix_sites, boostrap_n, n_cores, log_level):
    """
    Calculate relative mutation burden (AB method) between populations.

    This tool accepts either a VCF file or a genotype frequency file as input,
    along with sample grouping information and population names. It outputs
    mutation burden risk analyses and plots in the specified working directory.
    """
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='[%(asctime)s] %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    start = time.time()
    os.makedirs(work_dir, exist_ok=True)

    logging.info("Reading sample grouping file...")
    sample_info_df = pd.read_csv(group_info, sep='\s+')
    sample_info = {}
    for group, df in sample_info_df.groupby('Group'):
        sample_info[group] = df['Sample'].tolist()
        
    logging.info(f"Starting calcualte burden relative risk for {popA}({len(sample_info[popA])}samples) vs {popB}({len(sample_info[popB])}samples)")  

    if infile.endswith(('vcf.gz', 'vcf')):
        logging.info(f"Input file is in VCF format, starting conversion to gt_freq...")
        freq_file = os.path.join(work_dir, f'gt_freq_info.{popA}_vs_{popB}.tsv')
        vcf2gtfreq(infile, n_cores, sample_info, freq_file)
    elif infile.endswith((f'gt_freq_info.{popA}_vs_{popB}.tsv', f'gt_freq_info.{popA}_vs_{popB}.tsv.gz')):
        logging.info("Input file is frequency table, reading directly...")
        freq_file = infile
    else:
        logging.error("Invalid input file format. Expected .vcf(.gz) or gt_freq_info.A_vs_B.tsv(.gz).")
        return

    logging.info(f"Reading genotype frequency data ... ")
    
    df_info = read_gtfreq(freq_file, sample_info, popC)

    logging.info("Starting mutation burden risk calculation...")
    call_risk(df_info, work_dir, popA, popB, freq=freq, fix_sites=fix_sites, boostrap_n=boostrap_n)

    end = time.time()
    logging.info(f"Analysis completed, total time: {end - start:.2f} seconds.")

def read_vcf_header(vcf_gz_path, max_header_lines=10000):
    header_lines = []
    with gzip.open(vcf_gz_path, 'rt') as f:
        for _ in range(max_header_lines):
            line = f.readline()
            if not line:
                break  # 文件结束
            if line.startswith('#'):
                header_lines.append(line)
            else:
                break  # 一旦遇到非头部行就停止
    return header_lines

def vcf2gtfreq(vcf, n_cores, sample_info, freq_file):
    header_lines = read_vcf_header(vcf)
    vcf_dtypes = {
        '#CHROM': 'category', 'POS': 'int32', 'REF': 'category',
        'ALT': 'category', 'FORMAT': 'category', 'FILTER': 'category'
    }

    reader = pd.read_csv(
        vcf, sep='\t', compression='gzip',
        skiprows=(len(header_lines) - 1),
        iterator=True, dtype=vcf_dtypes
    )

    chunk_size = 10000
    is_apd = False
    pool = mp.Pool(n_cores)

    while True:
        try:
            chunk = reader.get_chunk(chunk_size)
            pool.apply_async(chunk_handle, args=(chunk, sample_info, is_apd, freq_file))
            is_apd = True
        except StopIteration:
            break
        except Exception as e:
            logging.error(f"Error occurred while reading VCF chunk: {e}")
            break

    logging.info("Waiting for all subprocesses to finish...")
    pool.close()
    pool.join()
    pool.terminate()
    logging.info("All subprocesses finished.")


def clean_read_csv(
    filepath,
    sep='\t',
    usecols=None,
    dtype=None,
    iterator=False,
    chunksize=None,
    verbose=True
):
    """
    Read a delimited text file after removing rows with wrong column count.

    Parameters
    ----------
    filepath : str
        Path to the original file.
    sep : str, default '\t'
        Field delimiter.
    usecols : list of str or None
        Columns to read.
    dtype : dict or None
        Dtype dict to use for pandas read_csv.
    iterator : bool, default False
        Whether to return an iterator.
    chunksize : int or None
        Chunk size if using iterator.
    verbose : bool
        Whether to print info about removed lines.

    Returns
    -------
    DataFrame or TextFileReader
        The cleaned dataframe or iterator.
    """

    # Step 1 — read header to know expected columns
    with open(filepath) as f:
        header_line = f.readline()
        header_cols = header_line.strip().split(sep)
        expected_cols = len(header_cols)

    # Step 2 — filter only lines with correct column count
    temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
    temp_file.write(header_line)

    bad_lines = 0
    total_lines = 0

    with open(filepath) as f:
        # skip header
        f.readline()
        for line in f:
            total_lines += 1
            if len(line.strip().split(sep)) == expected_cols:
                temp_file.write(line)
            else:
                bad_lines += 1

    temp_file.close()

    if verbose:
        if bad_lines > 0:
            print(
                f"⚠️ Removed {bad_lines} bad lines "
                f"out of {total_lines} total rows ({bad_lines/total_lines:.3%})"
            )
        else:
            print("✅ No bad lines found.")

    # Step 3 — load cleaned file with pandas
    df_or_iter = pd.read_csv(
        temp_file.name,
        sep=sep,
        usecols=usecols,
        dtype=dtype,
        iterator=iterator,
        chunksize=chunksize,
        low_memory=False
    )

    # Clean up temp file
    os.unlink(temp_file.name)
    return df_or_iter


def read_gtfreq(gt_freq_info, sample_info, outgrp):
    # step 1: 读取所有列名
    with open(gt_freq_info) as f:
        header = f.readline().strip().split('\t')

    # step 2: 设置已知的类型
    freq_dtypes = {
        '#CHROM': 'category', 'functional': 'category',
        'func_cate': 'category', 'gene': 'category'
    }
    target_cols = ['#CHROM', 'POS', 'gene', 'functional', 'func_cate', 'hgv.p']

    for group in sample_info:
        freq_dtypes[f'{group}.hom_alt.freq'] = 'float32'
        freq_dtypes[f'{group}.het_alt.freq'] = 'float32'
        target_cols.extend([f'{group}.hom_alt.freq', f'{group}.het_alt.freq'])

    # step 3: 补上其他列类型为 str
    for col in header:
        if col not in target_cols:
            target_cols.append(col)
            freq_dtypes[col] = str

    reader = clean_read_csv(
        gt_freq_info,
        sep='\t',
        usecols=target_cols,
        dtype=freq_dtypes,
        iterator=True,
        chunksize=10000
    )
    chunks = []
    while True:
        try:
            chunk = reader.get_chunk(10000)
            if outgrp:
                chunks.append(derived_allele(chunk, outgrp))
            else:
                chunks.append(chunk)
        except StopIteration:
            break

    df = pd.concat(chunks, ignore_index=True)
    df['functional'] = df['functional'].str.split('&').str[0]
    return df


def call_risk(df_info, workdir, popA, popB, boostrap_n=None, freq=None, fix_sites=None, norm_item='intergenic_region'):
    df_info = add_Gscores(df_info)
    df_info = pop_hom_het_freq(df_info, popA, popB)

    if freq:
        df_info = df_info[
            (df_info[f'{popA}.hom_alt.freq'] + df_info[f'{popA}.het_alt.freq'] < freq) &
            (df_info[f'{popB}.hom_alt.freq'] + df_info[f'{popB}.het_alt.freq'] < freq)
        ]

    funcfi1 = CallfunctionalFi(df_info, fix_sites=fix_sites, boostrap_n=boostrap_n)
    df_risk = CallBurdenRisk(funcfi1.AB, funcfi1.BA, norm_item=norm_item).df_risk

    risk_dir = os.path.join(workdir, 'riskAB')
    os.makedirs(risk_dir, exist_ok=True)

    risk_file = os.path.join(risk_dir, f'results_freq_{freq}.{popA}_vs_{popB}.tsv' if freq else f'results.{popA}_vs_{popB}.tsv')
    df_risk.to_csv(risk_file, sep='\t', index=False)

    import matplotlib.pyplot as plt
    plot_burden_risk(df_risk,popA, popB)
    pdf_file = os.path.join(risk_dir, f'Burden_risk_freq_{freq}.{popA}_vs_{popB}.pdf' if freq else f'Burden_risk.{popA}_vs_{popB}.pdf')
    png_file = os.path.join(risk_dir, f'Burden_risk_freq_{freq}.{popA}_vs_{popB}.png' if freq else f'Burden_risk.{popA}_vs_{popB}.png')
    plt.savefig(pdf_file, bbox_inches='tight')
    plt.savefig(png_file, bbox_inches='tight',dpi=300)


    df_info.to_csv(os.path.join(workdir, f'derived_info.{popA}_vs_{popB}.tsv'), sep='\t', index=False)

if __name__ == '__main__':
    main()
