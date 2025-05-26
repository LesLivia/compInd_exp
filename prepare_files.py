import itertools
import os

N_comp = [10, 50, 200, 1000]
repl = list(range(10))

LEARNED_SHA_PATH = 'resources/learned_sha/lego_plant/{}-completion/Experiment {}/'
DEST_PATH = 'resources/learned_sha/lego_plant/'

for n_c, r in itertools.product(N_comp, repl):
    files = os.listdir(LEARNED_SHA_PATH.format(n_c, r))
    files = [f for f in files if 'item' in f]
    for f in files:
        os.system('cp \"{}\" \"{}\"'.format(os.getcwd() + '/' + LEARNED_SHA_PATH.format(n_c, r) + f,
                                            os.getcwd() + '/' + DEST_PATH))
        if n_c != 200:
            os.system('mv \"{}\" \"{}\"'.format(os.getcwd() + '/' + DEST_PATH + f,
                                                os.getcwd() + '/' + DEST_PATH + f.replace('item', str(n_c))))
        else:
            os.system('mv \"{}\" \"{}\"'.format(os.getcwd() + '/' + DEST_PATH + f,
                                                os.getcwd() + '/' + DEST_PATH + f.replace('item-{}'.format(r + 10),
                                                                                          '{}-{}'.format(n_c, r))))
