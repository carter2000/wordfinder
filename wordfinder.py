#-*- coding: utf-8 -*-
import codecs
import getopt
import io
import os
import sys

class WordFinder:
    def __init__(self):
        self.__COUNT = "count"
        self.__LINENO = "lineno"
        self.__OCCURRED = "occurred"
        self.__path = os.getcwd()
        self.__findmode = self.__LINENO
        self.__fullword = False
        self.__recursive = False
        self.__storeresult = False
        self.__casesensitive = False
        self.__SetSuffixs("c,cpp,h,hpp,txt,xml,py,proto")

    def Find(self, line):
        word = ""
        optionstart = line.find("-")
        if optionstart == -1:
            word = line
        else:
            word = line[0 : optionstart - 1]
            args = line[optionstart : ].split()
            if not self.__ParseOptions(args):
                return

        if not os.path.exists(self.__path):
            print("'" + self.__path + "'" + " is not exists!")
            return
        print(os.path.abspath(self.__path))
        path = os.path.normpath(os.path.abspath(self.__path))

        filecount = 0
        wordcount = 0
        output = io.StringIO()
        if os.path.isdir(path):
            filecount, wordcount  = self.__FindInDir(path, word, output)
        elif os.path.isfile(path):
            wordcount = FindInFile(path, word)
            filecount = 1 if wordcount > 0 else 0

        outputline = "file-count:" + str(filecount)
        if self.__findmode != self.__OCCURRED:
            outputline += " word-count:" + str(wordcount)
        print(outputline)
        output.write(outputline + os.linesep)

        if self.__storeresult:
            outputfile = open("wordfinder.txt", "w")
            outputfile.writelines(output.getvalue())
            outputfile.close()
        output.close()

    def __SetSuffixs(self, line):
        self.__ignoresuffix = False
        self.__emptysuffix = False
        self.__suffixs = ()
        words = line.split(',')
        if '*' in words:
            self.__ignoresuffix = True
            return
        suffixwords = set()
        for word in words:
            if word == "":
                self.__emptysuffix = True
            else:
                suffixwords.add("." + word)
        self.__suffixs = tuple(suffixwords)

    def __FindInFile(self, path, word, output):
        assert(os.path.isfile(path))
        if (not os.path.exists(path)):
            return 0
        count = 0
        lineno = 0
        inputfile = codecs.open(path, "r", "utf-8", "ignore")
        for line in inputfile.readlines():
            lineno += 1
            cur_count = self.__CountWord(line, word)
            if cur_count > 0:
                if self.__findmode == self.__OCCURRED:
                    print(path)
                    output.write(path + os.linesep)
                    return 1
                elif self.__findmode == self.__LINENO:
                    outputline = path + " line:" + str(lineno) + " count:" + str(cur_count)
                    print(outputline)
                    output.write(outputline + os.linesep)
            count += cur_count
        if count > 0 and self.__findmode == self.__COUNT:
            outputline = path + " count:" + str(count)
            output.write(outputline + os.linesep)
        return count

    def __FindInDir(self, path, word, output):
        assert(os.path.isdir(path))
        if (not os.path.exists(path)):
            return 0, 0
        filecount = 0
        wordcount = 0
        for child in os.listdir(path):
            childpath = os.path.join(path, child)
            if os.path.isdir(childpath) and self.__recursive:
                fc, wc = self.__FindInDir(childpath, word, output)
                filecount += fc
                wordcount += wc
            elif os.path.isfile(childpath) and self.__CheckSuffix(childpath):
                wc = self.__FindInFile(childpath, word, output)
                if wc > 0:
                    wordcount += wc
                    filecount += 1
        return filecount, wordcount 

    def __CheckSuffix(self, path):
        assert(os.path.isfile(path))
        if self.__ignoresuffix:
            return True
        elif self.__emptysuffix and not "." in os.path.basename(path):
            return True
        else:
            return path.endswith(self.__suffixs)

    def PrintUsage(self):
        print("example input: word [-p, -m, --suffixs=]")
        print("    word: target word")
        print("    -p: target dir or file")
        print("    -m: 1 for occurred, 2 for word count, 3 for line no(default)")
        print("    --store: if specified, the result will be stored in 'wordfinder.txt'")
        print("    --rec: if specified, program will search the subdir recursively")
        print("    --case: if specified, the word is case sensitive")
        print("    --full: if specified, the word is full word")
        print("    --suffixs: specified the target files's suffixs, such as 'c,cpp,xml'")

    def __ParseOptions(self, args):
        try:
            options, _ = getopt.getopt(args, "p:m", ["rec", "store", "case", "full", "suffixs="])
        except:
            print("unknown option")
            return False
        for name, value in options:
            if name == "-m":
                if value == "1":
                    self.__findmode = self.__OCCURRED
                elif value == "2":
                    self.__findmode = self.__COUNT
                else:
                    self.__findmode = self.__LINENO
            elif name == "-p":
                self.__path = value
            elif name == "--rec":
                self.__recursive = True
            elif name == "--store":
                self.__storeresult = True
            elif name == "--case":
                self.__casesensitive = True
            elif name == "--full":
                self.__fullword = True
            elif name == "--suffixs":
                self.__SetSuffixs(value)
        return True

    def __CountWord(self, line, word):
        if not self.__casesensitive:
            line = line.upper()
            word = word.upper()
        count = 0
        wordlen = len(word)
        linelen = len(line)
        pos = line.find(word, 0)
        while pos != -1:
            if self.__fullword:
                if (pos > 0 and line[pos].isalpha()) or (pos + wordlen + 1 < linelen and line[pos + wordlen + 1].isalpha()):
                    pos = line.find(word, pos + 1)
                    continue
            count += 1
            pos = line.find(word, pos + wordlen + 1)

        return count


def main():
    finder = WordFinder()
    finder.PrintUsage()
    while True:
        try:
            line = input("input: ")
        except:
            sys.exit()
        if line == "exit" or line == "q":
            break;
        finder.Find(line)

if __name__ == "__main__":
    main()
