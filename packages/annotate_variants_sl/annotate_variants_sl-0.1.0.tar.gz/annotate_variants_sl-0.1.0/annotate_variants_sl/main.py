import argparse
import pandas as pd

from annotate_variants_sl.ensembl import EnsemblQuerier, QueryError


def main(args):
    eq = EnsemblQuerier()
    all_data = []
    error_log = []
    with open(args.input_file) as f:
        for line in f:
            id_ = line.strip()
            try:
                ret = eq.query(id_)
                all_data.append(ret)
            except QueryError as e:
                error_log.append({"input_variant": id_, "error": e})
    df = pd.DataFrame.from_dict(all_data)
    df.to_csv(args.output_file, index=False, sep="\t")
    if error_log:
        err_df = pd.DataFrame.from_dict(error_log)
        err_df.to_csv(args.error_log, index=False, sep="\t")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, help='required input file path')
    parser.add_argument('--output_file', type=str, default="output.tsv", help='optional output file name')
    parser.add_argument('--error_log', type=str, default="error.tsv", help='optional error log file name')
    return parser.parse_args()


def run_cli():
    main(parse_args())

if __name__ == "__main__":
    main(parse_args())
