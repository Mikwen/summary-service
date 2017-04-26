import io
import itertools

import networkx as nx
import nltk

class TextRank2:

    def filterForTags(self, tagged, tags=['NN','JJ','NNP']):
        return [item for item in tagged if item[1] in tags]

    def normalize(self, tagged):
        return [(item[0].replace('.', ''), item[1]) for item in tagged]

    def uniqueEverseen(self, iterable, key=None):
        seen = set()
        seenAdd = seen.add
        if key is None:
            for element in [x for x in iterable if x not in seen]:
                seenAdd(element)
                yield element
        else:
            for element in iterable:
                k = key(element)
                if k not in seen:
                    seenAdd(k)
                    yield element

    def lDistance(self, firstString, secondString):
        if len(firstString) > len(secondString):
            firstString, secondString = secondString, firstString
        distances = range(len(firstString) + 1)
        for index2, char2 in enumerate(secondString):
            newDistances = [index2 + 1]
            for index1, char1 in enumerate(firstString):
                if char1 == char2:
                    newDistances.append(distances[index1])
                else:
                    newDistances.append(1 + min((distances[index1], distances[index1 + 1], newDistances[-1])))
            distances = newDistances
        return distances[-1]

    def buildGraph(self, nodes):
        gr = nx.Graph()
        gr.add_nodes_from(nodes)
        nodePairs = list(itertools.combinations(nodes, 2))

        for pair in nodePairs:
            firstString = pair[0]
            secondString = pair[1]
            levDistance = self.lDistance(firstString, secondString)
            gr.add_edge(firstString, secondString, weight=levDistance)
        return gr

    def extractKeyphrases(self, text):
        wordTokens = nltk.word_tokenize(text)

        tagged = nltk.pos_tag(wordTokens)
        textlist = [x[0] for x in tagged]

        tagged = self.filterForTags(tagged)
        tagged = self.normalize(tagged)

        uniqueWordSet = self.uniqueEverseen([x[0] for x in tagged])
        wordSetList = list(uniqueWordSet)

        graph = self.buildGraph(wordSetList)

        calculatedPageRank = nx.pagerank(graph, weight='weight')

        keyphrases = sorted(calculatedPageRank, key=calculatedPageRank.get, reverse=True)

        aThird = len(wordSetList) // 3
        keyphrases = keyphrases[0: aThird +1]

        modifiedKeyprageses = set([])

        dealWith = set([])
        i = 0
        j = 1
        while j < len(textlist):
            firstWord = textlist[i]
            secondWord = textlist[j]
            if firstWord in keyphrases and secondWord in keyphrases:
                keyphrase = firstWord + ' ' + secondWord
                modifiedKeyprageses.add(keyphrase)
                dealWith.add(firstWord)
                dealWith.add(secondWord)
            else:
                if firstWord in keyphrases and firstWord not in dealWith:
                    modifiedKeyprageses.add(firstWord)
                if j == len(textlist) - 1 and secondWord in keyphrases and secondWord not in dealWith:
                    modifiedKeyprageses.add(secondWord)
            i += 1
            j += 1
        return modifiedKeyprageses

    def extractSentences(self, text, language):
        if language is 'norwegian':
            sentDetector = nltk.data.load('tokenizers/punkt/norwegian.pickle')
        else:
            sentDetector = nltk.data.load('tokenizer/punkt/english.pickle')
        sentenceTokens = sentDetector.tokenize(text.strip())
        graph = self.buildGraph(sentenceTokens)

        calculatedPageRank = nx.pagerank(graph, weight='weight')

        sentences = sorted(calculatedPageRank, key=calculatedPageRank.get, reverse=True)

        summary = ' '.join(sentences)
        summaryWords = summary.split('\n')
        summaryWords = summaryWords[0:101]
        summary = '\n'.join(summaryWords)

        return summary

    def getKeyphrasesFromFile(self, fileString):
        print('Generating output')
        keyphrases = self.extractKeyphrases(fileString)
        keyphraseFile = io.open('C:\\Users\\BenjaminAune\\PycharmProjects\\Repetisjonsforelsening\\PU\\Files\\keyphrasesTextTest.txt', 'w')
        for line in keyphrases:
            keyphraseFile.write(line + '\n')
        keyphraseFile.close()
        print('Done generating output')

    #Change this from using files to useing Strings
    def summarizeFile(self, fileString, outFile):
        print('Generating output')
        summary = self.extractSentences(fileString, 'english')
        summaryFile = io.open(outFile, 'w')
        summaryFile.write(summary)
        summaryFile.close()
        print('Done generating output')
