#!/usr/bin/python
##################################################
## PACscan - Identifies registered domains for PACs
## Author: Joshua Franklin
## Example input to start: 
## sudo ./electionBuster.py -p somePACname -y 2014
## 1: The first name of the PAC
## 2: The year you are scanning
##################################################

import sys
import time
import string
import argparse
from datetime import date
from urllib2 import Request, urlopen, URLError, HTTPError

# Program Timer
start_time = time.time()

# Function: casts and removes those pesky \r and \n
def stringAndStrip(input): 
	input = str(input)
	input =  input.rstrip()
	return input

#Parse command line arguments
parser = argparse.ArgumentParser(description='Identifies registered domains for a PAC')
parser.add_argument('-p','--PACname', help='The name of the PAC to scan',required=True)
parser.add_argument('-y','--year', help='Year of the election',required=True)
args = parser.parse_args()

# Stores command line argumetns
# Make all lowercase
# Runs stringAndStrip on everything 
PACname = args.PACname
PACname = stringAndStrip(PACname)
PACname = PACname.lower()
year = args.year
year = stringAndStrip(year)
smallYear = year[2:4]

# Expected URLs (obviously the list is different is the state var exists).
print 'We expect to find these URLs excluding subtle variances:'
print 'http://www.' + PACname + '.com'
print 'http://www.' + PACname + year + '.com'
print 'http://www.' + PACname + smallYear + '.com'

# This is the result output files
# Makes a unique filename based on data and time
now = date.today()
tempResults = 'results-' + PACname + '-' + str(now) + '.txt'

resultsFile = open(tempResults, "w")

# This clears the results files before reopening them
resultsFile.close()

resultsFile = open(tempResults, "a")

# Need a base alphabet for the first set of mangling functions
alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
vowels = "aeiouy"

confirmedURLs = []
testedURLs = []
skippedURLs = []

def tryURL(url) : 
	url = url
	if url not in testedURLs :
		try: 
			#Open input URL
			httpResponse = urlopen(url)
			print "*********************************************************************"
			print "Page Exists: " + httpResponse.geturl() + "."
			print httpResponse.info()
			print httpResponse.code
			print "*********************************************************************"
			confirmedURLs.append(url)
			testedURLs.append(url)
			resultsFile.write("*************************************************+" + "\n")
			resultsFile.write("Page Exists: " + httpResponse.geturl() + "\n")
			resultsFile.write(str(url) + ", " + str(httpResponse.code) + "\n")
			resultsFile.write(str(httpResponse.info()) + "\n")
			resultsFile.write("*************************************************+" + "\n")
						
		except HTTPError, e: 
			print "HTTPError"
			print e
			print e.code
			resultsFile.write(str(url) + ", HTTPError, " + str(e.code) + "\n")
			testedURLs.append(url)
			skippedURLs.append(url)
		except URLError, e: 
			print "URLError"
			print e.reason
			resultsFile.write(str(url) + ", URLError, " + str(e.reason) + "\n")
			testedURLs.append(url)
			skippedURLs.append(url)

def gen(website_name, alt_alphabet):
        A = 'abcdefghijklmnopqrstuvwxyz1234567890' # original alphabet string
        xform = string.maketrans(A, alt_alphabet)
        s = website_name.translate(xform)
        return s

def genAll(website_names, alphabets):
        results = []
        for s in website_names:
                for a in alphabets:
                        mangled_name = gen(s, a)
                        for domain_name_ending in tlds:
                                results.append( mangled_name + '.' + domain_name_ending )
	return results

def genAllDonate(website_names, alphabets):
        results = []
        for s in website_names:
                for a in alphabets:
                        mangled_name = gen(s, a)
                        for domain_name_ending in tlds:
                                results.append( mangled_name + 'donate.' + domain_name_ending )
	return results

# This function returns strings with each character missing
#['oshua', 'jshua', 'johua', 'josua', 'josha', 'joshu']
def skipLetter(s):
        kwds = []

        for i in range(1, len(s)+1):
            kwds.append(s[:i-1] + s[i:])
        return kwds

# This function subsitutes the wrong vowell for each letter
#'aoshua', 'boshua', 'coshua', 'doshua'
def wrongVowel(s):
        kwds = []
        for i in range(0, len(s)):
            for letter in vowels:
                if s[i] in vowels:
                    for vowel in vowels:
                        s_list = list(s)
                        s_list[i] = vowel
                        kwd = "".join(s_list)
                        kwds.append(kwd)
        return kwds

