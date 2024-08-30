import difflib
import os
import json


def is_test_file(file_path):
    if not file_path.endswith(('.py', '.java', '.c', '.cpp')):  # '.c'
        return False
    file_name = os.path.basename(file_path)
    if file_name.startswith('test_') or file_name.endswith('_test.'):
        return True
    if file_name.endswith('Test.java') or '.test.' in file_path:
        return True
    if file_name.startswith('Test') and not file_name[4].islower():
        return True
    return False


def find_production(test_file, non_test_files):
    test_basename = os.path.basename(test_file)
    prefix_or_suffix = ['Test', 'test_', '_test']
    production_basenames = set()
    for s in prefix_or_suffix:
        production_basenames.add(test_basename.replace(s, ''))
    production_candidates = set()
    for f in non_test_files:
        if os.path.basename(f) in production_basenames:
            production_candidates.add(f)
    match_results = difflib.get_close_matches(test_file, production_candidates, n=1, cutoff=0.0)
    closest_match = match_results[0] if match_results else None
    # if closest_match:
    #     print('---------------')
    #     print(test_file)
    #     print(production_basenames)
    #     print(production_candidates)
    #     print(closest_match)
    return closest_match


history_dir = '/Users/abigiris/Downloads/TestTD/Empirical/history/'
pair_dir = '/Users/abigiris/Downloads/TestTD/Empirical/pair/'
proj_list = ['avro.json', 'curator.json', 'gobblin.json', 'groovy.json', 'hudi.json']
# proj_list = os.listdir(history_dir)
for proj in proj_list:
    history_path = history_dir + proj
    print(history_path, os.path.exists(history_path))
    with open(history_path) as f:
        history = json.load(f)

    test_files = set()
    non_test_files = set()
    for release in history:
        for commit in history[release]:
            files = history[release][commit]['diff'].keys()
            for f in files:
                if is_test_file(f):
                    test_files.add(f)
                else:
                    non_test_files.add(f)

    production_files = set()
    tp_pairs = {}
    for t in test_files:
        production_file = find_production(t, non_test_files)
        tp_pairs[t] = production_file
        if production_file:
            production_files.add(production_file)

    pair_path = pair_dir + proj
    with open(pair_path, 'w') as f:
        json.dump(tp_pairs, f, indent=4)

    change_history = {'pt': 0, 'p': 0, 't': 0}
    for release in history:
        for commit in history[release]:
            files = history[release][commit]['diff'].keys()
            for t in test_files:
                p = tp_pairs[t]
                if not p:
                    continue
                if p in files and t in files:
                    change_history['pt'] += 1
                elif p in files:
                    change_history['p'] += 1
                elif t in files:
                    change_history['t'] += 1

    print(change_history)

