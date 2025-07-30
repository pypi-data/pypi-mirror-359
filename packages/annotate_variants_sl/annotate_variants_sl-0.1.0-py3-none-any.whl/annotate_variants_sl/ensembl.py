import requests
import re

ENSEMBL_ID_REGEX = r"NC_[0-9]{6}\.[0-9]{2}\:g\.[0-9]+[AGTC]>[AGTC]$"


class BaseQuerier():
    def __init__(self):
        self.headers = {
            "Content-type": "application/json"
        }

    def _parse_data(self, data):
        pass

    def get_query(self, query_url):
        resp = requests.get(query_url, headers=self.headers)
        data = resp.json()
        if not resp.ok:
            raise QueryError(data.get("error"))
        return self._parse_data(data[0])


class EnsemblQuerier(BaseQuerier):
    def __init__(self, base_url="http://rest.ensembl.org/vep/human/hgvs/{}"):
        super().__init__()
        self.base_url = base_url
        self.regex = ENSEMBL_ID_REGEX
        self.direct_colummns = [
            "assembly_name",
            "seq_region_name",
            "start",
            "end",
            "most_severe_consequence",
            "strand"
        ]

    def _get_genes(self, tcs):
        """get gene symbol and confirm they conform across transcript consequences (tcs)."""
        gene_symbols = set([tc.get("gene_symbol") for tc in tcs])
        if len(gene_symbols) != 1:
            raise QueryError(f"Found multiple gene symbols associated with query: {gene_symbols}")
        return next(iter(gene_symbols))

    def _parse_data(self, data):
        parsed_data = {}
        for col in self.direct_colummns:
            if col not in data:
                raise QueryError(f"Expected columns {col} in return data.")
            parsed_data[col] = data[col]
        parsed_data["genes"] = self._get_genes(data["transcript_consequences"])
        return parsed_data

    def query(self, identifier):
        self._validate_input(identifier)
        return {
            "input_variant": identifier,
            **self.get_query(self.base_url.format(identifier))
        }

    def _validate_input(self, identifier):
        if not re.match(self.regex, identifier):
            raise QueryError(f"identifier {identifier} does not conform to Ensembl id expectation.")

class QueryError(Exception):
    pass