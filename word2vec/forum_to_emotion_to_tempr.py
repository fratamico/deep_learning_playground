from nltk import tokenize

import csv
import string
import regex as re
"""from WNAffect_master.wnaffect import WNAffect

wna = WNAffect('wordnet-1.6/', 'wn-domains-3.2/')
emo = wna.get_emotion('angry', 'JJ')
print(emo)"""

# import modules & set up logging
import gensim, logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
 
#sentences = [['first', 'sentence'], ['second', 'sentence'], ['third', 'sentence'], ['second', 'sentence']]
# train word2vec on the two sentences
#model = gensim.models.Word2Vec(sentences, min_count=1)

#print model.most_similar('sentence', topn=5)

def standardize(text):
  # standardize lettercase - all lowercase
  text = text.lower()

  # standardize punctuation - turn all to whitespace
  #period_location = string.punctuation.find(".")
  translation_string = ' '*(len(string.punctuation))
  #translation_string[period_location] = "."
  replace_punctuation = string.maketrans(string.punctuation, translation_string)
  text = text.translate(replace_punctuation)
  #print text
  #sys.exit()

  #text = text.decode('utf-8', 'ignore')

  # standardize whitespace
  text = " ".join(text.split())
  return text

def standardize_unicode(text):
    text = text.lower()
    text = re.sub(ur"\p{P}+", "", text)
    text = " ".join(text.split())
    return text

num_words_posted_on_forums = {}

# read forums, print the top number of words used per person
with open('ctlt_hackathon2.0_data/UBCx__Climate101x__3T2015_cleaned/forum_posts_anonmyized.tsv', 'rb') as csvfile:
    csvreader = csv.reader(csvfile, delimiter='\t', quotechar='"')
    csvreader.next()
    for row in csvreader:
        user_id = row[0]
        post = row[9]

        post_cleaned = standardize(post)

        post_word_count = len(post_cleaned.split())

        if user_id not in num_words_posted_on_forums:
            num_words_posted_on_forums[user_id] = 0
        num_words_posted_on_forums[user_id] += post_word_count

sorted_dict = sorted(num_words_posted_on_forums.iteritems(), key=lambda x:-x[1])[:114] #114 people who posted more tha 100 words on the forum
top_posters = [x[0] for x in sorted_dict]


# get sentences posted on the forum for those all users to be used for training
# read forums, print the top number of words used per person
all_sentences = []

with open('ctlt_hackathon2.0_data/UBCx__Climate101x__3T2015_cleaned/forum_posts_anonmyized.tsv', 'rb') as csvfile:
    csvreader = csv.reader(csvfile, delimiter='\t', quotechar='"')
    csvreader.next()
    for row in csvreader:
        #user_id = row[0]

        #if user_id in top_posters:
        post = row[9]
        tokenized_post = tokenize.sent_tokenize(post.decode('utf-8'))
        for p in tokenized_post:
            cleaned_p = standardize_unicode(p).split()
            
            all_sentences.append(cleaned_p)


# train word2vec on those sentences (all_sentences)
model = gensim.models.Word2Vec(all_sentences, min_count=1)

print model.most_similar('science', topn=5)

word_to_top5 = {}

# for each word used, turn into feature vector, getting word similarity
with open('ctlt_hackathon2.0_data/UBCx__Climate101x__3T2015_cleaned/forum_posts_anonmyized.tsv', 'rb') as csvfile:
    csvreader = csv.reader(csvfile, delimiter='\t', quotechar='"')
    csvreader.next()
    for row in csvreader:
        user_id = row[0]

        #if user_id in top_posters:
        post = row[9]
        tokenized_post = tokenize.sent_tokenize(post.decode('utf-8'))
        for p in tokenized_post:
            cleaned_p = standardize_unicode(p).split()

            for w in cleaned_p:
                if not w in word_to_top5:
                    word_to_top5[w] = [new_w[0] for new_w in model.most_similar(w, topn=5)]


