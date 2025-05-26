import itertools
import json

from semantic_main.semantic_mgrs.dot2sha import parse_sha
from semantic_main.semantic_mgrs.semantic_links_identifier import Identifier
from skg_main.skg_model.automata import Automaton
from tqdm import tqdm

from utils.sha2upp import generate_upp_model
from utils.trace_gen import get_traces
from utils.verify import verify_compatibility


def all_pairs(n):
    return n * (n - 1) / 2


CS = 'lego_plant'
NAME = 'AUTO_TWIN_SKG_{}-{}_source.txt'
LEARNED_SHA_PATH = 'resources/learned_sha/{}/AUTO_TWIN_SKG_{}-{}_source.txt'
N_comp = [10, 50, 200, 1000]
repl = list(range(10))

domain_knowledge = {'lego_plant': (5 * 6, 5 * 10)}

MAPPINGS_PATH = './resources/config/{}_mappings.json'

print('{}: {} locs, {} edges'.format(CS, domain_knowledge[CS][0], domain_knowledge[CS][1]))

for n_c, r in itertools.product(N_comp, repl):
    LINKS_PATH = MAPPINGS_PATH.format(CS)
    LINKS_CONFIG = json.load(open(LINKS_PATH))

    AUTOMATON_PATH = LEARNED_SHA_PATH.format(CS, n_c, r)
    AUTOMATON_NAME = NAME.format(n_c, r)

    # VALIDATION BASED ON DOMAIN KNOWLEDGE
    AUTOMATON = Automaton(AUTOMATON_NAME, AUTOMATON_PATH)
    links_identifier = Identifier(AUTOMATON)
    links = links_identifier.identify_semantic_links(CS + '/' + AUTOMATON_NAME.replace('_source.txt', ''), '.')
    loc_links = [l for l in links if l.aut_feat[0].loc is not None]
    edge_links = [l for l in links if l.aut_feat[0].edge is not None]
    N_loc = len(loc_links) / domain_knowledge[CS][0]
    N_ed = len(edge_links) / domain_knowledge[CS][1]
    print('{}: {:.2f} locs, {:.2f} edges'.format(n_c, N_loc, N_ed))

    # VALIDATION BASED ON EXTRA TRACES
    # (traces not seen during learning)
    validation_traces = get_traces()

    sha = parse_sha(AUTOMATON_PATH, AUTOMATON_NAME)
    # Generated Uppaal model with:
    # DiscoveredSystem = learned automaton
    # Program = support automaton that fires events in the validation trace
    # Query file: A<> p.end -> property is satisfied only if the trace is compatible with the learned automaton
    compatible_traces = 0
    for trace in tqdm(validation_traces):
        model_path, query_path = generate_upp_model(sha, AUTOMATON_NAME, trace)
        success = verify_compatibility(AUTOMATON_NAME, model_path, query_path)
        if success:
            compatible_traces += 1
    print('{}/{} compatible traces'.format(compatible_traces, len(validation_traces)))
    with open('{}_res.txt'.format(CS), 'a') as f:
        f.write('{}\t{:.2f}\n'.format(AUTOMATON_NAME, compatible_traces / len(validation_traces)))
