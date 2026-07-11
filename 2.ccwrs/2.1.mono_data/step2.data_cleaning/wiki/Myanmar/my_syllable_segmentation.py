from sylbreak import syllable

input_file = "wiki_my_cleaned_20k_v2.txt"
output_file = "wiki_my_cleaned_20k_syllable_segmented.txt"

with open(input_file, "r", encoding="utf-8") as f_in, \
     open(output_file, "w", encoding="utf-8") as f_out:

    for line in f_in:

        line = line.strip()

        if not line:
            continue

        segmented = syllable(line)

        f_out.write(segmented + "\n")