# turn into list of events for each user
user_to_tempr_events = {}
with open('ctlt_hackathon2.0_data/UBCx__Climate101x__3T2015_cleaned/forum_posts_anonmyized.tsv', 'rb') as csvfile:
    csvreader = csv.reader(csvfile, delimiter='\t', quotechar='"')
    csvreader.next()
    for row in csvreader:
        user_id = row[0]

        #if user_id in top_posters:
        if user_id not in user_to_tempr_events:
            user_to_tempr_events[user_id] = []
        post = row[9]
        tokenized_post = tokenize.sent_tokenize(post.decode('utf-8'))
        for p in tokenized_post:
            cleaned_p = standardize_unicode(p).split()

            for w in cleaned_p:
                event = w + u"." + ".".join(word_to_top5[w])
                user_to_tempr_events[user_id].append(event)


"""outfile_m = open('Tempr---A-visual-knowledge-engineering-tool-master/code/processing/_MOOC_Climate_m_words.txt', 'w')
outfile_f = open('Tempr---A-visual-knowledge-engineering-tool-master/code/processing/_MOOC_Climate_f_words.txt', 'w')

count_m = 0
count_f = 0

def eliminate_bad_characters(string):
	string = re.sub('[^(a-z)(A-Z)(0-9)._-]', '_', string)
	return string

# maybe compare people who got a grade male vs female, old vs young
with open('ctlt_hackathon2.0_data/UBCx__Climate101x__3T2015_cleaned/person_course_cleaned.tsv', 'rb') as csvfile:
    csvreader = csv.reader(csvfile, delimiter='\t', quotechar='"')
    csvreader.next()
    for row in csvreader:
        user_id = row[0]
        education = row[1]
        YoB = row[5]
        gender = row[6]
        grade = row[7]

        if user_id in top_posters:

            if gender == "m" or gender == "f":
                if gender == "m":
                    count_m += 1
                    outfile_m.write("========================================" + "\n")
                    for temper_event in user_to_tempr_events[user_id]:
                        outfile_m.write(eliminate_bad_characters(temper_event).encode('ascii',errors='ignore') + "\n")
                if gender == "f":
                    count_f += 1
                    outfile_f.write("========================================" + "\n")
                    for temper_event in user_to_tempr_events[user_id]:
                        outfile_f.write(eliminate_bad_characters(temper_event).encode('ascii',errors='ignore') + "\n")


print "m", count_m
print "f", count_f

"""
outfile_m = open('Tempr---A-visual-knowledge-engineering-tool-master/code/processing/_MOOC_Climate_hl_words.txt', 'w')
outfile_f = open('Tempr---A-visual-knowledge-engineering-tool-master/code/processing/_MOOC_Climate_ll_words.txt', 'w')

count_m = 0
count_f = 0

def eliminate_bad_characters(string):
    string = re.sub('[^(a-z)(A-Z)(0-9)._-]', '_', string)
    return string

gains = []

# maybe compare people who got a grade male vs female, old vs young
with open('ctlt_hackathon2.0_data/UBCx__Climate101x__3T2015_cleaned/climate_pre_post_test.csv', 'rb') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    csvreader.next()
    for row in csvreader:
        user_id = row[0]
        gain = float(row[3])

        if user_id in top_posters:

            if gain >= 0.347593583:
                count_m += 1
                outfile_m.write("========================================" + "\n")
                for temper_event in user_to_tempr_events[user_id]:
                    outfile_m.write(eliminate_bad_characters(temper_event).encode('ascii',errors='ignore') + "\n")
            else:
                count_f += 1
                outfile_f.write("========================================" + "\n")
                for temper_event in user_to_tempr_events[user_id]:
                    outfile_f.write(eliminate_bad_characters(temper_event).encode('ascii',errors='ignore') + "\n")
        

print 
print "hl", count_m
print "ll", count_f


print model.most_similar('the', topn=5)
print model.most_similar('skeptical', topn=5)
print model.most_similar('environmentalist', topn=5)