# This function inserts each alphabetic character into each place in a word
#['ajoshua', 'jjoshua', 'jooshua', 'josshua', 'joshhua', 'joshuua', 'joshuaa']
def doubleLetter(s):
        kwds = []
        for i in range(0, len(s)+1):
            kwds.append(s[:i] + s[i-1] + s[i:])

        return kwds

# This function inserts each alphabetic character into each place in a word
#'jaoshua', 'jnoshua', 'josthua', 'joshuza', 'joshua2'
def insertLetter(s):
       
        kwds = []

        for i in range(0, len(s)):
            for char in alphabet:
                kwds.append(s[:i+1] + char + s[i+1:])

        return kwds

# This function reverses each letter
#['ojshua', 'jsohua', 'johsua', 'josuha', 'joshau']
def reverseLetter(s):
        kwds = []
        for i in range(0, len(s)):
            letters = s[i-1:i+1:1]
            if len(letters) != 2:
                continue

            reverse_letters = letters[1] + letters[0]
            kwds.append(s[:i-1] + reverse_letters + s[i+1:])

        return kwds
        
#'aoshua', josh9a', 'josqua', 'jzshua'        
def substitution(s):
        kwds = []

        for i in range(0, len(s)):
            for letter in alphabet:
                kwd = s[:i] + letter + s[i+1:]
                kwds.append(kwd)
                
        return kwds      
  
# alternative alphabets
# 0: No change
# 1: i -> 1 "Eye to One"
# 2: l -> i "El to Eye"
# 3: i -> l "Eye to El"
# 4: o -> 0 "Oh to Zero"
# 5: 0 -> o "Zero to Oh" 
# 6: n -> m "En to Em" TODO: Does this swap wrok right? 
# 7: m -> n "Em to En"
# 8: e -> 3 "Ee to three"
# 9: 3 -> e "Three to ee"

alt_alphabets = [ 'abcdefghijklmnopqrstuvwxyz1234567890',
				  'abcdefgh1jklmnopqrstuvwxyz1234567890',
				  'abcdefghijkimnopqrstuvwxyz1234567890',
				  'abcdefghljklmnopqrstuvwxyz1234567890',
				  'abcdefghijklmn0pqrstuvwxyz1234567890',
				  'abcdefghijklmnopqrstuvwxyz123456789o',
				  'abcdefghijklmmopqrstuvwxyz1234567890',
				  'abcdefghijklnnopqrstuvwxyz1234567890',				  
				  'abcd3fghijklmnopqrstuvwxyz1234567890',
				  'abcdefghijklmnopqrstuvwxyz12e4567890']

# These are the template names - refer to Loop 1 for examples


templates = [
			 PACname,
			 PACname + year, 
			 year + PACname,
			 PACname + smallYear, 
			 smallYear + PACname,
			 ]

# top-level domain-names
tlds = ['com', 'net', 'me' , 'org', 'net', 'biz', 'info', 'us' ]

# This generates the text mangling
results = genAll( templates, alt_alphabets)

# This generates the text mangling with some other alternatives
resultsDonate = genAllDonate( templates, alt_alphabets)

#### LOOP 1 ####
# All examples use the input of 'josh franklin 2014 president DC' 
##################
#http://www.joshfranklin.com

print "Entering template loop 1^^^^^^^^^^^^^^^^^^^^^^^^^^" 
print time.time() - start_time, "seconds"
for r in results:
	r = stringAndStrip(r) 
	url = 'http://www.' + r
	url = stringAndStrip(url)
	print 'Trying: ' + url
	tryURL(url)

### LOOP 2 ###
# Puts donate at the beginning & 
# Removes the period after 'www'
########################
#http://www.donatejoshfranklin.com
#http://wwwjoshfranklin.com

print "Entering template loop 2^^^^^^^^^^^^^^^^^^^^^^^^^^"
print "There were " + str(len(skippedURLs)) + " skipped so far."
print time.time() - start_time, "seconds"
for r in results:
	r = stringAndStrip(r) 
	
	#Donate at the beginning
	url = 'http://www.donate' + r
	url = stringAndStrip(url)
	print 'Trying: ' + url
	tryURL(url)

	#No period
	urlnoperiod = 'http://www' + r
	url = stringAndStrip(urlnoperiod)
	print 'Trying: ' + urlnoperiod
	tryURL(urlnoperiod)

