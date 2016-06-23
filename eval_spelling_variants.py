from glove import Glove,metrics

vecf = "/home/naomi/data/mittens/vectors/twitter_win10_d100.txt"
formal_vocab_fname = "/home/naomi/data/mittens/wikipedia_en.txt.vocab"
informal_vocab_fname = "/home/naomi/data/mittens/twitter_en.txt.vocab"
eval_fname = "/home/naomi/embeddings/urbandic-scraper/spelling_variants_valid.txt"

with open(formal_vocab_fname) as formal_vocab_fh:
    formal_vocab = set([line.split()[0] for line in formal_vocab_fh])
with open(informal_vocab_fname) as informal_vocab_fh:
    informal_vocab = set([line.split()[0] for line in informal_vocab_fh])
vectors = Glove.load_stanford(vecf)

def find_rank(similarity_list, target):
    for (i, (word, score)) in enumerate(similarity_list):
        if word == target:
            return i
    raise LookupError

def filter_informal(similarity_list):
    return filter(lambda ((word, score)): word in formal_vocab, similarity_list)

def eval_data_from_file(eval_fh):
    variants = []
    excluded_formal = 0
    excluded_informal = 0

    for line in eval_fh:
        (informal, formal) = line.split()
        if formal not in formal_vocab:
            excluded_formal += 1
            continue
        if formal not in informal_vocab or informal not in informal_vocab:
            excluded_informal += 1
            continue
        variants.append((informal, formal))
    print("excluded formal = %i" % excluded_formal)
    print("excluded informal = %i" % excluded_informal)
    return variants

with open(eval_fname) as eval_fh:
    eval_data = eval_data_from_file(eval_fh)
print("%i evaluation pairs" % len(eval_data))

def evaluate_pair((informal, formal), numsim=1000):
    most_sim =  filter_informal(vectors.most_similar(informal, numsim))
    return find_rank(most_sim, formal)

def evaluate_all_pairs():
    correct_cnt = 0
    top20_cnt = 0
    error_cnt = 0
    ranks = []
    for x in eval_data:
        try:
            rank = evaluate_pair(x, numsim=10000) 
            ranks.append(rank)
        except:
            error_cnt += 1
            continue
        if rank == 0:
            correct_cnt += 1
        if rank < 20:
            top20_cnt += 1
    print(ranks)
    print("%i pairs error" % error_cnt)
    print("%i pairs correct" % correct_cnt)
    print("%i pairs in top 20" % top20_cnt)

