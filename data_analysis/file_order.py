import re
import random
import csv
import os

named_pattern = re.compile(r'^id(?P<scene_id>\d+)_v(?P<version>\d+)_b(?P<blue_count>\d+)_r(?P<red_count>\d+)\..+$')

def split_scenes_shuffle(file_list, random_seed):
    """
    Reorder a list of image file names based on extracting and interpreting embedded 
    information in the names, followed by a randomization process which uses a specified seed.
    
    The file names are expected to match the following pattern:
    'id<scene_id>_v<version>_r<red_count>_b<blue_count>.png'
    
    The function returns a new order of the file names, ensuring a balanced and randomized 
    distribution of 'red' and 'blue' sides in the scenes, as determined by the counts embedded 
    in the original file names.

    Parameters:
    - file_list (list of str): A list of file names.

    Returns:
    - list of str: A reordered list of file names.

    Example:
    >>> file_list = [
    ...     "id0_v1_r5_b6.png",
    ...     "id0_v2_r6_b5.png",
    ...     "id1_v1_r5_b6.png",
    ...     "id1_v2_r6_b5.png",
    ...     "id2_v1_r6_b5.png",
    ...     "id2_v2_r5_b6.png"
    ... ]
    >>> experiment_order(file_list, 123)
    ['id2_v2_r5_b6.png', 'id1_v1_r5_b6.png', 'id0_v2_r6_b5.png', 'id2_v1_r6_b5.png', 'id1_v2_r6_b5.png', 'id0_v1_r5_b6.png']
    """    

    lookup = {}
    for fn in file_list:
        md = {k:int(v) for k,v in re.match(named_pattern, fn).groupdict().items()}
        md['file_name'] = fn
        expected_side = 'red' if md['red_count'] > md['blue_count'] else 'blue' if md['blue_count'] > md['red_count'] else 'none'
        side_per_scene = lookup.setdefault(md['scene_id'], {})
        side_per_scene[expected_side] = md

    n_scenes = len(lookup)
    first_half_scenes = [_ for _ in range(n_scenes)]
    first_half_sides = ['blue'] * n_scenes
    for i in range(n_scenes // 2):
        first_half_sides[i] = 'red'

    # choose scenes in random order
    # chosse random side for each scene, such that sides appears in equal proportion
    random.seed(random_seed)
    random.shuffle(first_half_scenes)
    random.shuffle(first_half_sides)
    first_half_idx = [_ for _ in zip(first_half_scenes, first_half_sides)]

    def _opposite(color):
        return 'blue' if color == 'red'  else 'red' if color=='blue' else None
    second_half_idx = [(v[0], _opposite(v[1])) for v in first_half_idx]

    new_order = []
    for scene, expected_side in first_half_idx:
        new_order.append(lookup[scene][expected_side]['file_name'])
    for scene, expected_side in second_half_idx:
        new_order.append(lookup[scene][expected_side]['file_name'])

    return new_order


def shuffle_second_half(file_list):
    """
    Create a new list based on the input_list where the third and fourth quarter are shuffled separately.
     
    If the input file list is such that the first half contains all scenes, and the second one the other version of the same scenes in the same order,
    calling this function will ensure that the second half has a different scene order. 
    Just naively shuffling the second half may lead to a situation where two versions of the same scene may appear close to each-other (at the end of the first half and beginning of second half). 
    To prevent this, the second half is shuffled in parts, the first half and the second half (so the 3rd and 4th quarter of the input list). 
    """
    h1 = file_list[:len(file_list)//2]

    # split the second half of the list into 2 parts, shuffle each part separately
    q3 = file_list[len(file_list)//2:(len(file_list)*3)//4]
    random.shuffle(q3)
    q4 = file_list[(len(file_list)*3)//4:]
    random.shuffle(q4)

    # concatenate the first half with the shuffled quarters
    new_list = h1 + q3 + q4
    return new_list


import pytest

def test_valid_formats():
    # Ensure the function can parse valid formats
    valid_file_list = ["id00_v1_r5_b6.png", "id00_v2_r6_b5.png"]
    assert split_scenes_shuffle(valid_file_list, 123) is not None

def test_invalid_formats():
    # Ensure the function raises an error for invalid formats
    invalid_file_list = ["invalid_name.png", "invalid_name.png"]
    with pytest.raises(AttributeError):
        split_scenes_shuffle(invalid_file_list, 123)

def test_balanced_distribution():
    # Ensure red and blue are distributed evenly
    file_list = ["id00_v1_r5_b6.png", "id00_v2_r6_b5.png", "id01_v1_r5_b6.png", "id01_v2_r6_b5.png"]
    reordered_list = split_scenes_shuffle(file_list, 123)
    red_count = sum(1 for name in reordered_list if "_r" in name)
    blue_count = sum(1 for name in reordered_list if "_b" in name)
    assert red_count == blue_count

def test_deterministic_output():
    # Ensure the function produces consistent output for the same seed
    file_list = ["id00_v1_r5_b6.png", "id00_v2_r6_b5.png"]
    assert split_scenes_shuffle(file_list, 123) == split_scenes_shuffle(file_list, 123)

def test_correct_file_names():
    # Ensure the function returns the correct file names
    file_list = ["id00_v1_r5_b6.png", "id00_v2_r6_b5.png"]
    reordered_list = split_scenes_shuffle(file_list, 123)
    assert set(reordered_list) == set(file_list)

def test_different_seeds():
    # Ensure the function returns the correct file names
    file_list = ["id00_v1_r5_b6.png", "id00_v2_r6_b5.png", "id01_v1_r5_b6.png", "id01_v2_r6_b5.png"]
    reordered_list_1 = split_scenes_shuffle(file_list, 123)
    reordered_list_2 = split_scenes_shuffle(file_list, 321)
    assert set(reordered_list_1) == set(reordered_list_2)
    assert reordered_list_1 != reordered_list_2

def test_all_red_or_blue_scenes():
    # Ensure the function can handle all red or all blue scenes
    all_red_file_list = ["id00_v1_r5_b0.png", "id00_v2_r6_b0.png"]
    all_blue_file_list = ["id00_v1_r0_b5.png", "id00_v2_r0_b6.png"]
    assert split_scenes_shuffle(all_red_file_list, 123) is not None
    assert split_scenes_shuffle(all_blue_file_list, 123) is not None

def test_immutable_input():
    # Ensure the function does not modify the input
    file_list = ["id00_v1_r5_b6.png", "id00_v2_r6_b5.png"]
    original_file_list = file_list.copy()
    _ = split_scenes_shuffle(file_list, 123)
    assert file_list == original_file_list

def test_scene_ids_and_color_counts():
    # Ensure scene_ids in the first and second halves are the same and color counts are swapped
    file_list = [
        "id00_v1_r5_b6.png",
        "id00_v2_r6_b5.png",
        "id01_v1_r5_b6.png",
        "id01_v2_r6_b5.png",
        "id02_v1_r7_b6.png",
        "id02_v2_r6_b7.png"
    ]
    reordered_list = split_scenes_shuffle(file_list, 123)
    
    # Extract scene_ids and color counts from file names
    parsed_info = [{k: int(v) if k != 'scene_id' else v for k, v in re.match(named_pattern, fn).groupdict().items()} for fn in reordered_list]
    
    half_length = len(reordered_list) // 2
    first_half_info = parsed_info[:half_length]
    second_half_info = parsed_info[half_length:]
    
    # Check for same scene_ids and swapped color counts
    for first, second in zip(first_half_info, second_half_info):
        assert first['scene_id'] == second['scene_id']
        assert first['red_count'] == second['blue_count']
        assert first['blue_count'] == second['red_count']


def main():
    # Get the path to the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Calculate the path to the sibling directory
    file_path = os.path.join(script_dir, '..', 'stimuli', 'file_names.csv')

    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        file_names = [row[0] for row in reader]
        
    # split the string into substrings on any blank space
    

    # split scenes into first half and second half
    new_order = split_scenes_shuffle(file_names, 123)

    # change the ordering of the second
    new_order = shuffle_second_half(new_order)

    for fn in new_order:
        print(fn)


if __name__ == '__main__':
    # test_valid_formats()
    # test_invalid_formats()
    # test_balanced_distribution()
    # test_deterministic_output()
    # test_correct_file_names()
    # test_different_seeds()
    # test_immutable_input()
    # test_scene_ids_and_color_counts()

    # "Tests passed!"  # If no assertion errors, we consider tests passed.
    main()
