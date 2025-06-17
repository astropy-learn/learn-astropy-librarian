# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Standardized Learn Astropy keywords."""

from pathlib import Path
from typing import Dict, List, Optional, Sequence, Union

import yaml

KeywordTable = Dict[str, List[str]]
"""Keyword table data type.

The canonical keyword is the key, and alternative forms are strings in the
list.
"""


class KeywordDb:
    """A database of Astropy keywords and sorter of keyword types.

    Parameters
    ----------
    astropy_package : `KeywordTable`
        Keywords in the "Astropy package" group.
    python_package : `KeywordTable`
        Keywords in the "Python package" group.
    task : `KeywordTable`
        Keywords in the "task" group.
    science : `KeywordTable`
        Keywords in the "science" group.
    """

    def __init__(self, **kwargs: KeywordTable) -> None:
        self._keyword_groups = kwargs

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "KeywordDb":
        """Load a KeywordDB from a YAML file.

        Parameters
        ----------
        path : `pathlib.Path`, optional
            Path to the YAML-formatted keyword database file. Leave as `None`
            to use the built-in keyword database.

        Returns
        -------
        KeywordDb
            A keyword database instance.
        """
        if path is None:
            path = Path(__file__).parent / "data" / "keywords.yaml"

        db = yaml.safe_load(path.read_text())

        keyword_groups: Dict[str, KeywordTable] = {}
        for group_name in db:
            keyword_groups[group_name] = cls._load_keyword_table(db[group_name])

        return cls(**keyword_groups)

    @staticmethod
    def _load_keyword_table(
        group: Sequence[Union[str, Dict[str, Sequence[str]]]],
    ) -> KeywordTable:
        keywords: KeywordTable = {}
        for keyword_item in group:
            if isinstance(keyword_item, dict):
                keyword = list(keyword_item.keys())[0]
                alternatives = list(keyword_item[keyword])
            elif isinstance(keyword_item, str):
                keyword = keyword_item
                alternatives = list()
            keywords[keyword] = alternatives
        return keywords

    def filter_keywords(
        self, input_keywords: List[str], keyword_group: str
    ) -> List[str]:
        """Filter keywords for a specific group.

        Parameters
        ----------
        input_keywords : list of str
            Input keywords are keywords accessed from a source document.
        keyword_group : str
            Name of the keyword group. This is a root-level key in
            astropylibrarian's ``keywords.yaml``

        Returns
        -------
        list of str
            Keywords that correspond to the keyword group. These keywords
            are normalized to match the vocabulary in ``keywords.yaml`` (some
            input keywords may be replaced with synonyms).
        """
        try:
            table = self._keyword_groups[keyword_group]
        except KeyError:
            raise ValueError(
                f"Keyword group {keyword_group} is unknown. Available groups "
                f"are: {self._keyword_groups.keys()}."
            )

        # Normalize the input keywords
        input_keywords = [k.lower().strip() for k in input_keywords]

        output_keywords: List[str] = []

        for input_keyword in input_keywords:
            if input_keyword in table.keys():
                # Keyword is in group and already the canonical form
                output_keywords.append(input_keyword)
            else:
                # See if the keyword is an alternative form
                for keyword, alternates in table.items():
                    if input_keyword in alternates:
                        output_keywords.append(keyword)

        return output_keywords
