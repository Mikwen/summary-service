#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import codecs
import os

from reportlab.pdfgen import canvas

import sys, json
from TextRank2 import TextRank2

class PDFConverter():

    def convertPdfToTxt(self, PDFPath):
        invalidWords = ['•', '–', '']
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        codec = 'utf-8'
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
        fp = open(PDFPath, 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        maxpages = 0
        caching = True

        for page in PDFPage.get_pages(fp, maxpages=maxpages, password=password, caching=caching, check_extractable=True):
            interpreter.process_page(page)
        text = retstr.getvalue()

        #vurdere å flytte denne delen til en egen klasse slik at den kan brukes av botten også

        txtString = ''
        i = 0
        lbList = []
        for line in text:
            if line is ('\n'):
                lbList.append(i)
            if not(i in lbList and (i - 1) in lbList) and (line not in invalidWords):
                txtString += ''.join(line)
            i += 1

        fp.close()
        device.close()
        retstr.close()
        return txtString

    def convertTxtToPdf(self, txtFile, filename):
        c = canvas.Canvas(filename)
        txtfile = open(txtFile, 'r')
        x = 10
        y = 10
        for word in txtfile:
            c.drawString(x,y, word)
            y += 15
        c.showPage()
        c.save()
        return 'PDF-File created.'

class ScraperBot():

    #ta inn text konvertert fra pdf og ta ut det viktige.
    #Needs: måte å detektere viktige ting i en foil på.
    #lese teksfil, og skrive ting til en ny.
    #måte å koble foil til fag på. DONE ISH
    #måte å skille ut uønskede tegn på.
    #varsling dersom noe går galt.
    #testing for å se om alle foils går gjennom.
    #hente nye foiler fra databasen. ISH DONE, Må ha database for å sjekke opp mot.
    #effektivisering

    summaryTool = None

    def __init__(self, summaryTool):
        self.summaryTool = summaryTool

    def makeSummaryFromFoil(self, txtString):
        #run all necessary methods for making a summary out of one foil.
        self.summaryTool.summaryRun(txtString)

    #write to a new txtfile
    def writeToNewFile(self, path, importatWords):
        finishedFile = open(path, 'w')
        for word in importatWords:
            finishedFile.write(word)
        finishedFile.close()

class SubjectCodeList():

    validLetters = ('V', 'C', 'Y', 'D', 'K', 'X', 'P', 'Q', 'F', 'E', 'L', 'R', 'H', 'Ø', 'M', 'S', 'T', 'N', 'A', 'O', 'B', 'U', 'J', 'G', 'Æ', 'W', 'Z', 'Å', 'I')
    stopLetters = ('0','1','2','3','4','5','6','7','8','9')
    subjectCodeList = []

    def subjectCodeLetters(self, letters):
        valid = True
        pos = 0
        stop = 0
        for letter in letters:
            if letter not in self.validLetters and letter not in self.stopLetters:
                valid = False
            if letter in self.stopLetters:
                stop = pos
                break
            pos += 1
        if valid:
            self.subjectCodeList.append(letters[:stop])

    def allSubjectCodeLetters(self, path):
        file = open(path, 'r')
        for line in file:
            self.subjectCodeLetters(line)
        file.close()

    def listToSet(self, l):
        l = set(l)
        l.discard('')
        return l


class SummaryTool():

    subjectCodeNums = ('0','1','2','3','4','5','6','7','8','9')
    subjectCodeLetters = ('TDT', 'TMA')

    def __init__(self):
        self.textRank = TextRank2()
        self.PDFConverter = PDFConverter()
        # self.SubjectCodeList = SubjectCodeList()
        # self.subjectCodeLetters = self.overwriteSubjectCodeLetters('C:\\Users\\BenjaminAune\\PycharmProjects\\Repetisjonsforelsening\\PU\\Files\\subCodes.txt')

    # #Just so the bot can stay updated on the different Subjectcodes
    # def overwriteSubjectCodeLetters(self, codefile):
        # self.SubjectCodeList.allSubjectCodeLetters(codefile)
        # self.subjectCodeLetters = self.SubjectCodeList.listToSet(self.SubjectCodeList.subjectCodeList)

    # #get the subjectcode for a given txtfile aka pdffoil
    # def getSubjectCode(self, file):
        # for word in file:
            # if word[0:3] in self.subjectCodeLetters:
                # numValid = True
                # for i in range(3,7):
                    # if word[i] not in self.subjectCodeNums:
                        # numValid = False
                        # break
                # if numValid:
                    # return word
        # return "No SubjectCode found."

    def summaryRun(self, pdfFilePath, outFile):
        tempFile = pdfFilePath + 'temp.txt'
        self.textRank.summarizeFile(self.PDFConverter.convertPdfToTxt(pdfFilePath), tempFile)
        self.PDFConverter.convertTxtToPdf(tempFile, outFile)
        os.remove(tempFile)

class RunBot():

    def __init__(self):
        self.summaryTool = SummaryTool()

    def readIn(self):
        PDFFile = sys.stdin.readlines()
        return json.loads(PDFFile[0])

    def run(self):
        PDFFile = self.readIn()
        self.summaryTool.summaryRun(PDFFile)

