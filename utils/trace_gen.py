import sys

import skg_main.skg_mgrs.connector_mgr as conn
from sha_learning.case_studies.auto_twin.sul_definition import getSUL
from sha_learning.domain.lshafeatures import Trace, Event
from skg_main.skg_mgrs.skg_reader import Skg_Reader
from skg_main.skg_model.schema import Timestamp as skg_Timestamp
from skg_main.skg_model.semantics import EntityForest


def parse_date(s: str):
    fields = s.split('-')
    return skg_Timestamp(int(fields[0]), int(fields[1]), int(fields[2]), int(fields[3]), int(fields[4]),
                         int(fields[5]))


def get_traces():
    SUL, events_labels_dict = getSUL()
    pov = 'item'
    START_T = '2025-01-22-17-04-00'
    END_T = '2025-01-22-18-30-00'

    START_T = parse_date(START_T)
    END_T = parse_date(END_T)

    # N = number of entities whose completions that occurred between START_T and END_T
    # will constitute the validation traces
    N = int(sys.argv[1])
    evt_seqs = []

    driver = conn.get_driver()
    querier: Skg_Reader = Skg_Reader(driver)
    labels_hierarchy = querier.get_entity_labels_hierarchy()

    entities = querier.get_items(labels_hierarchy=labels_hierarchy, limit=N, random=False,
                                 start_t=START_T, end_t=END_T)

    for entity in entities[:N]:
        entity_tree = querier.get_entity_tree(entity.entity_id, EntityForest([]), reverse=True)
        events = querier.get_events_by_entity_tree_and_timestamp(entity_tree[0], START_T, END_T, pov)
        split_events = []
        # necessary to split into individual runs
        loop_start_indexes = [i for i, e in enumerate(events) if ' LOAD_1' in e.activity]
        if len(loop_start_indexes) > 0:
            for i, ix in enumerate(loop_start_indexes):
                if i == 0 and ix > 0:
                    split_events.append(events[:ix + 1])
                if i == len(loop_start_indexes) - 1:
                    split_events.append(events[ix:])
                else:
                    split_events.append(events[ix:loop_start_indexes[i + 1] + 1])
        else:
            split_events.append(events)

        if len(events) > 0:
            evt_seqs.extend(split_events)

    conn.close_connection(driver)

    for t in evt_seqs:
        SUL.process_data(t)

    return [t for t in SUL.traces if t.startswith(Trace([Event('', '', 's11')]))]
