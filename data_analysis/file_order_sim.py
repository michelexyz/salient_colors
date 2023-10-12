import numpy as np
import re
import argparse

named_pattern = re.compile(r'^id(?P<scene_id>\d+)_v(?P<version>\d+)_r(?P<red_count>\d+)_b(?P<blue_count>\d+)\..+$')

def generate_file_list(n_scenes, seed, file_extension='jpg'):
    """
    Generates a file list with specified total length and random seed, ensuring at least 
    5 elements between repeating IDs.
    
    Parameters:
    - n_scenes (int): Total length of the list of file names to generate will have length n_scenes * 2
    - seed (int): Seed for random number generation.
    
    Returns:
    - list: A list of file names in the format 'idN_rX_bY.png'.
    """
    
    rng = np.random.default_rng(seed)
    x_values = [5, 6] * (n_scenes // 2)  
    rng.shuffle(x_values)  
    
    file_names = []
    for n, x in enumerate(x_values):
        y = 6 if x == 5 else 5
        file_name = f"id{n}_v1_r{x}_b{y}.{file_extension}"
        file_names.append(file_name)
    
    files = file_names.copy()
    rng.shuffle(files)


    def _opposite_sides(files):
        # return a new list where each element is a modified element from file such that id01_r6_b5.png turns into id01_r5_b6.png
        new_files = []
        for fn in files:
            pi = {k: int(v) if k != 'scene_id' else v for k, v in re.match(named_pattern, fn).groupdict().items()}
            new_file = f"id{pi['scene_id']}_v2_r{pi['blue_count']}_b{pi['red_count']}.{file_extension}"
            new_files.append(new_file)
        return new_files

    l = _opposite_sides(files)

    MIN_SPACING = min(n_scenes // 2, 5)
    while l:
        sampled_file = rng.choice(l)
        last_ids = [re.match(named_pattern, f).groupdict()['scene_id'] for f in files[-MIN_SPACING:]]
        sampled_id = re.match(named_pattern, sampled_file).groupdict()['scene_id']
        
        if sampled_id not in last_ids:
            files.append(sampled_file)
            l.remove(sampled_file)
    
    return files


def test_file_order(file_list):
    """
    Tests if a list of file names have at least 5 elements between repeating IDs.
    
    Parameters:
    - file_list (list): List of file names in the format 'idNN_rX_bY.png'.
    
    Returns:
    - bool: True if the condition is met, False otherwise.

    Example:
    >>> test_file_order(['id00_r5_b6.png', 'id01_r5_b6.png', 'id00_r6_b5.png', 'id02_r5_b6.png', 'id03_r6_b5.png', 'id00_r5_b6.png'])
    True
    >>> test_file_order(['id00_r5_b6.png', 'id01_r5_b6.png', 'id00_r6_b5.png', 'id02_r5_b6.png', 'id00_r5_b6.png'])
    False
    """
    ids = [re.match(named_pattern, f).groupdict()['scene_id'] for f in file_list]
    last_positions = {}
    
    for i, id_ in enumerate(ids):
        if id_ in last_positions and i - last_positions[id_] < 5:
            return False
        last_positions[id_] = i
    
    return True

def unit_test():
    """
    Generates 1000 file lists and tests them with `test_file_order` function.
    
    Raises an AssertionError if any list does not satisfy the condition.
    """
    for _ in range(1000):
        files = generate_file_list(12, seed=None)
        assert test_file_order(files), "Test failed for generated file list"
        assert len(files) == 2*12, "Incorrect number of files"
        assert len(set(files)) == len(files), "File name list not unique"

def main(n_scenes, seed, test):
    """
    Main function to generate file list and/or run tests based on input arguments.
    
    Parameters:
    - n_scenes (int): Number of scenes. Total number of files generated will be 2 x n_scenes
    - seed (int): Seed for random number generation.
    - test (bool): If True, run unit_test instead of generating file list.
    """
    if test:
        unit_test()
        print("All tests passed!")
    else:
        files = generate_file_list(n_scenes, seed)
        print("\n".join(files))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a file list for cognitive science experiment.')
    parser.add_argument('n_scenes', type=int, help='Number of scenes. Total number of files generated will be 2 x n_scenes.')
    parser.add_argument('seed', type=int, help='Seed for random number generation.')
    parser.add_argument('--test', action='store_true', help='Run unit tests instead of generating file list.')
    
    args = parser.parse_args()
    main(args.n_scenes, args.seed, args.test)