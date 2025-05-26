import configparser

from semantic_main.semantic_logger.logger import Logger
from semantic_main.semantic_model.sha import SHA
from sha_learning.domain.lshafeatures import Trace

config = configparser.ConfigParser()
config.sections()
config.read('./resources/config/config.ini')
config.sections()

LOGGER = Logger('Uppaal Model Generator')

NTA_TPLT_PATH = config['MODEL GENERATION']['tplt.path']
NTA_TPLT_NAME = 'nta_template.xml'
MACHINE_TPLT_NAME = 'sha_template.xml'
PROGRAM_TPLT_NAME = 'program_template.xml'

INVARIANT_FUN = config['AUTOMATON']['invariant.merge']

LOCATION_TPLT = """<location id="{}" x="{}" y="{}">\n\t<name x="{}" y="{}">{}</name></location>\n"""

X_START = 0
X_MAX = 900
X_RANGE = 300
Y_START = 0
Y_RANGE = 300

evts_dict = {'s11': 0, 's12': 1, 's13': 2, 's14': 3, 's15': 4, 's16': 5, 's21': 6, 's22': 7, 's23': 8, 's24': 9,
             's25': 10, 's26': 11, 's31': 12, 's32': 13, 's33': 14, 's34': 15, 's35': 16, 's36': 17, 's41': 18,
             's42': 19, 's43': 20, 's44': 21, 's45': 22, 's46': 23, 's51': 24, 's52': 25, 's53': 26, 's54': 27,
             's55': 28, 's56': 29}

EDGE_TPLT = """\n<transition>\n\t<source ref="{}"/>\n\t<target ref="{}"/>
\t<label kind="synchronisation" x="{}" y="{}">{}</label>
</transition>"""

QUERY_TPLT = "A<> p.end"

SAVE_PATH = config['MODEL GENERATION']['save.path']


def sha_to_upp_tplt(learned_sha: SHA):
    machine_path = (NTA_TPLT_PATH + MACHINE_TPLT_NAME).format(learned_sha.name)
    with open(machine_path, 'r') as machine_tplt:
        lines = machine_tplt.readlines()
        learned_sha_tplt = ''.join(lines)

    locations_str = ''
    x = X_START
    y = Y_START

    for i, loc in enumerate(learned_sha.locations):
        new_loc_str = LOCATION_TPLT.format('id' + str(loc.id), x, y, x, y - 20, loc.name, x, y - 30)

        loc.x = x
        loc.y = y
        locations_str += new_loc_str

        if loc.initial:
            learned_sha_tplt = learned_sha_tplt.replace('**INIT_ID**', 'id' + str(loc.id))

        if x < X_MAX:
            x = x + X_RANGE
        else:
            x = X_START
            y = y + Y_RANGE

    edges_str = ''
    for edge in learned_sha.edges:
        start_id = 'id' + str(edge.start.id)
        dest_id = 'id' + str(edge.dest.id)
        x1, y1, x2, y2 = edge.start.x, edge.start.y, edge.dest.x, edge.dest.y
        mid_x = abs(x1 - x2) / 2 + min(x1, x2)
        mid_y = abs(y1 - y2) / 2 + min(y1, y2)

        sync = 's[{}]?'
        sync = sync.format(evts_dict[edge.sync.replace('!', '')])

        new_edge_str = EDGE_TPLT.format(start_id, dest_id, mid_x, mid_y + 5, sync)
        edges_str += new_edge_str

    learned_sha_tplt = learned_sha_tplt.replace('**LOCATIONS**', locations_str)
    learned_sha_tplt = learned_sha_tplt.replace('**TRANSITIONS**', edges_str)

    return learned_sha_tplt


def generate_program_tplt(val_trace: Trace):
    n_e = len(val_trace)
    trace = ','.join([str(evts_dict[e.symbol]) for e in val_trace.events])
    with open(NTA_TPLT_PATH + PROGRAM_TPLT_NAME, 'r') as program_tplt:
        program_tplt = program_tplt.readlines()

    return str(n_e), trace, '\n'.join(program_tplt)


def generate_query_file(name: str):
    query_path = SAVE_PATH + name + '.q'
    with open(query_path, 'w') as q_file:
        q_file.write(QUERY_TPLT)
    return query_path


def generate_upp_model(learned_sha: SHA, name: str, val_trace: Trace):
    LOGGER.info("Starting Uppaal semantic_model generation...")

    # Learned SHA Management

    learned_sha_tplt = sha_to_upp_tplt(learned_sha)

    nta_path = (NTA_TPLT_PATH + NTA_TPLT_NAME)
    with open(nta_path, 'r') as nta_tplt:
        lines = nta_tplt.readlines()
        nta_tplt = ''.join(lines)

    unique_syncs = list(set([e.sync.replace('!', '') for e in learned_sha.edges]))
    nta_tplt = nta_tplt.replace('**CHANNELS**', ','.join(unique_syncs))
    nta_tplt = nta_tplt.replace('**MONITORS**', ','.join(['s.' + l.name for l in learned_sha.locations]))

    nta_tplt = nta_tplt.replace('**MACHINE**', learned_sha_tplt)
    n_e, trace, program = generate_program_tplt(val_trace)
    nta_tplt = nta_tplt.replace('**N_EVENTS**', n_e)
    nta_tplt = nta_tplt.replace('**TRACE**', trace)
    nta_tplt = nta_tplt.replace('**PROGRAM**', program)

    model_path = SAVE_PATH + name + '.xml'

    with open(model_path, 'w') as new_model:
        new_model.write(nta_tplt)

    LOGGER.info('Uppaal semantic_model successfully created.')

    query_path = generate_query_file(name)

    LOGGER.info('Uppaal query file successfully created.')

    return model_path, query_path
