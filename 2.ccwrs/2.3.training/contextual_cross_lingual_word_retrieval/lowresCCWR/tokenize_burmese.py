from pyidaungsu import tokenize

input_file = "wiki_my_clean_20k.txt"
output_file = "wiki_my_clean_20k_tokenized.txt"

with open(input_file) as f, open(output_file, "w") as out:
    for line in f:
        tokens = tokenize(line.strip())
        out.write(" ".join(tokens) + "\n")