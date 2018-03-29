from pyspark import SparkConf, SparkContext
import sys
import operator

conf = SparkConf().setAppName('word count')
sc = SparkContext(conf=conf)


def words_once(line):
    for w in line.split():
        yield (w, 1)


def get_key(kv):
    return kv[0]


def output_format(kv):
    k, v, m = kv
    return '%s %i %f' % (k, v, m)


if __name__ == '__main__':
    genre_list = ["crime", "fiction", "fantasy", "young-adult", "romance", "comedy", "dystopia",
                  "action", "historical", "non-fiction", "science fiction", "self-help"]

    for genre in genre_list:
        inputs = '../data/word_bags/' + genre + '_words.txt'
        output = '../data/word_counts/' + genre + '_counts/'

        text = sc.textFile(inputs)
        words = text.flatMap(words_once)
        wordcount = words.reduceByKey(operator.add)

        wordcount = wordcount.filter(lambda x: x[1] > 2)
        total_word_count = wordcount.map(lambda x: x[1]).sum()

        # print(total_word_count)

        words_with_count_percents = wordcount.map(lambda line: (line[0], line[1], (line[1] / total_word_count)))

        outdata = words_with_count_percents.sortBy(get_key).map(output_format)
        outdata.saveAsTextFile(output)