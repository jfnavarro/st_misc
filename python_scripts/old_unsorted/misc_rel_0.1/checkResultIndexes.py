import sys
import os


def usage():
    print "Usage:"
    print "python checkResultIndexes.py testResults.fastq mismatches_out.txt"


def main(result, mismatches_out):
    res = open(result)
    mismatches = open(mismatches_out, "w")

    wrongMappings = 0
    missedMappings = 0

    mismatch_format = "{}\n" \
                      "Quality:  {}\n" \
                      "Observed: {}\n" \
                      "Wrong:    {}\n" \
                      "Correct:  {}\n" \
                      "Shift:    {} -> {}\n\n"
    while True:
        name = res.readline().rstrip()
        if not name:
            break

        seq = res.readline().rstrip()
        #drop 2 more
        optional = res.readline().rstrip()
        qual = res.readline()
        try:
            foundId = optional.split(' ')[1].split('=')[1]

        except IndexError:
            missedMappings += 1
            continue

        correct_id, c_x, c_y = name.split("\t")[1:4]
        if foundId != correct_id:
            wrongMappings += 1
            o_x, o_y = optional.split("\t")[1:]
            mismatches.write(mismatch_format.format(seq,
                qual[10:10 + len(correct_id)],
                seq[10:10 + len(correct_id)],
                foundId,
                correct_id,
                (c_x, c_y),
                (o_x, o_y)))

    res.close()
    mismatches.close()

    print 'Wrong: ' + str(wrongMappings)
    print 'Missed: ' + str(missedMappings)


if __name__ == "__main__":
    #Should have three inputs.
    if len(sys.argv) != 3:
        usage()
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
