'''Contains various classes for generating synthetic data.'''

import random


def mutate_DNA_sequence(seq, min_distance, max_distance, substitution_prob, insertion_prob=0.0, deletion_prob=0.0):
    """Gets a sequence and mutates it to a desired distance range using a uniform substitution model.
    The weights govern the probability of generating a substitution, insertion or deletion.
    Setting the substitution prob to < 0 will make it be computed as (max_dist+min_dist)/(2*len(seq)).
    Returns a tuple with a mutated uppercase string and the Levenshtein distance.
    """
    if min_distance > max_distance or min_distance < 0:
        raise ValueError("Illegal min or max distance")

    seq = seq.upper()

    if seq == "" or max_distance == 0:
        return seq

    if substitution_prob < 0:
        substitution_prob = min(1.0, (min_distance + max_distance) / (2 * len(seq)))

    summ = substitution_prob + insertion_prob + deletion_prob
    substitution_prob /= summ
    insertion_prob /= summ
    deletion_prob /= summ
    bases = ['A','C','G','T']


    # Create sequence.
    dist = -1
    l = [char for char in seq]
    while dist < min_distance or dist > max_distance:
        dist = 0
        l = [char for char in seq]
        for i in range(len(seq)):
            r = random.random()
            if r < insertion_prob:
                # Insertion
                l[i] = random.choice(bases) + l[i]
                dist += 1
            elif r < (insertion_prob + deletion_prob):
                # Deletion
                l[i] = ""
                dist += 1
            elif r < (insertion_prob + deletion_prob + substitution_prob):
                # Substitution
                while seq[i] == l[i]:
                    l[i] = random.choice(bases)
                dist += 1
        # Tail insertion
        if random.random() < insertion_prob:
            l.append(random.choice(bases))
            dist += 1

    return "".join(l), dist