### LOOP 3 ###
# Puts donate at the end and removes the period after 'www'
########################
#http://www.joshfranklindonate.com
#http://wwwjoshfranklindonate.com
print "There were " + str(len(skippedURLs)) + " skipped so far."
print "Entering template loop 3^^^^^^^^^^^^^^^^^^^^^^^^^^" 
print time.time() - start_time, "seconds"
for r in resultsDonate:
	r = stringAndStrip(r) 
	
	#http://www.joshfranklindonate.com
	url = 'http://www.' + r
	url = stringAndStrip(url)
	print 'Trying: ' + url
	tryURL(url)
	
	#Donate at the end without periods after www
	#http://wwwjoshfranklindonate.com
	urlnoperiod = 'http://www' + r 
	url = stringAndStrip(urlnoperiod)
	print 'Trying: ' + urlnoperiod
	tryURL(urlnoperiod)

# TODO: add an extra o to situations with two 'o's, like "book" to "boook"
# TODO: try Rick for Richard etcetera 
# TODO: Turn 2014 into 14 so we look for http://www.lName+fName+14.com

### NEW TYPO FUNCTIONS###
# All examples use josh franklin 2014 president DC 

typoPACname = PACname
typoPACnameYear= PACname + year
typoPACnameSmallYear = PACname + smallYear

vowelResults1 = wrongVowel(typoPACname)
skipResults1 = skipLetter(typoPACname)
doubleResults1 = doubleLetter(typoPACname)
insertResults1 = insertLetter(typoPACname)
subResults1 = substitution(typoPACname)
reverseResults1 = reverseLetter(typoPACname)

vowelResults2 = wrongVowel(typoPACnameYear)
skipResults2 = skipLetter(typoPACnameYear)
doubleResults2 = doubleLetter(typoPACnameYear)
insertResults2 = insertLetter(typoPACnameYear)
subResults2 = substitution(typoPACnameYear)
reverseResults2 = reverseLetter(typoPACnameYear)

vowelResults3 = wrongVowel(typoPACnameSmallYear)
skipResults3 = skipLetter(typoPACnameSmallYear)
doubleResults3 = doubleLetter(typoPACnameSmallYear)
insertResults3 = insertLetter(typoPACnameSmallYear)
subResults3 = substitution(typoPACnameSmallYear)
reverseResults3 = reverseLetter(typoPACnameSmallYear)

### Typo loop 1 ###
print "There were " + str(len(skippedURLs)) + " skipped so far."
print "Entering vowel loop"
for r in vowelResults1 : 
	url = 'http://www.' + r
	url = stringAndStrip(url)
	for tld in tlds:
		tempURL = url + '.' + tld
		print 'Trying: ' + tempURL
		tryURL(tempURL)

print "Entering skip loop"
for r in skipResults1 : 
	url = 'http://www.' + r
	url = stringAndStrip(url)
	for tld in tlds:
		tempURL = url + '.' + tld
		print 'Trying: ' + tempURL
		tryURL(tempURL)	

print "Entering double loop"
for r in doubleResults1 : 
	url = 'http://www.' + r
	url = stringAndStrip(url)
	for tld in tlds:
		tempURL = url + '.' + tld
		print 'Trying: ' + tempURL
		tryURL(tempURL)	

print "Entering insert loop"
for r in insertResults1 : 
	url = 'http://www.' + r
	url = stringAndStrip(url)
	for tld in tlds:
		tempURL = url + '.' + tld
		print 'Trying: ' + tempURL
		tryURL(tempURL)		

print "Entering sub loop"
for r in subResults1 : 
	url = 'http://www.' + r
	url = stringAndStrip(url)
	for tld in tlds:
		tempURL = url + '.' + tld
		print 'Trying: ' + tempURL
		tryURL(tempURL)	

print "Entering reverse loop"
for r in reverseResults1 : 
	url = 'http://www.' + r
	url = stringAndStrip(url)
	for tld in tlds:
		tempURL = url + '.' + tld
		print 'Trying: ' + tempURL
		tryURL(tempURL)
					
### Typo loop 2 ###
print "There were " + str(len(skippedURLs)) + " skipped so far."
print "Entering vowel loop"
for r in vowelResults2 : 
	url = 'http://www.' + r
	url = stringAndStrip(url)
	for tld in tlds:
		tempURL = url + '.' + tld
		print 'Trying: ' + tempURL
		tryURL(tempURL)

print "Entering skip loop"
for r in skipResults2 : 
	url = 'http://www.' + r
	url = stringAndStrip(url)
	for tld in tlds:
		tempURL = url + '.' + tld
		print 'Trying: ' + tempURL
		tryURL(tempURL)	

