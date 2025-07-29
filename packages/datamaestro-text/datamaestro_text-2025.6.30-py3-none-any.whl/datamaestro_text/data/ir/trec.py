from typing import Dict, List, Optional
from datamaestro.data import Base
from experimaestro import documentation, Param, Meta
from pathlib import Path
from datamaestro.record import Record
from datamaestro_text.data.ir import (
    Documents,
    Topics,
    AdhocAssessments,
    AdhocRun,
    AdhocResults,
    Measure,
)
from datamaestro_text.data.ir.formats import TrecTopicRecord


class TrecTopics(Topics):
    path: Meta[Path]
    parts: Meta[List[str]]

    @documentation
    def iter(self):
        """Iterate over TREC adhoc topics"""
        import datamaestro_text.interfaces.trec as trec

        yield from trec.parse_query_format(self.path)

    @property
    def topic_recordtype(self):
        return TrecTopicRecord


class TrecAdhocAssessments(AdhocAssessments):
    path: Meta[Path]

    def trecpath(self):
        return self.path

    @documentation
    def iter(self):
        """Iterate over TREC adhoc topics"""
        import datamaestro_text.interfaces.trec as trec

        yield from trec.parse_qrels(self.path)


class TrecAdhocRun(AdhocRun):
    path: Param[Path]


class TrecAdhocResults(AdhocResults):
    """Adhoc results (TREC format)"""

    metrics: Param[List[Measure]]
    """List of reported metrics"""

    results: Param[Path]
    """Main results"""

    detailed: Param[Optional[Path]]
    """Results per topic (if any)"""

    def get_results(self) -> Dict[str, float]:
        """Returns the results as a dictionary {metric_name: value}"""
        import re

        re_spaces = re.compile(r"\s+")

        results = {}
        with self.results.open("rt") as fp:
            for line in fp.readlines():
                metric, _, value = re_spaces.split(line.strip())
                results[metric] = value

        return results


class TipsterCollection(Documents):
    path: Param[Path]

    def iter(self):
        raise NotImplementedError()