print "Entering double loop"
for r in doubleResults2 : 
	url = 'http://www.' + r
	url = stringAndStrip(url)
	for tld in tlds:
		tempURL = url + '.' + tld
		print 'Trying: ' + tempURL
		tryURL(tempURL)	

print "Entering insert loop"
for r in insertResults2 : 
	url = 'http://www.' + r
	url = stringAndStrip(url)
	for tld in tlds:
		tempURL = url + '.' + tld
		print 'Trying: ' + tempURL
		tryURL(tempURL)		

print "Entering sub loop"
for r in subResults2 : 
	url = 'http://www.' + r
	url = stringAndStrip(url)
	for tld in tlds:
		tempURL = url + '.' + tld
		print 'Trying: ' + tempURL
		tryURL(tempURL)	

print "Entering reverse loop"
for r in reverseResults2 : 
	url = 'http://www.' + r
	url = stringAndStrip(url)
	for tld in tlds:
		tempURL = url + '.' + tld
		print 'Trying: ' + tempURL
		tryURL(tempURL)

### Typo loop 3 ###
print "There were " + str(len(skippedURLs)) + " skipped so far."
print "Entering vowel loop"
for r in vowelResults3 : 
	url = 'http://www.' + r
	url = stringAndStrip(url)
	for tld in tlds:
		tempURL = url + '.' + tld
		print 'Trying: ' + tempURL
		tryURL(tempURL)

print "Entering skip loop"
for r in skipResults3 : 
	url = 'http://www.' + r
	url = stringAndStrip(url)
	for tld in tlds:
		tempURL = url + '.' + tld
		print 'Trying: ' + tempURL
		tryURL(tempURL)	

print "Entering double loop"
for r in doubleResults3 : 
	url = 'http://www.' + r
	url = stringAndStrip(url)
	for tld in tlds:
		tempURL = url + '.' + tld
		print 'Trying: ' + tempURL
		tryURL(tempURL)	

print "Entering insert loop"
for r in insertResults3 : 
	url = 'http://www.' + r
	url = stringAndStrip(url)
	for tld in tlds:
		tempURL = url + '.' + tld
		print 'Trying: ' + tempURL
		tryURL(tempURL)		

print "Entering sub loop"
for r in subResults3 : 
	url = 'http://www.' + r
	url = stringAndStrip(url)
	for tld in tlds:
		tempURL = url + '.' + tld
		print 'Trying: ' + tempURL
		tryURL(tempURL)	

print "Entering reverse loop"
for r in reverseResults3 : 
	url = 'http://www.' + r
	url = stringAndStrip(url)
	for tld in tlds:
		tempURL = url + '.' + tld
		print 'Trying: ' + tempURL
		tryURL(tempURL)

### CORNER CASES ###
# The following looks for odd domains that I've noticed 
'''
# This looks for 'teamfranklin'
url = 'http://www.team' + fName + '.com'
url = stringAndStrip(url)
print 'Trying: ' + url
tryURL(url)
'''
totalRuntime = time.time() - start_time, "seconds"

###### Write final results to logfile ###########
resultsFile.write("######################################" + "\n")
resultsFile.write("PACscan v1 Scan Results: " + "\n")
resultsFile.write("######################################" + "\n")
resultsFile.write("INPUTS = " + str(PACname) + ", " + str(year) + "\n") 
resultsFile.write("Total runtime was " + str(totalRuntime) + "\n")
resultsFile.write("There were " + str(len(confirmedURLs)) + " positive results." + "\n")
resultsFile.write("There were " + str(len(testedURLs)) + " unique URLs tested." + "\n")
resultsFile.write("-------------------------------------" + "\n")
resultsFile.write("Positive results: " + "\n")
resultsFile.write("-------------------------------------" + "\n")
for url in confirmedURLs:
	resultsFile.write(str(url) + "\n")
resultsFile.write("\n")
resultsFile.write("-------------------------------------" + "\n")
resultsFile.write("EOF " + "\n")
				
###### Print final results to screen ###########			
print "###################################### " + "\n"
print "PACscan v1 Scan Results: " + "\n"
print "###################################### " + "\n"
print "INPUTS" + "\n"
print "PAC name: " + PACname + "\n"
print "Year: " + year + "\n"
print "-------------------------------------" + "\n"
print "Total runtime was " + str(totalRuntime) + "\n"
print "-------------------------------------" + "\n"
print "Positive results: " + "\n"
print "There were " + str(len(confirmedURLs)) + " hits:" + "\n"
print "-------------------------------------" + "\n"
for url in confirmedURLs:
	print url
print "\n"

# Bad things happen if these files are not properly closed
resultsFile.close()
