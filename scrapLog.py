#! /usr/bin/env python3


# Scaps date, authors, affiliations and file changes from a Git Changelog 
#
# 


print ("this is pyhton")

# scraplog save with serialzie
# TODO functions returning NetworkX graphs 
 
import sys
import re 
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import itertools
import argparse

try:
	import cPickle as pickle
except:
	import pickle


import exportLogData
import networkMeasures 


import JISA2015specificAnalysis

print ("Executing " + str(sys.argv)) 

# Global parameters 

networkOutput = "NetworkOutput.file1.CSV"
atributesOutput = "AtributesOutput.file2.CSV"
graphmlOutput= "NetworkFile.graphML"


# Global structures 

# Keeps statistics of the scrappping 
stats = {'nlines': 0, 'nBlocks' :0 , 'nBlocksChagingCode':0, 'nBlocksNotChangingCode':0 , 'nChangedFiles':0}

# Keeps data as inially scrapped [(date, email, affilition), [files changed]]
# The one that can be saved , the only data structure keeping date information 
changeLogData = []

# Will keep agrregated data of authors that changed the same (file,[list of contributors changing it])
agreByFileContributors = {}


# Will keep agregated tuples of authors connecting due to working on a common file [(a-b),file)]

agreByConnWSF = []

# Will keep unique tuples of authors connected due to workin on common file. no repetitions for (a-b),(a-b) or (a-b),(b-a)
# Keeps unique collaborations and connections. [(a,b),(b,c),(a,c)]
uniqueConnections =[]

# Will keep a dictionary author afiliation i.e affiliation[mike@google.com]=google.com
affiliations = {}

# Will keep a dictionary networked author afiliation i.e affiliation[mike@google.com]=google.com
# Drops authors that do not connect with others
networked_affiliations = {}


# For ibm ex
#ibm_email_domains =  ["au1.ibm.com","linux.vnet.ibm.com","br.ibm.com", "zurich.ibm.com", "us.ibm.com" ,"cn.ibm.com","il.ibm.com","de.ibm.com","ca.ibm.com"] 
ibm_email_domains_prefix =  ["au1","linux","br", "zurich", "us" ,"cn","il","de","ca"]

# TOP10 companies in OpenStack
top10= ["rackspace", "nebula", "citrix", "redhat", "ibm", "hp", "cloudscaling", "mirantis" , "vmware" , "canonical", "intel"]


# Are we verbose? 
DEBUG_MODE = 0 

# Are we going to scraplog data? 
 
SAVE_MODE = 0 

# Are we starting with a ready to process stracplog saved previously in SAVE_MODE? 
LOAD_MODE = 0 


# Are we dealing with raw data from a git/svn log ?
RAW_MODE = 0 


def getAffiliationFromEmail(email):
    "gets affiliation from an given email" 

    #print ("getAffiliationFromEmail("+email+")")
    
    affiliation_pattern= re.compile('@(\w[\w\-]+)')
    match = affiliation_pattern.findall(email)


    if match == None or match == []:
        print ("ERROR unable to extract affiliation from email. Wrong email format?")
        print ("match=["+str(match)+"]")
        sys.exit()

    "implement an exception for IBM as their emails come from multiple domains" 
    "au1.ibm.com linux.vnet.ibm.com br.ibm.com zurich.ibm.com us.ibm.com cn.ibm.com il.ibm.com"

    if 'ibm' in email :
        #print ("Warning, ibm affiliation from multiple domains")
        
        if match[0] not in ibm_email_domains_prefix:
            print ("ERROR, ibm affilition from an unknow domain, check ibm_email_domain glob")
            print ("march=["+str(match[0])+"]")
            sys.exit()

        #print ("affiliation(" + email + ")=[ibm]") 
        return "ibm"        

    affiliation= match[0]
    #print ("affiliation(" + email + ")=["+affiliation+"]") 
    return affiliation



# 
# Extract date, nane and email 
# WK Sample line 
# ==Jenkins;jenkins@review.openstack.org;Thu Feb 20 03:56:00 2014 +0000==
# Format obtained by running: $git log --pretty=format:"==%an;%ae;%ad=="  --name-only
# Returned result would be ('Thu Feb 20 03:56:57 2014','Jenkins', 'jenkins@review.openstack.org', 

def getDateEmailAffiliation(line):   	 
    "gets the ==Name;email;date=="
    #print ("	getting name, email, date, affilication from the line["+line+"]")

    name_pattern = re.compile('^\\=\\=(.+);(.+);(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
    match = name_pattern.findall(line)
    
    #print ("match=" + str(match))   
    
    if match == None or match == []:

        ## expeptions handling ## 
        #"==name;email;date== is the most common pattern from a git log"
        #"however some entries are name less taking a different format:"
        atIndex=line.find('@')

        # Exception 1: Developer added name and email to name
        # ==Brad McConnell bmcconne@rackspace.com;;Tue Sep 20 06:50:27 2011 +0000==
        if ';;' in line and ' ' in line[0:atIndex] and '==Launchpad' not in line:
            print ("WARNING exceptional code commit header Exception 1 ")
            print ("LINE number "+str(stats['nlines'])+" ["+ line + "] double ;; <- name and email together on commit header")

            name_pattern = re.compile('^\\=\\=(.*)\ (.+@.+);;(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
            match = name_pattern.findall(line)
            print ("match=["+str(match)+"]")

        # Exception 2: If there is not name in the commit 
        # there is no spaces before the email (@)
        elif  ' ' not in line[0:atIndex] and '==Launchpad' not in line:
                  
            print ("WARNING exceptional code commit header Exception 2 ")
            print ("LINE number "+str(stats['nlines'])+" ["+ line + "] no name, just an email")

            name_pattern = re.compile('^\\=\\=(.+@.+);;(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
            tmpmatch = name_pattern.findall(line)
            
            # Workarround by adding name from the email
            # Warned about this name with name as  name? 
            match = [(line[2:line.find('@')], tmpmatch[0][0], tmpmatch[0][1], tmpmatch[0][2])]
            

        # Exception 3: Launchpad Translations
        # Drop as it is a bot
        #==Launchpad Translations on behalf of nova-core;;Sat Sep 3 05:50:53 2011 +0000
        elif "==Launchpad" in line:
            print ("WARNING exceptional code commit header Exception 3 ")
            print ("LINE number "+str(stats['nlines'])+" ["+ line + "] Lauchpad bot")
            
            name_pattern = re.compile('^\\=\\=(.+);;(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
            tmpmatch = name_pattern.findall(line)

            # Workarround by simpli addign it as a commiter 
            # Warned about this name with name as  Lauchpad_bot!
            match = [("Lauchpad_bot!", "Lauchpad@bot.bot", tmpmatch[0][1])]                                    
            
        # Exception 4: 
        # match=[('Jenkins', 'jenkins@review.openstack.org', 'Thu Jan 30 21:21:23 2014', '+')]
        # 
            

            
        # anything else ERROR with imput or this code
        else: 
            print("Error, unable to extract developer name, email or date from commit block")
            print("Regular expression not captured")
            print("Line=["+line+"]")
            sys.exit()    
    
    
    name=match[0][0]
    #print("name=["+name+"]")
    

    "get the email"
    email=match[0][1]
    #print("email=["+email+"]")    


    # Verify the email pattern 

    email_pattern = re.compile('([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)')
 
    if (email_pattern.search(email)== None):
        print ("WARNING commiter ["+email+"] have an invalidName")
        print ("Adding .com? to the end")
        email+=".com?"
    
    "gets the date"
    date = match[0][2]
    #print("date=["+date+"]")

    affiliation= getAffiliationFromEmail(email)
    
    return (date, email, affiliation)


"return a list of files modified by a commit log"
def findFilesOnBlock(block):
    #print ("finding files on block [" + str(block) + "]" )

    linesWithCode = []


    for line in block: 
    	#print ("line=["+line+"]")
    	if line == []:
    		break
    	if line == '\n': 
    		break
    	"append the file path (removing the last caracted \n)"	
    	linesWithCode.append(line[:-1]) 
    	stats['nBlocksChagingCode']+=1
    		
     

    #print ("Lines of changed code:")
    #for line in linesWithCode:
    #    print (line) 

    return linesWithCode

    

# processes a bloc of a change log (a developer change)
def scrapBlock( block):
    #print ("Processing [" + str(block) + "]")

    # Check if it is an empty block / change 
    if len(block) == 0:
        print ("ERROR: block / changelog to scrap is empty")
        return False 

    firstLine = block[0] 

    # check if the block starts with a date 
    if not firstLine[0:2] == '==':
        print ("ERROR: Invalid block / not starting with a date ")
        return False 

    daEmAf= getDateEmailAffiliation(block[0])
    
    #print ("")
    #print (daEmAf)


    # What file where affected by the change log
    changedFiles=findFilesOnBlock(block[1:])
    
    # Save it in changeLogData
    #(date, email, affilition), [files changed])
 
	 # GIT log changes that do not change files are irelevant 
    if changedFiles == []:
        return False 

    changeLogData.append((daEmAf, changedFiles))


# filter/slice the changeLogData by data
# Aproach: simply removes blocks wich date does not fit between a startDate and endDate
# Format end date should be  "Oct 11 2014" "MMM DD YYYY"

def filterChangeLogDataByDate ( startDate, endDate ):
    print ("Filtering ChangeLogData for  dates between ["+str(startDate)+"] and ["+str(endDate)+"]")

    # are they dates? 
    
    if type(startDate) != datetime or type(endDate) != datetime : 
        print ("ERROR: invalide data type, not a valid datetime object")
        sys.exit()

    # is channge log empty ? 

    if (len(changeLogData) < 1 ):
        print ("ERROR: changeLogData is empty")
    
    # if end date after start date? 

    res=[]

    for change in changeLogData:
        date = change[0][0]
        email = change[0][1]
        af = change[0][2]
        files = change [1]
        
        #print ("On " + date + " " + email + " from " + af + " worked on the following files:" )

        #print ("ChangeLogDateString=["+date+"]")
        #weekday =date[0:3]
        #month = date[4:7] 
        #day = date[8:10]
        #time = date[11:19]
        #year = date[20:24]

        # Get weekday month day time year  with regular expressions 
        name_pattern = re.compile('(.+)\s(.+)\s(\d+)\s(.+)\s(\d+)')
        match = name_pattern.findall(date)

        #print ("date_ match=["+str(match)+"]")
        
        # If there is no regulae expression match
        if (match == []):
            print ("ERROR: Change log date is not on proper format")
            print ("date_ match=["+str(match)+"]")
            sys.exit()
        
        weekday = match[0][0]
        month = match[0][1]
        day = match[0][2]
        time = match[0][3]
        year = match[0][4]
        
        #print ("ChangeLogDateCapture=["+weekday+ " " + month+ " " + day + " " + time + " " + year + "]")
    	
        #date(year, month, day) --> date object
        day = int (day)
        year= int (year)

        if month == "Jan": 
            month = 1
        elif month == "Feb":
            month = 2
        elif month == "Mar":
            month = 3 
        elif month == "Apr": 
            month = 4
        elif month == "May":
            month = 5
        elif month == "Jun":
            month = 6
        elif month == "Jul":
            month = 7
        elif month == "Aug":
            month = 8
        elif month == "Sep" :
            month = 9 
        elif month == "Oct": 
            month = 10
        elif month == "Nov":
            month = 11
        elif month == "Dec":
            month =12 
        else:
            print ("ERROR invalide month spec: unable to extract date")
            sys.exit()
        changeLogDate = datetime(year, month, day)

        #print("changeLogDate=["+ str(changeLogDate)+"]")
        
        if (changeLogDate < startDate) or changeLogDate > endDate:
            #print("drop change log due date")
            continue  
        else:
            #print("changeLogDate=["+ str(changeLogDate)+"] is between ["+str(startDate)+"] and ["+str(endDate)+"]" )
            res.append(change)
        
    return res

# print the changeLogData data scraped 
def print_changeLogData ():
        global changeLogData 
        

        print ("")
        print ("Printing change log data ... from the earliast change to the oldest change")
        for change in changeLogData:
                date = change[0][0]
                email = change[0][1]
                af = change[0][2]
                files = change [1]

                print ("On " + date + " " + email + " from " + af + " worked on the following files:" )

                for file in files:
                        print ("[" + file + "]")


# save the changeLogData data scraped into a filename  
def save_changeLogData (filename):
	
        global SAVE_MODE
        global changeLogData

        print ("")
        print ("TODO")
        print ('Saving changeLog to file ' +  str(filename) + '')

        if (SAVE_MODE != 1):
                print ("ERROR, not in saving mode")
                sys.exit()
	
        with open(filename, 'wb') as fp:
                pickle.dump(changeLogData, fp)

        print ("DONE changelog saved in ", filename, "NICE :)")
        sys.exit()


# load and return	 the changeLogData data scraped into a filename  
def load_changeLogData (filename):
        print ("")
        print ("TODO")
        print ("Loading changeLog from  file [", filename , "]")
        print ("test")
        with open(filename, 'rb') as fp:
                changeLogData= pickle.load(fp)
        return changeLogData 	


# print the agreByFileContributors agreefation resuting by  agregateByFileItsContributors
def print_agreByFileContributors():
    print ("" )
    print ("Printing files affected by commits on the changelLog  ... and developers resposable for it")
    
    for file in agreByFileContributors:
        fileName = file 
        authorEmails = agreByFileContributors[file]

        if (len(authorEmails)==0):
            print ("ERROR: File without contrubutors !!")
            exit()
        

        print ("The file " + fileName + "was changed by following [" + str(len(authorEmails))+ "]contributors" )
        
        for email in authorEmails:
            print ("[" + email + "]")


# print a list of contributor connected to each other cause they worked on a common files
def print_agreByConnWSF():
    #print (str(agreByConnWSF))

    print ("")
    print("Printing tuples of authors that collaborated + file that they contribute together too") 
    #format more a less like this [(a-b),file)]

    
    for connection in agreByConnWSF:
        contributorsPair = connection[0]
        fileName = connection[1]
        
        print ("Contributors " + str (contributorsPair) + " connected by collaborating on file [" + fileName + "]")


# Agregate by file and its contributors
def agregateByFileItsContributors():
    print ("")
    print ("Agregating data: for each file what are the contributors")
    
    # Agregated  by files and stores agregation in global agreByFileContributors   # 
    # (file,[list of contributors changing it])



    filesVisited = []
    

    for change in changeLogData:
        email = change[0][1]
        files = change [1]

        for file in files:
            # If its a new file 
            if file not in filesVisited:
                filesVisited.append(file)
                agreByFileContributors[file]=[]
                agreByFileContributors[file].append(email)
            # if a file that that was changed before
            elif file in filesVisited:
                # add a new author to the list of authors that changed the file
                if email not in agreByFileContributors[file]:
                    agreByFileContributors[file].append(email)
            else:
                print ("ERROR: list of file not visited") 
                exit()

    stats['nChangedFiles'] = len(filesVisited)

# Get tuple of authors getting connect due to working on a common file 
# [(a-b),file)]
def  getContributorsConnectionsTuplesWSF():
    
    # Interates over the list of files and its contributors 
    print ("")
    print ("Getting tuples of contributors that coded/contributed on the same file")
    

    # Stores contributors connected by working in the same file
    contributorsConnectedbyFile = []

    connectedByFile = []
    
    for change in agreByFileContributors:
        contributors = agreByFileContributors[change]
        for contributor in contributors:
            connectedByFile.append(contributor)
    
        contributorsConnectedbyFile.append((connectedByFile, change)) 
        connectedByFile = []
    
    #Print contributors connect by working in same file i.e. [(['cgarcia@igalia.com', 'jinwoo7.song@samsung.com'], '* Source/cmake/OptionsEfl.cmake:')
    #print (contributorsConnectedbyFile)



    for connection in contributorsConnectedbyFile:
        #print ("interating "+ str(connection))

        contributors=  connection[0]
        files =  connection[1]
        
        if len(contributors) == 0:
            print ("ERROR Not file changes can have 0  contributors")
            exit()
        elif len (contributors) == 1: 
            "One man file .. no connection"
            #print ("WARNING one man one file")            
        elif len(contributors) > 1:
            "add all combinations of contributors to global agreByConnWSF "
            for connection in itertools.combinations(contributors,2):
                agreByConnWSF.append((connection, files))


# Get a list of unique tubles of developers that collaborate. List of tubles with linked nodes. 
def getUniqueConnectionsTuplesList(tuplesListWithFile):    
    
    # verify arguments data
    ## verify tuplesListWithFile 
    
    if type(tuplesListWithFile) != list :
        print ("\tERROR collaboration tuplesList is not a list !!")
        exit()
    if len(tuplesListWithFile) < 1 :
        print ("\tERROR collaboration tuplesList is empty !!")
        exit()

    seen = {}

    
    for connection in tuplesListWithFile:
        ((author1, author2), fileName ) = connection

        #Do not consider if author1 or author2 been already connected 1->2 or 2-< 1 
        if (author1,author2) and (author2,author1) not in seen:
            seen[(author1,author2)]= True

    return list(seen.keys())
    


# Pring unique connections - lust of tuples [(a,b),(b.c)]
def print_unique_connections():
    print ("\nPrinting author unique collaborations (straps repeated collaborations):\n ")

    if len(uniqueConnections) < 1:
        print ("Error, there are no unique connections between developers that should be printed")
        exit()

    print ("\t------/------\n")
    for (dev1,dev2)  in  uniqueConnections:
        print ("\t" + dev1 + " collaborated  with " + dev2)
    print ("\t TOTAL number of unique collaborations =[" + str(len(uniqueConnections)) +"]")
    print ("\t------/------\n")


# Get the affiliations of all authors commiting code 
# Author emails is its unique identifier
def getAffiliations():
    print ("Getting author affiliations from their unique email in changeLogData")
    for change in changeLogData:
        email = change[0][1]
        affiliations[email]= getAffiliationFromEmail(email)

    print ("Getting networked-author affiliations from their unique email in changeLogData")
    for connection in agreByConnWSF:
        contributorsPair = connection[0]
        fileName = connection[1]

        (contr1, contr2 ) = contributorsPair
        networked_affiliations [contr1] =  getAffiliationFromEmail(contr1)
        networked_affiliations [contr2] =  getAffiliationFromEmail(contr2)
        

# Pring the affiliation of each author 
def print_Affiliations():
    print ("\nPrinting author affiliations:\n ")
    for author  in  affiliations:
        print ("\t" + author + " is affiliatied with " + affiliations[author])

    print ("\nPrinting network-author affiliations:\n ")
    for author  in  networked_affiliations:
        print ("\t" + author + " is affiliatied with " + affiliations[author])

# Reprocess all variables from changeLogData
def reprocess():
    
    print ("\n Reprocessing changeLogData")
    
    global agreByFileContributors
    global agreByConnWSF
    global affiliations
    global networked_affiliations
    global uniqueConnections

    agreByFileContributors = {}
    agreByConnWSF = []
    affiliations = {}
    networked_affiliations = {}


    # Reprocess with the new changeLogData
    agregateByFileItsContributors()
    getContributorsConnectionsTuplesWSF()
    uniqueConnections= getUniqueConnectionsTuplesList(agreByConnWSF)
    getAffiliations() 


## MAIN 

def main():
        
        global changeLogData
        global agreByFileContributors
        global agreByConnWSF
        global affiliations
        global networked_affiliations
        global uniqueConnections

        global SAVE_MODE
        global RAW_MODE
        global LOAD_MODE
        global DEBUG_MODE

        ## Process the arguments 
        # -s for serialized save (already provessed changeLog)
        # -r for extrating raw changelog git log

        parser = argparse.ArgumentParser(description='Scrap some chagelog to create networks/graphs for research purpses')
        parser.add_argument('-l','--lser',action='store', type=str, help='loads and processes an serialized changelog')
        parser.add_argument('-r','--raw', action='store', type=str, help='processes from a raw git changelog')
        parser.add_argument('-s','--sser',action='store', type=str, help='processses from a raw git changelog and saves it into a serialized changelog. Requires -r for imput')
        parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true") 

        args = parser.parse_args()

        if args.verbose:
                print("verbosity turned on")
                DEBUG_MODE=1

        if args.lser:
                print ("loanding and processing [lser=",args.lser,"]")
                print ("not implmented yet")
                LOAD_MODE=1 
                RAW_MODE=0
                SAVE_MODE=0
        elif args.sser and args.raw:
                print ("processing [raw=",args.raw,"]", " and saving [sser=", args.sser, "]")
                SAVE_MODE=1
                RAW_MODE=1
                LOAD_MODE=0 
        elif args.raw:
                RAW_MODE=1
                LOAD_MODE=0
                SAVE_MODE=0
                print ("processing [raw=",args.raw,"]")
        else: 
                print ("unrecognized argumets ... see --help")
                sys.exit()

        if RAW_MODE == 1:
                ##  if we are not in load mode, we need to strap the log	
                print ("Scrapping changeLog from ", args.raw )
                t0 = datetime.now()
                print ("STARTING the scrap of changeLog file " + args.raw + " on " +  str(t0))


                ## Opening the files 

                workfile = args.raw

                f = open(workfile, 'r')


                ## Read line by line 
                ## Keep also the stats
                ## Detect blocks ... process them


                ## Will save a commit block lines : From == to next ==


   

                lines = f.readlines()


                # Break everything in blocks and grab the data in ChangLogData 

                for line in lines:
                    #print("reading line [" + line +"]")

                    # Ignore empty lines
                    if line == "\n":
                        continue 

                    # Updates the count of number of lines in the file
                    stats['nlines']+=1


                    # if starts with '==' we have a new commit-block  
                    if line[0:2] == '==': 
                        # Process last temporay block and the cleans it 
                        if (stats['nBlocks'] != 0) :
                            scrapBlock(tmpBlock)
                        tmpBlock = []
                        tmpBlock.append(line)

                        # Updates the could of change log blocks 
                        stats['nBlocks']+=1
                        continue 
                    # then, eithier is a file or an error
                    elif not line[0:2] == '==':
                        # must be a file path 
                        # having a / a . or stenlen bigger than 5
                        if '.' in line or '/' in line or len(line)>=5:
                            tmpBlock.append(line)
                            continue
                        else:
                            print ("ERROR: not a file path. Commit blocs not starting with == must be file paths") 
                            print ("ERROR processing line ["+str(stats['nlines'])+"]"+ "line=["+line+"]")
                            sys.exit()
                    else:
                        print ("ERROR: Something wrong with the changeLog blocks L 107") 
                        sys.exit()
                        break


        if (RAW_MODE == 1):
                print ("\n:)1st SUCESS Data scraped from changlog files (stored in ChangeLogData data structure)")
                #print_changeLogData()
        

        elif (LOAD_MODE == 1):	
                changeLogData = load_changeLogData(args.lser) 
                print ("1st SUCESS Change log loaded from ", args.lser, " ")

                if len(changeLogData) < 1:
                        print ("to small loaded change log, len <1" )
                        sys.exit()
                
                #print_changeLogData()
        
        else:
                print ("ERROR: In what mode are we afer all= No SAVE,LOAD or RAW")
                sys.exit()


        if (SAVE_MODE == 1):
                print ("Saving file")
                save_changeLogData(args.sser)



        
        # Agregate by file ... 

        agregateByFileItsContributors()
        print ("\n:)2nd SUCESS2 Data agregated by files and its contributors")
        ##print_agreByFileContributors()


        # agreate list of authors that worked on the each files

        getContributorsConnectionsTuplesWSF()
        print ("\n:) 3rd SUCESS tubles of authors that collaborated (coded in the same source code file) were generated")
        #print_agreByConnWSF()


        # agreate an list of authors that worked on the each files (do not repeat author tuples)
        # For getting unique edges/collaborations (do not include repetitions of the same collaborations)
        uniqueConnections= getUniqueConnectionsTuplesList(agreByConnWSF)
        print ("\n:) 4rd SUCESS unique authors that collaborated tuples (coded in the same source code file) were generated")
        #print_unique_connections()



        # for every author, get its affiliation. result will be saved in the  affiliation global dictionart
        getAffiliations() 
        ##print_Affiliations()

        print ("\n:) 5rd SUCESS got author -> affiliation dictionary")


        #### UCI NET format #### 
        #### Used for WebKit SIGMISCPT paper #### 
        # Export to data files to Ucitnet format 
        ## Both networkOutput and atributesOutput are global atributes defined on the header


        #exportLogData.createNetworkFileCSV(agreByConnSF, networkOutput)
        #exportLogData.createAtributesFileCSV(changeLogData, atributesOutput )
        #print ("\n:) UciNet export SUCESS exported UCInet network to file:"+networkOutput+" and its attributes to file:"+atributesOutput)

        # GRAPH ML#

        # Create an GraphML file 

        #exportLogData.createGraphML(uniqueConnections,networked_affiliations, graphmlOutput)
        #print ("\n:) GRAPHML export SUCESS exported GraphML network to file:"+graphmlOutput)

        #print ("\t\n:) GRAPHML export Number of nodes/authors = " + str(len(affiliations)))
        #print ("\t\n:) GRAPHML export Number of networked nodes/authors = " + str(len(networked_affiliations)))

        #print ("\t\n:) GRAPHML export Number of nodes/atribute/affiliations  = " + str(networkMeasures.getNumberOfAffiliations(affiliations)))
        #print ("\t\n:) GRAPHML export Number of networked nodes/atribute/affiliations  = " + str(networkMeasures.getNumberOfAffiliations(networked_affiliations)))
        #print ("\t\n:) GRAPHML export Number of edges/collaborations (include repetitions of the same collaboration) = " + str(networkMeasures.getNumberOfEdges(agreByConnWSF)))

        #print ("\t\n:) GRAPHML export Number of unique edges/collaborations (do not include repetitions of the same collaborations) = " + str(networkMeasures.getNumberOfUniqueEdges(agreByConnWSF)))

        #print ("\t\n:) GRAPHML export Number of unique edges/collaborations (do not include repetitions of the same collaborations) = " + str(len(uniqueConnections)))

        # Create an graphML file filtered by company
        # In this case_ red_hat,enovance and intel
        # Others are ignored, not grouped 
        #exportLogData.createGraphML_filterByAffiliation(uniqueConnections,networked_affiliations, "FilteredByCompanies"+ graphmlOutput , ["red_hat","enovance", "intel", "ibm", "hp","mirantis","nebula","vmware" ])

        print ("\n")

        sizeOriginalChangeLogData = len(changeLogData)

        # Filter changeLogByDate
        #changeLogData=filterChangeLogDataByDate (datetime(2014,1,1), datetime (2014,6,1))

        # Filter nothing  
        #changeLogData=filterChangeLogDataByDate (datetime(1900,1,1), datetime (2020,1,1))


        # Filter changeLogData for dates between Xmas and valentines 
        # FOR TESTING PURPOSES ONLY

        #print "Number of edges overall[", len(uniqueConnections), "]"
        #XmasDate=datetime(2012,12,15)
        #valentinesDate=datetime(2014,2,14)
        #changeLogData=filterChangeLogDataByDate (datetime(2014,1,1), datetime (2014,6,1))
        #reprocess()
        #print "Number of edges between Xmas and Fall[", len(uniqueConnections), "]"

        print ("\nSegmenting by release \n\
        0 Icehouse released Apr 17, 2014 \n\
        1 Havana  released Oct 17, 2013 \n\
        2 Grizzly released Apr 4, 2013 \n\
        3 Folsom  released Sep 27, 2012 \n\
        4 Essex released Apr 5, 2012 \n\
        5 Diablo released Sep 22, 2011 \n\
        6 Cactus released Apr 15, 2011 \n\
        7 Bexar released Feb 3, 2011  \n\
        8 Austin released Oct 21, 2010\n")

        releases = []


        releases.append(("Icehouse",datetime (2014, 4, 17)))
        releases.append(("Havana", datetime (2013,10,17)))
        releases.append(("Grizzly",datetime (2013,4,4)))
        releases.append(("Folsom", datetime (2012,9,27)))
        releases.append(("Essex",datetime (2012,4,5)))
        releases.append(("Diablo",datetime (2011,9,22)))
        releases.append(("Cactus",datetime (2011,4,15)))
        releases.append(("Bexar",datetime (2011,2,3)))
        releases.append(("Austin",datetime (2010,10,21)))

        tmpBkupLogData = changeLogData

        # Creates logitudinal network segments for open-stack 
        #for i in range (len(releases)-1):
        #    (release_name, release_date) = releases[i]
        #    prior_release_date= releases[i+1][1]
        #    print ("\t --- Generating grapth["+ release_name+"]" + "from ["+  str(prior_release_date) +"] and rel on [" + str(release_date) + "]\n")
        #    print ("\t --- Filtering change log data for [" + str(prior_release_date)+ "] <--> ["+ str(release_date)+"]")
        #    changeLogData=filterChangeLogDataByDate (prior_release_date,release_date)
        #    reprocess() 
        #    print("\t --- Filtering by date is done. [" + str (sizeOriginalChangeLogData-len(changeLogData)) +"] changeLogs removed due their change date")
        #    exportLogData.createGraphML_filterByAffiliation(uniqueConnections,networked_affiliations, release_name + graphmlOutput , top10)
        #    print("\t --- Network for " + release_name+ " release created at " + release_name + graphmlOutput + " for " + str(top10) + "\n")
        #    changeLogData = tmpBkupLogData


        # Get the number of edges betwen releases i and i+1 


        nodesiip1 = []
        nodesiip1Top10 = [] 
        edgesiip1 = []
        edgesiip1Top10 = []
        
        for i in range (len(releases)-1):
                (release_name, release_date) = releases[i]
                prior_release_date= releases[i+1][1]
                print ("\t --- Filtering change log data for [" + str(prior_release_date)+ "] <--> ["+ str(release_date)+"]")
                changeLogData=filterChangeLogDataByDate (prior_release_date,release_date)
                reprocess() 
                print("\t --- Filtering by date is done. [" + str (sizeOriginalChangeLogData-len(changeLogData)) +"] changeLogs removed due their change date")

                nnodes= len(JISA2015specificAnalysis.getNodesBetweenDatesInConnList(uniqueConnections))
                nnodestop10 = len(JISA2015specificAnalysis.getNodesBetweenDates4SelectedFirmsDatesInConnList(uniqueConnections, networked_affiliations, top10))
                nedges =  len(uniqueConnections)
                nedgestop10 = len(JISA2015specificAnalysis.getConnectionsAmongTop10Only(uniqueConnections,networked_affiliations, top10))

                print ("Number of nodes between[", str(prior_release_date), "] <--> [", str(release_date), "] = ",nnodes )
                print ("Number of nodes (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodestop10  )

                print ("Number of edges between[", str(prior_release_date), "] <--> [", str(release_date), "] = ",nedges, ";"	)
                print ("Number of edges (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ",nedgestop10, ";"	)
                
                nodesiip1.append(nnodes)
                nodesiip1Top10.append(nnodestop10)
                edgesiip1.append(nedges)
                edgesiip1Top10.append(nedgestop10)
                
                changeLogData = tmpBkupLogData

                # for debug only 
                # print the edges among top10 for first release
                #print "pringing edged for reease", release_name , ":"  
                #top10con = getConnectionsAmongTop10Only(uniqueConnections)
                #for edge in top10con:	
                #	(a,b) = edge 
                #	if top10con.count(edge) != 1:
                #		print "ERROR:Not a single edge:"
                #		print "top10con.count(edge)=[", top10con.count(edge),"] --> repeated edges"
                #		print "edge in question:", edge 
                #		sys.exit()  
                #	if (b,a) in top10con: 
                #		print "ERROR:Not a single edge:"
                #		print "top10con.count(edge)=[", top10con.count((b,a)),"] --> repeated edges (inverse relationship already accounted)"
                #		print "edge in question:", edge, " and its inverse " , (b,a)
                #		sys.exit()
                #
                #sys.exit()

                


        # Get the number of nodes and edges betwen releases i-1month and i+1 
        nodesim1ip1 = []
        nodesim1ip1Top10 = []
        edgesim1ip1 = []
        edgesim1ip1Top10 = []

        releasesm1 = []
        for release in releases:
                (releasename,date ) = release  
                
                # for 4 weeks / 1 month  
                # releasesm1.append((releasename, date - relativedelta(months=1)))
                
                # for 3 weeks 
                #releasesm1.append((releasename, date - relativedelta(weeks=3)))

                # for 2 weeks 
                #releasesm1.append((releasename, date - relativedelta(weeks=2)))
                
                # for 1 week 
                releasesm1.append((releasename, date - relativedelta(weeks=1)))
                
        # Get the number of edges betwen releases i and i+1 
        for i in range (len(releasesm1)-1):
                (release_name, release_date) = releases[i]
                prior_release_date= releasesm1[i+1][1]
                print ("\t --- Filtering change log data for [" + str(prior_release_date)+ "] <--> ["+ str(release_date)+"]")
                changeLogData=filterChangeLogDataByDate (prior_release_date,release_date)
                reprocess() 
                print("\t --- Filtering by date is done. [" + str (sizeOriginalChangeLogData-len(changeLogData)) +"] changeLogs removed due their change date")

                nnodes= len(JISA2015specificAnalysis.getNodesBetweenDatesInConnList(uniqueConnections))
                nnodestop10 = len(JISA2015specificAnalysis.getNodesBetweenDates4SelectedFirmsDatesInConnList(uniqueConnections, networked_affiliations, top10))
               
                nedges=len(uniqueConnections) 
                nedgestop10= len(JISA2015specificAnalysis.getConnectionsAmongTop10Only(uniqueConnections,networked_affiliations, top10))

                print ("Number of nodes between[", str(prior_release_date), "] <--> [", str(release_date), "] = ",nnodes )
                print ("Number of nodes (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodestop10 )
                
                print ("Number of edges between[", str(prior_release_date), "] <--> [", str(release_date), "] = ",nedges, ";"	)
                print ("Number of edges (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ",nedgestop10, ";")
                
                nodesim1ip1.append(nnodes) 
                nodesim1ip1Top10.append(nnodestop10) 
                edgesim1ip1.append(nedges)
                edgesim1ip1Top10.append(nedgestop10)	
                changeLogData = tmpBkupLogData

        # print releases name 
        # Not that they are in reverse cronological order, therefore ::-1
        rname = []
        for r in releases:
                (name, nc) = r  
                rname.append(name + ";")
        print ("rname",rname[::-1])


        # For all nodes 
        print ("\t ALL NODES ")
        
        print ("nodesiip1" , nodesiip1[::-1] )
        print ("nodesiim1p1" , nodesim1ip1[::-1])
        print ("diff capture nodes less 1 month", map(int.__sub__, nodesiip1, nodesim1ip1)[::-1])
        print (" % captured nodes less 1 month", map(float.__div__, [float(i) for i in nodesiip1], [float(i) for i in nodesim1ip1])[::-1])

        print ("edgesiip1", edgesiip1[::-1])        
        print ("edgesim1ip1", edgesim1ip1[::-1])
        print ("diff edges less 1 month", map(int.__sub__, edgesiip1, edgesim1ip1)[::-1])
        print ("% captured edges less 1 month", map(float.__div__, [float(i) for i in edgesiip1], [float(i) for i in edgesim1ip1])[::-1])

        # For top 10 onlys
        print ("\t TOP 10 NODES ")

        print ("nodesiip1Top10",  nodesiip1Top10[::-1])
        print ("nodesim1ip1Top10", nodesim1ip1Top10[::-1])
        print ("diff nodes top10 less 1 month", map(int.__sub__, nodesiip1Top10, nodesim1ip1Top10)[::-1])
        print ("% captured nodes less 1 month", map(float.__div__, [float(i) for i in nodesiip1Top10], [float(i) for i in nodesim1ip1Top10])[::-1])
        
        print ("dgesiip1Top10", edgesiip1Top10[::-1])
        print ("dgesim1ip1Top10", edgesim1ip1Top10[::-1])
        print ("iff edfes top10 less 1 month", map(int.__sub__, edgesiip1Top10, edgesim1ip1Top10)[::-1])
        print ("% captured edges less 1 month", map(float.__div__, [float(i) for i in edgesiip1Top10], [float(i) for i in edgesim1ip1Top10])[::-1])


        print ("")
        print ("FINNISHED " + str(datetime.now()))
        
        if (LOAD_MODE != 1):
                print ("TOTAL TIME " + str(datetime.now() - t0))

        # Ending stats

        print ("Number of analized lines [" +  str(stats['nlines']) + "]")
        print ("Number of analized changelog blocks [" +  str(stats['nBlocks']) + "]")
        print ("Number of analized changelog blocks changing code files [" +  str(stats['nBlocksChagingCode']) + "?]")
        print ("Number of analized changelog blocks not changing code files (i.e. testCases)[" +  str(stats['nBlocksNotChangingCode']) + "?]")
        print ("Number of files affected by the commits reported by change log[" +  str(stats['nChangedFiles']) + "]")

if __name__ == "__main__":
    main()

#! /usr/bin/env python3


# Scaps date, authors, affiliations and file changes from WebKit SVN Changelog
#
#


import networkMeasures
import re
import JISA2015specificAnalysis
import exportLogData
import argparse
import itertools
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import sys
print("this is pyhton")

# scraplog save with serialzie
# TODO functions returning NetworkX graphs


try:
    import cPickle as pickle
except:
    import pickle


print("Executing " + str(sys.argv))

# Global parameters

networkOutput = "NetworkOutput.file1.CSV"
atributesOutput = "AtributesOutput.file2.CSV"
graphmlOutput = "NetworkFile.graphML"


# Global structures

# Keeps statistics of the scrappping
stats = {'nlines': 0, 'nBlocks': 0, 'nBlocksChagingCode': 0,
         'nBlocksNotChangingCode': 0, 'nChangedFiles': 0}

# Keeps data as inially scrapped [(date, email, affilition), [files changed]]
# The one that can be saved , the only data structure keeping date information
changeLogData = []

# Will keep agrregated data of authors that changed the same (file,[list of contributors changing it])
agreByFileContributors = {}


# Will keep agregated tuples of authors connecting due to working on a common file [(a-b),file)]

agreByConnWSF = []

# Will keep unique tuples of authors connected due to workin on common file. no repetitions for (a-b),(a-b) or (a-b),(b-a)
# Keeps unique collaborations and connections. [(a,b),(b,c),(a,c)]
uniqueConnections = []

# Will keep a dictionary author afiliation i.e affiliation[mike@google.com]=google.com
affiliations = {}

# Will keep a dictionary networked author afiliation i.e affiliation[mike@google.com]=google.com
# Drops authors that do not connect with others
networked_affiliations = {}


# For ibm ex
# ibm_email_domains =  ["au1.ibm.com","linux.vnet.ibm.com","br.ibm.com", "zurich.ibm.com", "us.ibm.com" ,"cn.ibm.com","il.ibm.com","de.ibm.com","ca.ibm.com"]
ibm_email_domains_prefix = ["au1", "linux",
                            "br", "zurich", "us", "cn", "il", "de", "ca"]

# TOP10 companies in OpenStack
top10 = ["rackspace", "nebula", "citrix", "redhat", "ibm", "hp",
         "cloudscaling", "mirantis", "vmware", "canonical", "intel"]


# Are we verbose?
DEBUG_MODE = 0

# Are we going to scraplog data?

SAVE_MODE = 0

# Are we starting with a ready to process stracplog saved previously in SAVE_MODE?
LOAD_MODE = 0


# Are we dealing with raw data from a git/svn log ?
RAW_MODE = 0


def getAffiliationFromEmail(email):
    "gets affiliation from an given email"

    # print ("getAffiliationFromEmail("+email+")")

    affiliation_pattern = re.compile('@(\w[\w\-]+)')
    match = affiliation_pattern.findall(email)

    if match == None or match == []:
        print("ERROR unable to extract affiliation from email. Wrong email format?")
        print("match=["+str(match)+"]")
        sys.exit()

    "implement an exception for IBM as their emails come from multiple domains"
    "au1.ibm.com linux.vnet.ibm.com br.ibm.com zurich.ibm.com us.ibm.com cn.ibm.com il.ibm.com"

    if 'ibm' in email:
        # print ("Warning, ibm affiliation from multiple domains")

        if match[0] not in ibm_email_domains_prefix:
            print(
                "ERROR, ibm affilition from an unknow domain, check ibm_email_domain glob")
            print("march=["+str(match[0])+"]")
            sys.exit()

        # print ("affiliation(" + email + ")=[ibm]")
        return "ibm"

    affiliation = match[0]
    # print ("affiliation(" + email + ")=["+affiliation+"]")
    return affiliation


#
# Extract date, nane and email
# WK Sample line
# ==Jenkins;jenkins@review.openstack.org;Thu Feb 20 03:56:00 2014 +0000==
# Format obtained by running: $git log --pretty=format:"==%an;%ae;%ad=="  --name-only
# Returned result would be ('Thu Feb 20 03:56:57 2014','Jenkins', 'jenkins@review.openstack.org',

def getDateEmailAffiliation(line):
    "gets the ==Name;email;date=="
    # print ("	getting name, email, date, affilication from the line["+line+"]")

    name_pattern = re.compile(
        '^\\=\\=(.+);(.+);(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
    match = name_pattern.findall(line)

    # print ("match=" + str(match))

    if match == None or match == []:

        ## expeptions handling ##
        # "==name;email;date== is the most common pattern from a git log"
        # "however some entries are name less taking a different format:"
        atIndex = line.find('@')

        # Exception 1: Developer added name and email to name
        # ==Brad McConnell bmcconne@rackspace.com;;Tue Sep 20 06:50:27 2011 +0000==
        if ';;' in line and ' ' in line[0:atIndex] and '==Launchpad' not in line:
            print("WARNING exceptional code commit header Exception 1 ")
            print("LINE number "+str(stats['nlines'])+" [" + line +
                  "] double ;; <- name and email together on commit header")

            name_pattern = re.compile(
                '^\\=\\=(.*)\ (.+@.+);;(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
            match = name_pattern.findall(line)
            print("match=["+str(match)+"]")

        # Exception 2: If there is not name in the commit
        # there is no spaces before the email (@)
        elif ' ' not in line[0:atIndex] and '==Launchpad' not in line:

            print("WARNING exceptional code commit header Exception 2 ")
            print("LINE number "+str(stats['nlines']) +
                  " [" + line + "] no name, just an email")

            name_pattern = re.compile(
                '^\\=\\=(.+@.+);;(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
            tmpmatch = name_pattern.findall(line)

            # Workarround by adding name from the email
            # Warned about this name with name as  name?
            match = [(line[2:line.find('@')], tmpmatch[0]
                      [0], tmpmatch[0][1], tmpmatch[0][2])]

        # Exception 3: Launchpad Translations
        # Drop as it is a bot
        # ==Launchpad Translations on behalf of nova-core;;Sat Sep 3 05:50:53 2011 +0000
        elif "==Launchpad" in line:
            print("WARNING exceptional code commit header Exception 3 ")
            print("LINE number " +
                  str(stats['nlines'])+" [" + line + "] Lauchpad bot")

            name_pattern = re.compile(
                '^\\=\\=(.+);;(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
            tmpmatch = name_pattern.findall(line)

            # Workarround by simpli addign it as a commiter
            # Warned about this name with name as  Lauchpad_bot!
            match = [("Lauchpad_bot!", "Lauchpad@bot.bot", tmpmatch[0][1])]

        # Exception 4:
        # match=[('Jenkins', 'jenkins@review.openstack.org', 'Thu Jan 30 21:21:23 2014', '+')]
        #

        # anything else ERROR with imput or this code
        else:
            print(
                "Error, unable to extract developer name, email or date from commit block")
            print("Regular expression not captured")
            print("Line=["+line+"]")
            sys.exit()

    name = match[0][0]
    # print("name=["+name+"]")

    "get the email"
    email = match[0][1]
    # print("email=["+email+"]")

    # Verify the email pattern

    email_pattern = re.compile('([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)')

    if (email_pattern.search(email) == None):
        print("WARNING commiter ["+email+"] have an invalidName")
        print("Adding .com? to the end")
        email += ".com?"

    "gets the date"
    date = match[0][2]
    # print("date=["+date+"]")

    affiliation = getAffiliationFromEmail(email)

    return (date, email, affiliation)


"return a list of files modified by a commit log"


def findFilesOnBlock(block):
    # print ("finding files on block [" + str(block) + "]" )

    linesWithCode = []

    for line in block:
        # print ("line=["+line+"]")
        if line == []:
            break
        if line == '\n':
            break
        "append the file path (removing the last caracted \n)"
        linesWithCode.append(line[:-1])
        stats['nBlocksChagingCode'] += 1

    # print ("Lines of changed code:")
    # for line in linesWithCode:
    #    print (line)

    return linesWithCode


# processes a bloc of a change log (a developer change)
def scrapBlock(block):
    # print ("Processing [" + str(block) + "]")

    # Check if it is an empty block / change
    if len(block) == 0:
        print("ERROR: block / changelog to scrap is empty")
        return False

    firstLine = block[0]

    # check if the block starts with a date
    if not firstLine[0:2] == '==':
        print("ERROR: Invalid block / not starting with a date ")
        return False

    daEmAf = getDateEmailAffiliation(block[0])

    # print ("")
    # print (daEmAf)

    # What file where affected by the change log
    changedFiles = findFilesOnBlock(block[1:])

    # Save it in changeLogData
    # (date, email, affilition), [files changed])

    # GIT log changes that do not change files are irelevant
    if changedFiles == []:
        return False

    changeLogData.append((daEmAf, changedFiles))


# filter/slice the changeLogData by data
# Aproach: simply removes blocks wich date does not fit between a startDate and endDate
# Format end date should be  "Oct 11 2014" "MMM DD YYYY"

def filterChangeLogDataByDate(startDate, endDate):
    print(
        "Filtering ChangeLogData for  dates between ["+str(startDate)+"] and ["+str(endDate)+"]")

    # are they dates?

    if type(startDate) != datetime or type(endDate) != datetime:
        print("ERROR: invalide data type, not a valid datetime object")
        sys.exit()

    # is channge log empty ?

    if (len(changeLogData) < 1):
        print("ERROR: changeLogData is empty")

    # if end date after start date?

    res = []

    for change in changeLogData:
        date = change[0][0]
        email = change[0][1]
        af = change[0][2]
        files = change[1]

        # print ("On " + date + " " + email + " from " + af + " worked on the following files:" )

        # print ("ChangeLogDateString=["+date+"]")
        # weekday =date[0:3]
        # month = date[4:7]
        # day = date[8:10]
        # time = date[11:19]
        # year = date[20:24]

        # Get weekday month day time year  with regular expressions
        name_pattern = re.compile('(.+)\s(.+)\s(\d+)\s(.+)\s(\d+)')
        match = name_pattern.findall(date)

        # print ("date_ match=["+str(match)+"]")

        # If there is no regulae expression match
        if (match == []):
            print("ERROR: Change log date is not on proper format")
            print("date_ match=["+str(match)+"]")
            sys.exit()

        weekday = match[0][0]
        month = match[0][1]
        day = match[0][2]
        time = match[0][3]
        year = match[0][4]

        # print ("ChangeLogDateCapture=["+weekday+ " " + month+ " " + day + " " + time + " " + year + "]")

        # date(year, month, day) --> date object
        day = int(day)
        year = int(year)

        if month == "Jan":
            month = 1
        elif month == "Feb":
            month = 2
        elif month == "Mar":
            month = 3
        elif month == "Apr":
            month = 4
        elif month == "May":
            month = 5
        elif month == "Jun":
            month = 6
        elif month == "Jul":
            month = 7
        elif month == "Aug":
            month = 8
        elif month == "Sep":
            month = 9
        elif month == "Oct":
            month = 10
        elif month == "Nov":
            month = 11
        elif month == "Dec":
            month = 12
        else:
            print("ERROR invalide month spec: unable to extract date")
            sys.exit()
        changeLogDate = datetime(year, month, day)

        # print("changeLogDate=["+ str(changeLogDate)+"]")

        if (changeLogDate < startDate) or changeLogDate > endDate:
            # print("drop change log due date")
            continue
        else:
            # print("changeLogDate=["+ str(changeLogDate)+"] is between ["+str(startDate)+"] and ["+str(endDate)+"]" )
            res.append(change)

    return res

# print the changeLogData data scraped


def print_changeLogData():
    global changeLogData

    print("")
    print("Printing change log data ... from the earliast change to the oldest change")
    for change in changeLogData:
        date = change[0][0]
        email = change[0][1]
        af = change[0][2]
        files = change[1]

        print("On " + date + " " + email + " from " +
              af + " worked on the following files:")

        for file in files:
            print("[" + file + "]")


# save the changeLogData data scraped into a filename
def save_changeLogData(filename):

    global SAVE_MODE
    global changeLogData

    print("")
    print("TODO")
    print('Saving changeLog to file ' + str(filename) + '')

    if (SAVE_MODE != 1):
        print ("ERROR, not in saving mode")
        sys.exit()

    with open(filename, 'wb') as fp:
        pickle.dump(changeLogData, fp)

    print ("DONE changelog saved in ", filename, "NICE :)")
    sys.exit()


# load and return	 the changeLogData data scraped into a filename
def load_changeLogData(filename):
    print ("")
    print ("TODO")
    print ("Loading changeLog from  file [", filename, "]")

    with open(filename, 'rb') as fp:
        changeLogData = pickle.load(fp)

    return changeLogData


# print the agreByFileContributors agreefation resuting by  agregateByFileItsContributors
def print_agreByFileContributors():
    print("")
    print("Printing files affected by commits on the changelLog  ... and developers resposable for it")

    for file in agreByFileContributors:
        fileName = file
        authorEmails = agreByFileContributors[file]

        if (len(authorEmails) == 0):
            print("ERROR: File without contrubutors !!")
            exit()

        print("The file " + fileName +
              "was changed by following [" + str(len(authorEmails)) + "]contributors")

        for email in authorEmails:
            print("[" + email + "]")


# print a list of contributor connected to each other cause they worked on a common files
def print_agreByConnWSF():
    # print (str(agreByConnWSF))

    print("")
    print("Printing tuples of authors that collaborated + file that they contribute together too")
    # format more a less like this [(a-b),file)]

    for connection in agreByConnWSF:
        contributorsPair = connection[0]
        fileName = connection[1]

        print("Contributors " + str(contributorsPair) +
              " connected by collaborating on file [" + fileName + "]")


# Agregate by file and its contributors
def agregateByFileItsContributors():
    print("")
    print("Agregating data: for each file what are the contributors")

    # Agregated  by files and stores agregation in global agreByFileContributors   #
    # (file,[list of contributors changing it])

    filesVisited = []

    for change in changeLogData:
        email = change[0][1]
        files = change[1]

        for file in files:
            # If its a new file
            if file not in filesVisited:
                filesVisited.append(file)
                agreByFileContributors[file] = []
                agreByFileContributors[file].append(email)
            # if a file that that was changed before
            elif file in filesVisited:
                # add a new author to the list of authors that changed the file
                if email not in agreByFileContributors[file]:
                    agreByFileContributors[file].append(email)
            else:
                print("ERROR: list of file not visited")
                exit()

    stats['nChangedFiles'] = len(filesVisited)

# Get tuple of authors getting connect due to working on a common file
# [(a-b),file)]


def getContributorsConnectionsTuplesWSF():

    # Interates over the list of files and its contributors
    print("")
    print("Getting tuples of contributors that coded/contributed on the same file")

    # Stores contributors connected by working in the same file
    contributorsConnectedbyFile = []

    connectedByFile = []

    for change in agreByFileContributors:
        contributors = agreByFileContributors[change]
        for contributor in contributors:
            connectedByFile.append(contributor)

        contributorsConnectedbyFile.append((connectedByFile, change))
        connectedByFile = []

    # Print contributors connect by working in same file i.e. [(['cgarcia@igalia.com', 'jinwoo7.song@samsung.com'], '* Source/cmake/OptionsEfl.cmake:')
    # print (contributorsConnectedbyFile)

    for connection in contributorsConnectedbyFile:
        # print ("interating "+ str(connection))

        contributors = connection[0]
        files = connection[1]

        if len(contributors) == 0:
            print("ERROR Not file changes can have 0  contributors")
            exit()
        elif len(contributors) == 1:
            "One man file .. no connection"
            # print ("WARNING one man one file")
        elif len(contributors) > 1:
            "add all combinations of contributors to global agreByConnWSF "
            for connection in itertools.combinations(contributors, 2):
                agreByConnWSF.append((connection, files))


# Get a list of unique tubles of developers that collaborate. List of tubles with linked nodes.
def getUniqueConnectionsTuplesList(tuplesListWithFile):

    # verify arguments data
    # verify tuplesListWithFile

    if type(tuplesListWithFile) != list:
        print("\tERROR collaboration tuplesList is not a list !!")
        exit()
    if len(tuplesListWithFile) < 1:
        print("\tERROR collaboration tuplesList is empty !!")
        exit()

    seen = {}

    for connection in tuplesListWithFile:
        ((author1, author2), fileName) = connection

        # Do not consider if author1 or author2 been already connected 1->2 or 2-< 1
        if (author1, author2) and (author2, author1) not in seen:
            seen[(author1, author2)] = True

    return list(seen.keys())


# Pring unique connections - lust of tuples [(a,b),(b.c)]
def print_unique_connections():
    print("\nPrinting author unique collaborations (straps repeated collaborations):\n ")

    if len(uniqueConnections) < 1:
        print("Error, there are no unique connections between developers that should be printed")
        exit()

    print("\t------/------\n")
    for (dev1, dev2) in uniqueConnections:
        print("\t" + dev1 + " collaborated  with " + dev2)
    print(
        "\t TOTAL number of unique collaborations =[" + str(len(uniqueConnections)) + "]")
    print("\t------/------\n")


# Get the affiliations of all authors commiting code
# Author emails is its unique identifier
def getAffiliations():
    print("Getting author affiliations from their unique email in changeLogData")
    for change in changeLogData:
        email = change[0][1]
        affiliations[email] = getAffiliationFromEmail(email)

    print("Getting networked-author affiliations from their unique email in changeLogData")
    for connection in agreByConnWSF:
        contributorsPair = connection[0]
        fileName = connection[1]

        (contr1, contr2) = contributorsPair
        networked_affiliations[contr1] = getAffiliationFromEmail(contr1)
        networked_affiliations[contr2] = getAffiliationFromEmail(contr2)


# Pring the affiliation of each author
def print_Affiliations():
    print("\nPrinting author affiliations:\n ")
    for author in affiliations:
        print("\t" + author + " is affiliatied with " + affiliations[author])

    print("\nPrinting network-author affiliations:\n ")
    for author in networked_affiliations:
        print("\t" + author + " is affiliatied with " + affiliations[author])

# Reprocess all variables from changeLogData


def reprocess():

    print("\n Reprocessing changeLogData")

    global agreByFileContributors
    global agreByConnWSF
    global affiliations
    global networked_affiliations
    global uniqueConnections

    agreByFileContributors = {}
    agreByConnWSF = []
    affiliations = {}
    networked_affiliations = {}

    # Reprocess with the new changeLogData
    agregateByFileItsContributors()
    getContributorsConnectionsTuplesWSF()
    uniqueConnections = getUniqueConnectionsTuplesList(agreByConnWSF)
    getAffiliations()


# MAIN

def main():

    global changeLogData
    global agreByFileContributors
    global agreByConnWSF
    global affiliations
    global networked_affiliations
    global uniqueConnections

    global SAVE_MODE
    global RAW_MODE
    global LOAD_MODE
    global DEBUG_MODE

    # Process the arguments
    # -s for serialized save (already provessed changeLog)
    # -r for extrating raw changelog git log

    parser = argparse.ArgumentParser(
        description='Scrap some chagelog to create networks/graphs for research purpses')
    parser.add_argument('-l', '--lser', action='store', type=str,
                        help='loads and processes an serialized changelog')
    parser.add_argument('-r', '--raw', action='store',
                        type=str, help='processes from a raw git changelog')
    parser.add_argument('-s', '--sser', action='store', type=str,
                        help='processses from a raw git changelog and saves it into a serialized changelog. Requires -r for imput')
    parser.add_argument("-v", "--verbose",
                        help="increase output verbosity", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        print("verbosity turned on")
        DEBUG_MODE = 1

    if args.lser:
        print ("loanding and processing [lser=", args.lser, "]")
        print ("not implmented yet")
        LOAD_MODE = 1
        RAW_MODE = 0
        SAVE_MODE = 0
    elif args.sser and args.raw:
        print (" processing [raw=", args.raw, "]", " and saving [sser=", args.sser, "]")
        SAVE_MODE = 1
        RAW_MODE = 1
        LOAD_MODE = 0
    elif args.raw:
        RAW_MODE = 1
        LOAD_MODE = 0
        SAVE_MODE = 0
        print (" processing [raw=", args.raw, "]")
    else:
        print ("unrecognized argumets ... see --help")
        sys.exit()

    if RAW_MODE == 1:
        # if we are not in load mode, we need to strap the log
        print ("Scrapping changeLog from ", args.raw)
        t0 = datetime.now()
        print("STARTING the scrap of changeLog file " +
              args.raw + " on " + str(t0))

        # Opening the files

        workfile = args.raw

        f = open(workfile, 'r')

        # Read line by line
        # Keep also the stats
        # Detect blocks ... process them

        # Will save a commit block lines : From == to next ==

        lines = f.readlines()

        # Break everything in blocks and grab the data in ChangLogData

        for line in lines:
            # print("reading line [" + line +"]")

            # Ignore empty lines
            if line == "\n":
                continue

            # Updates the count of number of lines in the file
            stats['nlines'] += 1

            # if starts with '==' we have a new commit-block
            if line[0:2] == '==':
                # Process last temporay block and the cleans it
                if (stats['nBlocks'] != 0):
                    scrapBlock(tmpBlock)
                tmpBlock = []
                tmpBlock.append(line)

                # Updates the could of change log blocks
                stats['nBlocks'] += 1
                continue
            # then, eithier is a file or an error
            elif not line[0:2] == '==':
                # must be a file path
                # having a / a . or stenlen bigger than 5
                if '.' in line or '/' in line or len(line) >= 5:
                    tmpBlock.append(line)
                    continue
                else:
                    print(
                        "ERROR: not a file path. Commit blocs not starting with == must be file paths")
                    print(
                        "ERROR processing line ["+str(stats['nlines'])+"]" + "line=["+line+"]")
                    sys.exit()
            else:
                print("ERROR: Something wrong with the changeLog blocks L 107")
                sys.exit()
                break

    if (RAW_MODE == 1):
        print("\n:)1st SUCESS Data scraped from changlog files (stored in ChangeLogData data structure)")
        # print_changeLogData()

    elif (LOAD_MODE == 1):
        changeLogData = load_changeLogData(args.lser)
        print ("1st SUCESS Change log loaded from ", args.lser, " ")

        if len(changeLogData) < 1:
            print ("to small loaded change log, len <1")
            sys.exit()

        # print_changeLogData()

    else:
        print ("ERROR: In what mode are we afer all= No SAVE,LOAD or RAW")
        sys.exit()

    if (SAVE_MODE == 1):
        print ("Saving file")
        save_changeLogData(args.sser)

    # Agregate by file ...

    agregateByFileItsContributors()
    print("\n:)2nd SUCESS2 Data agregated by files and its contributors")
    # print_agreByFileContributors()

    # agreate list of authors that worked on the each files

    getContributorsConnectionsTuplesWSF()
    print("\n:) 3rd SUCESS tubles of authors that collaborated (coded in the same source code file) were generated")
    # print_agreByConnWSF()

    # agreate an list of authors that worked on the each files (do not repeat author tuples)
    # For getting unique edges/collaborations (do not include repetitions of the same collaborations)
    uniqueConnections = getUniqueConnectionsTuplesList(agreByConnWSF)
    print("\n:) 4rd SUCESS unique authors that collaborated tuples (coded in the same source code file) were generated")
    # print_unique_connections()

    # for every author, get its affiliation. result will be saved in the  affiliation global dictionart
    getAffiliations()
    # print_Affiliations()

    print("\n:) 5rd SUCESS got author -> affiliation dictionary")

    #### UCI NET format ####
    #### Used for WebKit SIGMISCPT paper ####
    # Export to data files to Ucitnet format
    # Both networkOutput and atributesOutput are global atributes defined on the header

    # exportLogData.createNetworkFileCSV(agreByConnSF, networkOutput)
    # exportLogData.createAtributesFileCSV(changeLogData, atributesOutput )
    # print ("\n:) UciNet export SUCESS exported UCInet network to file:"+networkOutput+" and its attributes to file:"+atributesOutput)

    # GRAPH ML#

    # Create an GraphML file

    # exportLogData.createGraphML(uniqueConnections,networked_affiliations, graphmlOutput)
    # print ("\n:) GRAPHML export SUCESS exported GraphML network to file:"+graphmlOutput)

    # print ("\t\n:) GRAPHML export Number of nodes/authors = " + str(len(affiliations)))
    # print ("\t\n:) GRAPHML export Number of networked nodes/authors = " + str(len(networked_affiliations)))

    # print ("\t\n:) GRAPHML export Number of nodes/atribute/affiliations  = " + str(networkMeasures.getNumberOfAffiliations(affiliations)))
    # print ("\t\n:) GRAPHML export Number of networked nodes/atribute/affiliations  = " + str(networkMeasures.getNumberOfAffiliations(networked_affiliations)))
    # print ("\t\n:) GRAPHML export Number of edges/collaborations (include repetitions of the same collaboration) = " + str(networkMeasures.getNumberOfEdges(agreByConnWSF)))

    # print ("\t\n:) GRAPHML export Number of unique edges/collaborations (do not include repetitions of the same collaborations) = " + str(networkMeasures.getNumberOfUniqueEdges(agreByConnWSF)))

    # print ("\t\n:) GRAPHML export Number of unique edges/collaborations (do not include repetitions of the same collaborations) = " + str(len(uniqueConnections)))

    # Create an graphML file filtered by company
    # In this case_ red_hat,enovance and intel
    # Others are ignored, not grouped
    # exportLogData.createGraphML_filterByAffiliation(uniqueConnections,networked_affiliations, "FilteredByCompanies"+ graphmlOutput , ["red_hat","enovance", "intel", "ibm", "hp","mirantis","nebula","vmware" ])

    print("\n")

    sizeOriginalChangeLogData = len(changeLogData)

    # Filter changeLogByDate
    # changeLogData=filterChangeLogDataByDate (datetime(2014,1,1), datetime (2014,6,1))

    # Filter nothing
    # changeLogData=filterChangeLogDataByDate (datetime(1900,1,1), datetime (2020,1,1))

    # Filter changeLogData for dates between Xmas and valentines
    # FOR TESTING PURPOSES ONLY

    # print "Number of edges overall[", len(uniqueConnections), "]"
    # XmasDate=datetime(2012,12,15)
    # valentinesDate=datetime(2014,2,14)
    # changeLogData=filterChangeLogDataByDate (datetime(2014,1,1), datetime (2014,6,1))
    # reprocess()
    # print "Number of edges between Xmas and Fall[", len(uniqueConnections), "]"

    print("\nSegmenting by release \n\
        0 Icehouse released Apr 17, 2014 \n\
        1 Havana  released Oct 17, 2013 \n\
        2 Grizzly released Apr 4, 2013 \n\
        3 Folsom  released Sep 27, 2012 \n\
        4 Essex released Apr 5, 2012 \n\
        5 Diablo released Sep 22, 2011 \n\
        6 Cactus released Apr 15, 2011 \n\
        7 Bexar released Feb 3, 2011  \n\
        8 Austin released Oct 21, 2010\n")

    releases = []

    releases.append(("Icehouse", datetime(2014, 4, 17)))
    releases.append(("Havana", datetime(2013, 10, 17)))
    releases.append(("Grizzly", datetime(2013, 4, 4)))
    releases.append(("Folsom", datetime(2012, 9, 27)))
    releases.append(("Essex", datetime(2012, 4, 5)))
    releases.append(("Diablo", datetime(2011, 9, 22)))
    releases.append(("Cactus", datetime(2011, 4, 15)))
    releases.append(("Bexar", datetime(2011, 2, 3)))
    releases.append(("Austin", datetime(2010, 10, 21)))

    tmpBkupLogData = changeLogData

    # Creates logitudinal network segments for open-stack
    # for i in range (len(releases)-1):
    #    (release_name, release_date) = releases[i]
    #    prior_release_date= releases[i+1][1]
    #    print ("\t --- Generating grapth["+ release_name+"]" + "from ["+  str(prior_release_date) +"] and rel on [" + str(release_date) + "]\n")
    #    print ("\t --- Filtering change log data for [" + str(prior_release_date)+ "] <--> ["+ str(release_date)+"]")
    #    changeLogData=filterChangeLogDataByDate (prior_release_date,release_date)
    #    reprocess()
    #    print("\t --- Filtering by date is done. [" + str (sizeOriginalChangeLogData-len(changeLogData)) +"] changeLogs removed due their change date")
    #    exportLogData.createGraphML_filterByAffiliation(uniqueConnections,networked_affiliations, release_name + graphmlOutput , top10)
    #    print("\t --- Network for " + release_name+ " release created at " + release_name + graphmlOutput + " for " + str(top10) + "\n")
    #    changeLogData = tmpBkupLogData

    # Get the number of edges betwen releases i and i+1

    nodesiip1 = []
    nodesiip1Top10 = []
    edgesiip1 = []
    edgesiip1Top10 = []

    for i in range(len(releases)-1):
        (release_name, release_date) = releases[i]
        prior_release_date = releases[i+1][1]
        print("\t --- Filtering change log data for [" + str(
            prior_release_date) + "] <--> [" + str(release_date)+"]")
        changeLogData = filterChangeLogDataByDate(
            prior_release_date, release_date)
        reprocess()
        print("\t --- Filtering by date is done. [" + str(sizeOriginalChangeLogData-len(
            changeLogData)) + "] changeLogs removed due their change date")

        nnodes = len(
            JISA2015specificAnalysis.getNodesBetweenDatesInConnList(uniqueConnections))
        nnodestop10 = len(JISA2015specificAnalysis.getNodesBetweenDates4SelectedFirmsDatesInConnList(
            uniqueConnections, networked_affiliations, top10))
        nedges = len(uniqueConnections)
        nedgestop10 = len(JISA2015specificAnalysis.getConnectionsAmongTop10Only(
            uniqueConnections, networked_affiliations, top10))

        print ("Number of nodes between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodes)
        print ("Number of nodes (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodestop10) 

        print ("Number of edges between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nedges, ";")
        print ("Number of edges (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nedgestop10, ";")

        nodesiip1.append(nnodes)
        nodesiip1Top10.append(nnodestop10)
        edgesiip1.append(nedges)
        edgesiip1Top10.append(nedgestop10)

        changeLogData = tmpBkupLogData

        # for debug only
        # print the edges among top10 for first release
        # print "pringing edged for reease", release_name , ":"
        # top10con = getConnectionsAmongTop10Only(uniqueConnections)
        # for edge in top10con:
        # (a,b) = edge
        # if top10con.count(edge) != 1:
        # print "ERROR:Not a single edge:"
        # print "top10con.count(edge)=[", top10con.count(edge),"] --> repeated edges"
        # print "edge in question:", edge
        # sys.exit()
        # if (b,a) in top10con:
        # print "ERROR:Not a single edge:"
        # print "top10con.count(edge)=[", top10con.count((b,a)),"] --> repeated edges (inverse relationship already accounted)"
        # print "edge in question:", edge, " and its inverse " , (b,a)
        # sys.exit()
        #
        # sys.exit()

    # Get the number of nodes and edges betwen releases i-1month and i+1
    nodesim1ip1 = []
    nodesim1ip1Top10 = []
    edgesim1ip1 = []
    edgesim1ip1Top10 = []

    releasesm1 = []
    for release in releases:
        (releasename, date) = release

        # for 4 weeks / 1 month
        # releasesm1.append((releasename, date - relativedelta(months=1)))

        # for 3 weeks
        # releasesm1.append((releasename, date - relativedelta(weeks=3)))

        # for 2 weeks
        # releasesm1.append((releasename, date - relativedelta(weeks=2)))

        # for 1 week
        releasesm1.append((releasename, date - relativedelta(weeks=1)))

    # Get the number of edges betwen releases i and i+1
    for i in range(len(releasesm1)-1):
        (release_name, release_date) = releases[i]
        prior_release_date = releasesm1[i+1][1]
        print("\t --- Filtering change log data for [" + str(
            prior_release_date) + "] <--> [" + str(release_date)+"]")
        changeLogData = filterChangeLogDataByDate(
            prior_release_date, release_date)
        reprocess()
        print("\t --- Filtering by date is done. [" + str(sizeOriginalChangeLogData-len(
            changeLogData)) + "] changeLogs removed due their change date")

        nnodes = len(
            JISA2015specificAnalysis.getNodesBetweenDatesInConnList(uniqueConnections))
        nnodestop10 = len(JISA2015specificAnalysis.getNodesBetweenDates4SelectedFirmsDatesInConnList(
            uniqueConnections, networked_affiliations, top10))

        nedges = len(uniqueConnections)
        nedgestop10 = len(JISA2015specificAnalysis.getConnectionsAmongTop10Only(
            uniqueConnections, networked_affiliations, top10))

        print ("Number of nodes between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodes)
        print ("Number of nodes (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodestop10)

        print ("Number of edges between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nedges, ";")
        print ("Number of edges (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nedgestop10, ";")

        nodesim1ip1.append(nnodes)
        nodesim1ip1Top10.append(nnodestop10)
        edgesim1ip1.append(nedges)
        edgesim1ip1Top10.append(nedgestop10)
        changeLogData = tmpBkupLogData

    # print releases name
    # Not that they are in reverse cronological order, therefore ::-1
    rname = []
    for r in releases:
        (name, nc) = r
        rname.append(name + ";")
    print ("rname", rname[::-1])

    # For all nodes
    print( "\t ALL NODES ")

    print ("nodesiip1", nodesiip1[::-1])
    print ("nodesiim1p1", nodesim1ip1[::-1])
    print ("diff capture nodes less 1 month", map(int.__sub__, nodesiip1, nodesim1ip1)[::-1])
    print ("% captured nodes less 1 month", map(float.__div__, [float(i) for i in nodesiip1], [float(i) for i in nodesim1ip1])[::-1])

    print ("edgesiip1", edgesiip1[::-1])
    print ("edgesim1ip1", edgesim1ip1[::-1])
    print ("diff edges less 1 month", map(int.__sub__, edgesiip1, edgesim1ip1)[::-1])
    print ("% captured edges less 1 month", map(float.__div__, [float(i) for i in edgesiip1], [float(i) for i in edgesim1ip1])[::-1]) 

    # For top 10 onlys
    print ("\t TOP 10 NODES ")

    print ("nodesiip1Top10",  nodesiip1Top10[::-1])
    print ("nodesim1ip1Top10", nodesim1ip1Top10[::-1])
    print ("diff nodes top10 less 1 month", map(int.__sub__, nodesiip1Top10, nodesim1ip1Top10)[::-1])
    print ("% captured nodes less 1 month", map(float.__div__, [float(i) for i in nodesiip1Top10], [float(i) for i in nodesim1ip1Top10])[::-1])

    print ("edgesiip1Top10", edgesiip1Top10[::-1])
    print ("edgesim1ip1Top10", edgesim1ip1Top10[::-1])
    print ("diff edfes top10 less 1 month", map(int.__sub__, edgesiip1Top10, edgesim1ip1Top10)[::-1])
    print ("% captured edges less 1 month", map(float.__div__, [float(i) for i in edgesiip1Top10], [float(i) for i in edgesim1ip1Top10])[::-1])

    print("")
    print("FINNISHED " + str(datetime.now()))

    if (LOAD_MODE != 1):
        print("TOTAL TIME " + str(datetime.now() - t0))

    # Ending stats

    print("Number of analized lines [" + str(stats['nlines']) + "]")
    print(
        "Number of analized changelog blocks [" + str(stats['nBlocks']) + "]")
    print("Number of analized changelog blocks changing code files [" + str(
        stats['nBlocksChagingCode']) + "?]")
    print("Number of analized changelog blocks not changing code files (i.e. testCases)[" + str(
        stats['nBlocksNotChangingCode']) + "?]")
    print("Number of files affected by the commits reported by change log[" + str(
        stats['nChangedFiles']) + "]")


if __name__ == "__main__":
    main()
#! /usr/bin/env python3


# Scaps date, authors, affiliations and file changes from WebKit SVN Changelog
#
#


import re
import networkMeasures
import JISA2015specificAnalysis
import exportLogData
import argparse
import itertools
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import sys
print("this is pyhton")

# scraplog save with serialzie
# TODO functions returning NetworkX graphs


try:
    import cPickle as pickle
except:
    import pickle


print("Executing " + str(sys.argv))

# Global parameters

networkOutput = "NetworkOutput.file1.CSV"
atributesOutput = "AtributesOutput.file2.CSV"
graphmlOutput = "NetworkFile.graphML"


# Global structures

# Keeps statistics of the scrappping
stats = {'nlines': 0, 'nBlocks': 0, 'nBlocksChagingCode': 0,
         'nBlocksNotChangingCode': 0, 'nChangedFiles': 0}

# Keeps data as inially scrapped [(date, email, affilition), [files changed]]
# The one that can be saved , the only data structure keeping date information
changeLogData = []

# Will keep agrregated data of authors that changed the same (file,[list of contributors changing it])
agreByFileContributors = {}


# Will keep agregated tuples of authors connecting due to working on a common file [(a-b),file)]

agreByConnWSF = []

# Will keep unique tuples of authors connected due to workin on common file. no repetitions for (a-b),(a-b) or (a-b),(b-a)
# Keeps unique collaborations and connections. [(a,b),(b,c),(a,c)]
uniqueConnections = []

# Will keep a dictionary author afiliation i.e affiliation[mike@google.com]=google.com
affiliations = {}

# Will keep a dictionary networked author afiliation i.e affiliation[mike@google.com]=google.com
# Drops authors that do not connect with others
networked_affiliations = {}


# For ibm ex
# ibm_email_domains =  ["au1.ibm.com","linux.vnet.ibm.com","br.ibm.com", "zurich.ibm.com", "us.ibm.com" ,"cn.ibm.com","il.ibm.com","de.ibm.com","ca.ibm.com"]
ibm_email_domains_prefix = ["au1", "linux",
                            "br", "zurich", "us", "cn", "il", "de", "ca"]

# TOP10 companies in OpenStack
top10 = ["rackspace", "nebula", "citrix", "redhat", "ibm", "hp",
         "cloudscaling", "mirantis", "vmware", "canonical", "intel"]


# Are we verbose?
DEBUG_MODE = 0

# Are we going to scraplog data?

SAVE_MODE = 0

# Are we starting with a ready to process stracplog saved previously in SAVE_MODE?
LOAD_MODE = 0


# Are we dealing with raw data from a git/svn log ?
RAW_MODE = 0


def getAffiliationFromEmail(email):
    "gets affiliation from an given email"

    # print ("getAffiliationFromEmail("+email+")")

    affiliation_pattern = re.compile('@(\w[\w\-]+)')
    match = affiliation_pattern.findall(email)

    if match == None or match == []:
        print("ERROR unable to extract affiliation from email. Wrong email format?")
        print("match=["+str(match)+"]")
        sys.exit()

    "implement an exception for IBM as their emails come from multiple domains"
    "au1.ibm.com linux.vnet.ibm.com br.ibm.com zurich.ibm.com us.ibm.com cn.ibm.com il.ibm.com"

    if 'ibm' in email:
        # print ("Warning, ibm affiliation from multiple domains")

        if match[0] not in ibm_email_domains_prefix:
            print(
                "ERROR, ibm affilition from an unknow domain, check ibm_email_domain glob")
            print("march=["+str(match[0])+"]")
            sys.exit()

        # print ("affiliation(" + email + ")=[ibm]")
        return "ibm"

    affiliation = match[0]
    # print ("affiliation(" + email + ")=["+affiliation+"]")
    return affiliation


#
# Extract date, nane and email
# WK Sample line
# ==Jenkins;jenkins@review.openstack.org;Thu Feb 20 03:56:00 2014 +0000==
# Format obtained by running: $git log --pretty=format:"==%an;%ae;%ad=="  --name-only
# Returned result would be ('Thu Feb 20 03:56:57 2014','Jenkins', 'jenkins@review.openstack.org',

def getDateEmailAffiliation(line):
    "gets the ==Name;email;date=="
    # print ("	getting name, email, date, affilication from the line["+line+"]")

    name_pattern = re.compile(
        '^\\=\\=(.+);(.+);(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
    match = name_pattern.findall(line)

    # print ("match=" + str(match))

    if match == None or match == []:

        ## expeptions handling ##
        # "==name;email;date== is the most common pattern from a git log"
        # "however some entries are name less taking a different format:"
        atIndex = line.find('@')

        # Exception 1: Developer added name and email to name
        # ==Brad McConnell bmcconne@rackspace.com;;Tue Sep 20 06:50:27 2011 +0000==
        if ';;' in line and ' ' in line[0:atIndex] and '==Launchpad' not in line:
            print("WARNING exceptional code commit header Exception 1 ")
            print("LINE number "+str(stats['nlines'])+" [" + line +
                  "] double ;; <- name and email together on commit header")

            name_pattern = re.compile(
                '^\\=\\=(.*)\ (.+@.+);;(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
            match = name_pattern.findall(line)
            print("match=["+str(match)+"]")

        # Exception 2: If there is not name in the commit
        # there is no spaces before the email (@)
        elif ' ' not in line[0:atIndex] and '==Launchpad' not in line:

            print("WARNING exceptional code commit header Exception 2 ")
            print("LINE number "+str(stats['nlines']) +
                  " [" + line + "] no name, just an email")

            name_pattern = re.compile(
                '^\\=\\=(.+@.+);;(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
            tmpmatch = name_pattern.findall(line)

            # Workarround by adding name from the email
            # Warned about this name with name as  name?
            match = [(line[2:line.find('@')], tmpmatch[0]
                      [0], tmpmatch[0][1], tmpmatch[0][2])]

        # Exception 3: Launchpad Translations
        # Drop as it is a bot
        # ==Launchpad Translations on behalf of nova-core;;Sat Sep 3 05:50:53 2011 +0000
        elif "==Launchpad" in line:
            print("WARNING exceptional code commit header Exception 3 ")
            print("LINE number " +
                  str(stats['nlines'])+" [" + line + "] Lauchpad bot")

            name_pattern = re.compile(
                '^\\=\\=(.+);;(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
            tmpmatch = name_pattern.findall(line)

            # Workarround by simpli addign it as a commiter
            # Warned about this name with name as  Lauchpad_bot!
            match = [("Lauchpad_bot!", "Lauchpad@bot.bot", tmpmatch[0][1])]

        # Exception 4:
        # match=[('Jenkins', 'jenkins@review.openstack.org', 'Thu Jan 30 21:21:23 2014', '+')]
        #

        # anything else ERROR with imput or this code
        else:
            print(
                "Error, unable to extract developer name, email or date from commit block")
            print("Regular expression not captured")
            print("Line=["+line+"]")
            sys.exit()

    name = match[0][0]
    # print("name=["+name+"]")

    "get the email"
    email = match[0][1]
    # print("email=["+email+"]")

    # Verify the email pattern

    email_pattern = re.compile('([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)')

    if (email_pattern.search(email) == None):
        print("WARNING commiter ["+email+"] have an invalidName")
        print("Adding .com? to the end")
        email += ".com?"

    "gets the date"
    date = match[0][2]
    # print("date=["+date+"]")

    affiliation = getAffiliationFromEmail(email)

    return (date, email, affiliation)


"return a list of files modified by a commit log"


def findFilesOnBlock(block):
    # print ("finding files on block [" + str(block) + "]" )

    linesWithCode = []

    for line in block:
        # print ("line=["+line+"]")
        if line == []:
            break
        if line == '\n':
            break
        "append the file path (removing the last caracted \n)"
        linesWithCode.append(line[:-1])
        stats['nBlocksChagingCode'] += 1

    # print ("Lines of changed code:")
    # for line in linesWithCode:
    #    print (line)

    return linesWithCode


# processes a bloc of a change log (a developer change)
def scrapBlock(block):
    # print ("Processing [" + str(block) + "]")

    # Check if it is an empty block / change
    if len(block) == 0:
        print("ERROR: block / changelog to scrap is empty")
        return False

    firstLine = block[0]

    # check if the block starts with a date
    if not firstLine[0:2] == '==':
        print("ERROR: Invalid block / not starting with a date ")
        return False

    daEmAf = getDateEmailAffiliation(block[0])

    # print ("")
    # print (daEmAf)

    # What file where affected by the change log
    changedFiles = findFilesOnBlock(block[1:])

    # Save it in changeLogData
    # (date, email, affilition), [files changed])

    # GIT log changes that do not change files are irelevant
    if changedFiles == []:
        return False

    changeLogData.append((daEmAf, changedFiles))


# filter/slice the changeLogData by data
# Aproach: simply removes blocks wich date does not fit between a startDate and endDate
# Format end date should be  "Oct 11 2014" "MMM DD YYYY"

def filterChangeLogDataByDate(startDate, endDate):
    print(
        "Filtering ChangeLogData for  dates between ["+str(startDate)+"] and ["+str(endDate)+"]")

    # are they dates?

    if type(startDate) != datetime or type(endDate) != datetime:
        print("ERROR: invalide data type, not a valid datetime object")
        sys.exit()

    # is channge log empty ?

    if (len(changeLogData) < 1):
        print("ERROR: changeLogData is empty")

    # if end date after start date?

    res = []

    for change in changeLogData:
        date = change[0][0]
        email = change[0][1]
        af = change[0][2]
        files = change[1]

        # print ("On " + date + " " + email + " from " + af + " worked on the following files:" )

        # print ("ChangeLogDateString=["+date+"]")
        # weekday =date[0:3]
        # month = date[4:7]
        # day = date[8:10]
        # time = date[11:19]
        # year = date[20:24]

        # Get weekday month day time year  with regular expressions
        name_pattern = re.compile('(.+)\s(.+)\s(\d+)\s(.+)\s(\d+)')
        match = name_pattern.findall(date)

        # print ("date_ match=["+str(match)+"]")

        # If there is no regulae expression match
        if (match == []):
            print("ERROR: Change log date is not on proper format")
            print("date_ match=["+str(match)+"]")
            sys.exit()

        weekday = match[0][0]
        month = match[0][1]
        day = match[0][2]
        time = match[0][3]
        year = match[0][4]

        # print ("ChangeLogDateCapture=["+weekday+ " " + month+ " " + day + " " + time + " " + year + "]")

        # date(year, month, day) --> date object
        day = int(day)
        year = int(year)

        if month == "Jan":
            month = 1
        elif month == "Feb":
            month = 2
        elif month == "Mar":
            month = 3
        elif month == "Apr":
            month = 4
        elif month == "May":
            month = 5
        elif month == "Jun":
            month = 6
        elif month == "Jul":
            month = 7
        elif month == "Aug":
            month = 8
        elif month == "Sep":
            month = 9
        elif month == "Oct":
            month = 10
        elif month == "Nov":
            month = 11
        elif month == "Dec":
            month = 12
        else:
            print("ERROR invalide month spec: unable to extract date")
            sys.exit()
        changeLogDate = datetime(year, month, day)

        # print("changeLogDate=["+ str(changeLogDate)+"]")

        if (changeLogDate < startDate) or changeLogDate > endDate:
            # print("drop change log due date")
            continue
        else:
            # print("changeLogDate=["+ str(changeLogDate)+"] is between ["+str(startDate)+"] and ["+str(endDate)+"]" )
            res.append(change)

    return res

# print the changeLogData data scraped


def print_changeLogData():
    global changeLogData

    print("")
    print("Printing change log data ... from the earliast change to the oldest change")
    for change in changeLogData:
        date = change[0][0]
        email = change[0][1]
        af = change[0][2]
        files = change[1]

        print("On " + date + " " + email + " from " +
              af + " worked on the following files:")

        for file in files:
            print("[" + file + "]")


# save the changeLogData data scraped into a filename
def save_changeLogData(filename):

    global SAVE_MODE
    global changeLogData

    print("")
    print("TODO")
    print('Saving changeLog to file ' + str(filename) + '')

    if (SAVE_MODE != 1):
        print ("ERROR, not in saving mode")
        sys.exit()

    with open(filename, 'wb') as fp:
        pickle.dump(changeLogData, fp)

    print ("DONE changelog saved in ", filename, "NICE :)")
    sys.exit()


# load and return	 the changeLogData data scraped into a filename
def load_changeLogData(filename):
    print ("")
    print ("TODO")
    print ("Loading changeLog from  file [", filename, "]")

    with open(filename, 'rb') as fp:
        changeLogData = pickle.load(fp)

    return changeLogData


# print the agreByFileContributors agreefation resuting by  agregateByFileItsContributors
def print_agreByFileContributors():
    print("")
    print("Printing files affected by commits on the changelLog  ... and developers resposable for it")

    for file in agreByFileContributors:
        fileName = file
        authorEmails = agreByFileContributors[file]

        if (len(authorEmails) == 0):
            print("ERROR: File without contrubutors !!")
            exit()

        print("The file " + fileName +
              "was changed by following [" + str(len(authorEmails)) + "]contributors")

        for email in authorEmails:
            print("[" + email + "]")


# print a list of contributor connected to each other cause they worked on a common files
def print_agreByConnWSF():
    # print (str(agreByConnWSF))

    print("")
    print("Printing tuples of authors that collaborated + file that they contribute together too")
    # format more a less like this [(a-b),file)]

    for connection in agreByConnWSF:
        contributorsPair = connection[0]
        fileName = connection[1]

        print("Contributors " + str(contributorsPair) +
              " connected by collaborating on file [" + fileName + "]")


# Agregate by file and its contributors
def agregateByFileItsContributors():
    print("")
    print("Agregating data: for each file what are the contributors")

    # Agregated  by files and stores agregation in global agreByFileContributors   #
    # (file,[list of contributors changing it])

    filesVisited = []

    for change in changeLogData:
        email = change[0][1]
        files = change[1]

        for file in files:
            # If its a new file
            if file not in filesVisited:
                filesVisited.append(file)
                agreByFileContributors[file] = []
                agreByFileContributors[file].append(email)
            # if a file that that was changed before
            elif file in filesVisited:
                # add a new author to the list of authors that changed the file
                if email not in agreByFileContributors[file]:
                    agreByFileContributors[file].append(email)
            else:
                print("ERROR: list of file not visited")
                exit()

    stats['nChangedFiles'] = len(filesVisited)

# Get tuple of authors getting connect due to working on a common file
# [(a-b),file)]


def getContributorsConnectionsTuplesWSF():

    # Interates over the list of files and its contributors
    print("")
    print("Getting tuples of contributors that coded/contributed on the same file")

    # Stores contributors connected by working in the same file
    contributorsConnectedbyFile = []

    connectedByFile = []

    for change in agreByFileContributors:
        contributors = agreByFileContributors[change]
        for contributor in contributors:
            connectedByFile.append(contributor)

        contributorsConnectedbyFile.append((connectedByFile, change))
        connectedByFile = []

    # Print contributors connect by working in same file i.e. [(['cgarcia@igalia.com', 'jinwoo7.song@samsung.com'], '* Source/cmake/OptionsEfl.cmake:')
    # print (contributorsConnectedbyFile)

    for connection in contributorsConnectedbyFile:
        # print ("interating "+ str(connection))

        contributors = connection[0]
        files = connection[1]

        if len(contributors) == 0:
            print("ERROR Not file changes can have 0  contributors")
            exit()
        elif len(contributors) == 1:
            "One man file .. no connection"
            # print ("WARNING one man one file")
        elif len(contributors) > 1:
            "add all combinations of contributors to global agreByConnWSF "
            for connection in itertools.combinations(contributors, 2):
                agreByConnWSF.append((connection, files))


# Get a list of unique tubles of developers that collaborate. List of tubles with linked nodes.
def getUniqueConnectionsTuplesList(tuplesListWithFile):

    # verify arguments data
    # verify tuplesListWithFile

    if type(tuplesListWithFile) != list:
        print("\tERROR collaboration tuplesList is not a list !!")
        exit()
    if len(tuplesListWithFile) < 1:
        print("\tERROR collaboration tuplesList is empty !!")
        exit()

    seen = {}

    for connection in tuplesListWithFile:
        ((author1, author2), fileName) = connection

        # Do not consider if author1 or author2 been already connected 1->2 or 2-< 1
        if (author1, author2) and (author2, author1) not in seen:
            seen[(author1, author2)] = True

    return list(seen.keys())


# Pring unique connections - lust of tuples [(a,b),(b.c)]
def print_unique_connections():
    print("\nPrinting author unique collaborations (straps repeated collaborations):\n ")

    if len(uniqueConnections) < 1:
        print("Error, there are no unique connections between developers that should be printed")
        exit()

    print("\t------/------\n")
    for (dev1, dev2) in uniqueConnections:
        print("\t" + dev1 + " collaborated  with " + dev2)
    print(
        "\t TOTAL number of unique collaborations =[" + str(len(uniqueConnections)) + "]")
    print("\t------/------\n")


# Get the affiliations of all authors commiting code
# Author emails is its unique identifier
def getAffiliations():
    print("Getting author affiliations from their unique email in changeLogData")
    for change in changeLogData:
        email = change[0][1]
        affiliations[email] = getAffiliationFromEmail(email)

    print("Getting networked-author affiliations from their unique email in changeLogData")
    for connection in agreByConnWSF:
        contributorsPair = connection[0]
        fileName = connection[1]

        (contr1, contr2) = contributorsPair
        networked_affiliations[contr1] = getAffiliationFromEmail(contr1)
        networked_affiliations[contr2] = getAffiliationFromEmail(contr2)


# Pring the affiliation of each author
def print_Affiliations():
    print("\nPrinting author affiliations:\n ")
    for author in affiliations:
        print("\t" + author + " is affiliatied with " + affiliations[author])

    print("\nPrinting network-author affiliations:\n ")
    for author in networked_affiliations:
        print("\t" + author + " is affiliatied with " + affiliations[author])

# Reprocess all variables from changeLogData


def reprocess():

    print("\n Reprocessing changeLogData")

    global agreByFileContributors
    global agreByConnWSF
    global affiliations
    global networked_affiliations
    global uniqueConnections

    agreByFileContributors = {}
    agreByConnWSF = []
    affiliations = {}
    networked_affiliations = {}

    # Reprocess with the new changeLogData
    agregateByFileItsContributors()
    getContributorsConnectionsTuplesWSF()
    uniqueConnections = getUniqueConnectionsTuplesList(agreByConnWSF)
    getAffiliations()


# MAIN

def main():

    global changeLogData
    global agreByFileContributors
    global agreByConnWSF
    global affiliations
    global networked_affiliations
    global uniqueConnections

    global SAVE_MODE
    global RAW_MODE
    global LOAD_MODE
    global DEBUG_MODE

    # Process the arguments
    # -s for serialized save (already provessed changeLog)
    # -r for extrating raw changelog git log

    parser = argparse.ArgumentParser(
        description='Scrap some chagelog to create networks/graphs for research purpses')
    parser.add_argument('-l', '--lser', action='store', type=str,
                        help='loads and processes an serialized changelog')
    parser.add_argument('-r', '--raw', action='store',
                        type=str, help='processes from a raw git changelog')
    parser.add_argument('-s', '--sser', action='store', type=str,
                        help='processses from a raw git changelog and saves it into a serialized changelog. Requires -r for imput')
    parser.add_argument("-v", "--verbose",
                        help="increase output verbosity", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        print("verbosity turned on")
        DEBUG_MODE = 1

    if args.lser:
        print (" loanding and processing [lser=", args.lser, "]")
        print ("not implmented yet")
        LOAD_MODE = 1
        RAW_MODE = 0
        SAVE_MODE = 0
    elif args.sser and args.raw:
        print (" processing [raw=", args.raw, "]", " and saving [sser=", args.sser, "]")
        SAVE_MODE = 1
        RAW_MODE = 1
        LOAD_MODE = 0
    elif args.raw:
        RAW_MODE = 1
        LOAD_MODE = 0
        SAVE_MODE = 0
        print (" processing [raw=", args.raw, "]")
    else:
        print ("unrecognized argumets ... see --help")
        sys.exit()

    if RAW_MODE == 1:
        # if we are not in load mode, we need to strap the log
        print ("Scrapping changeLog from ", args.raw)
        t0 = datetime.now()
        print("STARTING the scrap of changeLog file " +
              args.raw + " on " + str(t0))

        # Opening the files

        workfile = args.raw

        f = open(workfile, 'r')

        # Read line by line
        # Keep also the stats
        # Detect blocks ... process them

        # Will save a commit block lines : From == to next ==

        lines = f.readlines()

        # Break everything in blocks and grab the data in ChangLogData

        for line in lines:
            # print("reading line [" + line +"]")

            # Ignore empty lines
            if line == "\n":
                continue

            # Updates the count of number of lines in the file
            stats['nlines'] += 1

            # if starts with '==' we have a new commit-block
            if line[0:2] == '==':
                # Process last temporay block and the cleans it
                if (stats['nBlocks'] != 0):
                    scrapBlock(tmpBlock)
                tmpBlock = []
                tmpBlock.append(line)

                # Updates the could of change log blocks
                stats['nBlocks'] += 1
                continue
            # then, eithier is a file or an error
            elif not line[0:2] == '==':
                # must be a file path
                # having a / a . or stenlen bigger than 5
                if '.' in line or '/' in line or len(line) >= 5:
                    tmpBlock.append(line)
                    continue
                else:
                    print(
                        "ERROR: not a file path. Commit blocs not starting with == must be file paths")
                    print(
                        "ERROR processing line ["+str(stats['nlines'])+"]" + "line=["+line+"]")
                    sys.exit()
            else:
                print("ERROR: Something wrong with the changeLog blocks L 107")
                sys.exit()
                break

    if (RAW_MODE == 1):
        print("\n:)1st SUCESS Data scraped from changlog files (stored in ChangeLogData data structure)")
        # print_changeLogData()

    elif (LOAD_MODE == 1):
        changeLogData = load_changeLogData(args.lser)
        print ("1st SUCESS Change log loaded from ", args.lser, " ")

        if len(changeLogData) < 1:
            print ("to small loaded change log, len <1")
            sys.exit()

        # print_changeLogData()

    else:
        print ("ERROR: In what mode are we afer all= No SAVE,LOAD or RAW")
        sys.exit()

    if (SAVE_MODE == 1):
        print ("Saving file")
        save_changeLogData(args.sser)

    # Agregate by file ...

    agregateByFileItsContributors()
    print("\n:)2nd SUCESS2 Data agregated by files and its contributors")
    # print_agreByFileContributors()

    # agreate list of authors that worked on the each files

    getContributorsConnectionsTuplesWSF()
    print("\n:) 3rd SUCESS tubles of authors that collaborated (coded in the same source code file) were generated")
    # print_agreByConnWSF()

    # agreate an list of authors that worked on the each files (do not repeat author tuples)
    # For getting unique edges/collaborations (do not include repetitions of the same collaborations)
    uniqueConnections = getUniqueConnectionsTuplesList(agreByConnWSF)
    print("\n:) 4rd SUCESS unique authors that collaborated tuples (coded in the same source code file) were generated")
    # print_unique_connections()

    # for every author, get its affiliation. result will be saved in the  affiliation global dictionart
    getAffiliations()
    # print_Affiliations()

    print("\n:) 5rd SUCESS got author -> affiliation dictionary")

    #### UCI NET format ####
    #### Used for WebKit SIGMISCPT paper ####
    # Export to data files to Ucitnet format
    # Both networkOutput and atributesOutput are global atributes defined on the header

    # exportLogData.createNetworkFileCSV(agreByConnSF, networkOutput)
    # exportLogData.createAtributesFileCSV(changeLogData, atributesOutput )
    # print ("\n:) UciNet export SUCESS exported UCInet network to file:"+networkOutput+" and its attributes to file:"+atributesOutput)

    # GRAPH ML#

    # Create an GraphML file

    # exportLogData.createGraphML(uniqueConnections,networked_affiliations, graphmlOutput)
    # print ("\n:) GRAPHML export SUCESS exported GraphML network to file:"+graphmlOutput)

    # print ("\t\n:) GRAPHML export Number of nodes/authors = " + str(len(affiliations)))
    # print ("\t\n:) GRAPHML export Number of networked nodes/authors = " + str(len(networked_affiliations)))

    # print ("\t\n:) GRAPHML export Number of nodes/atribute/affiliations  = " + str(networkMeasures.getNumberOfAffiliations(affiliations)))
    # print ("\t\n:) GRAPHML export Number of networked nodes/atribute/affiliations  = " + str(networkMeasures.getNumberOfAffiliations(networked_affiliations)))
    # print ("\t\n:) GRAPHML export Number of edges/collaborations (include repetitions of the same collaboration) = " + str(networkMeasures.getNumberOfEdges(agreByConnWSF)))

    # print ("\t\n:) GRAPHML export Number of unique edges/collaborations (do not include repetitions of the same collaborations) = " + str(networkMeasures.getNumberOfUniqueEdges(agreByConnWSF)))

    # print ("\t\n:) GRAPHML export Number of unique edges/collaborations (do not include repetitions of the same collaborations) = " + str(len(uniqueConnections)))

    # Create an graphML file filtered by company
    # In this case_ red_hat,enovance and intel
    # Others are ignored, not grouped
    # exportLogData.createGraphML_filterByAffiliation(uniqueConnections,networked_affiliations, "FilteredByCompanies"+ graphmlOutput , ["red_hat","enovance", "intel", "ibm", "hp","mirantis","nebula","vmware" ])

    print("\n")

    sizeOriginalChangeLogData = len(changeLogData)

    # Filter changeLogByDate
    # changeLogData=filterChangeLogDataByDate (datetime(2014,1,1), datetime (2014,6,1))

    # Filter nothing
    # changeLogData=filterChangeLogDataByDate (datetime(1900,1,1), datetime (2020,1,1))

    # Filter changeLogData for dates between Xmas and valentines
    # FOR TESTING PURPOSES ONLY

    # print "Number of edges overall[", len(uniqueConnections), "]"
    # XmasDate=datetime(2012,12,15)
    # valentinesDate=datetime(2014,2,14)
    # changeLogData=filterChangeLogDataByDate (datetime(2014,1,1), datetime (2014,6,1))
    # reprocess()
    # print "Number of edges between Xmas and Fall[", len(uniqueConnections), "]"

    print("\nSegmenting by release \n\
        0 Icehouse released Apr 17, 2014 \n\
        1 Havana  released Oct 17, 2013 \n\
        2 Grizzly released Apr 4, 2013 \n\
        3 Folsom  released Sep 27, 2012 \n\
        4 Essex released Apr 5, 2012 \n\
        5 Diablo released Sep 22, 2011 \n\
        6 Cactus released Apr 15, 2011 \n\
        7 Bexar released Feb 3, 2011  \n\
        8 Austin released Oct 21, 2010\n")

    releases = []

    releases.append(("Icehouse", datetime(2014, 4, 17)))
    releases.append(("Havana", datetime(2013, 10, 17)))
    releases.append(("Grizzly", datetime(2013, 4, 4)))
    releases.append(("Folsom", datetime(2012, 9, 27)))
    releases.append(("Essex", datetime(2012, 4, 5)))
    releases.append(("Diablo", datetime(2011, 9, 22)))
    releases.append(("Cactus", datetime(2011, 4, 15)))
    releases.append(("Bexar", datetime(2011, 2, 3)))
    releases.append(("Austin", datetime(2010, 10, 21)))

    tmpBkupLogData = changeLogData

    # Creates logitudinal network segments for open-stack
    # for i in range (len(releases)-1):
    #    (release_name, release_date) = releases[i]
    #    prior_release_date= releases[i+1][1]
    #    print ("\t --- Generating grapth["+ release_name+"]" + "from ["+  str(prior_release_date) +"] and rel on [" + str(release_date) + "]\n")
    #    print ("\t --- Filtering change log data for [" + str(prior_release_date)+ "] <--> ["+ str(release_date)+"]")
    #    changeLogData=filterChangeLogDataByDate (prior_release_date,release_date)
    #    reprocess()
    #    print("\t --- Filtering by date is done. [" + str (sizeOriginalChangeLogData-len(changeLogData)) +"] changeLogs removed due their change date")
    #    exportLogData.createGraphML_filterByAffiliation(uniqueConnections,networked_affiliations, release_name + graphmlOutput , top10)
    #    print("\t --- Network for " + release_name+ " release created at " + release_name + graphmlOutput + " for " + str(top10) + "\n")
    #    changeLogData = tmpBkupLogData

    # Get the number of edges betwen releases i and i+1

    nodesiip1 = []
    nodesiip1Top10 = []
    edgesiip1 = []
    edgesiip1Top10 = []

    for i in range(len(releases)-1):
        (release_name, release_date) = releases[i]
        prior_release_date = releases[i+1][1]
        print("\t --- Filtering change log data for [" + str(
            prior_release_date) + "] <--> [" + str(release_date)+"]")
        changeLogData = filterChangeLogDataByDate(
            prior_release_date, release_date)
        reprocess()
        print("\t --- Filtering by date is done. [" + str(sizeOriginalChangeLogData-len(
            changeLogData)) + "] changeLogs removed due their change date")

        nnodes = len(
            JISA2015specificAnalysis.getNodesBetweenDatesInConnList(uniqueConnections))
        nnodestop10 = len(JISA2015specificAnalysis.getNodesBetweenDates4SelectedFirmsDatesInConnList(
            uniqueConnections, networked_affiliations, top10))
        nedges = len(uniqueConnections)
        nedgestop10 = len(JISA2015specificAnalysis.getConnectionsAmongTop10Only(
            uniqueConnections, networked_affiliations, top10))

        print ("Number of nodes between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodes)
        print ("Number of nodes (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodestop10)

        print ("Number of edges between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nedges, ";")
        print ("Number of edges (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nedgestop10, ";")

        nodesiip1.append(nnodes)
        nodesiip1Top10.append(nnodestop10)
        edgesiip1.append(nedges)
        edgesiip1Top10.append(nedgestop10)

        changeLogData = tmpBkupLogData

        # for debug only
        # print the edges among top10 for first release
        # print "pringing edged for reease", release_name , ":"
        # top10con = getConnectionsAmongTop10Only(uniqueConnections)
        # for edge in top10con:
        # (a,b) = edge
        # if top10con.count(edge) != 1:
        # print "ERROR:Not a single edge:"
        # print "top10con.count(edge)=[", top10con.count(edge),"] --> repeated edges"
        # print "edge in question:", edge
        # sys.exit()
        # if (b,a) in top10con:
        # print "ERROR:Not a single edge:"
        # print "top10con.count(edge)=[", top10con.count((b,a)),"] --> repeated edges (inverse relationship already accounted)"
        # print "edge in question:", edge, " and its inverse " , (b,a)
        # sys.exit()
        #
        # sys.exit()

    # Get the number of nodes and edges betwen releases i-1month and i+1
    nodesim1ip1 = []
    nodesim1ip1Top10 = []
    edgesim1ip1 = []
    edgesim1ip1Top10 = []

    releasesm1 = []
    for release in releases:
        (releasename, date) = release

        # for 4 weeks / 1 month
        # releasesm1.append((releasename, date - relativedelta(months=1)))

        # for 3 weeks
        # releasesm1.append((releasename, date - relativedelta(weeks=3)))

        # for 2 weeks
        # releasesm1.append((releasename, date - relativedelta(weeks=2)))

        # for 1 week
        releasesm1.append((releasename, date - relativedelta(weeks=1)))

    # Get the number of edges betwen releases i and i+1
    for i in range(len(releasesm1)-1):
        (release_name, release_date) = releases[i]
        prior_release_date = releasesm1[i+1][1]
        print("\t --- Filtering change log data for [" + str(
            prior_release_date) + "] <--> [" + str(release_date)+"]")
        changeLogData = filterChangeLogDataByDate(
            prior_release_date, release_date)
        reprocess()
        print("\t --- Filtering by date is done. [" + str(sizeOriginalChangeLogData-len(
            changeLogData)) + "] changeLogs removed due their change date")

        nnodes = len(
            JISA2015specificAnalysis.getNodesBetweenDatesInConnList(uniqueConnections))
        nnodestop10 = len(JISA2015specificAnalysis.getNodesBetweenDates4SelectedFirmsDatesInConnList(
            uniqueConnections, networked_affiliations, top10))

        nedges = len(uniqueConnections)
        nedgestop10 = len(JISA2015specificAnalysis.getConnectionsAmongTop10Only(
            uniqueConnections, networked_affiliations, top10))

        print ("Number of nodes between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodes)
        print ("Number of nodes (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodestop10)

        print ("Number of edges between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nedges, ";")
        print ("Number of edges (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nedgestop10, ";")

        nodesim1ip1.append(nnodes)
        nodesim1ip1Top10.append(nnodestop10)
        edgesim1ip1.append(nedges)
        edgesim1ip1Top10.append(nedgestop10)
        changeLogData = tmpBkupLogData

    # print releases name
    # Not that they are in reverse cronological order, therefore ::-1
    rname = []
    for r in releases:
        (name, nc) = r
        rname.append(name + ";")
    print ("rname", rname[::-1])

    # For all nodes
    print ("\t ALL NODES ")

    print ("nodesiip1", nodesiip1[::-1])
    print ("nodesiim1p1", nodesim1ip1[::-1])
    print ("diff capture nodes less 1 month", map(int.__sub__, nodesiip1, nodesim1ip1)[::-1])
    print ("% captured nodes less 1 month", map(float.__div__, [float(i) for i in nodesiip1], [float(i) for i in nodesim1ip1])[::-1])

    print ("edgesiip1", edgesiip1[::-1])
    print ("edgesim1ip1", edgesim1ip1[::-1])
    print ("diff edges less 1 month", map(int.__sub__, edgesiip1, edgesim1ip1)[::-1])
    print ("% captured edges less 1 month", map(float.__div__, [float(i) for i in edgesiip1], [float(i) for i in edgesim1ip1])[::-1])

    # For top 10 onlys
    print ("\t TOP 10 NODES ")

    print ("nodesiip1Top10",  nodesiip1Top10[::-1])
    print ("nodesim1ip1Top10", nodesim1ip1Top10[::-1])
    print ("diff nodes top10 less 1 month", map(int.__sub__, nodesiip1Top10, nodesim1ip1Top10)[::-1])
    print ("% captured nodes less 1 month", map(float.__div__, [float(i) for i in nodesiip1Top10], [float(i) for i in nodesim1ip1Top10])[::-1])

    print ("edgesiip1Top10", edgesiip1Top10[::-1])
    print ("edgesim1ip1Top10", edgesim1ip1Top10[::-1])
    print ("diff edfes top10 less 1 month", map(int.__sub__, edgesiip1Top10, edgesim1ip1Top10)[::-1])
    print ("% captured edges less 1 month", map(float.__div__, [float(i) for i in edgesiip1Top10], [float(i) for i in edgesim1ip1Top10])[::-1])

    print("")
    print("FINNISHED " + str(datetime.now()))

    if (LOAD_MODE != 1):
        print("TOTAL TIME " + str(datetime.now() - t0))

    # Ending stats

    print("Number of analized lines [" + str(stats['nlines']) + "]")
    print(
        "Number of analized changelog blocks [" + str(stats['nBlocks']) + "]")
    print("Number of analized changelog blocks changing code files [" + str(
        stats['nBlocksChagingCode']) + "?]")
    print("Number of analized changelog blocks not changing code files (i.e. testCases)[" + str(
        stats['nBlocksNotChangingCode']) + "?]")
    print("Number of files affected by the commits reported by change log[" + str(
        stats['nChangedFiles']) + "]")


if __name__ == "__main__":
    main()

#! /usr/bin/env python3


# Scaps date, authors, affiliations and file changes from WebKit SVN Changelog
#
#


print("this is pyhton")

# scraplog save with serialzie
# TODO functions returning NetworkX graphs


try:
    import cPickle as pickle
except:
    import pickle


print("Executing " + str(sys.argv))

# Global parameters

networkOutput = "NetworkOutput.file1.CSV"
atributesOutput = "AtributesOutput.file2.CSV"
graphmlOutput = "NetworkFile.graphML"


# Global structures

# Keeps statistics of the scrappping
stats = {'nlines': 0, 'nBlocks': 0, 'nBlocksChagingCode': 0,
         'nBlocksNotChangingCode': 0, 'nChangedFiles': 0}

# Keeps data as inially scrapped [(date, email, affilition), [files changed]]
# The one that can be saved , the only data structure keeping date information
changeLogData = []

# Will keep agrregated data of authors that changed the same (file,[list of contributors changing it])
agreByFileContributors = {}


# Will keep agregated tuples of authors connecting due to working on a common file [(a-b),file)]

agreByConnWSF = []

# Will keep unique tuples of authors connected due to workin on common file. no repetitions for (a-b),(a-b) or (a-b),(b-a)
# Keeps unique collaborations and connections. [(a,b),(b,c),(a,c)]
uniqueConnections = []

# Will keep a dictionary author afiliation i.e affiliation[mike@google.com]=google.com
affiliations = {}

# Will keep a dictionary networked author afiliation i.e affiliation[mike@google.com]=google.com
# Drops authors that do not connect with others
networked_affiliations = {}


# For ibm ex
# ibm_email_domains =  ["au1.ibm.com","linux.vnet.ibm.com","br.ibm.com", "zurich.ibm.com", "us.ibm.com" ,"cn.ibm.com","il.ibm.com","de.ibm.com","ca.ibm.com"]
ibm_email_domains_prefix = ["au1", "linux",
                            "br", "zurich", "us", "cn", "il", "de", "ca"]

# TOP10 companies in OpenStack
top10 = ["rackspace", "nebula", "citrix", "redhat", "ibm", "hp",
         "cloudscaling", "mirantis", "vmware", "canonical", "intel"]


# Are we verbose?
DEBUG_MODE = 0

# Are we going to scraplog data?

SAVE_MODE = 0

# Are we starting with a ready to process stracplog saved previously in SAVE_MODE?
LOAD_MODE = 0


# Are we dealing with raw data from a git/svn log ?
RAW_MODE = 0


def getAffiliationFromEmail(email):
    "gets affiliation from an given email"

    # print ("getAffiliationFromEmail("+email+")")

    affiliation_pattern = re.compile('@(\w[\w\-]+)')
    match = affiliation_pattern.findall(email)

    if match == None or match == []:
        print("ERROR unable to extract affiliation from email. Wrong email format?")
        print("match=["+str(match)+"]")
        sys.exit()

    "implement an exception for IBM as their emails come from multiple domains"
    "au1.ibm.com linux.vnet.ibm.com br.ibm.com zurich.ibm.com us.ibm.com cn.ibm.com il.ibm.com"

    if 'ibm' in email:
        # print ("Warning, ibm affiliation from multiple domains")

        if match[0] not in ibm_email_domains_prefix:
            print(
                "ERROR, ibm affilition from an unknow domain, check ibm_email_domain glob")
            print("march=["+str(match[0])+"]")
            sys.exit()

        # print ("affiliation(" + email + ")=[ibm]")
        return "ibm"

    affiliation = match[0]
    # print ("affiliation(" + email + ")=["+affiliation+"]")
    return affiliation


#
# Extract date, nane and email
# WK Sample line
# ==Jenkins;jenkins@review.openstack.org;Thu Feb 20 03:56:00 2014 +0000==
# Format obtained by running: $git log --pretty=format:"==%an;%ae;%ad=="  --name-only
# Returned result would be ('Thu Feb 20 03:56:57 2014','Jenkins', 'jenkins@review.openstack.org',

def getDateEmailAffiliation(line):
    "gets the ==Name;email;date=="
    # print ("	getting name, email, date, affilication from the line["+line+"]")

    name_pattern = re.compile(
        '^\\=\\=(.+);(.+);(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
    match = name_pattern.findall(line)

    # print ("match=" + str(match))

    if match == None or match == []:

        ## expeptions handling ##
        # "==name;email;date== is the most common pattern from a git log"
        # "however some entries are name less taking a different format:"
        atIndex = line.find('@')

        # Exception 1: Developer added name and email to name
        # ==Brad McConnell bmcconne@rackspace.com;;Tue Sep 20 06:50:27 2011 +0000==
        if ';;' in line and ' ' in line[0:atIndex] and '==Launchpad' not in line:
            print("WARNING exceptional code commit header Exception 1 ")
            print("LINE number "+str(stats['nlines'])+" [" + line +
                  "] double ;; <- name and email together on commit header")

            name_pattern = re.compile(
                '^\\=\\=(.*)\ (.+@.+);;(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
            match = name_pattern.findall(line)
            print("match=["+str(match)+"]")

        # Exception 2: If there is not name in the commit
        # there is no spaces before the email (@)
        elif ' ' not in line[0:atIndex] and '==Launchpad' not in line:

            print("WARNING exceptional code commit header Exception 2 ")
            print("LINE number "+str(stats['nlines']) +
                  " [" + line + "] no name, just an email")

            name_pattern = re.compile(
                '^\\=\\=(.+@.+);;(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
            tmpmatch = name_pattern.findall(line)

            # Workarround by adding name from the email
            # Warned about this name with name as  name?
            match = [(line[2:line.find('@')], tmpmatch[0]
                      [0], tmpmatch[0][1], tmpmatch[0][2])]

        # Exception 3: Launchpad Translations
        # Drop as it is a bot
        # ==Launchpad Translations on behalf of nova-core;;Sat Sep 3 05:50:53 2011 +0000
        elif "==Launchpad" in line:
            print("WARNING exceptional code commit header Exception 3 ")
            print("LINE number " +
                  str(stats['nlines'])+" [" + line + "] Lauchpad bot")

            name_pattern = re.compile(
                '^\\=\\=(.+);;(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
            tmpmatch = name_pattern.findall(line)

            # Workarround by simpli addign it as a commiter
            # Warned about this name with name as  Lauchpad_bot!
            match = [("Lauchpad_bot!", "Lauchpad@bot.bot", tmpmatch[0][1])]

        # Exception 4:
        # match=[('Jenkins', 'jenkins@review.openstack.org', 'Thu Jan 30 21:21:23 2014', '+')]
        #

        # anything else ERROR with imput or this code
        else:
            print(
                "Error, unable to extract developer name, email or date from commit block")
            print("Regular expression not captured")
            print("Line=["+line+"]")
            sys.exit()

    name = match[0][0]
    # print("name=["+name+"]")

    "get the email"
    email = match[0][1]
    # print("email=["+email+"]")

    # Verify the email pattern

    email_pattern = re.compile('([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)')

    if (email_pattern.search(email) == None):
        print("WARNING commiter ["+email+"] have an invalidName")
        print("Adding .com? to the end")
        email += ".com?"

    "gets the date"
    date = match[0][2]
    # print("date=["+date+"]")

    affiliation = getAffiliationFromEmail(email)

    return (date, email, affiliation)


"return a list of files modified by a commit log"


def findFilesOnBlock(block):
    # print ("finding files on block [" + str(block) + "]" )

    linesWithCode = []

    for line in block:
        # print ("line=["+line+"]")
        if line == []:
            break
        if line == '\n':
            break
        "append the file path (removing the last caracted \n)"
        linesWithCode.append(line[:-1])
        stats['nBlocksChagingCode'] += 1

    # print ("Lines of changed code:")
    # for line in linesWithCode:
    #    print (line)

    return linesWithCode


# processes a bloc of a change log (a developer change)
def scrapBlock(block):
    # print ("Processing [" + str(block) + "]")

    # Check if it is an empty block / change
    if len(block) == 0:
        print("ERROR: block / changelog to scrap is empty")
        return False

    firstLine = block[0]

    # check if the block starts with a date
    if not firstLine[0:2] == '==':
        print("ERROR: Invalid block / not starting with a date ")
        return False

    daEmAf = getDateEmailAffiliation(block[0])

    # print ("")
    # print (daEmAf)

    # What file where affected by the change log
    changedFiles = findFilesOnBlock(block[1:])

    # Save it in changeLogData
    # (date, email, affilition), [files changed])

    # GIT log changes that do not change files are irelevant
    if changedFiles == []:
        return False

    changeLogData.append((daEmAf, changedFiles))


# filter/slice the changeLogData by data
# Aproach: simply removes blocks wich date does not fit between a startDate and endDate
# Format end date should be  "Oct 11 2014" "MMM DD YYYY"

def filterChangeLogDataByDate(startDate, endDate):
    print(
        "Filtering ChangeLogData for  dates between ["+str(startDate)+"] and ["+str(endDate)+"]")

    # are they dates?

    if type(startDate) != datetime or type(endDate) != datetime:
        print("ERROR: invalide data type, not a valid datetime object")
        sys.exit()

    # is channge log empty ?

    if (len(changeLogData) < 1):
        print("ERROR: changeLogData is empty")

    # if end date after start date?

    res = []

    for change in changeLogData:
        date = change[0][0]
        email = change[0][1]
        af = change[0][2]
        files = change[1]

        # print ("On " + date + " " + email + " from " + af + " worked on the following files:" )

        # print ("ChangeLogDateString=["+date+"]")
        # weekday =date[0:3]
        # month = date[4:7]
        # day = date[8:10]
        # time = date[11:19]
        # year = date[20:24]

        # Get weekday month day time year  with regular expressions
        name_pattern = re.compile('(.+)\s(.+)\s(\d+)\s(.+)\s(\d+)')
        match = name_pattern.findall(date)

        # print ("date_ match=["+str(match)+"]")

        # If there is no regulae expression match
        if (match == []):
            print("ERROR: Change log date is not on proper format")
            print("date_ match=["+str(match)+"]")
            sys.exit()

        weekday = match[0][0]
        month = match[0][1]
        day = match[0][2]
        time = match[0][3]
        year = match[0][4]

        # print ("ChangeLogDateCapture=["+weekday+ " " + month+ " " + day + " " + time + " " + year + "]")

        # date(year, month, day) --> date object
        day = int(day)
        year = int(year)

        if month == "Jan":
            month = 1
        elif month == "Feb":
            month = 2
        elif month == "Mar":
            month = 3
        elif month == "Apr":
            month = 4
        elif month == "May":
            month = 5
        elif month == "Jun":
            month = 6
        elif month == "Jul":
            month = 7
        elif month == "Aug":
            month = 8
        elif month == "Sep":
            month = 9
        elif month == "Oct":
            month = 10
        elif month == "Nov":
            month = 11
        elif month == "Dec":
            month = 12
        else:
            print("ERROR invalide month spec: unable to extract date")
            sys.exit()
        changeLogDate = datetime(year, month, day)

        # print("changeLogDate=["+ str(changeLogDate)+"]")

        if (changeLogDate < startDate) or changeLogDate > endDate:
            # print("drop change log due date")
            continue
        else:
            # print("changeLogDate=["+ str(changeLogDate)+"] is between ["+str(startDate)+"] and ["+str(endDate)+"]" )
            res.append(change)

    return res

# print the changeLogData data scraped


def print_changeLogData():
    global changeLogData

    print("")
    print("Printing change log data ... from the earliast change to the oldest change")
    for change in changeLogData:
        date = change[0][0]
        email = change[0][1]
        af = change[0][2]
        files = change[1]

        print("On " + date + " " + email + " from " +
              af + " worked on the following files:")

        for file in files:
            print("[" + file + "]")


# save the changeLogData data scraped into a filename
def save_changeLogData(filename):

    global SAVE_MODE
    global changeLogData

    print("")
    print("TODO")
    print('Saving changeLog to file ' + str(filename) + '')

    if (SAVE_MODE != 1):
        print ("ERROR, not in saving mode")
        sys.exit()

    with open(filename, 'wb') as fp:
        pickle.dump(changeLogData, fp)

    print ("DONE changelog saved in ", filename, "NICE :)")
    sys.exit()


# load and return	 the changeLogData data scraped into a filename
def load_changeLogData(filename):
    print ("")
    print ("TODO")
    print ("Loading changeLog from  file [", filename, "]")

    with open(filename, 'rb') as fp:
        changeLogData = pickle.load(fp)

    return changeLogData


# print the agreByFileContributors agreefation resuting by  agregateByFileItsContributors
def print_agreByFileContributors():
    print("")
    print("Printing files affected by commits on the changelLog  ... and developers resposable for it")

    for file in agreByFileContributors:
        fileName = file
        authorEmails = agreByFileContributors[file]

        if (len(authorEmails) == 0):
            print("ERROR: File without contrubutors !!")
            exit()

        print("The file " + fileName +
              "was changed by following [" + str(len(authorEmails)) + "]contributors")

        for email in authorEmails:
            print("[" + email + "]")


# print a list of contributor connected to each other cause they worked on a common files
def print_agreByConnWSF():
    # print (str(agreByConnWSF))

    print("")
    print("Printing tuples of authors that collaborated + file that they contribute together too")
    # format more a less like this [(a-b),file)]

    for connection in agreByConnWSF:
        contributorsPair = connection[0]
        fileName = connection[1]

        print("Contributors " + str(contributorsPair) +
              " connected by collaborating on file [" + fileName + "]")


# Agregate by file and its contributors
def agregateByFileItsContributors():
    print("")
    print("Agregating data: for each file what are the contributors")

    # Agregated  by files and stores agregation in global agreByFileContributors   #
    # (file,[list of contributors changing it])

    filesVisited = []

    for change in changeLogData:
        email = change[0][1]
        files = change[1]

        for file in files:
            # If its a new file
            if file not in filesVisited:
                filesVisited.append(file)
                agreByFileContributors[file] = []
                agreByFileContributors[file].append(email)
            # if a file that that was changed before
            elif file in filesVisited:
                # add a new author to the list of authors that changed the file
                if email not in agreByFileContributors[file]:
                    agreByFileContributors[file].append(email)
            else:
                print("ERROR: list of file not visited")
                exit()

    stats['nChangedFiles'] = len(filesVisited)

# Get tuple of authors getting connect due to working on a common file
# [(a-b),file)]


def getContributorsConnectionsTuplesWSF():

    # Interates over the list of files and its contributors
    print("")
    print("Getting tuples of contributors that coded/contributed on the same file")

    # Stores contributors connected by working in the same file
    contributorsConnectedbyFile = []

    connectedByFile = []

    for change in agreByFileContributors:
        contributors = agreByFileContributors[change]
        for contributor in contributors:
            connectedByFile.append(contributor)

        contributorsConnectedbyFile.append((connectedByFile, change))
        connectedByFile = []

    # Print contributors connect by working in same file i.e. [(['cgarcia@igalia.com', 'jinwoo7.song@samsung.com'], '* Source/cmake/OptionsEfl.cmake:')
    # print (contributorsConnectedbyFile)

    for connection in contributorsConnectedbyFile:
        # print ("interating "+ str(connection))

        contributors = connection[0]
        files = connection[1]

        if len(contributors) == 0:
            print("ERROR Not file changes can have 0  contributors")
            exit()
        elif len(contributors) == 1:
            "One man file .. no connection"
            # print ("WARNING one man one file")
        elif len(contributors) > 1:
            "add all combinations of contributors to global agreByConnWSF "
            for connection in itertools.combinations(contributors, 2):
                agreByConnWSF.append((connection, files))


# Get a list of unique tubles of developers that collaborate. List of tubles with linked nodes.
def getUniqueConnectionsTuplesList(tuplesListWithFile):

    # verify arguments data
    # verify tuplesListWithFile

    if type(tuplesListWithFile) != list:
        print("\tERROR collaboration tuplesList is not a list !!")
        exit()
    if len(tuplesListWithFile) < 1:
        print("\tERROR collaboration tuplesList is empty !!")
        exit()

    seen = {}

    for connection in tuplesListWithFile:
        ((author1, author2), fileName) = connection

        # Do not consider if author1 or author2 been already connected 1->2 or 2-< 1
        if (author1, author2) and (author2, author1) not in seen:
            seen[(author1, author2)] = True

    return list(seen.keys())


# Pring unique connections - lust of tuples [(a,b),(b.c)]
def print_unique_connections():
    print("\nPrinting author unique collaborations (straps repeated collaborations):\n ")

    if len(uniqueConnections) < 1:
        print("Error, there are no unique connections between developers that should be printed")
        exit()

    print("\t------/------\n")
    for (dev1, dev2) in uniqueConnections:
        print("\t" + dev1 + " collaborated  with " + dev2)
    print(
        "\t TOTAL number of unique collaborations =[" + str(len(uniqueConnections)) + "]")
    print("\t------/------\n")


# Get the affiliations of all authors commiting code
# Author emails is its unique identifier
def getAffiliations():
    print("Getting author affiliations from their unique email in changeLogData")
    for change in changeLogData:
        email = change[0][1]
        affiliations[email] = getAffiliationFromEmail(email)

    print("Getting networked-author affiliations from their unique email in changeLogData")
    for connection in agreByConnWSF:
        contributorsPair = connection[0]
        fileName = connection[1]

        (contr1, contr2) = contributorsPair
        networked_affiliations[contr1] = getAffiliationFromEmail(contr1)
        networked_affiliations[contr2] = getAffiliationFromEmail(contr2)


# Pring the affiliation of each author
def print_Affiliations():
    print("\nPrinting author affiliations:\n ")
    for author in affiliations:
        print("\t" + author + " is affiliatied with " + affiliations[author])

    print("\nPrinting network-author affiliations:\n ")
    for author in networked_affiliations:
        print("\t" + author + " is affiliatied with " + affiliations[author])

# Reprocess all variables from changeLogData


def reprocess():

    print("\n Reprocessing changeLogData")

    global agreByFileContributors
    global agreByConnWSF
    global affiliations
    global networked_affiliations
    global uniqueConnections

    agreByFileContributors = {}
    agreByConnWSF = []
    affiliations = {}
    networked_affiliations = {}

    # Reprocess with the new changeLogData
    agregateByFileItsContributors()
    getContributorsConnectionsTuplesWSF()
    uniqueConnections = getUniqueConnectionsTuplesList(agreByConnWSF)
    getAffiliations()


# MAIN

def main():

    global changeLogData
    global agreByFileContributors
    global agreByConnWSF
    global affiliations
    global networked_affiliations
    global uniqueConnections

    global SAVE_MODE
    global RAW_MODE
    global LOAD_MODE
    global DEBUG_MODE

    # Process the arguments
    # -s for serialized save (already provessed changeLog)
    # -r for extrating raw changelog git log

    parser = argparse.ArgumentParser(
        description='Scrap some chagelog to create networks/graphs for research purpses')
    parser.add_argument('-l', '--lser', action='store', type=str,
                        help='loads and processes an serialized changelog')
    parser.add_argument('-r', '--raw', action='store',
                        type=str, help='processes from a raw git changelog')
    parser.add_argument('-s', '--sser', action='store', type=str,
                        help='processses from a raw git changelog and saves it into a serialized changelog. Requires -r for imput')
    parser.add_argument("-v", "--verbose",
                        help="increase output verbosity", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        print("verbosity turned on")
        DEBUG_MODE = 1

    if args.lser:
        print (" loanding and processing [lser=", args.lser, "]")
        print ("not implmented yet")
        LOAD_MODE = 1
        RAW_MODE = 0
        SAVE_MODE = 0
    elif args.sser and args.raw:
        print (" processing [raw=", args.raw, "]", " and saving [sser=", args.sser, "]")
        SAVE_MODE = 1
        RAW_MODE = 1
        LOAD_MODE = 0
    elif args.raw:
        RAW_MODE = 1
        LOAD_MODE = 0
        SAVE_MODE = 0
        print( " processing [raw=", args.raw, "]")
    else:
        print ("unrecognized argumets ... see --help")
        sys.exit()

    if RAW_MODE == 1:
        # if we are not in load mode, we need to strap the log
        print ("Scrapping changeLog from ", args.raw)
        t0 = datetime.now()
        print("STARTING the scrap of changeLog file " +
              args.raw + " on " + str(t0))

        # Opening the files

        workfile = args.raw

        f = open(workfile, 'r')

        # Read line by line
        # Keep also the stats
        # Detect blocks ... process them

        # Will save a commit block lines : From == to next ==

        lines = f.readlines()

        # Break everything in blocks and grab the data in ChangLogData

        for line in lines:
            # print("reading line [" + line +"]")

            # Ignore empty lines
            if line == "\n":
                continue

            # Updates the count of number of lines in the file
            stats['nlines'] += 1

            # if starts with '==' we have a new commit-block
            if line[0:2] == '==':
                # Process last temporay block and the cleans it
                if (stats['nBlocks'] != 0):
                    scrapBlock(tmpBlock)
                tmpBlock = []
                tmpBlock.append(line)

                # Updates the could of change log blocks
                stats['nBlocks'] += 1
                continue
            # then, eithier is a file or an error
            elif not line[0:2] == '==':
                # must be a file path
                # having a / a . or stenlen bigger than 5
                if '.' in line or '/' in line or len(line) >= 5:
                    tmpBlock.append(line)
                    continue
                else:
                    print(
                        "ERROR: not a file path. Commit blocs not starting with == must be file paths")
                    print(
                        "ERROR processing line ["+str(stats['nlines'])+"]" + "line=["+line+"]")
                    sys.exit()
            else:
                print("ERROR: Something wrong with the changeLog blocks L 107")
                sys.exit()
                break

    if (RAW_MODE == 1):
        print("\n:)1st SUCESS Data scraped from changlog files (stored in ChangeLogData data structure)")
        # print_changeLogData()

    elif (LOAD_MODE == 1):
        changeLogData = load_changeLogData(args.lser)
        print ("1st SUCESS Change log loaded from ", args.lser, " ")

        if len(changeLogData) < 1:
            print ("to small loaded change log, len <1")
            sys.exit()

        # print_changeLogData()

    else:
        print ("ERROR: In what mode are we afer all= No SAVE,LOAD or RAW")
        sys.exit()

    if (SAVE_MODE == 1):
        print ("Saving file")
        save_changeLogData(args.sser)

    # Agregate by file ...

    agregateByFileItsContributors()
    print("\n:)2nd SUCESS2 Data agregated by files and its contributors")
    # print_agreByFileContributors()

    # agreate list of authors that worked on the each files

    getContributorsConnectionsTuplesWSF()
    print("\n:) 3rd SUCESS tubles of authors that collaborated (coded in the same source code file) were generated")
    # print_agreByConnWSF()

    # agreate an list of authors that worked on the each files (do not repeat author tuples)
    # For getting unique edges/collaborations (do not include repetitions of the same collaborations)
    uniqueConnections = getUniqueConnectionsTuplesList(agreByConnWSF)
    print("\n:) 4rd SUCESS unique authors that collaborated tuples (coded in the same source code file) were generated")
    # print_unique_connections()

    # for every author, get its affiliation. result will be saved in the  affiliation global dictionart
    getAffiliations()
    # print_Affiliations()

    print("\n:) 5rd SUCESS got author -> affiliation dictionary")

    #### UCI NET format ####
    #### Used for WebKit SIGMISCPT paper ####
    # Export to data files to Ucitnet format
    # Both networkOutput and atributesOutput are global atributes defined on the header

    # exportLogData.createNetworkFileCSV(agreByConnSF, networkOutput)
    # exportLogData.createAtributesFileCSV(changeLogData, atributesOutput )
    # print ("\n:) UciNet export SUCESS exported UCInet network to file:"+networkOutput+" and its attributes to file:"+atributesOutput)

    # GRAPH ML#

    # Create an GraphML file

    # exportLogData.createGraphML(uniqueConnections,networked_affiliations, graphmlOutput)
    # print ("\n:) GRAPHML export SUCESS exported GraphML network to file:"+graphmlOutput)

    # print ("\t\n:) GRAPHML export Number of nodes/authors = " + str(len(affiliations)))
    # print ("\t\n:) GRAPHML export Number of networked nodes/authors = " + str(len(networked_affiliations)))

    # print ("\t\n:) GRAPHML export Number of nodes/atribute/affiliations  = " + str(networkMeasures.getNumberOfAffiliations(affiliations)))
    # print ("\t\n:) GRAPHML export Number of networked nodes/atribute/affiliations  = " + str(networkMeasures.getNumberOfAffiliations(networked_affiliations)))
    # print ("\t\n:) GRAPHML export Number of edges/collaborations (include repetitions of the same collaboration) = " + str(networkMeasures.getNumberOfEdges(agreByConnWSF)))

    # print ("\t\n:) GRAPHML export Number of unique edges/collaborations (do not include repetitions of the same collaborations) = " + str(networkMeasures.getNumberOfUniqueEdges(agreByConnWSF)))

    # print ("\t\n:) GRAPHML export Number of unique edges/collaborations (do not include repetitions of the same collaborations) = " + str(len(uniqueConnections)))

    # Create an graphML file filtered by company
    # In this case_ red_hat,enovance and intel
    # Others are ignored, not grouped
    # exportLogData.createGraphML_filterByAffiliation(uniqueConnections,networked_affiliations, "FilteredByCompanies"+ graphmlOutput , ["red_hat","enovance", "intel", "ibm", "hp","mirantis","nebula","vmware" ])

    print("\n")

    sizeOriginalChangeLogData = len(changeLogData)

    # Filter changeLogByDate
    # changeLogData=filterChangeLogDataByDate (datetime(2014,1,1), datetime (2014,6,1))

    # Filter nothing
    # changeLogData=filterChangeLogDataByDate (datetime(1900,1,1), datetime (2020,1,1))

    # Filter changeLogData for dates between Xmas and valentines
    # FOR TESTING PURPOSES ONLY

    # print "Number of edges overall[", len(uniqueConnections), "]"
    # XmasDate=datetime(2012,12,15)
    # valentinesDate=datetime(2014,2,14)
    # changeLogData=filterChangeLogDataByDate (datetime(2014,1,1), datetime (2014,6,1))
    # reprocess()
    # print "Number of edges between Xmas and Fall[", len(uniqueConnections), "]"

    print("\nSegmenting by release \n\
        0 Icehouse released Apr 17, 2014 \n\
        1 Havana  released Oct 17, 2013 \n\
        2 Grizzly released Apr 4, 2013 \n\
        3 Folsom  released Sep 27, 2012 \n\
        4 Essex released Apr 5, 2012 \n\
        5 Diablo released Sep 22, 2011 \n\
        6 Cactus released Apr 15, 2011 \n\
        7 Bexar released Feb 3, 2011  \n\
        8 Austin released Oct 21, 2010\n")

    releases = []

    releases.append(("Icehouse", datetime(2014, 4, 17)))
    releases.append(("Havana", datetime(2013, 10, 17)))
    releases.append(("Grizzly", datetime(2013, 4, 4)))
    releases.append(("Folsom", datetime(2012, 9, 27)))
    releases.append(("Essex", datetime(2012, 4, 5)))
    releases.append(("Diablo", datetime(2011, 9, 22)))
    releases.append(("Cactus", datetime(2011, 4, 15)))
    releases.append(("Bexar", datetime(2011, 2, 3)))
    releases.append(("Austin", datetime(2010, 10, 21)))

    tmpBkupLogData = changeLogData

    # Creates logitudinal network segments for open-stack
    # for i in range (len(releases)-1):
    #    (release_name, release_date) = releases[i]
    #    prior_release_date= releases[i+1][1]
    #    print ("\t --- Generating grapth["+ release_name+"]" + "from ["+  str(prior_release_date) +"] and rel on [" + str(release_date) + "]\n")
    #    print ("\t --- Filtering change log data for [" + str(prior_release_date)+ "] <--> ["+ str(release_date)+"]")
    #    changeLogData=filterChangeLogDataByDate (prior_release_date,release_date)
    #    reprocess()
    #    print("\t --- Filtering by date is done. [" + str (sizeOriginalChangeLogData-len(changeLogData)) +"] changeLogs removed due their change date")
    #    exportLogData.createGraphML_filterByAffiliation(uniqueConnections,networked_affiliations, release_name + graphmlOutput , top10)
    #    print("\t --- Network for " + release_name+ " release created at " + release_name + graphmlOutput + " for " + str(top10) + "\n")
    #    changeLogData = tmpBkupLogData

    # Get the number of edges betwen releases i and i+1

    nodesiip1 = []
    nodesiip1Top10 = []
    edgesiip1 = []
    edgesiip1Top10 = []

    for i in range(len(releases)-1):
        (release_name, release_date) = releases[i]
        prior_release_date = releases[i+1][1]
        print("\t --- Filtering change log data for [" + str(
            prior_release_date) + "] <--> [" + str(release_date)+"]")
        changeLogData = filterChangeLogDataByDate(
            prior_release_date, release_date)
        reprocess()
        print("\t --- Filtering by date is done. [" + str(sizeOriginalChangeLogData-len(
            changeLogData)) + "] changeLogs removed due their change date")

        nnodes = len(
            JISA2015specificAnalysis.getNodesBetweenDatesInConnList(uniqueConnections))
        nnodestop10 = len(JISA2015specificAnalysis.getNodesBetweenDates4SelectedFirmsDatesInConnList(
            uniqueConnections, networked_affiliations, top10))
        nedges = len(uniqueConnections)
        nedgestop10 = len(JISA2015specificAnalysis.getConnectionsAmongTop10Only(
            uniqueConnections, networked_affiliations, top10))

        print ("Number of nodes between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodes)
        print ("Number of nodes (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodestop10)

        print ("Number of edges between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nedges, ";")
        print ("Number of edges (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nedgestop10, ";")

        nodesiip1.append(nnodes)
        nodesiip1Top10.append(nnodestop10)
        edgesiip1.append(nedges)
        edgesiip1Top10.append(nedgestop10)

        changeLogData = tmpBkupLogData

        # for debug only
        # print the edges among top10 for first release
        # print "pringing edged for reease", release_name , ":"
        # top10con = getConnectionsAmongTop10Only(uniqueConnections)
        # for edge in top10con:
        # (a,b) = edge
        # if top10con.count(edge) != 1:
        # print "ERROR:Not a single edge:"
        # print "top10con.count(edge)=[", top10con.count(edge),"] --> repeated edges"
        # print "edge in question:", edge
        # sys.exit()
        # if (b,a) in top10con:
        # print "ERROR:Not a single edge:"
        # print "top10con.count(edge)=[", top10con.count((b,a)),"] --> repeated edges (inverse relationship already accounted)"
        # print "edge in question:", edge, " and its inverse " , (b,a)
        # sys.exit()
        #
        # sys.exit()

    # Get the number of nodes and edges betwen releases i-1month and i+1
    nodesim1ip1 = []
    nodesim1ip1Top10 = []
    edgesim1ip1 = []
    edgesim1ip1Top10 = []

    releasesm1 = []
    for release in releases:
        (releasename, date) = release

        # for 4 weeks / 1 month
        # releasesm1.append((releasename, date - relativedelta(months=1)))

        # for 3 weeks
        # releasesm1.append((releasename, date - relativedelta(weeks=3)))

        # for 2 weeks
        # releasesm1.append((releasename, date - relativedelta(weeks=2)))

        # for 1 week
        releasesm1.append((releasename, date - relativedelta(weeks=1)))

    # Get the number of edges betwen releases i and i+1
    for i in range(len(releasesm1)-1):
        (release_name, release_date) = releases[i]
        prior_release_date = releasesm1[i+1][1]
        print("\t --- Filtering change log data for [" + str(
            prior_release_date) + "] <--> [" + str(release_date)+"]")
        changeLogData = filterChangeLogDataByDate(
            prior_release_date, release_date)
        reprocess()
        print("\t --- Filtering by date is done. [" + str(sizeOriginalChangeLogData-len(
            changeLogData)) + "] changeLogs removed due their change date")

        nnodes = len(
            JISA2015specificAnalysis.getNodesBetweenDatesInConnList(uniqueConnections))
        nnodestop10 = len(JISA2015specificAnalysis.getNodesBetweenDates4SelectedFirmsDatesInConnList(
            uniqueConnections, networked_affiliations, top10))

        nedges = len(uniqueConnections)
        nedgestop10 = len(JISA2015specificAnalysis.getConnectionsAmongTop10Only(
            uniqueConnections, networked_affiliations, top10))

        print ("Number of nodes between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodes)
        print ("Number of nodes (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodestop10)

        print ("Number of edges between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nedges, ";")
        print ("Number of edges (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nedgestop10, ";") 

        nodesim1ip1.append(nnodes)
        nodesim1ip1Top10.append(nnodestop10)
        edgesim1ip1.append(nedges)
        edgesim1ip1Top10.append(nedgestop10)
        changeLogData = tmpBkupLogData

    # print releases name
    # Not that they are in reverse cronological order, therefore ::-1
    rname = []
    for r in releases:
        (name, nc) = r
        rname.append(name + ";")
    print ("rname", rname[::-1])

    # For all nodes
    print( "\t ALL NODES ")

    print("nodesiip1", nodesiip1[::-1])
    print("nodesiim1p1", nodesim1ip1[::-1])
    print( "diff capture nodes less 1 month", map(int.__sub__, nodesiip1, nodesim1ip1)[::-1])
    print( "% captured nodes less 1 month", map(float.__div__, [float(i) for i in nodesiip1], [float(i) for i in nodesim1ip1])[::-1])

    print ("edgesiip1", edgesiip1[::-1])
    print ("edgesim1ip1", edgesim1ip1[::-1])
    print ("diff edges less 1 month", map(int.__sub__, edgesiip1, edgesim1ip1)[::-1])
    print ("% captured edges less 1 month", map(float.__div__, [float(i) for i in edgesiip1], [float(i) for i in edgesim1ip1])[::-1])

    # For top 10 onlys
    print ("\t TOP 10 NODES ")

    print ("nodesiip1Top10",  nodesiip1Top10[::-1])
    print ("nodesim1ip1Top10", nodesim1ip1Top10[::-1])
    print ("diff nodes top10 less 1 month", map(int.__sub__, nodesiip1Top10, nodesim1ip1Top10)[::-1])
    print ("% captured nodes less 1 month", map(float.__div__, [float(i) for i in nodesiip1Top10], [float(i) for i in nodesim1ip1Top10])[::-1])

    print ("edgesiip1Top10", edgesiip1Top10[::-1])
    print ("edgesim1ip1Top10", edgesim1ip1Top10[::-1])
    print ("diff edfes top10 less 1 month", map(int.__sub__, edgesiip1Top10, edgesim1ip1Top10)[::-1])
    print ("% captured edges less 1 month", map(float.__div__, [float(i) for i in edgesiip1Top10], [float(i) for i in edgesim1ip1Top10])[::-1])

    print("")
    print("FINNISHED " + str(datetime.now()))

    if (LOAD_MODE != 1):
        print("TOTAL TIME " + str(datetime.now() - t0))

    # Ending stats

    print("Number of analized lines [" + str(stats['nlines']) + "]")
    print(
        "Number of analized changelog blocks [" + str(stats['nBlocks']) + "]")
    print("Number of analized changelog blocks changing code files [" + str(
        stats['nBlocksChagingCode']) + "?]")
    print("Number of analized changelog blocks not changing code files (i.e. testCases)[" + str(
        stats['nBlocksNotChangingCode']) + "?]")
    print("Number of files affected by the commits reported by change log[" + str(
        stats['nChangedFiles']) + "]")


if __name__ == "__main__":
    main()
#! /usr/bin/env python3


# Scaps date, authors, affiliations and file changes from WebKit SVN Changelog
#
#


import re
import networkMeasures
import JISA2015specificAnalysis
import exportLogData
import argparse
import itertools
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import sys
print("this is pyhton")

# scraplog save with serialzie
# TODO functions returning NetworkX graphs


try:
    import cPickle as pickle
except:
    import pickle


print("Executing " + str(sys.argv))

# Global parameters

networkOutput = "NetworkOutput.file1.CSV"
atributesOutput = "AtributesOutput.file2.CSV"
graphmlOutput = "NetworkFile.graphML"


# Global structures

# Keeps statistics of the scrappping
stats = {'nlines': 0, 'nBlocks': 0, 'nBlocksChagingCode': 0,
         'nBlocksNotChangingCode': 0, 'nChangedFiles': 0}

# Keeps data as inially scrapped [(date, email, affilition), [files changed]]
# The one that can be saved , the only data structure keeping date information
changeLogData = []

# Will keep agrregated data of authors that changed the same (file,[list of contributors changing it])
agreByFileContributors = {}


# Will keep agregated tuples of authors connecting due to working on a common file [(a-b),file)]

agreByConnWSF = []

# Will keep unique tuples of authors connected due to workin on common file. no repetitions for (a-b),(a-b) or (a-b),(b-a)
# Keeps unique collaborations and connections. [(a,b),(b,c),(a,c)]
uniqueConnections = []

# Will keep a dictionary author afiliation i.e affiliation[mike@google.com]=google.com
affiliations = {}

# Will keep a dictionary networked author afiliation i.e affiliation[mike@google.com]=google.com
# Drops authors that do not connect with others
networked_affiliations = {}


# For ibm ex
# ibm_email_domains =  ["au1.ibm.com","linux.vnet.ibm.com","br.ibm.com", "zurich.ibm.com", "us.ibm.com" ,"cn.ibm.com","il.ibm.com","de.ibm.com","ca.ibm.com"]
ibm_email_domains_prefix = ["au1", "linux",
                            "br", "zurich", "us", "cn", "il", "de", "ca"]

# TOP10 companies in OpenStack
top10 = ["rackspace", "nebula", "citrix", "redhat", "ibm", "hp",
         "cloudscaling", "mirantis", "vmware", "canonical", "intel"]


# Are we verbose?
DEBUG_MODE = 0

# Are we going to scraplog data?

SAVE_MODE = 0

# Are we starting with a ready to process stracplog saved previously in SAVE_MODE?
LOAD_MODE = 0


# Are we dealing with raw data from a git/svn log ?
RAW_MODE = 0


def getAffiliationFromEmail(email):
    "gets affiliation from an given email"

    # print ("getAffiliationFromEmail("+email+")")

    affiliation_pattern = re.compile('@(\w[\w\-]+)')
    match = affiliation_pattern.findall(email)

    if match == None or match == []:
        print("ERROR unable to extract affiliation from email. Wrong email format?")
        print("match=["+str(match)+"]")
        sys.exit()

    "implement an exception for IBM as their emails come from multiple domains"
    "au1.ibm.com linux.vnet.ibm.com br.ibm.com zurich.ibm.com us.ibm.com cn.ibm.com il.ibm.com"

    if 'ibm' in email:
        # print ("Warning, ibm affiliation from multiple domains")

        if match[0] not in ibm_email_domains_prefix:
            print(
                "ERROR, ibm affilition from an unknow domain, check ibm_email_domain glob")
            print("march=["+str(match[0])+"]")
            sys.exit()

        # print ("affiliation(" + email + ")=[ibm]")
        return "ibm"

    affiliation = match[0]
    # print ("affiliation(" + email + ")=["+affiliation+"]")
    return affiliation


#
# Extract date, nane and email
# WK Sample line
# ==Jenkins;jenkins@review.openstack.org;Thu Feb 20 03:56:00 2014 +0000==
# Format obtained by running: $git log --pretty=format:"==%an;%ae;%ad=="  --name-only
# Returned result would be ('Thu Feb 20 03:56:57 2014','Jenkins', 'jenkins@review.openstack.org',

def getDateEmailAffiliation(line):
    "gets the ==Name;email;date=="
    # print ("	getting name, email, date, affilication from the line["+line+"]")

    name_pattern = re.compile(
        '^\\=\\=(.+);(.+);(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
    match = name_pattern.findall(line)

    # print ("match=" + str(match))

    if match == None or match == []:

        ## expeptions handling ##
        # "==name;email;date== is the most common pattern from a git log"
        # "however some entries are name less taking a different format:"
        atIndex = line.find('@')

        # Exception 1: Developer added name and email to name
        # ==Brad McConnell bmcconne@rackspace.com;;Tue Sep 20 06:50:27 2011 +0000==
        if ';;' in line and ' ' in line[0:atIndex] and '==Launchpad' not in line:
            print("WARNING exceptional code commit header Exception 1 ")
            print("LINE number "+str(stats['nlines'])+" [" + line +
                  "] double ;; <- name and email together on commit header")

            name_pattern = re.compile(
                '^\\=\\=(.*)\ (.+@.+);;(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
            match = name_pattern.findall(line)
            print("match=["+str(match)+"]")

        # Exception 2: If there is not name in the commit
        # there is no spaces before the email (@)
        elif ' ' not in line[0:atIndex] and '==Launchpad' not in line:

            print("WARNING exceptional code commit header Exception 2 ")
            print("LINE number "+str(stats['nlines']) +
                  " [" + line + "] no name, just an email")

            name_pattern = re.compile(
                '^\\=\\=(.+@.+);;(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
            tmpmatch = name_pattern.findall(line)

            # Workarround by adding name from the email
            # Warned about this name with name as  name?
            match = [(line[2:line.find('@')], tmpmatch[0]
                      [0], tmpmatch[0][1], tmpmatch[0][2])]

        # Exception 3: Launchpad Translations
        # Drop as it is a bot
        # ==Launchpad Translations on behalf of nova-core;;Sat Sep 3 05:50:53 2011 +0000
        elif "==Launchpad" in line:
            print("WARNING exceptional code commit header Exception 3 ")
            print("LINE number " +
                  str(stats['nlines'])+" [" + line + "] Lauchpad bot")

            name_pattern = re.compile(
                '^\\=\\=(.+);;(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
            tmpmatch = name_pattern.findall(line)

            # Workarround by simpli addign it as a commiter
            # Warned about this name with name as  Lauchpad_bot!
            match = [("Lauchpad_bot!", "Lauchpad@bot.bot", tmpmatch[0][1])]

        # Exception 4:
        # match=[('Jenkins', 'jenkins@review.openstack.org', 'Thu Jan 30 21:21:23 2014', '+')]
        #

        # anything else ERROR with imput or this code
        else:
            print(
                "Error, unable to extract developer name, email or date from commit block")
            print("Regular expression not captured")
            print("Line=["+line+"]")
            sys.exit()

    name = match[0][0]
    # print("name=["+name+"]")

    "get the email"
    email = match[0][1]
    # print("email=["+email+"]")

    # Verify the email pattern

    email_pattern = re.compile('([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)')

    if (email_pattern.search(email) == None):
        print("WARNING commiter ["+email+"] have an invalidName")
        print("Adding .com? to the end")
        email += ".com?"

    "gets the date"
    date = match[0][2]
    # print("date=["+date+"]")

    affiliation = getAffiliationFromEmail(email)

    return (date, email, affiliation)


"return a list of files modified by a commit log"


def findFilesOnBlock(block):
    # print ("finding files on block [" + str(block) + "]" )

    linesWithCode = []

    for line in block:
        # print ("line=["+line+"]")
        if line == []:
            break
        if line == '\n':
            break
        "append the file path (removing the last caracted \n)"
        linesWithCode.append(line[:-1])
        stats['nBlocksChagingCode'] += 1

    # print ("Lines of changed code:")
    # for line in linesWithCode:
    #    print (line)

    return linesWithCode


# processes a bloc of a change log (a developer change)
def scrapBlock(block):
    # print ("Processing [" + str(block) + "]")

    # Check if it is an empty block / change
    if len(block) == 0:
        print("ERROR: block / changelog to scrap is empty")
        return False

    firstLine = block[0]

    # check if the block starts with a date
    if not firstLine[0:2] == '==':
        print("ERROR: Invalid block / not starting with a date ")
        return False

    daEmAf = getDateEmailAffiliation(block[0])

    # print ("")
    # print (daEmAf)

    # What file where affected by the change log
    changedFiles = findFilesOnBlock(block[1:])

    # Save it in changeLogData
    # (date, email, affilition), [files changed])

    # GIT log changes that do not change files are irelevant
    if changedFiles == []:
        return False

    changeLogData.append((daEmAf, changedFiles))


# filter/slice the changeLogData by data
# Aproach: simply removes blocks wich date does not fit between a startDate and endDate
# Format end date should be  "Oct 11 2014" "MMM DD YYYY"

def filterChangeLogDataByDate(startDate, endDate):
    print(
        "Filtering ChangeLogData for  dates between ["+str(startDate)+"] and ["+str(endDate)+"]")

    # are they dates?

    if type(startDate) != datetime or type(endDate) != datetime:
        print("ERROR: invalide data type, not a valid datetime object")
        sys.exit()

    # is channge log empty ?

    if (len(changeLogData) < 1):
        print("ERROR: changeLogData is empty")

    # if end date after start date?

    res = []

    for change in changeLogData:
        date = change[0][0]
        email = change[0][1]
        af = change[0][2]
        files = change[1]

        # print ("On " + date + " " + email + " from " + af + " worked on the following files:" )

        # print ("ChangeLogDateString=["+date+"]")
        # weekday =date[0:3]
        # month = date[4:7]
        # day = date[8:10]
        # time = date[11:19]
        # year = date[20:24]

        # Get weekday month day time year  with regular expressions
        name_pattern = re.compile('(.+)\s(.+)\s(\d+)\s(.+)\s(\d+)')
        match = name_pattern.findall(date)

        # print ("date_ match=["+str(match)+"]")

        # If there is no regulae expression match
        if (match == []):
            print("ERROR: Change log date is not on proper format")
            print("date_ match=["+str(match)+"]")
            sys.exit()

        weekday = match[0][0]
        month = match[0][1]
        day = match[0][2]
        time = match[0][3]
        year = match[0][4]

        # print ("ChangeLogDateCapture=["+weekday+ " " + month+ " " + day + " " + time + " " + year + "]")

        # date(year, month, day) --> date object
        day = int(day)
        year = int(year)

        if month == "Jan":
            month = 1
        elif month == "Feb":
            month = 2
        elif month == "Mar":
            month = 3
        elif month == "Apr":
            month = 4
        elif month == "May":
            month = 5
        elif month == "Jun":
            month = 6
        elif month == "Jul":
            month = 7
        elif month == "Aug":
            month = 8
        elif month == "Sep":
            month = 9
        elif month == "Oct":
            month = 10
        elif month == "Nov":
            month = 11
        elif month == "Dec":
            month = 12
        else:
            print("ERROR invalide month spec: unable to extract date")
            sys.exit()
        changeLogDate = datetime(year, month, day)

        # print("changeLogDate=["+ str(changeLogDate)+"]")

        if (changeLogDate < startDate) or changeLogDate > endDate:
            # print("drop change log due date")
            continue
        else:
            # print("changeLogDate=["+ str(changeLogDate)+"] is between ["+str(startDate)+"] and ["+str(endDate)+"]" )
            res.append(change)

    return res

# print the changeLogData data scraped


def print_changeLogData():
    global changeLogData

    print("")
    print("Printing change log data ... from the earliast change to the oldest change")
    for change in changeLogData:
        date = change[0][0]
        email = change[0][1]
        af = change[0][2]
        files = change[1]

        print("On " + date + " " + email + " from " +
              af + " worked on the following files:")

        for file in files:
            print("[" + file + "]")


# save the changeLogData data scraped into a filename
def save_changeLogData(filename):

    global SAVE_MODE
    global changeLogData

    print("")
    print("TODO")
    print('Saving changeLog to file ' + str(filename) + '')

    if (SAVE_MODE != 1):
        print("ERROR, not in saving mode")
        sys.exit()

    with open(filename, 'wb') as fp:
        pickle.dump(changeLogData, fp)

    print("DONE changelog saved in ", filename, "NICE :)")
    sys.exit()


# load and return	 the changeLogData data scraped into a filename
def load_changeLogData(filename):
    print("")
    print("TODO")
    print("Loading changeLog from  file [", filename, "]")

    with open(filename, 'rb') as fp:
        changeLogData = pickle.load(fp)

    return changeLogData


# print the agreByFileContributors agreefation resuting by  agregateByFileItsContributors
def print_agreByFileContributors():
    print("")
    print("Printing files affected by commits on the changelLog  ... and developers resposable for it")

    for file in agreByFileContributors:
        fileName = file
        authorEmails = agreByFileContributors[file]

        if (len(authorEmails) == 0):
            print("ERROR: File without contrubutors !!")
            exit()

        print("The file " + fileName +
              "was changed by following [" + str(len(authorEmails)) + "]contributors")

        for email in authorEmails:
            print("[" + email + "]")


# print a list of contributor connected to each other cause they worked on a common files
def print_agreByConnWSF():
    # print (str(agreByConnWSF))

    print("")
    print("Printing tuples of authors that collaborated + file that they contribute together too")
    # format more a less like this [(a-b),file)]

    for connection in agreByConnWSF:
        contributorsPair = connection[0]
        fileName = connection[1]

        print("Contributors " + str(contributorsPair) +
              " connected by collaborating on file [" + fileName + "]")


# Agregate by file and its contributors
def agregateByFileItsContributors():
    print("")
    print("Agregating data: for each file what are the contributors")

    # Agregated  by files and stores agregation in global agreByFileContributors   #
    # (file,[list of contributors changing it])

    filesVisited = []

    for change in changeLogData:
        email = change[0][1]
        files = change[1]

        for file in files:
            # If its a new file
            if file not in filesVisited:
                filesVisited.append(file)
                agreByFileContributors[file] = []
                agreByFileContributors[file].append(email)
            # if a file that that was changed before
            elif file in filesVisited:
                # add a new author to the list of authors that changed the file
                if email not in agreByFileContributors[file]:
                    agreByFileContributors[file].append(email)
            else:
                print("ERROR: list of file not visited")
                exit()

    stats['nChangedFiles'] = len(filesVisited)

# Get tuple of authors getting connect due to working on a common file
# [(a-b),file)]


def getContributorsConnectionsTuplesWSF():

    # Interates over the list of files and its contributors
    print("")
    print("Getting tuples of contributors that coded/contributed on the same file")

    # Stores contributors connected by working in the same file
    contributorsConnectedbyFile = []

    connectedByFile = []

    for change in agreByFileContributors:
        contributors = agreByFileContributors[change]
        for contributor in contributors:
            connectedByFile.append(contributor)

        contributorsConnectedbyFile.append((connectedByFile, change))
        connectedByFile = []

    # Print contributors connect by working in same file i.e. [(['cgarcia@igalia.com', 'jinwoo7.song@samsung.com'], '* Source/cmake/OptionsEfl.cmake:')
    # print (contributorsConnectedbyFile)

    for connection in contributorsConnectedbyFile:
        # print ("interating "+ str(connection))

        contributors = connection[0]
        files = connection[1]

        if len(contributors) == 0:
            print("ERROR Not file changes can have 0  contributors")
            exit()
        elif len(contributors) == 1:
            "One man file .. no connection"
            # print ("WARNING one man one file")
        elif len(contributors) > 1:
            "add all combinations of contributors to global agreByConnWSF "
            for connection in itertools.combinations(contributors, 2):
                agreByConnWSF.append((connection, files))


# Get a list of unique tubles of developers that collaborate. List of tubles with linked nodes.
def getUniqueConnectionsTuplesList(tuplesListWithFile):

    # verify arguments data
    # verify tuplesListWithFile

    if type(tuplesListWithFile) != list:
        print("\tERROR collaboration tuplesList is not a list !!")
        exit()
    if len(tuplesListWithFile) < 1:
        print("\tERROR collaboration tuplesList is empty !!")
        exit()

    seen = {}

    for connection in tuplesListWithFile:
        ((author1, author2), fileName) = connection

        # Do not consider if author1 or author2 been already connected 1->2 or 2-< 1
        if (author1, author2) and (author2, author1) not in seen:
            seen[(author1, author2)] = True

    return list(seen.keys())


# Pring unique connections - lust of tuples [(a,b),(b.c)]
def print_unique_connections():
    print("\nPrinting author unique collaborations (straps repeated collaborations):\n ")

    if len(uniqueConnections) < 1:
        print("Error, there are no unique connections between developers that should be printed")
        exit()

    print("\t------/------\n")
    for (dev1, dev2) in uniqueConnections:
        print("\t" + dev1 + " collaborated  with " + dev2)
    print(
        "\t TOTAL number of unique collaborations =[" + str(len(uniqueConnections)) + "]")
    print("\t------/------\n")


# Get the affiliations of all authors commiting code
# Author emails is its unique identifier
def getAffiliations():
    print("Getting author affiliations from their unique email in changeLogData")
    for change in changeLogData:
        email = change[0][1]
        affiliations[email] = getAffiliationFromEmail(email)

    print("Getting networked-author affiliations from their unique email in changeLogData")
    for connection in agreByConnWSF:
        contributorsPair = connection[0]
        fileName = connection[1]

        (contr1, contr2) = contributorsPair
        networked_affiliations[contr1] = getAffiliationFromEmail(contr1)
        networked_affiliations[contr2] = getAffiliationFromEmail(contr2)


# Pring the affiliation of each author
def print_Affiliations():
    print("\nPrinting author affiliations:\n ")
    for author in affiliations:
        print("\t" + author + " is affiliatied with " + affiliations[author])

    print("\nPrinting network-author affiliations:\n ")
    for author in networked_affiliations:
        print("\t" + author + " is affiliatied with " + affiliations[author])

# Reprocess all variables from changeLogData


def reprocess():

    print("\n Reprocessing changeLogData")

    global agreByFileContributors
    global agreByConnWSF
    global affiliations
    global networked_affiliations
    global uniqueConnections

    agreByFileContributors = {}
    agreByConnWSF = []
    affiliations = {}
    networked_affiliations = {}

    # Reprocess with the new changeLogData
    agregateByFileItsContributors()
    getContributorsConnectionsTuplesWSF()
    uniqueConnections = getUniqueConnectionsTuplesList(agreByConnWSF)
    getAffiliations()


# MAIN

def main():

    global changeLogData
    global agreByFileContributors
    global agreByConnWSF
    global affiliations
    global networked_affiliations
    global uniqueConnections

    global SAVE_MODE
    global RAW_MODE
    global LOAD_MODE
    global DEBUG_MODE

    # Process the arguments
    # -s for serialized save (already provessed changeLog)
    # -r for extrating raw changelog git log

    parser = argparse.ArgumentParser(
        description='Scrap some chagelog to create networks/graphs for research purpses')
    parser.add_argument('-l', '--lser', action='store', type=str,
                        help='loads and processes an serialized changelog')
    parser.add_argument('-r', '--raw', action='store',
                        type=str, help='processes from a raw git changelog')
    parser.add_argument('-s', '--sser', action='store', type=str,
                        help='processses from a raw git changelog and saves it into a serialized changelog. Requires -r for imput')
    parser.add_argument("-v", "--verbose",
                        help="increase output verbosity", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        print("verbosity turned on")
        DEBUG_MODE = 1

    if args.lser:
        print (" loanding and processing [lser=", args.lser, "]")
        print ("not implmented yet")
        LOAD_MODE = 1
        RAW_MODE = 0
        SAVE_MODE = 0
    elif args.sser and args.raw:
        print (" processing [raw=", args.raw, "]", " and saving [sser=", args.sser, "]")
        SAVE_MODE = 1
        RAW_MODE = 1
        LOAD_MODE = 0
    elif args.raw:
        RAW_MODE = 1
        LOAD_MODE = 0
        SAVE_MODE = 0
        print (" processing [raw=", args.raw, "]")
    else:
        print ("unrecognized argumets ... see --help")
        sys.exit()

    if RAW_MODE == 1:
        # if we are not in load mode, we need to strap the log
        print ("Scrapping changeLog from ", args.raw)
        t0 = datetime.now()
        print("STARTING the scrap of changeLog file " +
              args.raw + " on " + str(t0))

        # Opening the files

        workfile = args.raw

        f = open(workfile, 'r')

        # Read line by line
        # Keep also the stats
        # Detect blocks ... process them

        # Will save a commit block lines : From == to next ==

        lines = f.readlines()

        # Break everything in blocks and grab the data in ChangLogData

        for line in lines:
            # print("reading line [" + line +"]")

            # Ignore empty lines
            if line == "\n":
                continue

            # Updates the count of number of lines in the file
            stats['nlines'] += 1

            # if starts with '==' we have a new commit-block
            if line[0:2] == '==':
                # Process last temporay block and the cleans it
                if (stats['nBlocks'] != 0):
                    scrapBlock(tmpBlock)
                tmpBlock = []
                tmpBlock.append(line)

                # Updates the could of change log blocks
                stats['nBlocks'] += 1
                continue
            # then, eithier is a file or an error
            elif not line[0:2] == '==':
                # must be a file path
                # having a / a . or stenlen bigger than 5
                if '.' in line or '/' in line or len(line) >= 5:
                    tmpBlock.append(line)
                    continue
                else:
                    print(
                        "ERROR: not a file path. Commit blocs not starting with == must be file paths")
                    print(
                        "ERROR processing line ["+str(stats['nlines'])+"]" + "line=["+line+"]")
                    sys.exit()
            else:
                print("ERROR: Something wrong with the changeLog blocks L 107")
                sys.exit()
                break

    if (RAW_MODE == 1):
        print("\n:)1st SUCESS Data scraped from changlog files (stored in ChangeLogData data structure)")
        # print_changeLogData()

    elif (LOAD_MODE == 1):
        changeLogData = load_changeLogData(args.lser)
        print ("1st SUCESS Change log loaded from ", args.lser, " ")

        if len(changeLogData) < 1:
            print ("to small loaded change log, len <1")
            sys.exit()

        # print_changeLogData()

    else:
        print ("ERROR: In what mode are we afer all= No SAVE,LOAD or RAW")
        sys.exit()

    if (SAVE_MODE == 1):
        print ("Saving file")
        save_changeLogData(args.sser)

    # Agregate by file ...

    agregateByFileItsContributors()
    print("\n:)2nd SUCESS2 Data agregated by files and its contributors")
    # print_agreByFileContributors()

    # agreate list of authors that worked on the each files

    getContributorsConnectionsTuplesWSF()
    print("\n:) 3rd SUCESS tubles of authors that collaborated (coded in the same source code file) were generated")
    # print_agreByConnWSF()

    # agreate an list of authors that worked on the each files (do not repeat author tuples)
    # For getting unique edges/collaborations (do not include repetitions of the same collaborations)
    uniqueConnections = getUniqueConnectionsTuplesList(agreByConnWSF)
    print("\n:) 4rd SUCESS unique authors that collaborated tuples (coded in the same source code file) were generated")
    # print_unique_connections()

    # for every author, get its affiliation. result will be saved in the  affiliation global dictionart
    getAffiliations()
    # print_Affiliations()

    print("\n:) 5rd SUCESS got author -> affiliation dictionary")

    #### UCI NET format ####
    #### Used for WebKit SIGMISCPT paper ####
    # Export to data files to Ucitnet format
    # Both networkOutput and atributesOutput are global atributes defined on the header

    # exportLogData.createNetworkFileCSV(agreByConnSF, networkOutput)
    # exportLogData.createAtributesFileCSV(changeLogData, atributesOutput )
    # print ("\n:) UciNet export SUCESS exported UCInet network to file:"+networkOutput+" and its attributes to file:"+atributesOutput)

    # GRAPH ML#

    # Create an GraphML file

    # exportLogData.createGraphML(uniqueConnections,networked_affiliations, graphmlOutput)
    # print ("\n:) GRAPHML export SUCESS exported GraphML network to file:"+graphmlOutput)

    # print ("\t\n:) GRAPHML export Number of nodes/authors = " + str(len(affiliations)))
    # print ("\t\n:) GRAPHML export Number of networked nodes/authors = " + str(len(networked_affiliations)))

    # print ("\t\n:) GRAPHML export Number of nodes/atribute/affiliations  = " + str(networkMeasures.getNumberOfAffiliations(affiliations)))
    # print ("\t\n:) GRAPHML export Number of networked nodes/atribute/affiliations  = " + str(networkMeasures.getNumberOfAffiliations(networked_affiliations)))
    # print ("\t\n:) GRAPHML export Number of edges/collaborations (include repetitions of the same collaboration) = " + str(networkMeasures.getNumberOfEdges(agreByConnWSF)))

    # print ("\t\n:) GRAPHML export Number of unique edges/collaborations (do not include repetitions of the same collaborations) = " + str(networkMeasures.getNumberOfUniqueEdges(agreByConnWSF)))

    # print ("\t\n:) GRAPHML export Number of unique edges/collaborations (do not include repetitions of the same collaborations) = " + str(len(uniqueConnections)))

    # Create an graphML file filtered by company
    # In this case_ red_hat,enovance and intel
    # Others are ignored, not grouped
    # exportLogData.createGraphML_filterByAffiliation(uniqueConnections,networked_affiliations, "FilteredByCompanies"+ graphmlOutput , ["red_hat","enovance", "intel", "ibm", "hp","mirantis","nebula","vmware" ])

    print("\n")

    sizeOriginalChangeLogData = len(changeLogData)

    # Filter changeLogByDate
    # changeLogData=filterChangeLogDataByDate (datetime(2014,1,1), datetime (2014,6,1))

    # Filter nothing
    # changeLogData=filterChangeLogDataByDate (datetime(1900,1,1), datetime (2020,1,1))

    # Filter changeLogData for dates between Xmas and valentines
    # FOR TESTING PURPOSES ONLY

    # print "Number of edges overall[", len(uniqueConnections), "]"
    # XmasDate=datetime(2012,12,15)
    # valentinesDate=datetime(2014,2,14)
    # changeLogData=filterChangeLogDataByDate (datetime(2014,1,1), datetime (2014,6,1))
    # reprocess()
    # print "Number of edges between Xmas and Fall[", len(uniqueConnections), "]"

    print("\nSegmenting by release \n\
        0 Icehouse released Apr 17, 2014 \n\
        1 Havana  released Oct 17, 2013 \n\
        2 Grizzly released Apr 4, 2013 \n\
        3 Folsom  released Sep 27, 2012 \n\
        4 Essex released Apr 5, 2012 \n\
        5 Diablo released Sep 22, 2011 \n\
        6 Cactus released Apr 15, 2011 \n\
        7 Bexar released Feb 3, 2011  \n\
        8 Austin released Oct 21, 2010\n")

    releases = []

    releases.append(("Icehouse", datetime(2014, 4, 17)))
    releases.append(("Havana", datetime(2013, 10, 17)))
    releases.append(("Grizzly", datetime(2013, 4, 4)))
    releases.append(("Folsom", datetime(2012, 9, 27)))
    releases.append(("Essex", datetime(2012, 4, 5)))
    releases.append(("Diablo", datetime(2011, 9, 22)))
    releases.append(("Cactus", datetime(2011, 4, 15)))
    releases.append(("Bexar", datetime(2011, 2, 3)))
    releases.append(("Austin", datetime(2010, 10, 21)))

    tmpBkupLogData = changeLogData

    # Creates logitudinal network segments for open-stack
    # for i in range (len(releases)-1):
    #    (release_name, release_date) = releases[i]
    #    prior_release_date= releases[i+1][1]
    #    print ("\t --- Generating grapth["+ release_name+"]" + "from ["+  str(prior_release_date) +"] and rel on [" + str(release_date) + "]\n")
    #    print ("\t --- Filtering change log data for [" + str(prior_release_date)+ "] <--> ["+ str(release_date)+"]")
    #    changeLogData=filterChangeLogDataByDate (prior_release_date,release_date)
    #    reprocess()
    #    print("\t --- Filtering by date is done. [" + str (sizeOriginalChangeLogData-len(changeLogData)) +"] changeLogs removed due their change date")
    #    exportLogData.createGraphML_filterByAffiliation(uniqueConnections,networked_affiliations, release_name + graphmlOutput , top10)
    #    print("\t --- Network for " + release_name+ " release created at " + release_name + graphmlOutput + " for " + str(top10) + "\n")
    #    changeLogData = tmpBkupLogData

    # Get the number of edges betwen releases i and i+1

    nodesiip1 = []
    nodesiip1Top10 = []
    edgesiip1 = []
    edgesiip1Top10 = []

    for i in range(len(releases)-1):
        (release_name, release_date) = releases[i]
        prior_release_date = releases[i+1][1]
        print("\t --- Filtering change log data for [" + str(
            prior_release_date) + "] <--> [" + str(release_date)+"]")
        changeLogData = filterChangeLogDataByDate(
            prior_release_date, release_date)
        reprocess()
        print("\t --- Filtering by date is done. [" + str(sizeOriginalChangeLogData-len(
            changeLogData)) + "] changeLogs removed due their change date")

        nnodes = len(
            JISA2015specificAnalysis.getNodesBetweenDatesInConnList(uniqueConnections))
        nnodestop10 = len(JISA2015specificAnalysis.getNodesBetweenDates4SelectedFirmsDatesInConnList(
            uniqueConnections, networked_affiliations, top10))
        nedges = len(uniqueConnections)
        nedgestop10 = len(JISA2015specificAnalysis.getConnectionsAmongTop10Only(
            uniqueConnections, networked_affiliations, top10))

        print ("Number of nodes between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodes)
        print ("Number of nodes (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodestop10 )

        print ("Number of edges between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nedges, ";" ) 
        print ("Number of edges (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nedgestop10, ";" ) 

        nodesiip1.append(nnodes)
        nodesiip1Top10.append(nnodestop10)
        edgesiip1.append(nedges)
        edgesiip1Top10.append(nedgestop10)

        changeLogData = tmpBkupLogData

        # for debug only
        # print the edges among top10 for first release
        # print "pringing edged for reease", release_name , ":"
        # top10con = getConnectionsAmongTop10Only(uniqueConnections)
        # for edge in top10con:
        # (a,b) = edge
        # if top10con.count(edge) != 1:
        # print "ERROR:Not a single edge:"
        # print "top10con.count(edge)=[", top10con.count(edge),"] --> repeated edges"
        # print "edge in question:", edge
        # sys.exit()
        # if (b,a) in top10con:
        # print "ERROR:Not a single edge:"
        # print "top10con.count(edge)=[", top10con.count((b,a)),"] --> repeated edges (inverse relationship already accounted)"
        # print "edge in question:", edge, " and its inverse " , (b,a)
        # sys.exit()
        #
        # sys.exit()

    # Get the number of nodes and edges betwen releases i-1month and i+1
    nodesim1ip1 = []
    nodesim1ip1Top10 = []
    edgesim1ip1 = []
    edgesim1ip1Top10 = []

    releasesm1 = []
    for release in releases:
        (releasename, date) = release

        # for 4 weeks / 1 month
        # releasesm1.append((releasename, date - relativedelta(months=1)))

        # for 3 weeks
        # releasesm1.append((releasename, date - relativedelta(weeks=3)))

        # for 2 weeks
        # releasesm1.append((releasename, date - relativedelta(weeks=2)))

        # for 1 week
        releasesm1.append((releasename, date - relativedelta(weeks=1)))

    # Get the number of edges betwen releases i and i+1
    for i in range(len(releasesm1)-1):
        (release_name, release_date) = releases[i]
        prior_release_date = releasesm1[i+1][1]
        print("\t --- Filtering change log data for [" + str(
            prior_release_date) + "] <--> [" + str(release_date)+"]")
        changeLogData = filterChangeLogDataByDate(
            prior_release_date, release_date)
        reprocess()
        print("\t --- Filtering by date is done. [" + str(sizeOriginalChangeLogData-len(
            changeLogData)) + "] changeLogs removed due their change date")

        nnodes = len(
            JISA2015specificAnalysis.getNodesBetweenDatesInConnList(uniqueConnections))
        nnodestop10 = len(JISA2015specificAnalysis.getNodesBetweenDates4SelectedFirmsDatesInConnList(
            uniqueConnections, networked_affiliations, top10))

        nedges = len(uniqueConnections)
        nedgestop10 = len(JISA2015specificAnalysis.getConnectionsAmongTop10Only(
            uniqueConnections, networked_affiliations, top10))

        print ("Number of nodes between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodes)
        print ("Number of nodes (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodestop10)

        print ("Number of edges between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nedges, ";")
        print ("Number of edges (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nedgestop10, ";")

        nodesim1ip1.append(nnodes)
        nodesim1ip1Top10.append(nnodestop10)
        edgesim1ip1.append(nedges)
        edgesim1ip1Top10.append(nedgestop10)
        changeLogData = tmpBkupLogData

    # print releases name
    # Not that they are in reverse cronological order, therefore ::-1
    rname = []
    for r in releases:
        (name, nc) = r
        rname.append(name + ";")
    print ("rname", rname[::-1])

    # For all nodes
    print ("\ ALL NODES ")

    print ("nodesiip1", nodesiip1[::-1]) 
    print ("nodesiim1p1", nodesim1ip1[::-1])
    print ("diff capture nodes less 1 month", map(int.__sub__, nodesiip1, nodesim1ip1)[::-1])
    print ("% captured nodes less 1 month", map(float.__div__, [float(i) for i in nodesiip1], [float(i) for i in nodesim1ip1])[::-1])

    print ("edgesiip1", edgesiip1[::-1])
    print ("edgesim1ip1", edgesim1ip1[::-1])
    print ("diff edges less 1 month", map(int.__sub__, edgesiip1, edgesim1ip1)[::-1])
    print ("% captured edges less 1 month", map(float.__div__, [float(i) for i in edgesiip1], [float(i) for i in edgesim1ip1])[::-1]) 

    # For top 10 onlys
    print ("\t TOP 10 NODES ")

    print ("nodesiip1Top10",  nodesiip1Top10[::-1])
    print ("nodesim1ip1Top10", nodesim1ip1Top10[::-1])
    print ("diff nodes top10 less 1 month", map(int.__sub__, nodesiip1Top10, nodesim1ip1Top10)[::-1])
    print ("% captured nodes less 1 month", map(float.__div__, [float(i) for i in nodesiip1Top10], [float(i) for i in nodesim1ip1Top10])[::-1])

    print ("edgesiip1Top10", edgesiip1Top10[::-1])
    print ("edgesim1ip1Top10", edgesim1ip1Top10[::-1])
    print ("diff edfes top10 less 1 month", map(int.__sub__, edgesiip1Top10, edgesim1ip1Top10)[::-1])
    print ("% captured edges less 1 month", map(float.__div__, [float(i) for i in edgesiip1Top10], [float(i) for i in edgesim1ip1Top10])[::-1])

    print("")
    print("FINNISHED " + str(datetime.now()))

    if (LOAD_MODE != 1):
        print("TOTAL TIME " + str(datetime.now() - t0))

    # Ending stats

    print("Number of analized lines [" + str(stats['nlines']) + "]")
    print(
        "Number of analized changelog blocks [" + str(stats['nBlocks']) + "]")
    print("Number of analized changelog blocks changing code files [" + str(
        stats['nBlocksChagingCode']) + "?]")
    print("Number of analized changelog blocks not changing code files (i.e. testCases)[" + str(
        stats['nBlocksNotChangingCode']) + "?]")
    print("Number of files affected by the commits reported by change log[" + str(
        stats['nChangedFiles']) + "]")


if __name__ == "__main__":
    main()

#! /usr/bin/env python3


# Scaps date, authors, affiliations and file changes from WebKit SVN Changelog
#
#


print("this is pyhton")

# scraplog save with serialzie
# TODO functions returning NetworkX graphs


try:
    import cPickle as pickle
except:
    import pickle


print("Executing " + str(sys.argv))

# Global parameters

networkOutput = "NetworkOutput.file1.CSV"
atributesOutput = "AtributesOutput.file2.CSV"
graphmlOutput = "NetworkFile.graphML"


# Global structures

# Keeps statistics of the scrappping
stats = {'nlines': 0, 'nBlocks': 0, 'nBlocksChagingCode': 0,
         'nBlocksNotChangingCode': 0, 'nChangedFiles': 0}

# Keeps data as inially scrapped [(date, email, affilition), [files changed]]
# The one that can be saved , the only data structure keeping date information
changeLogData = []

# Will keep agrregated data of authors that changed the same (file,[list of contributors changing it])
agreByFileContributors = {}


# Will keep agregated tuples of authors connecting due to working on a common file [(a-b),file)]

agreByConnWSF = []

# Will keep unique tuples of authors connected due to workin on common file. no repetitions for (a-b),(a-b) or (a-b),(b-a)
# Keeps unique collaborations and connections. [(a,b),(b,c),(a,c)]
uniqueConnections = []

# Will keep a dictionary author afiliation i.e affiliation[mike@google.com]=google.com
affiliations = {}

# Will keep a dictionary networked author afiliation i.e affiliation[mike@google.com]=google.com
# Drops authors that do not connect with others
networked_affiliations = {}


# For ibm ex
# ibm_email_domains =  ["au1.ibm.com","linux.vnet.ibm.com","br.ibm.com", "zurich.ibm.com", "us.ibm.com" ,"cn.ibm.com","il.ibm.com","de.ibm.com","ca.ibm.com"]
ibm_email_domains_prefix = ["au1", "linux",
                            "br", "zurich", "us", "cn", "il", "de", "ca"]

# TOP10 companies in OpenStack
top10 = ["rackspace", "nebula", "citrix", "redhat", "ibm", "hp",
         "cloudscaling", "mirantis", "vmware", "canonical", "intel"]


# Are we verbose?
DEBUG_MODE = 0

# Are we going to scraplog data?

SAVE_MODE = 0

# Are we starting with a ready to process stracplog saved previously in SAVE_MODE?
LOAD_MODE = 0


# Are we dealing with raw data from a git/svn log ?
RAW_MODE = 0


def getAffiliationFromEmail(email):
    "gets affiliation from an given email"

    # print ("getAffiliationFromEmail("+email+")")

    affiliation_pattern = re.compile('@(\w[\w\-]+)')
    match = affiliation_pattern.findall(email)

    if match == None or match == []:
        print("ERROR unable to extract affiliation from email. Wrong email format?")
        print("match=["+str(match)+"]")
        sys.exit()

    "implement an exception for IBM as their emails come from multiple domains"
    "au1.ibm.com linux.vnet.ibm.com br.ibm.com zurich.ibm.com us.ibm.com cn.ibm.com il.ibm.com"

    if 'ibm' in email:
        # print ("Warning, ibm affiliation from multiple domains")

        if match[0] not in ibm_email_domains_prefix:
            print(
                "ERROR, ibm affilition from an unknow domain, check ibm_email_domain glob")
            print("march=["+str(match[0])+"]")
            sys.exit()

        # print ("affiliation(" + email + ")=[ibm]")
        return "ibm"

    affiliation = match[0]
    # print ("affiliation(" + email + ")=["+affiliation+"]")
    return affiliation


#
# Extract date, nane and email
# WK Sample line
# ==Jenkins;jenkins@review.openstack.org;Thu Feb 20 03:56:00 2014 +0000==
# Format obtained by running: $git log --pretty=format:"==%an;%ae;%ad=="  --name-only
# Returned result would be ('Thu Feb 20 03:56:57 2014','Jenkins', 'jenkins@review.openstack.org',

def getDateEmailAffiliation(line):
    "gets the ==Name;email;date=="
    # print ("	getting name, email, date, affilication from the line["+line+"]")

    name_pattern = re.compile(
        '^\\=\\=(.+);(.+);(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
    match = name_pattern.findall(line)

    # print ("match=" + str(match))

    if match == None or match == []:

        ## expeptions handling ##
        # "==name;email;date== is the most common pattern from a git log"
        # "however some entries are name less taking a different format:"
        atIndex = line.find('@')

        # Exception 1: Developer added name and email to name
        # ==Brad McConnell bmcconne@rackspace.com;;Tue Sep 20 06:50:27 2011 +0000==
        if ';;' in line and ' ' in line[0:atIndex] and '==Launchpad' not in line:
            print("WARNING exceptional code commit header Exception 1 ")
            print("LINE number "+str(stats['nlines'])+" [" + line +
                  "] double ;; <- name and email together on commit header")

            name_pattern = re.compile(
                '^\\=\\=(.*)\ (.+@.+);;(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
            match = name_pattern.findall(line)
            print("match=["+str(match)+"]")

        # Exception 2: If there is not name in the commit
        # there is no spaces before the email (@)
        elif ' ' not in line[0:atIndex] and '==Launchpad' not in line:

            print("WARNING exceptional code commit header Exception 2 ")
            print("LINE number "+str(stats['nlines']) +
                  " [" + line + "] no name, just an email")

            name_pattern = re.compile(
                '^\\=\\=(.+@.+);;(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
            tmpmatch = name_pattern.findall(line)

            # Workarround by adding name from the email
            # Warned about this name with name as  name?
            match = [(line[2:line.find('@')], tmpmatch[0]
                      [0], tmpmatch[0][1], tmpmatch[0][2])]

        # Exception 3: Launchpad Translations
        # Drop as it is a bot
        # ==Launchpad Translations on behalf of nova-core;;Sat Sep 3 05:50:53 2011 +0000
        elif "==Launchpad" in line:
            print("WARNING exceptional code commit header Exception 3 ")
            print("LINE number " +
                  str(stats['nlines'])+" [" + line + "] Lauchpad bot")

            name_pattern = re.compile(
                '^\\=\\=(.+);;(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
            tmpmatch = name_pattern.findall(line)

            # Workarround by simpli addign it as a commiter
            # Warned about this name with name as  Lauchpad_bot!
            match = [("Lauchpad_bot!", "Lauchpad@bot.bot", tmpmatch[0][1])]

        # Exception 4:
        # match=[('Jenkins', 'jenkins@review.openstack.org', 'Thu Jan 30 21:21:23 2014', '+')]
        #

        # anything else ERROR with imput or this code
        else:
            print(
                "Error, unable to extract developer name, email or date from commit block")
            print("Regular expression not captured")
            print("Line=["+line+"]")
            sys.exit()

    name = match[0][0]
    # print("name=["+name+"]")

    "get the email"
    email = match[0][1]
    # print("email=["+email+"]")

    # Verify the email pattern

    email_pattern = re.compile('([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)')

    if (email_pattern.search(email) == None):
        print("WARNING commiter ["+email+"] have an invalidName")
        print("Adding .com? to the end")
        email += ".com?"

    "gets the date"
    date = match[0][2]
    # print("date=["+date+"]")

    affiliation = getAffiliationFromEmail(email)

    return (date, email, affiliation)


"return a list of files modified by a commit log"


def findFilesOnBlock(block):
    # print ("finding files on block [" + str(block) + "]" )

    linesWithCode = []

    for line in block:
        # print ("line=["+line+"]")
        if line == []:
            break
        if line == '\n':
            break
        "append the file path (removing the last caracted \n)"
        linesWithCode.append(line[:-1])
        stats['nBlocksChagingCode'] += 1

    # print ("Lines of changed code:")
    # for line in linesWithCode:
    #    print (line)

    return linesWithCode


# processes a bloc of a change log (a developer change)
def scrapBlock(block):
    # print ("Processing [" + str(block) + "]")

    # Check if it is an empty block / change
    if len(block) == 0:
        print("ERROR: block / changelog to scrap is empty")
        return False

    firstLine = block[0]

    # check if the block starts with a date
    if not firstLine[0:2] == '==':
        print("ERROR: Invalid block / not starting with a date ")
        return False

    daEmAf = getDateEmailAffiliation(block[0])

    # print ("")
    # print (daEmAf)

    # What file where affected by the change log
    changedFiles = findFilesOnBlock(block[1:])

    # Save it in changeLogData
    # (date, email, affilition), [files changed])

    # GIT log changes that do not change files are irelevant
    if changedFiles == []:
        return False

    changeLogData.append((daEmAf, changedFiles))


# filter/slice the changeLogData by data
# Aproach: simply removes blocks wich date does not fit between a startDate and endDate
# Format end date should be  "Oct 11 2014" "MMM DD YYYY"

def filterChangeLogDataByDate(startDate, endDate):
    print(
        "Filtering ChangeLogData for  dates between ["+str(startDate)+"] and ["+str(endDate)+"]")

    # are they dates?

    if type(startDate) != datetime or type(endDate) != datetime:
        print("ERROR: invalide data type, not a valid datetime object")
        sys.exit()

    # is channge log empty ?

    if (len(changeLogData) < 1):
        print("ERROR: changeLogData is empty")

    # if end date after start date?

    res = []

    for change in changeLogData:
        date = change[0][0]
        email = change[0][1]
        af = change[0][2]
        files = change[1]

        # print ("On " + date + " " + email + " from " + af + " worked on the following files:" )

        # print ("ChangeLogDateString=["+date+"]")
        # weekday =date[0:3]
        # month = date[4:7]
        # day = date[8:10]
        # time = date[11:19]
        # year = date[20:24]

        # Get weekday month day time year  with regular expressions
        name_pattern = re.compile('(.+)\s(.+)\s(\d+)\s(.+)\s(\d+)')
        match = name_pattern.findall(date)

        # print ("date_ match=["+str(match)+"]")

        # If there is no regulae expression match
        if (match == []):
            print("ERROR: Change log date is not on proper format")
            print("date_ match=["+str(match)+"]")
            sys.exit()

        weekday = match[0][0]
        month = match[0][1]
        day = match[0][2]
        time = match[0][3]
        year = match[0][4]

        # print ("ChangeLogDateCapture=["+weekday+ " " + month+ " " + day + " " + time + " " + year + "]")

        # date(year, month, day) --> date object
        day = int(day)
        year = int(year)

        if month == "Jan":
            month = 1
        elif month == "Feb":
            month = 2
        elif month == "Mar":
            month = 3
        elif month == "Apr":
            month = 4
        elif month == "May":
            month = 5
        elif month == "Jun":
            month = 6
        elif month == "Jul":
            month = 7
        elif month == "Aug":
            month = 8
        elif month == "Sep":
            month = 9
        elif month == "Oct":
            month = 10
        elif month == "Nov":
            month = 11
        elif month == "Dec":
            month = 12
        else:
            print("ERROR invalide month spec: unable to extract date")
            sys.exit()
        changeLogDate = datetime(year, month, day)

        # print("changeLogDate=["+ str(changeLogDate)+"]")

        if (changeLogDate < startDate) or changeLogDate > endDate:
            # print("drop change log due date")
            continue
        else:
            # print("changeLogDate=["+ str(changeLogDate)+"] is between ["+str(startDate)+"] and ["+str(endDate)+"]" )
            res.append(change)

    return res

# print the changeLogData data scraped


def print_changeLogData():
    global changeLogData

    print("")
    print("Printing change log data ... from the earliast change to the oldest change")
    for change in changeLogData:
        date = change[0][0]
        email = change[0][1]
        af = change[0][2]
        files = change[1]

        print("On " + date + " " + email + " from " +
              af + " worked on the following files:")

        for file in files:
            print("[" + file + "]")


# save the changeLogData data scraped into a filename
def save_changeLogData(filename):

    global SAVE_MODE
    global changeLogData

    print("")
    print("TODO")
    print('Saving changeLog to file ' + str(filename) + '')

    if (SAVE_MODE != 1):
        print ("ERROR, not in saving mode")
        sys.exit()

    with open(filename, 'wb') as fp:
        pickle.dump(changeLogData, fp)

    print ("DONE changelog saved in ", filename, "NICE :)")
    sys.exit()


# load and return	 the changeLogData data scraped into a filename
def load_changeLogData(filename):
    print ("")
    print ("TODO")
    print ("Loading changeLog from  file [", filename, "]")

    with open(filename, 'rb') as fp:
        changeLogData = pickle.load(fp)

    return changeLogData


# print the agreByFileContributors agreefation resuting by  agregateByFileItsContributors
def print_agreByFileContributors():
    print("")
    print("Printing files affected by commits on the changelLog  ... and developers resposable for it")

    for file in agreByFileContributors:
        fileName = file
        authorEmails = agreByFileContributors[file]

        if (len(authorEmails) == 0):
            print("ERROR: File without contrubutors !!")
            exit()

        print("The file " + fileName +
              "was changed by following [" + str(len(authorEmails)) + "]contributors")

        for email in authorEmails:
            print("[" + email + "]")


# print a list of contributor connected to each other cause they worked on a common files
def print_agreByConnWSF():
    # print (str(agreByConnWSF))

    print("")
    print("Printing tuples of authors that collaborated + file that they contribute together too")
    # format more a less like this [(a-b),file)]

    for connection in agreByConnWSF:
        contributorsPair = connection[0]
        fileName = connection[1]

        print("Contributors " + str(contributorsPair) +
              " connected by collaborating on file [" + fileName + "]")


# Agregate by file and its contributors
def agregateByFileItsContributors():
    print("")
    print("Agregating data: for each file what are the contributors")

    # Agregated  by files and stores agregation in global agreByFileContributors   #
    # (file,[list of contributors changing it])

    filesVisited = []

    for change in changeLogData:
        email = change[0][1]
        files = change[1]

        for file in files:
            # If its a new file
            if file not in filesVisited:
                filesVisited.append(file)
                agreByFileContributors[file] = []
                agreByFileContributors[file].append(email)
            # if a file that that was changed before
            elif file in filesVisited:
                # add a new author to the list of authors that changed the file
                if email not in agreByFileContributors[file]:
                    agreByFileContributors[file].append(email)
            else:
                print("ERROR: list of file not visited")
                exit()

    stats['nChangedFiles'] = len(filesVisited)

# Get tuple of authors getting connect due to working on a common file
# [(a-b),file)]


def getContributorsConnectionsTuplesWSF():

    # Interates over the list of files and its contributors
    print("")
    print("Getting tuples of contributors that coded/contributed on the same file")

    # Stores contributors connected by working in the same file
    contributorsConnectedbyFile = []

    connectedByFile = []

    for change in agreByFileContributors:
        contributors = agreByFileContributors[change]
        for contributor in contributors:
            connectedByFile.append(contributor)

        contributorsConnectedbyFile.append((connectedByFile, change))
        connectedByFile = []

    # Print contributors connect by working in same file i.e. [(['cgarcia@igalia.com', 'jinwoo7.song@samsung.com'], '* Source/cmake/OptionsEfl.cmake:')
    # print (contributorsConnectedbyFile)

    for connection in contributorsConnectedbyFile:
        # print ("interating "+ str(connection))

        contributors = connection[0]
        files = connection[1]

        if len(contributors) == 0:
            print("ERROR Not file changes can have 0  contributors")
            exit()
        elif len(contributors) == 1:
            "One man file .. no connection"
            # print ("WARNING one man one file")
        elif len(contributors) > 1:
            "add all combinations of contributors to global agreByConnWSF "
            for connection in itertools.combinations(contributors, 2):
                agreByConnWSF.append((connection, files))


# Get a list of unique tubles of developers that collaborate. List of tubles with linked nodes.
def getUniqueConnectionsTuplesList(tuplesListWithFile):

    # verify arguments data
    # verify tuplesListWithFile

    if type(tuplesListWithFile) != list:
        print("\tERROR collaboration tuplesList is not a list !!")
        exit()
    if len(tuplesListWithFile) < 1:
        print("\tERROR collaboration tuplesList is empty !!")
        exit()

    seen = {}

    for connection in tuplesListWithFile:
        ((author1, author2), fileName) = connection

        # Do not consider if author1 or author2 been already connected 1->2 or 2-< 1
        if (author1, author2) and (author2, author1) not in seen:
            seen[(author1, author2)] = True

    return list(seen.keys())


# Pring unique connections - lust of tuples [(a,b),(b.c)]
def print_unique_connections():
    print("\nPrinting author unique collaborations (straps repeated collaborations):\n ")

    if len(uniqueConnections) < 1:
        print("Error, there are no unique connections between developers that should be printed")
        exit()

    print("\t------/------\n")
    for (dev1, dev2) in uniqueConnections:
        print("\t" + dev1 + " collaborated  with " + dev2)
    print(
        "\t TOTAL number of unique collaborations =[" + str(len(uniqueConnections)) + "]")
    print("\t------/------\n")


# Get the affiliations of all authors commiting code
# Author emails is its unique identifier
def getAffiliations():
    print("Getting author affiliations from their unique email in changeLogData")
    for change in changeLogData:
        email = change[0][1]
        affiliations[email] = getAffiliationFromEmail(email)

    print("Getting networked-author affiliations from their unique email in changeLogData")
    for connection in agreByConnWSF:
        contributorsPair = connection[0]
        fileName = connection[1]

        (contr1, contr2) = contributorsPair
        networked_affiliations[contr1] = getAffiliationFromEmail(contr1)
        networked_affiliations[contr2] = getAffiliationFromEmail(contr2)


# Pring the affiliation of each author
def print_Affiliations():
    print("\nPrinting author affiliations:\n ")
    for author in affiliations:
        print("\t" + author + " is affiliatied with " + affiliations[author])

    print("\nPrinting network-author affiliations:\n ")
    for author in networked_affiliations:
        print("\t" + author + " is affiliatied with " + affiliations[author])

# Reprocess all variables from changeLogData


def reprocess():

    print("\n Reprocessing changeLogData")

    global agreByFileContributors
    global agreByConnWSF
    global affiliations
    global networked_affiliations
    global uniqueConnections

    agreByFileContributors = {}
    agreByConnWSF = []
    affiliations = {}
    networked_affiliations = {}

    # Reprocess with the new changeLogData
    agregateByFileItsContributors()
    getContributorsConnectionsTuplesWSF()
    uniqueConnections = getUniqueConnectionsTuplesList(agreByConnWSF)
    getAffiliations()


# MAIN

def main():

    global changeLogData
    global agreByFileContributors
    global agreByConnWSF
    global affiliations
    global networked_affiliations
    global uniqueConnections

    global SAVE_MODE
    global RAW_MODE
    global LOAD_MODE
    global DEBUG_MODE

    # Process the arguments
    # -s for serialized save (already provessed changeLog)
    # -r for extrating raw changelog git log

    parser = argparse.ArgumentParser(
        description='Scrap some chagelog to create networks/graphs for research purpses')
    parser.add_argument('-l', '--lser', action='store', type=str,
                        help='loads and processes an serialized changelog')
    parser.add_argument('-r', '--raw', action='store',
                        type=str, help='processes from a raw git changelog')
    parser.add_argument('-s', '--sser', action='store', type=str,
                        help='processses from a raw git changelog and saves it into a serialized changelog. Requires -r for imput')
    parser.add_argument("-v", "--verbose",
                        help="increase output verbosity", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        print("verbosity turned on")
        DEBUG_MODE = 1

    if args.lser:
        print (" loanding and processing [lser=", args.lser, "]")
        print ("not implmented yet")
        LOAD_MODE = 1
        RAW_MODE = 0
        SAVE_MODE = 0
    elif args.sser and args.raw:
        print (" processing [raw=", args.raw, "]", " and saving [sser=", args.sser, "]")
        SAVE_MODE = 1
        RAW_MODE = 1
        LOAD_MODE = 0
    elif args.raw:
        RAW_MODE = 1
        LOAD_MODE = 0
        SAVE_MODE = 0
        print (" processing [raw=", args.raw, "]")
    else:
        print ("unrecognized argumets ... see --help")
        sys.exit()

    if RAW_MODE == 1:
        # if we are not in load mode, we need to strap the log
        print ("Scrapping changeLog from ", args.raw)
        t0 = datetime.now()
        print("STARTING the scrap of changeLog file " +
              args.raw + " on " + str(t0))

        # Opening the files

        workfile = args.raw

        f = open(workfile, 'r')

        # Read line by line
        # Keep also the stats
        # Detect blocks ... process them

        # Will save a commit block lines : From == to next ==

        lines = f.readlines()

        # Break everything in blocks and grab the data in ChangLogData

        for line in lines:
            # print("reading line [" + line +"]")

            # Ignore empty lines
            if line == "\n":
                continue

            # Updates the count of number of lines in the file
            stats['nlines'] += 1

            # if starts with '==' we have a new commit-block
            if line[0:2] == '==':
                # Process last temporay block and the cleans it
                if (stats['nBlocks'] != 0):
                    scrapBlock(tmpBlock)
                tmpBlock = []
                tmpBlock.append(line)

                # Updates the could of change log blocks
                stats['nBlocks'] += 1
                continue
            # then, eithier is a file or an error
            elif not line[0:2] == '==':
                # must be a file path
                # having a / a . or stenlen bigger than 5
                if '.' in line or '/' in line or len(line) >= 5:
                    tmpBlock.append(line)
                    continue
                else:
                    print(
                        "ERROR: not a file path. Commit blocs not starting with == must be file paths")
                    print(
                        "ERROR processing line ["+str(stats['nlines'])+"]" + "line=["+line+"]")
                    sys.exit()
            else:
                print("ERROR: Something wrong with the changeLog blocks L 107")
                sys.exit()
                break

    if (RAW_MODE == 1):
        print("\n:)1st SUCESS Data scraped from changlog files (stored in ChangeLogData data structure)")
        # print_changeLogData()

    elif (LOAD_MODE == 1):
        changeLogData = load_changeLogData(args.lser)
        print ("1st SUCESS Change log loaded from ", args.lser, " ")

        if len(changeLogData) < 1:
            print( "to small loaded change log, len <1")
            sys.exit()

        # print_changeLogData()

    else:
        print ("ERROR: In what mode are we afer all= No SAVE,LOAD or RAW")
        sys.exit()

    if (SAVE_MODE == 1):
        print ("Saving file")
        save_changeLogData(args.sser)

    # Agregate by file ...

    agregateByFileItsContributors()
    print("\n:)2nd SUCESS2 Data agregated by files and its contributors")
    # print_agreByFileContributors()

    # agreate list of authors that worked on the each files

    getContributorsConnectionsTuplesWSF()
    print("\n:) 3rd SUCESS tubles of authors that collaborated (coded in the same source code file) were generated")
    # print_agreByConnWSF()

    # agreate an list of authors that worked on the each files (do not repeat author tuples)
    # For getting unique edges/collaborations (do not include repetitions of the same collaborations)
    uniqueConnections = getUniqueConnectionsTuplesList(agreByConnWSF)
    print("\n:) 4rd SUCESS unique authors that collaborated tuples (coded in the same source code file) were generated")
    # print_unique_connections()

    # for every author, get its affiliation. result will be saved in the  affiliation global dictionart
    getAffiliations()
    # print_Affiliations()

    print("\n:) 5rd SUCESS got author -> affiliation dictionary")

    #### UCI NET format ####
    #### Used for WebKit SIGMISCPT paper ####
    # Export to data files to Ucitnet format
    # Both networkOutput and atributesOutput are global atributes defined on the header

    # exportLogData.createNetworkFileCSV(agreByConnSF, networkOutput)
    # exportLogData.createAtributesFileCSV(changeLogData, atributesOutput )
    # print ("\n:) UciNet export SUCESS exported UCInet network to file:"+networkOutput+" and its attributes to file:"+atributesOutput)

    # GRAPH ML#

    # Create an GraphML file

    # exportLogData.createGraphML(uniqueConnections,networked_affiliations, graphmlOutput)
    # print ("\n:) GRAPHML export SUCESS exported GraphML network to file:"+graphmlOutput)

    # print ("\t\n:) GRAPHML export Number of nodes/authors = " + str(len(affiliations)))
    # print ("\t\n:) GRAPHML export Number of networked nodes/authors = " + str(len(networked_affiliations)))

    # print ("\t\n:) GRAPHML export Number of nodes/atribute/affiliations  = " + str(networkMeasures.getNumberOfAffiliations(affiliations)))
    # print ("\t\n:) GRAPHML export Number of networked nodes/atribute/affiliations  = " + str(networkMeasures.getNumberOfAffiliations(networked_affiliations)))
    # print ("\t\n:) GRAPHML export Number of edges/collaborations (include repetitions of the same collaboration) = " + str(networkMeasures.getNumberOfEdges(agreByConnWSF)))

    # print ("\t\n:) GRAPHML export Number of unique edges/collaborations (do not include repetitions of the same collaborations) = " + str(networkMeasures.getNumberOfUniqueEdges(agreByConnWSF)))

    # print ("\t\n:) GRAPHML export Number of unique edges/collaborations (do not include repetitions of the same collaborations) = " + str(len(uniqueConnections)))

    # Create an graphML file filtered by company
    # In this case_ red_hat,enovance and intel
    # Others are ignored, not grouped
    # exportLogData.createGraphML_filterByAffiliation(uniqueConnections,networked_affiliations, "FilteredByCompanies"+ graphmlOutput , ["red_hat","enovance", "intel", "ibm", "hp","mirantis","nebula","vmware" ])

    print("\n")

    sizeOriginalChangeLogData = len(changeLogData)

    # Filter changeLogByDate
    # changeLogData=filterChangeLogDataByDate (datetime(2014,1,1), datetime (2014,6,1))

    # Filter nothing
    # changeLogData=filterChangeLogDataByDate (datetime(1900,1,1), datetime (2020,1,1))

    # Filter changeLogData for dates between Xmas and valentines
    # FOR TESTING PURPOSES ONLY

    # print "Number of edges overall[", len(uniqueConnections), "]"
    # XmasDate=datetime(2012,12,15)
    # valentinesDate=datetime(2014,2,14)
    # changeLogData=filterChangeLogDataByDate (datetime(2014,1,1), datetime (2014,6,1))
    # reprocess()
    # print "Number of edges between Xmas and Fall[", len(uniqueConnections), "]"

    print("\nSegmenting by release \n\
        0 Icehouse released Apr 17, 2014 \n\
        1 Havana  released Oct 17, 2013 \n\
        2 Grizzly released Apr 4, 2013 \n\
        3 Folsom  released Sep 27, 2012 \n\
        4 Essex released Apr 5, 2012 \n\
        5 Diablo released Sep 22, 2011 \n\
        6 Cactus released Apr 15, 2011 \n\
        7 Bexar released Feb 3, 2011  \n\
        8 Austin released Oct 21, 2010\n")

    releases = []

    releases.append(("Icehouse", datetime(2014, 4, 17)))
    releases.append(("Havana", datetime(2013, 10, 17)))
    releases.append(("Grizzly", datetime(2013, 4, 4)))
    releases.append(("Folsom", datetime(2012, 9, 27)))
    releases.append(("Essex", datetime(2012, 4, 5)))
    releases.append(("Diablo", datetime(2011, 9, 22)))
    releases.append(("Cactus", datetime(2011, 4, 15)))
    releases.append(("Bexar", datetime(2011, 2, 3)))
    releases.append(("Austin", datetime(2010, 10, 21)))

    tmpBkupLogData = changeLogData

    # Creates logitudinal network segments for open-stack
    # for i in range (len(releases)-1):
    #    (release_name, release_date) = releases[i]
    #    prior_release_date= releases[i+1][1]
    #    print ("\t --- Generating grapth["+ release_name+"]" + "from ["+  str(prior_release_date) +"] and rel on [" + str(release_date) + "]\n")
    #    print ("\t --- Filtering change log data for [" + str(prior_release_date)+ "] <--> ["+ str(release_date)+"]")
    #    changeLogData=filterChangeLogDataByDate (prior_release_date,release_date)
    #    reprocess()
    #    print("\t --- Filtering by date is done. [" + str (sizeOriginalChangeLogData-len(changeLogData)) +"] changeLogs removed due their change date")
    #    exportLogData.createGraphML_filterByAffiliation(uniqueConnections,networked_affiliations, release_name + graphmlOutput , top10)
    #    print("\t --- Network for " + release_name+ " release created at " + release_name + graphmlOutput + " for " + str(top10) + "\n")
    #    changeLogData = tmpBkupLogData

    # Get the number of edges betwen releases i and i+1

    nodesiip1 = []
    nodesiip1Top10 = []
    edgesiip1 = []
    edgesiip1Top10 = []

    for i in range(len(releases)-1):
        (release_name, release_date) = releases[i]
        prior_release_date = releases[i+1][1]
        print("\t --- Filtering change log data for [" + str(
            prior_release_date) + "] <--> [" + str(release_date)+"]")
        changeLogData = filterChangeLogDataByDate(
            prior_release_date, release_date)
        reprocess()
        print("\t --- Filtering by date is done. [" + str(sizeOriginalChangeLogData-len(
            changeLogData)) + "] changeLogs removed due their change date")

        nnodes = len(
            JISA2015specificAnalysis.getNodesBetweenDatesInConnList(uniqueConnections))
        nnodestop10 = len(JISA2015specificAnalysis.getNodesBetweenDates4SelectedFirmsDatesInConnList(
            uniqueConnections, networked_affiliations, top10))
        nedges = len(uniqueConnections)
        nedgestop10 = len(JISA2015specificAnalysis.getConnectionsAmongTop10Only(
            uniqueConnections, networked_affiliations, top10))

        print ("Number of nodes between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodes) 
        print ("Number of nodes (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodestop10) 

        print ("Number of edges between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nedges, ";")
        print ("Number of edges (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nedgestop10, ";") 

        nodesiip1.append(nnodes)
        nodesiip1Top10.append(nnodestop10)
        edgesiip1.append(nedges)
        edgesiip1Top10.append(nedgestop10)

        changeLogData = tmpBkupLogData

        # for debug only
        # print the edges among top10 for first release
        # print "pringing edged for reease", release_name , ":"
        # top10con = getConnectionsAmongTop10Only(uniqueConnections)
        # for edge in top10con:
        # (a,b) = edge
        # if top10con.count(edge) != 1:
        # print "ERROR:Not a single edge:"
        # print "top10con.count(edge)=[", top10con.count(edge),"] --> repeated edges"
        # print "edge in question:", edge
        # sys.exit()
        # if (b,a) in top10con:
        # print "ERROR:Not a single edge:"
        # print "top10con.count(edge)=[", top10con.count((b,a)),"] --> repeated edges (inverse relationship already accounted)"
        # print "edge in question:", edge, " and its inverse " , (b,a)
        # sys.exit()
        #
        # sys.exit()

    # Get the number of nodes and edges betwen releases i-1month and i+1
    nodesim1ip1 = []
    nodesim1ip1Top10 = []
    edgesim1ip1 = []
    edgesim1ip1Top10 = []

    releasesm1 = []
    for release in releases:
        (releasename, date) = release

        # for 4 weeks / 1 month
        # releasesm1.append((releasename, date - relativedelta(months=1)))

        # for 3 weeks
        # releasesm1.append((releasename, date - relativedelta(weeks=3)))

        # for 2 weeks
        # releasesm1.append((releasename, date - relativedelta(weeks=2)))

        # for 1 week
        releasesm1.append((releasename, date - relativedelta(weeks=1)))

    # Get the number of edges betwen releases i and i+1
    for i in range(len(releasesm1)-1):
        (release_name, release_date) = releases[i]
        prior_release_date = releasesm1[i+1][1]
        print("\t --- Filtering change log data for [" + str(
            prior_release_date) + "] <--> [" + str(release_date)+"]")
        changeLogData = filterChangeLogDataByDate(
            prior_release_date, release_date)
        reprocess()
        print("\t --- Filtering by date is done. [" + str(sizeOriginalChangeLogData-len(
            changeLogData)) + "] changeLogs removed due their change date")

        nnodes = len(
            JISA2015specificAnalysis.getNodesBetweenDatesInConnList(uniqueConnections))
        nnodestop10 = len(JISA2015specificAnalysis.getNodesBetweenDates4SelectedFirmsDatesInConnList(
            uniqueConnections, networked_affiliations, top10))

        nedges = len(uniqueConnections)
        nedgestop10 = len(JISA2015specificAnalysis.getConnectionsAmongTop10Only(
            uniqueConnections, networked_affiliations, top10))

        print ("Number of nodes between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodes)
        print ("Number of nodes (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodestop10)

        print ("Number of edges between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nedges, ";")
        print ("Number of edges (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nedgestop10, ";")

        nodesim1ip1.append(nnodes)
        nodesim1ip1Top10.append(nnodestop10)
        edgesim1ip1.append(nedges)
        edgesim1ip1Top10.append(nedgestop10)
        changeLogData = tmpBkupLogData

    # print releases name
    # Not that they are in reverse cronological order, therefore ::-1
    rname = []
    for r in releases:
        (name, nc) = r
        rname.append(name + ";")
    print ("rname", rname[::-1])

    # For all nodes
    print ("\t ALL NODES ")

    print ("nodesiip1", nodesiip1[::-1])
    print ("nodesiim1p1", nodesim1ip1[::-1])
    print ("diff capture nodes less 1 month", map(int.__sub__, nodesiip1, nodesim1ip1)[::-1])
    print ("% captured nodes less 1 month", map(float.__div__, [float(i) for i in nodesiip1], [float(i) for i in nodesim1ip1])[::-1])

    print ("edgesiip1", edgesiip1[::-1])
    print ("edgesim1ip1", edgesim1ip1[::-1])
    print ("diff edges less 1 month", map(int.__sub__, edgesiip1, edgesim1ip1)[::-1])
    print ("% captured edges less 1 month", map(float.__div__, [float(i) for i in edgesiip1], [float(i) for i in edgesim1ip1])[::-1])

    # For top 10 onlys
    print ("\t TOP 10 NODES ")

    print ("nodesiip1Top10",  nodesiip1Top10[::-1])
    print ("nodesim1ip1Top10", nodesim1ip1Top10[::-1])
    print ("diff nodes top10 less 1 month", map(int.__sub__, nodesiip1Top10, nodesim1ip1Top10)[::-1])
    print ("% captured nodes less 1 month", map(float.__div__, [float(i) for i in nodesiip1Top10], [float(i) for i in nodesim1ip1Top10])[::-1])

    print ("edgesiip1Top10", edgesiip1Top10[::-1])
    print ("edgesim1ip1Top10", edgesim1ip1Top10[::-1])
    print ("diff edfes top10 less 1 month", map(int.__sub__, edgesiip1Top10, edgesim1ip1Top10)[::-1])
    print ("% captured edges less 1 month", map(float.__div__, [float(i) for i in edgesiip1Top10], [float(i) for i in edgesim1ip1Top10])[::-1])

    print("")
    print("FINNISHED " + str(datetime.now()))

    if (LOAD_MODE != 1):
        print("TOTAL TIME " + str(datetime.now() - t0))

    # Ending stats

    print("Number of analized lines [" + str(stats['nlines']) + "]")
    print(
        "Number of analized changelog blocks [" + str(stats['nBlocks']) + "]")
    print("Number of analized changelog blocks changing code files [" + str(
        stats['nBlocksChagingCode']) + "?]")
    print("Number of analized changelog blocks not changing code files (i.e. testCases)[" + str(
        stats['nBlocksNotChangingCode']) + "?]")
    print("Number of files affected by the commits reported by change log[" + str(
        stats['nChangedFiles']) + "]")


if __name__ == "__main__":
    main()
#! /usr/bin/env python3


# Scaps date, authors, affiliations and file changes from WebKit SVN Changelog
#
#


print("this is pyhton")

# scraplog save with serialzie
# TODO functions returning NetworkX graphs


try:
    import cPickle as pickle
except:
    import pickle


print("Executing " + str(sys.argv))

# Global parameters

networkOutput = "NetworkOutput.file1.CSV"
atributesOutput = "AtributesOutput.file2.CSV"
graphmlOutput = "NetworkFile.graphML"


# Global structures

# Keeps statistics of the scrappping
stats = {'nlines': 0, 'nBlocks': 0, 'nBlocksChagingCode': 0,
         'nBlocksNotChangingCode': 0, 'nChangedFiles': 0}

# Keeps data as inially scrapped [(date, email, affilition), [files changed]]
# The one that can be saved , the only data structure keeping date information
changeLogData = []

# Will keep agrregated data of authors that changed the same (file,[list of contributors changing it])
agreByFileContributors = {}


# Will keep agregated tuples of authors connecting due to working on a common file [(a-b),file)]

agreByConnWSF = []

# Will keep unique tuples of authors connected due to workin on common file. no repetitions for (a-b),(a-b) or (a-b),(b-a)
# Keeps unique collaborations and connections. [(a,b),(b,c),(a,c)]
uniqueConnections = []

# Will keep a dictionary author afiliation i.e affiliation[mike@google.com]=google.com
affiliations = {}

# Will keep a dictionary networked author afiliation i.e affiliation[mike@google.com]=google.com
# Drops authors that do not connect with others
networked_affiliations = {}


# For ibm ex
# ibm_email_domains =  ["au1.ibm.com","linux.vnet.ibm.com","br.ibm.com", "zurich.ibm.com", "us.ibm.com" ,"cn.ibm.com","il.ibm.com","de.ibm.com","ca.ibm.com"]
ibm_email_domains_prefix = ["au1", "linux",
                            "br", "zurich", "us", "cn", "il", "de", "ca"]

# TOP10 companies in OpenStack
top10 = ["rackspace", "nebula", "citrix", "redhat", "ibm", "hp",
         "cloudscaling", "mirantis", "vmware", "canonical", "intel"]


# Are we verbose?
DEBUG_MODE = 0

# Are we going to scraplog data?

SAVE_MODE = 0

# Are we starting with a ready to process stracplog saved previously in SAVE_MODE?
LOAD_MODE = 0


# Are we dealing with raw data from a git/svn log ?
RAW_MODE = 0


def getAffiliationFromEmail(email):
    "gets affiliation from an given email"

    # print ("getAffiliationFromEmail("+email+")")

    affiliation_pattern = re.compile('@(\w[\w\-]+)')
    match = affiliation_pattern.findall(email)

    if match == None or match == []:
        print("ERROR unable to extract affiliation from email. Wrong email format?")
        print("match=["+str(match)+"]")
        sys.exit()

    "implement an exception for IBM as their emails come from multiple domains"
    "au1.ibm.com linux.vnet.ibm.com br.ibm.com zurich.ibm.com us.ibm.com cn.ibm.com il.ibm.com"

    if 'ibm' in email:
        # print ("Warning, ibm affiliation from multiple domains")

        if match[0] not in ibm_email_domains_prefix:
            print(
                "ERROR, ibm affilition from an unknow domain, check ibm_email_domain glob")
            print("march=["+str(match[0])+"]")
            sys.exit()

        # print ("affiliation(" + email + ")=[ibm]")
        return "ibm"

    affiliation = match[0]
    # print ("affiliation(" + email + ")=["+affiliation+"]")
    return affiliation


#
# Extract date, nane and email
# WK Sample line
# ==Jenkins;jenkins@review.openstack.org;Thu Feb 20 03:56:00 2014 +0000==
# Format obtained by running: $git log --pretty=format:"==%an;%ae;%ad=="  --name-only
# Returned result would be ('Thu Feb 20 03:56:57 2014','Jenkins', 'jenkins@review.openstack.org',

def getDateEmailAffiliation(line):
    "gets the ==Name;email;date=="
    # print ("	getting name, email, date, affilication from the line["+line+"]")

    name_pattern = re.compile(
        '^\\=\\=(.+);(.+);(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
    match = name_pattern.findall(line)

    # print ("match=" + str(match))

    if match == None or match == []:

        ## expeptions handling ##
        # "==name;email;date== is the most common pattern from a git log"
        # "however some entries are name less taking a different format:"
        atIndex = line.find('@')

        # Exception 1: Developer added name and email to name
        # ==Brad McConnell bmcconne@rackspace.com;;Tue Sep 20 06:50:27 2011 +0000==
        if ';;' in line and ' ' in line[0:atIndex] and '==Launchpad' not in line:
            print("WARNING exceptional code commit header Exception 1 ")
            print("LINE number "+str(stats['nlines'])+" [" + line +
                  "] double ;; <- name and email together on commit header")

            name_pattern = re.compile(
                '^\\=\\=(.*)\ (.+@.+);;(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
            match = name_pattern.findall(line)
            print("match=["+str(match)+"]")

        # Exception 2: If there is not name in the commit
        # there is no spaces before the email (@)
        elif ' ' not in line[0:atIndex] and '==Launchpad' not in line:

            print("WARNING exceptional code commit header Exception 2 ")
            print("LINE number "+str(stats['nlines']) +
                  " [" + line + "] no name, just an email")

            name_pattern = re.compile(
                '^\\=\\=(.+@.+);;(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
            tmpmatch = name_pattern.findall(line)

            # Workarround by adding name from the email
            # Warned about this name with name as  name?
            match = [(line[2:line.find('@')], tmpmatch[0]
                      [0], tmpmatch[0][1], tmpmatch[0][2])]

        # Exception 3: Launchpad Translations
        # Drop as it is a bot
        # ==Launchpad Translations on behalf of nova-core;;Sat Sep 3 05:50:53 2011 +0000
        elif "==Launchpad" in line:
            print("WARNING exceptional code commit header Exception 3 ")
            print("LINE number " +
                  str(stats['nlines'])+" [" + line + "] Lauchpad bot")

            name_pattern = re.compile(
                '^\\=\\=(.+);;(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
            tmpmatch = name_pattern.findall(line)

            # Workarround by simpli addign it as a commiter
            # Warned about this name with name as  Lauchpad_bot!
            match = [("Lauchpad_bot!", "Lauchpad@bot.bot", tmpmatch[0][1])]

        # Exception 4:
        # match=[('Jenkins', 'jenkins@review.openstack.org', 'Thu Jan 30 21:21:23 2014', '+')]
        #

        # anything else ERROR with imput or this code
        else:
            print(
                "Error, unable to extract developer name, email or date from commit block")
            print("Regular expression not captured")
            print("Line=["+line+"]")
            sys.exit()

    name = match[0][0]
    # print("name=["+name+"]")

    "get the email"
    email = match[0][1]
    # print("email=["+email+"]")

    # Verify the email pattern

    email_pattern = re.compile('([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)')

    if (email_pattern.search(email) == None):
        print("WARNING commiter ["+email+"] have an invalidName")
        print("Adding .com? to the end")
        email += ".com?"

    "gets the date"
    date = match[0][2]
    # print("date=["+date+"]")

    affiliation = getAffiliationFromEmail(email)

    return (date, email, affiliation)


"return a list of files modified by a commit log"


def findFilesOnBlock(block):
    # print ("finding files on block [" + str(block) + "]" )

    linesWithCode = []

    for line in block:
        # print ("line=["+line+"]")
        if line == []:
            break
        if line == '\n':
            break
        "append the file path (removing the last caracted \n)"
        linesWithCode.append(line[:-1])
        stats['nBlocksChagingCode'] += 1

    # print ("Lines of changed code:")
    # for line in linesWithCode:
    #    print (line)

    return linesWithCode


# processes a bloc of a change log (a developer change)
def scrapBlock(block):
    # print ("Processing [" + str(block) + "]")

    # Check if it is an empty block / change
    if len(block) == 0:
        print("ERROR: block / changelog to scrap is empty")
        return False

    firstLine = block[0]

    # check if the block starts with a date
    if not firstLine[0:2] == '==':
        print("ERROR: Invalid block / not starting with a date ")
        return False

    daEmAf = getDateEmailAffiliation(block[0])

    # print ("")
    # print (daEmAf)

    # What file where affected by the change log
    changedFiles = findFilesOnBlock(block[1:])

    # Save it in changeLogData
    # (date, email, affilition), [files changed])

    # GIT log changes that do not change files are irelevant
    if changedFiles == []:
        return False

    changeLogData.append((daEmAf, changedFiles))


# filter/slice the changeLogData by data
# Aproach: simply removes blocks wich date does not fit between a startDate and endDate
# Format end date should be  "Oct 11 2014" "MMM DD YYYY"

def filterChangeLogDataByDate(startDate, endDate):
    print(
        "Filtering ChangeLogData for  dates between ["+str(startDate)+"] and ["+str(endDate)+"]")

    # are they dates?

    if type(startDate) != datetime or type(endDate) != datetime:
        print("ERROR: invalide data type, not a valid datetime object")
        sys.exit()

    # is channge log empty ?

    if (len(changeLogData) < 1):
        print("ERROR: changeLogData is empty")

    # if end date after start date?

    res = []

    for change in changeLogData:
        date = change[0][0]
        email = change[0][1]
        af = change[0][2]
        files = change[1]

        # print ("On " + date + " " + email + " from " + af + " worked on the following files:" )

        # print ("ChangeLogDateString=["+date+"]")
        # weekday =date[0:3]
        # month = date[4:7]
        # day = date[8:10]
        # time = date[11:19]
        # year = date[20:24]

        # Get weekday month day time year  with regular expressions
        name_pattern = re.compile('(.+)\s(.+)\s(\d+)\s(.+)\s(\d+)')
        match = name_pattern.findall(date)

        # print ("date_ match=["+str(match)+"]")

        # If there is no regulae expression match
        if (match == []):
            print("ERROR: Change log date is not on proper format")
            print("date_ match=["+str(match)+"]")
            sys.exit()

        weekday = match[0][0]
        month = match[0][1]
        day = match[0][2]
        time = match[0][3]
        year = match[0][4]

        # print ("ChangeLogDateCapture=["+weekday+ " " + month+ " " + day + " " + time + " " + year + "]")

        # date(year, month, day) --> date object
        day = int(day)
        year = int(year)

        if month == "Jan":
            month = 1
        elif month == "Feb":
            month = 2
        elif month == "Mar":
            month = 3
        elif month == "Apr":
            month = 4
        elif month == "May":
            month = 5
        elif month == "Jun":
            month = 6
        elif month == "Jul":
            month = 7
        elif month == "Aug":
            month = 8
        elif month == "Sep":
            month = 9
        elif month == "Oct":
            month = 10
        elif month == "Nov":
            month = 11
        elif month == "Dec":
            month = 12
        else:
            print("ERROR invalide month spec: unable to extract date")
            sys.exit()
        changeLogDate = datetime(year, month, day)

        # print("changeLogDate=["+ str(changeLogDate)+"]")

        if (changeLogDate < startDate) or changeLogDate > endDate:
            # print("drop change log due date")
            continue
        else:
            # print("changeLogDate=["+ str(changeLogDate)+"] is between ["+str(startDate)+"] and ["+str(endDate)+"]" )
            res.append(change)

    return res

# print the changeLogData data scraped


def print_changeLogData():
    global changeLogData

    print("")
    print("Printing change log data ... from the earliast change to the oldest change")
    for change in changeLogData:
        date = change[0][0]
        email = change[0][1]
        af = change[0][2]
        files = change[1]

        print("On " + date + " " + email + " from " +
              af + " worked on the following files:")

        for file in files:
            print("[" + file + "]")


# save the changeLogData data scraped into a filename
def save_changeLogData(filename):

    global SAVE_MODE
    global changeLogData

    print("")
    print("TODO")
    print('Saving changeLog to file ' + str(filename) + '')

    if (SAVE_MODE != 1):
        print ("ERROR, not in saving mode")
        sys.exit()

    with open(filename, 'wb') as fp:
        pickle.dump(changeLogData, fp)

    print ("DONE changelog saved in ", filename, "NICE :)")
    sys.exit()


# load and return	 the changeLogData data scraped into a filename
def load_changeLogData(filename):
    print ("")
    print ("TODO")
    print ("Loading changeLog from  file [", filename, "]")

    with open(filename, 'rb') as fp:
        changeLogData = pickle.load(fp)

    return changeLogData


# print the agreByFileContributors agreefation resuting by  agregateByFileItsContributors
def print_agreByFileContributors():
    print("")
    print("Printing files affected by commits on the changelLog  ... and developers resposable for it")

    for file in agreByFileContributors:
        fileName = file
        authorEmails = agreByFileContributors[file]

        if (len(authorEmails) == 0):
            print("ERROR: File without contrubutors !!")
            exit()

        print("The file " + fileName +
              "was changed by following [" + str(len(authorEmails)) + "]contributors")

        for email in authorEmails:
            print("[" + email + "]")


# print a list of contributor connected to each other cause they worked on a common files
def print_agreByConnWSF():
    # print (str(agreByConnWSF))

    print("")
    print("Printing tuples of authors that collaborated + file that they contribute together too")
    # format more a less like this [(a-b),file)]

    for connection in agreByConnWSF:
        contributorsPair = connection[0]
        fileName = connection[1]

        print("Contributors " + str(contributorsPair) +
              " connected by collaborating on file [" + fileName + "]")


# Agregate by file and its contributors
def agregateByFileItsContributors():
    print("")
    print("Agregating data: for each file what are the contributors")

    # Agregated  by files and stores agregation in global agreByFileContributors   #
    # (file,[list of contributors changing it])

    filesVisited = []

    for change in changeLogData:
        email = change[0][1]
        files = change[1]

        for file in files:
            # If its a new file
            if file not in filesVisited:
                filesVisited.append(file)
                agreByFileContributors[file] = []
                agreByFileContributors[file].append(email)
            # if a file that that was changed before
            elif file in filesVisited:
                # add a new author to the list of authors that changed the file
                if email not in agreByFileContributors[file]:
                    agreByFileContributors[file].append(email)
            else:
                print("ERROR: list of file not visited")
                exit()

    stats['nChangedFiles'] = len(filesVisited)

# Get tuple of authors getting connect due to working on a common file
# [(a-b),file)]


def getContributorsConnectionsTuplesWSF():

    # Interates over the list of files and its contributors
    print("")
    print("Getting tuples of contributors that coded/contributed on the same file")

    # Stores contributors connected by working in the same file
    contributorsConnectedbyFile = []

    connectedByFile = []

    for change in agreByFileContributors:
        contributors = agreByFileContributors[change]
        for contributor in contributors:
            connectedByFile.append(contributor)

        contributorsConnectedbyFile.append((connectedByFile, change))
        connectedByFile = []

    # Print contributors connect by working in same file i.e. [(['cgarcia@igalia.com', 'jinwoo7.song@samsung.com'], '* Source/cmake/OptionsEfl.cmake:')
    # print (contributorsConnectedbyFile)

    for connection in contributorsConnectedbyFile:
        # print ("interating "+ str(connection))

        contributors = connection[0]
        files = connection[1]

        if len(contributors) == 0:
            print("ERROR Not file changes can have 0  contributors")
            exit()
        elif len(contributors) == 1:
            "One man file .. no connection"
            # print ("WARNING one man one file")
        elif len(contributors) > 1:
            "add all combinations of contributors to global agreByConnWSF "
            for connection in itertools.combinations(contributors, 2):
                agreByConnWSF.append((connection, files))


# Get a list of unique tubles of developers that collaborate. List of tubles with linked nodes.
def getUniqueConnectionsTuplesList(tuplesListWithFile):

    # verify arguments data
    # verify tuplesListWithFile

    if type(tuplesListWithFile) != list:
        print("\tERROR collaboration tuplesList is not a list !!")
        exit()
    if len(tuplesListWithFile) < 1:
        print("\tERROR collaboration tuplesList is empty !!")
        exit()

    seen = {}

    for connection in tuplesListWithFile:
        ((author1, author2), fileName) = connection

        # Do not consider if author1 or author2 been already connected 1->2 or 2-< 1
        if (author1, author2) and (author2, author1) not in seen:
            seen[(author1, author2)] = True

    return list(seen.keys())


# Pring unique connections - lust of tuples [(a,b),(b.c)]
def print_unique_connections():
    print("\nPrinting author unique collaborations (straps repeated collaborations):\n ")

    if len(uniqueConnections) < 1:
        print("Error, there are no unique connections between developers that should be printed")
        exit()

    print("\t------/------\n")
    for (dev1, dev2) in uniqueConnections:
        print("\t" + dev1 + " collaborated  with " + dev2)
    print(
        "\t TOTAL number of unique collaborations =[" + str(len(uniqueConnections)) + "]")
    print("\t------/------\n")


# Get the affiliations of all authors commiting code
# Author emails is its unique identifier
def getAffiliations():
    print("Getting author affiliations from their unique email in changeLogData")
    for change in changeLogData:
        email = change[0][1]
        affiliations[email] = getAffiliationFromEmail(email)

    print("Getting networked-author affiliations from their unique email in changeLogData")
    for connection in agreByConnWSF:
        contributorsPair = connection[0]
        fileName = connection[1]

        (contr1, contr2) = contributorsPair
        networked_affiliations[contr1] = getAffiliationFromEmail(contr1)
        networked_affiliations[contr2] = getAffiliationFromEmail(contr2)


# Pring the affiliation of each author
def print_Affiliations():
    print("\nPrinting author affiliations:\n ")
    for author in affiliations:
        print("\t" + author + " is affiliatied with " + affiliations[author])

    print("\nPrinting network-author affiliations:\n ")
    for author in networked_affiliations:
        print("\t" + author + " is affiliatied with " + affiliations[author])

# Reprocess all variables from changeLogData


def reprocess():

    print("\n Reprocessing changeLogData")

    global agreByFileContributors
    global agreByConnWSF
    global affiliations
    global networked_affiliations
    global uniqueConnections

    agreByFileContributors = {}
    agreByConnWSF = []
    affiliations = {}
    networked_affiliations = {}

    # Reprocess with the new changeLogData
    agregateByFileItsContributors()
    getContributorsConnectionsTuplesWSF()
    uniqueConnections = getUniqueConnectionsTuplesList(agreByConnWSF)
    getAffiliations()


# MAIN

def main():

    global changeLogData
    global agreByFileContributors
    global agreByConnWSF
    global affiliations
    global networked_affiliations
    global uniqueConnections

    global SAVE_MODE
    global RAW_MODE
    global LOAD_MODE
    global DEBUG_MODE

    # Process the arguments
    # -s for serialized save (already provessed changeLog)
    # -r for extrating raw changelog git log

    parser = argparse.ArgumentParser(
        description='Scrap some chagelog to create networks/graphs for research purpses')
    parser.add_argument('-l', '--lser', action='store', type=str,
                        help='loads and processes an serialized changelog')
    parser.add_argument('-r', '--raw', action='store',
                        type=str, help='processes from a raw git changelog')
    parser.add_argument('-s', '--sser', action='store', type=str,
                        help='processses from a raw git changelog and saves it into a serialized changelog. Requires -r for imput')
    parser.add_argument("-v", "--verbose",
                        help="increase output verbosity", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        print("verbosity turned on")
        DEBUG_MODE = 1

    if args.lser:
        print( " loanding and processing [lser=", args.lser, "]")
        print( "not implmented yet")
        LOAD_MODE = 1
        RAW_MODE = 0
        SAVE_MODE = 0
    elif args.sser and args.raw:
        print( " processing [raw=", args.raw, "]", " and saving [sser=", args.sser, "]")
        SAVE_MODE = 1
        RAW_MODE = 1
        LOAD_MODE = 0
    elif args.raw:
        RAW_MODE = 1
        LOAD_MODE = 0
        SAVE_MODE = 0
        print (" processing [raw=", args.raw, "]")
    else:
        print ("unrecognized argumets ... see --help")
        sys.exit()

    if RAW_MODE == 1:
        # if we are not in load mode, we need to strap the log
        print ("Scrapping changeLog from ", args.raw)
        t0 = datetime.now()
        print("STARTING the scrap of changeLog file " +
              args.raw + " on " + str(t0))

        # Opening the files

        workfile = args.raw

        f = open(workfile, 'r')

        # Read line by line
        # Keep also the stats
        # Detect blocks ... process them

        # Will save a commit block lines : From == to next ==

        lines = f.readlines()

        # Break everything in blocks and grab the data in ChangLogData

        for line in lines:
            # print("reading line [" + line +"]")

            # Ignore empty lines
            if line == "\n":
                continue

            # Updates the count of number of lines in the file
            stats['nlines'] += 1

            # if starts with '==' we have a new commit-block
            if line[0:2] == '==':
                # Process last temporay block and the cleans it
                if (stats['nBlocks'] != 0):
                    scrapBlock(tmpBlock)
                tmpBlock = []
                tmpBlock.append(line)

                # Updates the could of change log blocks
                stats['nBlocks'] += 1
                continue
            # then, eithier is a file or an error
            elif not line[0:2] == '==':
                # must be a file path
                # having a / a . or stenlen bigger than 5
                if '.' in line or '/' in line or len(line) >= 5:
                    tmpBlock.append(line)
                    continue
                else:
                    print(
                        "ERROR: not a file path. Commit blocs not starting with == must be file paths")
                    print(
                        "ERROR processing line ["+str(stats['nlines'])+"]" + "line=["+line+"]")
                    sys.exit()
            else:
                print("ERROR: Something wrong with the changeLog blocks L 107")
                sys.exit()
                break

    if (RAW_MODE == 1):
        print("\n:)1st SUCESS Data scraped from changlog files (stored in ChangeLogData data structure)")
        # print_changeLogData()

    elif (LOAD_MODE == 1):
        changeLogData = load_changeLogData(args.lser)
        print( "1st SUCESS Change log loaded from ", args.lser, " ")

        if len(changeLogData) < 1:
            print ("to small loaded change log, len <1")
            sys.exit()

        # print_changeLogData()

    else:
        print("ERROR: In what mode are we afer all= No SAVE,LOAD or RAW")
        sys.exit()

    if (SAVE_MODE == 1):
        print("Saving file")
        save_changeLogData(args.sser)

    # Agregate by file ...

    agregateByFileItsContributors()
    print("\n:)2nd SUCESS2 Data agregated by files and its contributors")
    # print_agreByFileContributors()

    # agreate list of authors that worked on the each files

    getContributorsConnectionsTuplesWSF()
    print("\n:) 3rd SUCESS tubles of authors that collaborated (coded in the same source code file) were generated")
    # print_agreByConnWSF()

    # agreate an list of authors that worked on the each files (do not repeat author tuples)
    # For getting unique edges/collaborations (do not include repetitions of the same collaborations)
    uniqueConnections = getUniqueConnectionsTuplesList(agreByConnWSF)
    print("\n:) 4rd SUCESS unique authors that collaborated tuples (coded in the same source code file) were generated")
    # print_unique_connections()

    # for every author, get its affiliation. result will be saved in the  affiliation global dictionart
    getAffiliations()
    # print_Affiliations()

    print("\n:) 5rd SUCESS got author -> affiliation dictionary")

    #### UCI NET format ####
    #### Used for WebKit SIGMISCPT paper ####
    # Export to data files to Ucitnet format
    # Both networkOutput and atributesOutput are global atributes defined on the header

    # exportLogData.createNetworkFileCSV(agreByConnSF, networkOutput)
    # exportLogData.createAtributesFileCSV(changeLogData, atributesOutput )
    # print ("\n:) UciNet export SUCESS exported UCInet network to file:"+networkOutput+" and its attributes to file:"+atributesOutput)

    # GRAPH ML#

    # Create an GraphML file

    # exportLogData.createGraphML(uniqueConnections,networked_affiliations, graphmlOutput)
    # print ("\n:) GRAPHML export SUCESS exported GraphML network to file:"+graphmlOutput)

    # print ("\t\n:) GRAPHML export Number of nodes/authors = " + str(len(affiliations)))
    # print ("\t\n:) GRAPHML export Number of networked nodes/authors = " + str(len(networked_affiliations)))

    # print ("\t\n:) GRAPHML export Number of nodes/atribute/affiliations  = " + str(networkMeasures.getNumberOfAffiliations(affiliations)))
    # print ("\t\n:) GRAPHML export Number of networked nodes/atribute/affiliations  = " + str(networkMeasures.getNumberOfAffiliations(networked_affiliations)))
    # print ("\t\n:) GRAPHML export Number of edges/collaborations (include repetitions of the same collaboration) = " + str(networkMeasures.getNumberOfEdges(agreByConnWSF)))

    # print ("\t\n:) GRAPHML export Number of unique edges/collaborations (do not include repetitions of the same collaborations) = " + str(networkMeasures.getNumberOfUniqueEdges(agreByConnWSF)))

    # print ("\t\n:) GRAPHML export Number of unique edges/collaborations (do not include repetitions of the same collaborations) = " + str(len(uniqueConnections)))

    # Create an graphML file filtered by company
    # In this case_ red_hat,enovance and intel
    # Others are ignored, not grouped
    # exportLogData.createGraphML_filterByAffiliation(uniqueConnections,networked_affiliations, "FilteredByCompanies"+ graphmlOutput , ["red_hat","enovance", "intel", "ibm", "hp","mirantis","nebula","vmware" ])

    print("\n")

    sizeOriginalChangeLogData = len(changeLogData)

    # Filter changeLogByDate
    # changeLogData=filterChangeLogDataByDate (datetime(2014,1,1), datetime (2014,6,1))

    # Filter nothing
    # changeLogData=filterChangeLogDataByDate (datetime(1900,1,1), datetime (2020,1,1))

    # Filter changeLogData for dates between Xmas and valentines
    # FOR TESTING PURPOSES ONLY

    # print "Number of edges overall[", len(uniqueConnections), "]"
    # XmasDate=datetime(2012,12,15)
    # valentinesDate=datetime(2014,2,14)
    # changeLogData=filterChangeLogDataByDate (datetime(2014,1,1), datetime (2014,6,1))
    # reprocess()
    # print "Number of edges between Xmas and Fall[", len(uniqueConnections), "]"

    print("\nSegmenting by release \n\
        0 Icehouse released Apr 17, 2014 \n\
        1 Havana  released Oct 17, 2013 \n\
        2 Grizzly released Apr 4, 2013 \n\
        3 Folsom  released Sep 27, 2012 \n\
        4 Essex released Apr 5, 2012 \n\
        5 Diablo released Sep 22, 2011 \n\
        6 Cactus released Apr 15, 2011 \n\
        7 Bexar released Feb 3, 2011  \n\
        8 Austin released Oct 21, 2010\n")

    releases = []

    releases.append(("Icehouse", datetime(2014, 4, 17)))
    releases.append(("Havana", datetime(2013, 10, 17)))
    releases.append(("Grizzly", datetime(2013, 4, 4)))
    releases.append(("Folsom", datetime(2012, 9, 27)))
    releases.append(("Essex", datetime(2012, 4, 5)))
    releases.append(("Diablo", datetime(2011, 9, 22)))
    releases.append(("Cactus", datetime(2011, 4, 15)))
    releases.append(("Bexar", datetime(2011, 2, 3)))
    releases.append(("Austin", datetime(2010, 10, 21)))

    tmpBkupLogData = changeLogData

    # Creates logitudinal network segments for open-stack
    # for i in range (len(releases)-1):
    #    (release_name, release_date) = releases[i]
    #    prior_release_date= releases[i+1][1]
    #    print ("\t --- Generating grapth["+ release_name+"]" + "from ["+  str(prior_release_date) +"] and rel on [" + str(release_date) + "]\n")
    #    print ("\t --- Filtering change log data for [" + str(prior_release_date)+ "] <--> ["+ str(release_date)+"]")
    #    changeLogData=filterChangeLogDataByDate (prior_release_date,release_date)
    #    reprocess()
    #    print("\t --- Filtering by date is done. [" + str (sizeOriginalChangeLogData-len(changeLogData)) +"] changeLogs removed due their change date")
    #    exportLogData.createGraphML_filterByAffiliation(uniqueConnections,networked_affiliations, release_name + graphmlOutput , top10)
    #    print("\t --- Network for " + release_name+ " release created at " + release_name + graphmlOutput + " for " + str(top10) + "\n")
    #    changeLogData = tmpBkupLogData

    # Get the number of edges betwen releases i and i+1

    nodesiip1 = []
    nodesiip1Top10 = []
    edgesiip1 = []
    edgesiip1Top10 = []

    for i in range(len(releases)-1):
        (release_name, release_date) = releases[i]
        prior_release_date = releases[i+1][1]
        print("\t --- Filtering change log data for [" + str(
            prior_release_date) + "] <--> [" + str(release_date)+"]")
        changeLogData = filterChangeLogDataByDate(
            prior_release_date, release_date)
        reprocess()
        print("\t --- Filtering by date is done. [" + str(sizeOriginalChangeLogData-len(
            changeLogData)) + "] changeLogs removed due their change date")

        nnodes = len(
            JISA2015specificAnalysis.getNodesBetweenDatesInConnList(uniqueConnections))
        nnodestop10 = len(JISA2015specificAnalysis.getNodesBetweenDates4SelectedFirmsDatesInConnList(
            uniqueConnections, networked_affiliations, top10))
        nedges = len(uniqueConnections)
        nedgestop10 = len(JISA2015specificAnalysis.getConnectionsAmongTop10Only(
            uniqueConnections, networked_affiliations, top10))

        print("Number of nodes between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodes)
        print("Number of nodes (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodestop10)

        print("Number of edges between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nedges, ";")
        print("Number of edges (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nedgestop10, ";")

        nodesiip1.append(nnodes)
        nodesiip1Top10.append(nnodestop10)
        edgesiip1.append(nedges)
        edgesiip1Top10.append(nedgestop10)

        changeLogData = tmpBkupLogData

        # for debug only
        # print the edges among top10 for first release
        # print "pringing edged for reease", release_name , ":"
        # top10con = getConnectionsAmongTop10Only(uniqueConnections)
        # for edge in top10con:
        # (a,b) = edge
        # if top10con.count(edge) != 1:
        # print "ERROR:Not a single edge:"
        # print "top10con.count(edge)=[", top10con.count(edge),"] --> repeated edges"
        # print "edge in question:", edge
        # sys.exit()
        # if (b,a) in top10con:
        # print "ERROR:Not a single edge:"
        # print "top10con.count(edge)=[", top10con.count((b,a)),"] --> repeated edges (inverse relationship already accounted)"
        # print "edge in question:", edge, " and its inverse " , (b,a)
        # sys.exit()
        #
        # sys.exit()

    # Get the number of nodes and edges betwen releases i-1month and i+1
    nodesim1ip1 = []
    nodesim1ip1Top10 = []
    edgesim1ip1 = []
    edgesim1ip1Top10 = []

    releasesm1 = []
    for release in releases:
        (releasename, date) = release

        # for 4 weeks / 1 month
        # releasesm1.append((releasename, date - relativedelta(months=1)))

        # for 3 weeks
        # releasesm1.append((releasename, date - relativedelta(weeks=3)))

        # for 2 weeks
        # releasesm1.append((releasename, date - relativedelta(weeks=2)))

        # for 1 week
        releasesm1.append((releasename, date - relativedelta(weeks=1)))

    # Get the number of edges betwen releases i and i+1
    for i in range(len(releasesm1)-1):
        (release_name, release_date) = releases[i]
        prior_release_date = releasesm1[i+1][1]
        print("\t --- Filtering change log data for [" + str(
            prior_release_date) + "] <--> [" + str(release_date)+"]")
        changeLogData = filterChangeLogDataByDate(
            prior_release_date, release_date)
        reprocess()
        print("\t --- Filtering by date is done. [" + str(sizeOriginalChangeLogData-len(
            changeLogData)) + "] changeLogs removed due their change date")

        nnodes = len(
            JISA2015specificAnalysis.getNodesBetweenDatesInConnList(uniqueConnections))
        nnodestop10 = len(JISA2015specificAnalysis.getNodesBetweenDates4SelectedFirmsDatesInConnList(
            uniqueConnections, networked_affiliations, top10))

        nedges = len(uniqueConnections)
        nedgestop10 = len(JISA2015specificAnalysis.getConnectionsAmongTop10Only(
            uniqueConnections, networked_affiliations, top10))

        print ("Number of nodes between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodes)
        print ("Number of nodes (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodestop10)

        print ("Number of edges between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nedges, ";")
        print ("Number of edges (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nedgestop10, ";")

        nodesim1ip1.append(nnodes)
        nodesim1ip1Top10.append(nnodestop10)
        edgesim1ip1.append(nedges)
        edgesim1ip1Top10.append(nedgestop10)
        changeLogData = tmpBkupLogData

    # print releases name
    # Not that they are in reverse cronological order, therefore ::-1
    rname = []
    for r in releases:
        (name, nc) = r
        rname.append(name + ";")
    print( "rname", rname[::-1])

    # For all nodes
    print ("\t ALL NODES ")

    print( "nodesiip1", nodesiip1[::-1])
    print( "nodesiim1p1", nodesim1ip1[::-1])
    print( "diff capture nodes less 1 month", map(int.__sub__, nodesiip1, nodesim1ip1)[::-1])
    print( "% captured nodes less 1 month", map(float.__div__, [float(i) for i in nodesiip1], [float(i) for i in nodesim1ip1])[::-1])

    print( "edgesiip1", edgesiip1[::-1])
    print( "edgesim1ip1", edgesim1ip1[::-1])
    print( "diff edges less 1 month", map(int.__sub__, edgesiip1, edgesim1ip1)[::-1])
    print( "% captured edges less 1 month", map(float.__div__, [float(i) for i in edgesiip1], [float(i) for i in edgesim1ip1])[::-1])

    # For top 10 onlys
    print( "\t TOP 10 NODES ")

    print( "nodesiip1Top10",  nodesiip1Top10[::-1])
    print( "nodesim1ip1Top10", nodesim1ip1Top10[::-1])
    print( "diff nodes top10 less 1 month", map(int.__sub__, nodesiip1Top10, nodesim1ip1Top10)[::-1])
    print( "% captured nodes less 1 month", map(float.__div__, [float(i) for i in nodesiip1Top10], [float(i) for i in nodesim1ip1Top10])[::-1])

    print( "edgesiip1Top10", edgesiip1Top10[::-1])
    print( "edgesim1ip1Top10", edgesim1ip1Top10[::-1])
    print( "diff edfes top10 less 1 month", map(int.__sub__, edgesiip1Top10, edgesim1ip1Top10)[::-1])
    print( "% captured edges less 1 month", map(float.__div__, [float(i) for i in edgesiip1Top10], [float(i) for i in edgesim1ip1Top10])[::-1])

    print("")
    print("FINNISHED " + str(datetime.now()))

    if (LOAD_MODE != 1):
        print("TOTAL TIME " + str(datetime.now() - t0))

    # Ending stats

    print("Number of analized lines [" + str(stats['nlines']) + "]")
    print(
        "Number of analized changelog blocks [" + str(stats['nBlocks']) + "]")
    print("Number of analized changelog blocks changing code files [" + str(
        stats['nBlocksChagingCode']) + "?]")
    print("Number of analized changelog blocks not changing code files (i.e. testCases)[" + str(
        stats['nBlocksNotChangingCode']) + "?]")
    print("Number of files affected by the commits reported by change log[" + str(
        stats['nChangedFiles']) + "]")


if __name__ == "__main__":
    main()

#! /usr/bin/env python3


# Scaps date, authors, affiliations and file changes from WebKit SVN Changelog
#
#


print("this is pyhton")

# scraplog save with serialzie
# TODO functions returning NetworkX graphs


try:
    import cPickle as pickle
except:
    import pickle


print("Executing " + str(sys.argv))

# Global parameters

networkOutput = "NetworkOutput.file1.CSV"
atributesOutput = "AtributesOutput.file2.CSV"
graphmlOutput = "NetworkFile.graphML"


# Global structures

# Keeps statistics of the scrappping
stats = {'nlines': 0, 'nBlocks': 0, 'nBlocksChagingCode': 0,
         'nBlocksNotChangingCode': 0, 'nChangedFiles': 0}

# Keeps data as inially scrapped [(date, email, affilition), [files changed]]
# The one that can be saved , the only data structure keeping date information
changeLogData = []

# Will keep agrregated data of authors that changed the same (file,[list of contributors changing it])
agreByFileContributors = {}


# Will keep agregated tuples of authors connecting due to working on a common file [(a-b),file)]

agreByConnWSF = []

# Will keep unique tuples of authors connected due to workin on common file. no repetitions for (a-b),(a-b) or (a-b),(b-a)
# Keeps unique collaborations and connections. [(a,b),(b,c),(a,c)]
uniqueConnections = []

# Will keep a dictionary author afiliation i.e affiliation[mike@google.com]=google.com
affiliations = {}

# Will keep a dictionary networked author afiliation i.e affiliation[mike@google.com]=google.com
# Drops authors that do not connect with others
networked_affiliations = {}


# For ibm ex
# ibm_email_domains =  ["au1.ibm.com","linux.vnet.ibm.com","br.ibm.com", "zurich.ibm.com", "us.ibm.com" ,"cn.ibm.com","il.ibm.com","de.ibm.com","ca.ibm.com"]
ibm_email_domains_prefix = ["au1", "linux",
                            "br", "zurich", "us", "cn", "il", "de", "ca"]

# TOP10 companies in OpenStack
top10 = ["rackspace", "nebula", "citrix", "redhat", "ibm", "hp",
         "cloudscaling", "mirantis", "vmware", "canonical", "intel"]


# Are we verbose?
DEBUG_MODE = 0

# Are we going to scraplog data?

SAVE_MODE = 0

# Are we starting with a ready to process stracplog saved previously in SAVE_MODE?
LOAD_MODE = 0


# Are we dealing with raw data from a git/svn log ?
RAW_MODE = 0


def getAffiliationFromEmail(email):
    "gets affiliation from an given email"

    # print ("getAffiliationFromEmail("+email+")")

    affiliation_pattern = re.compile('@(\w[\w\-]+)')
    match = affiliation_pattern.findall(email)

    if match == None or match == []:
        print("ERROR unable to extract affiliation from email. Wrong email format?")
        print("match=["+str(match)+"]")
        sys.exit()

    "implement an exception for IBM as their emails come from multiple domains"
    "au1.ibm.com linux.vnet.ibm.com br.ibm.com zurich.ibm.com us.ibm.com cn.ibm.com il.ibm.com"

    if 'ibm' in email:
        # print ("Warning, ibm affiliation from multiple domains")

        if match[0] not in ibm_email_domains_prefix:
            print(
                "ERROR, ibm affilition from an unknow domain, check ibm_email_domain glob")
            print("march=["+str(match[0])+"]")
            sys.exit()

        # print ("affiliation(" + email + ")=[ibm]")
        return "ibm"

    affiliation = match[0]
    # print ("affiliation(" + email + ")=["+affiliation+"]")
    return affiliation


#
# Extract date, nane and email
# WK Sample line
# ==Jenkins;jenkins@review.openstack.org;Thu Feb 20 03:56:00 2014 +0000==
# Format obtained by running: $git log --pretty=format:"==%an;%ae;%ad=="  --name-only
# Returned result would be ('Thu Feb 20 03:56:57 2014','Jenkins', 'jenkins@review.openstack.org',

def getDateEmailAffiliation(line):
    "gets the ==Name;email;date=="
    # print ("	getting name, email, date, affilication from the line["+line+"]")

    name_pattern = re.compile(
        '^\\=\\=(.+);(.+);(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
    match = name_pattern.findall(line)

    # print ("match=" + str(match))

    if match == None or match == []:

        ## expeptions handling ##
        # "==name;email;date== is the most common pattern from a git log"
        # "however some entries are name less taking a different format:"
        atIndex = line.find('@')

        # Exception 1: Developer added name and email to name
        # ==Brad McConnell bmcconne@rackspace.com;;Tue Sep 20 06:50:27 2011 +0000==
        if ';;' in line and ' ' in line[0:atIndex] and '==Launchpad' not in line:
            print("WARNING exceptional code commit header Exception 1 ")
            print("LINE number "+str(stats['nlines'])+" [" + line +
                  "] double ;; <- name and email together on commit header")

            name_pattern = re.compile(
                '^\\=\\=(.*)\ (.+@.+);;(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
            match = name_pattern.findall(line)
            print("match=["+str(match)+"]")

        # Exception 2: If there is not name in the commit
        # there is no spaces before the email (@)
        elif ' ' not in line[0:atIndex] and '==Launchpad' not in line:

            print("WARNING exceptional code commit header Exception 2 ")
            print("LINE number "+str(stats['nlines']) +
                  " [" + line + "] no name, just an email")

            name_pattern = re.compile(
                '^\\=\\=(.+@.+);;(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
            tmpmatch = name_pattern.findall(line)

            # Workarround by adding name from the email
            # Warned about this name with name as  name?
            match = [(line[2:line.find('@')], tmpmatch[0]
                      [0], tmpmatch[0][1], tmpmatch[0][2])]

        # Exception 3: Launchpad Translations
        # Drop as it is a bot
        # ==Launchpad Translations on behalf of nova-core;;Sat Sep 3 05:50:53 2011 +0000
        elif "==Launchpad" in line:
            print("WARNING exceptional code commit header Exception 3 ")
            print("LINE number " +
                  str(stats['nlines'])+" [" + line + "] Lauchpad bot")

            name_pattern = re.compile(
                '^\\=\\=(.+);;(.+)\\ (\\+|\\-)\d\d\d\d\\=\\=$')
            tmpmatch = name_pattern.findall(line)

            # Workarround by simpli addign it as a commiter
            # Warned about this name with name as  Lauchpad_bot!
            match = [("Lauchpad_bot!", "Lauchpad@bot.bot", tmpmatch[0][1])]

        # Exception 4:
        # match=[('Jenkins', 'jenkins@review.openstack.org', 'Thu Jan 30 21:21:23 2014', '+')]
        #

        # anything else ERROR with imput or this code
        else:
            print(
                "Error, unable to extract developer name, email or date from commit block")
            print("Regular expression not captured")
            print("Line=["+line+"]")
            sys.exit()

    name = match[0][0]
    # print("name=["+name+"]")

    "get the email"
    email = match[0][1]
    # print("email=["+email+"]")

    # Verify the email pattern

    email_pattern = re.compile('([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)')

    if (email_pattern.search(email) == None):
        print("WARNING commiter ["+email+"] have an invalidName")
        print("Adding .com? to the end")
        email += ".com?"

    "gets the date"
    date = match[0][2]
    # print("date=["+date+"]")

    affiliation = getAffiliationFromEmail(email)

    return (date, email, affiliation)


"return a list of files modified by a commit log"


def findFilesOnBlock(block):
    # print ("finding files on block [" + str(block) + "]" )

    linesWithCode = []

    for line in block:
        # print ("line=["+line+"]")
        if line == []:
            break
        if line == '\n':
            break
        "append the file path (removing the last caracted \n)"
        linesWithCode.append(line[:-1])
        stats['nBlocksChagingCode'] += 1

    # print ("Lines of changed code:")
    # for line in linesWithCode:
    #    print (line)

    return linesWithCode


# processes a bloc of a change log (a developer change)
def scrapBlock(block):
    # print ("Processing [" + str(block) + "]")

    # Check if it is an empty block / change
    if len(block) == 0:
        print("ERROR: block / changelog to scrap is empty")
        return False

    firstLine = block[0]

    # check if the block starts with a date
    if not firstLine[0:2] == '==':
        print("ERROR: Invalid block / not starting with a date ")
        return False

    daEmAf = getDateEmailAffiliation(block[0])

    # print ("")
    # print (daEmAf)

    # What file where affected by the change log
    changedFiles = findFilesOnBlock(block[1:])

    # Save it in changeLogData
    # (date, email, affilition), [files changed])

    # GIT log changes that do not change files are irelevant
    if changedFiles == []:
        return False

    changeLogData.append((daEmAf, changedFiles))


# filter/slice the changeLogData by data
# Aproach: simply removes blocks wich date does not fit between a startDate and endDate
# Format end date should be  "Oct 11 2014" "MMM DD YYYY"

def filterChangeLogDataByDate(startDate, endDate):
    print(
        "Filtering ChangeLogData for  dates between ["+str(startDate)+"] and ["+str(endDate)+"]")

    # are they dates?

    if type(startDate) != datetime or type(endDate) != datetime:
        print("ERROR: invalide data type, not a valid datetime object")
        sys.exit()

    # is channge log empty ?

    if (len(changeLogData) < 1):
        print("ERROR: changeLogData is empty")

    # if end date after start date?

    res = []

    for change in changeLogData:
        date = change[0][0]
        email = change[0][1]
        af = change[0][2]
        files = change[1]

        # print ("On " + date + " " + email + " from " + af + " worked on the following files:" )

        # print ("ChangeLogDateString=["+date+"]")
        # weekday =date[0:3]
        # month = date[4:7]
        # day = date[8:10]
        # time = date[11:19]
        # year = date[20:24]

        # Get weekday month day time year  with regular expressions
        name_pattern = re.compile('(.+)\s(.+)\s(\d+)\s(.+)\s(\d+)')
        match = name_pattern.findall(date)

        # print ("date_ match=["+str(match)+"]")

        # If there is no regulae expression match
        if (match == []):
            print("ERROR: Change log date is not on proper format")
            print("date_ match=["+str(match)+"]")
            sys.exit()

        weekday = match[0][0]
        month = match[0][1]
        day = match[0][2]
        time = match[0][3]
        year = match[0][4]

        # print ("ChangeLogDateCapture=["+weekday+ " " + month+ " " + day + " " + time + " " + year + "]")

        # date(year, month, day) --> date object
        day = int(day)
        year = int(year)

        if month == "Jan":
            month = 1
        elif month == "Feb":
            month = 2
        elif month == "Mar":
            month = 3
        elif month == "Apr":
            month = 4
        elif month == "May":
            month = 5
        elif month == "Jun":
            month = 6
        elif month == "Jul":
            month = 7
        elif month == "Aug":
            month = 8
        elif month == "Sep":
            month = 9
        elif month == "Oct":
            month = 10
        elif month == "Nov":
            month = 11
        elif month == "Dec":
            month = 12
        else:
            print("ERROR invalide month spec: unable to extract date")
            sys.exit()
        changeLogDate = datetime(year, month, day)

        # print("changeLogDate=["+ str(changeLogDate)+"]")

        if (changeLogDate < startDate) or changeLogDate > endDate:
            # print("drop change log due date")
            continue
        else:
            # print("changeLogDate=["+ str(changeLogDate)+"] is between ["+str(startDate)+"] and ["+str(endDate)+"]" )
            res.append(change)

    return res

# print the changeLogData data scraped


def print_changeLogData():
    global changeLogData

    print("")
    print("Printing change log data ... from the earliast change to the oldest change")
    for change in changeLogData:
        date = change[0][0]
        email = change[0][1]
        af = change[0][2]
        files = change[1]

        print("On " + date + " " + email + " from " +
              af + " worked on the following files:")

        for file in files:
            print("[" + file + "]")


# save the changeLogData data scraped into a filename
def save_changeLogData(filename):

    global SAVE_MODE
    global changeLogData

    print("")
    print("TODO")
    print('Saving changeLog to file ' + str(filename) + '')

    if (SAVE_MODE != 1):
        print( "ERROR, not in saving mode")
        sys.exit()

    with open(filename, 'wb') as fp:
        pickle.dump(changeLogData, fp)

    print ( "DONE changelog saved in ", filename, "NICE :)")
    sys.exit()


# load and return	 the changeLogData data scraped into a filename
def load_changeLogData(filename):
    print( "")
    print( "TODO")
    print( "Loading changeLog from  file [", filename, "]")

    with open(filename, 'rb') as fp:
        changeLogData = pickle.load(fp)

    return changeLogData


# print the agreByFileContributors agreefation resuting by  agregateByFileItsContributors
def print_agreByFileContributors():
    print("")
    print("Printing files affected by commits on the changelLog  ... and developers resposable for it")

    for file in agreByFileContributors:
        fileName = file
        authorEmails = agreByFileContributors[file]

        if (len(authorEmails) == 0):
            print("ERROR: File without contrubutors !!")
            exit()

        print("The file " + fileName +
              "was changed by following [" + str(len(authorEmails)) + "]contributors")

        for email in authorEmails:
            print("[" + email + "]")


# print a list of contributor connected to each other cause they worked on a common files
def print_agreByConnWSF():
    # print (str(agreByConnWSF))

    print("")
    print("Printing tuples of authors that collaborated + file that they contribute together too")
    # format more a less like this [(a-b),file)]

    for connection in agreByConnWSF:
        contributorsPair = connection[0]
        fileName = connection[1]

        print("Contributors " + str(contributorsPair) +
              " connected by collaborating on file [" + fileName + "]")


# Agregate by file and its contributors
def agregateByFileItsContributors():
    print("")
    print("Agregating data: for each file what are the contributors")

    # Agregated  by files and stores agregation in global agreByFileContributors   #
    # (file,[list of contributors changing it])

    filesVisited = []

    for change in changeLogData:
        email = change[0][1]
        files = change[1]

        for file in files:
            # If its a new file
            if file not in filesVisited:
                filesVisited.append(file)
                agreByFileContributors[file] = []
                agreByFileContributors[file].append(email)
            # if a file that that was changed before
            elif file in filesVisited:
                # add a new author to the list of authors that changed the file
                if email not in agreByFileContributors[file]:
                    agreByFileContributors[file].append(email)
            else:
                print("ERROR: list of file not visited")
                exit()

    stats['nChangedFiles'] = len(filesVisited)

# Get tuple of authors getting connect due to working on a common file
# [(a-b),file)]


def getContributorsConnectionsTuplesWSF():

    # Interates over the list of files and its contributors
    print("")
    print("Getting tuples of contributors that coded/contributed on the same file")

    # Stores contributors connected by working in the same file
    contributorsConnectedbyFile = []

    connectedByFile = []

    for change in agreByFileContributors:
        contributors = agreByFileContributors[change]
        for contributor in contributors:
            connectedByFile.append(contributor)

        contributorsConnectedbyFile.append((connectedByFile, change))
        connectedByFile = []

    # Print contributors connect by working in same file i.e. [(['cgarcia@igalia.com', 'jinwoo7.song@samsung.com'], '* Source/cmake/OptionsEfl.cmake:')
    # print (contributorsConnectedbyFile)

    for connection in contributorsConnectedbyFile:
        # print ("interating "+ str(connection))

        contributors = connection[0]
        files = connection[1]

        if len(contributors) == 0:
            print("ERROR Not file changes can have 0  contributors")
            exit()
        elif len(contributors) == 1:
            "One man file .. no connection"
            # print ("WARNING one man one file")
        elif len(contributors) > 1:
            "add all combinations of contributors to global agreByConnWSF "
            for connection in itertools.combinations(contributors, 2):
                agreByConnWSF.append((connection, files))


# Get a list of unique tubles of developers that collaborate. List of tubles with linked nodes.
def getUniqueConnectionsTuplesList(tuplesListWithFile):

    # verify arguments data
    # verify tuplesListWithFile

    if type(tuplesListWithFile) != list:
        print("\tERROR collaboration tuplesList is not a list !!")
        exit()
    if len(tuplesListWithFile) < 1:
        print("\tERROR collaboration tuplesList is empty !!")
        exit()

    seen = {}

    for connection in tuplesListWithFile:
        ((author1, author2), fileName) = connection

        # Do not consider if author1 or author2 been already connected 1->2 or 2-< 1
        if (author1, author2) and (author2, author1) not in seen:
            seen[(author1, author2)] = True

    return list(seen.keys())


# Pring unique connections - lust of tuples [(a,b),(b.c)]
def print_unique_connections():
    print("\nPrinting author unique collaborations (straps repeated collaborations):\n ")

    if len(uniqueConnections) < 1:
        print("Error, there are no unique connections between developers that should be printed")
        exit()

    print("\t------/------\n")
    for (dev1, dev2) in uniqueConnections:
        print("\t" + dev1 + " collaborated  with " + dev2)
    print(
        "\t TOTAL number of unique collaborations =[" + str(len(uniqueConnections)) + "]")
    print("\t------/------\n")


# Get the affiliations of all authors commiting code
# Author emails is its unique identifier
def getAffiliations():
    print("Getting author affiliations from their unique email in changeLogData")
    for change in changeLogData:
        email = change[0][1]
        affiliations[email] = getAffiliationFromEmail(email)

    print("Getting networked-author affiliations from their unique email in changeLogData")
    for connection in agreByConnWSF:
        contributorsPair = connection[0]
        fileName = connection[1]

        (contr1, contr2) = contributorsPair
        networked_affiliations[contr1] = getAffiliationFromEmail(contr1)
        networked_affiliations[contr2] = getAffiliationFromEmail(contr2)


# Pring the affiliation of each author
def print_Affiliations():
    print("\nPrinting author affiliations:\n ")
    for author in affiliations:
        print("\t" + author + " is affiliatied with " + affiliations[author])

    print("\nPrinting network-author affiliations:\n ")
    for author in networked_affiliations:
        print("\t" + author + " is affiliatied with " + affiliations[author])

# Reprocess all variables from changeLogData


def reprocess():

    print("\n Reprocessing changeLogData")

    global agreByFileContributors
    global agreByConnWSF
    global affiliations
    global networked_affiliations
    global uniqueConnections

    agreByFileContributors = {}
    agreByConnWSF = []
    affiliations = {}
    networked_affiliations = {}

    # Reprocess with the new changeLogData
    agregateByFileItsContributors()
    getContributorsConnectionsTuplesWSF()
    uniqueConnections = getUniqueConnectionsTuplesList(agreByConnWSF)
    getAffiliations()


# MAIN

def main():

    global changeLogData
    global agreByFileContributors
    global agreByConnWSF
    global affiliations
    global networked_affiliations
    global uniqueConnections

    global SAVE_MODE
    global RAW_MODE
    global LOAD_MODE
    global DEBUG_MODE

    # Process the arguments
    # -s for serialized save (already provessed changeLog)
    # -r for extrating raw changelog git log

    parser = argparse.ArgumentParser(
        description='Scrap some chagelog to create networks/graphs for research purpses')
    parser.add_argument('-l', '--lser', action='store', type=str,
                        help='loads and processes an serialized changelog')
    parser.add_argument('-r', '--raw', action='store',
                        type=str, help='processes from a raw git changelog')
    parser.add_argument('-s', '--sser', action='store', type=str,
                        help='processses from a raw git changelog and saves it into a serialized changelog. Requires -r for imput')
    parser.add_argument("-v", "--verbose",
                        help="increase output verbosity", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        print("verbosity turned on")
        DEBUG_MODE = 1

    if args.lser:
        print(" loanding and processing [lser=", args.lser, "]")
        print("not implmented yet")
        LOAD_MODE = 1
        RAW_MODE = 0
        SAVE_MODE = 0
    elif args.sser and args.raw:
        print(" processing [raw=", args.raw, "]", " and saving [sser=", args.sser, "]")
        SAVE_MODE = 1
        RAW_MODE = 1
        LOAD_MODE = 0
    elif args.raw:
        RAW_MODE = 1
        LOAD_MODE = 0
        SAVE_MODE = 0
        print(" processing [raw=", args.raw, "]")
    else:
        print("unrecognized argumets ... see --help")
        sys.exit()

    if RAW_MODE == 1:
        # if we are not in load mode, we need to strap the log
        print("Scrapping changeLog from ", args.raw)
        t0 = datetime.now()
        print("STARTING the scrap of changeLog file " +
              args.raw + " on " + str(t0))

        # Opening the files

        workfile = args.raw

        f = open(workfile, 'r')

        # Read line by line
        # Keep also the stats
        # Detect blocks ... process them

        # Will save a commit block lines : From == to next ==

        lines = f.readlines()

        # Break everything in blocks and grab the data in ChangLogData

        for line in lines:
            # print("reading line [" + line +"]")

            # Ignore empty lines
            if line == "\n":
                continue

            # Updates the count of number of lines in the file
            stats['nlines'] += 1

            # if starts with '==' we have a new commit-block
            if line[0:2] == '==':
                # Process last temporay block and the cleans it
                if (stats['nBlocks'] != 0):
                    scrapBlock(tmpBlock)
                tmpBlock = []
                tmpBlock.append(line)

                # Updates the could of change log blocks
                stats['nBlocks'] += 1
                continue
            # then, eithier is a file or an error
            elif not line[0:2] == '==':
                # must be a file path
                # having a / a . or stenlen bigger than 5
                if '.' in line or '/' in line or len(line) >= 5:
                    tmpBlock.append(line)
                    continue
                else:
                    print(
                        "ERROR: not a file path. Commit blocs not starting with == must be file paths")
                    print(
                        "ERROR processing line ["+str(stats['nlines'])+"]" + "line=["+line+"]")
                    sys.exit()
            else:
                print("ERROR: Something wrong with the changeLog blocks L 107")
                sys.exit()
                break

    if (RAW_MODE == 1):
        print("\n:)1st SUCESS Data scraped from changlog files (stored in ChangeLogData data structure)")
        # print_changeLogData()

    elif (LOAD_MODE == 1):
        changeLogData = load_changeLogData(args.lser)
        print( "1st SUCESS Change log loaded from ", args.lser, " ")

        if len(changeLogData) < 1:
            print( "to small loaded change log, len <1")
            sys.exit()

        # print_changeLogData()

    else:
        print( "ERROR: In what mode are we afer all= No SAVE,LOAD or RAW")
        sys.exit()

    if (SAVE_MODE == 1):
        print ("Saving file")
        save_changeLogData(args.sser)

    # Agregate by file ...

    agregateByFileItsContributors()
    print("\n:)2nd SUCESS2 Data agregated by files and its contributors")
    # print_agreByFileContributors()

    # agreate list of authors that worked on the each files

    getContributorsConnectionsTuplesWSF()
    print("\n:) 3rd SUCESS tubles of authors that collaborated (coded in the same source code file) were generated")
    # print_agreByConnWSF()

    # agreate an list of authors that worked on the each files (do not repeat author tuples)
    # For getting unique edges/collaborations (do not include repetitions of the same collaborations)
    uniqueConnections = getUniqueConnectionsTuplesList(agreByConnWSF)
    print("\n:) 4rd SUCESS unique authors that collaborated tuples (coded in the same source code file) were generated")
    # print_unique_connections()

    # for every author, get its affiliation. result will be saved in the  affiliation global dictionart
    getAffiliations()
    # print_Affiliations()

    print("\n:) 5rd SUCESS got author -> affiliation dictionary")

    #### UCI NET format ####
    #### Used for WebKit SIGMISCPT paper ####
    # Export to data files to Ucitnet format
    # Both networkOutput and atributesOutput are global atributes defined on the header

    # exportLogData.createNetworkFileCSV(agreByConnSF, networkOutput)
    # exportLogData.createAtributesFileCSV(changeLogData, atributesOutput )
    # print ("\n:) UciNet export SUCESS exported UCInet network to file:"+networkOutput+" and its attributes to file:"+atributesOutput)

    # GRAPH ML#

    # Create an GraphML file

    # exportLogData.createGraphML(uniqueConnections,networked_affiliations, graphmlOutput)
    # print ("\n:) GRAPHML export SUCESS exported GraphML network to file:"+graphmlOutput)

    # print ("\t\n:) GRAPHML export Number of nodes/authors = " + str(len(affiliations)))
    # print ("\t\n:) GRAPHML export Number of networked nodes/authors = " + str(len(networked_affiliations)))

    # print ("\t\n:) GRAPHML export Number of nodes/atribute/affiliations  = " + str(networkMeasures.getNumberOfAffiliations(affiliations)))
    # print ("\t\n:) GRAPHML export Number of networked nodes/atribute/affiliations  = " + str(networkMeasures.getNumberOfAffiliations(networked_affiliations)))
    # print ("\t\n:) GRAPHML export Number of edges/collaborations (include repetitions of the same collaboration) = " + str(networkMeasures.getNumberOfEdges(agreByConnWSF)))

    # print ("\t\n:) GRAPHML export Number of unique edges/collaborations (do not include repetitions of the same collaborations) = " + str(networkMeasures.getNumberOfUniqueEdges(agreByConnWSF)))

    # print ("\t\n:) GRAPHML export Number of unique edges/collaborations (do not include repetitions of the same collaborations) = " + str(len(uniqueConnections)))

    # Create an graphML file filtered by company
    # In this case_ red_hat,enovance and intel
    # Others are ignored, not grouped
    # exportLogData.createGraphML_filterByAffiliation(uniqueConnections,networked_affiliations, "FilteredByCompanies"+ graphmlOutput , ["red_hat","enovance", "intel", "ibm", "hp","mirantis","nebula","vmware" ])

    print("\n")

    sizeOriginalChangeLogData = len(changeLogData)

    # Filter changeLogByDate
    # changeLogData=filterChangeLogDataByDate (datetime(2014,1,1), datetime (2014,6,1))

    # Filter nothing
    # changeLogData=filterChangeLogDataByDate (datetime(1900,1,1), datetime (2020,1,1))

    # Filter changeLogData for dates between Xmas and valentines
    # FOR TESTING PURPOSES ONLY

    # print "Number of edges overall[", len(uniqueConnections), "]"
    # XmasDate=datetime(2012,12,15)
    # valentinesDate=datetime(2014,2,14)
    # changeLogData=filterChangeLogDataByDate (datetime(2014,1,1), datetime (2014,6,1))
    # reprocess()
    # print "Number of edges between Xmas and Fall[", len(uniqueConnections), "]"

    print("\nSegmenting by release \n\
        0 Icehouse released Apr 17, 2014 \n\
        1 Havana  released Oct 17, 2013 \n\
        2 Grizzly released Apr 4, 2013 \n\
        3 Folsom  released Sep 27, 2012 \n\
        4 Essex released Apr 5, 2012 \n\
        5 Diablo released Sep 22, 2011 \n\
        6 Cactus released Apr 15, 2011 \n\
        7 Bexar released Feb 3, 2011  \n\
        8 Austin released Oct 21, 2010\n")

    releases = []

    releases.append(("Icehouse", datetime(2014, 4, 17)))
    releases.append(("Havana", datetime(2013, 10, 17)))
    releases.append(("Grizzly", datetime(2013, 4, 4)))
    releases.append(("Folsom", datetime(2012, 9, 27)))
    releases.append(("Essex", datetime(2012, 4, 5)))
    releases.append(("Diablo", datetime(2011, 9, 22)))
    releases.append(("Cactus", datetime(2011, 4, 15)))
    releases.append(("Bexar", datetime(2011, 2, 3)))
    releases.append(("Austin", datetime(2010, 10, 21)))

    tmpBkupLogData = changeLogData

    # Creates logitudinal network segments for open-stack
    # for i in range (len(releases)-1):
    #    (release_name, release_date) = releases[i]
    #    prior_release_date= releases[i+1][1]
    #    print ("\t --- Generating grapth["+ release_name+"]" + "from ["+  str(prior_release_date) +"] and rel on [" + str(release_date) + "]\n")
    #    print ("\t --- Filtering change log data for [" + str(prior_release_date)+ "] <--> ["+ str(release_date)+"]")
    #    changeLogData=filterChangeLogDataByDate (prior_release_date,release_date)
    #    reprocess()
    #    print("\t --- Filtering by date is done. [" + str (sizeOriginalChangeLogData-len(changeLogData)) +"] changeLogs removed due their change date")
    #    exportLogData.createGraphML_filterByAffiliation(uniqueConnections,networked_affiliations, release_name + graphmlOutput , top10)
    #    print("\t --- Network for " + release_name+ " release created at " + release_name + graphmlOutput + " for " + str(top10) + "\n")
    #    changeLogData = tmpBkupLogData

    # Get the number of edges betwen releases i and i+1

    nodesiip1 = []
    nodesiip1Top10 = []
    edgesiip1 = []
    edgesiip1Top10 = []

    for i in range(len(releases)-1):
        (release_name, release_date) = releases[i]
        prior_release_date = releases[i+1][1]
        print("\t --- Filtering change log data for [" + str(
            prior_release_date) + "] <--> [" + str(release_date)+"]")
        changeLogData = filterChangeLogDataByDate(
            prior_release_date, release_date)
        reprocess()
        print("\t --- Filtering by date is done. [" + str(sizeOriginalChangeLogData-len(
            changeLogData)) + "] changeLogs removed due their change date")

        nnodes = len(
            JISA2015specificAnalysis.getNodesBetweenDatesInConnList(uniqueConnections))
        nnodestop10 = len(JISA2015specificAnalysis.getNodesBetweenDates4SelectedFirmsDatesInConnList(
            uniqueConnections, networked_affiliations, top10))
        nedges = len(uniqueConnections)
        nedgestop10 = len(JISA2015specificAnalysis.getConnectionsAmongTop10Only(
            uniqueConnections, networked_affiliations, top10))

        print("Number of nodes between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodes)
        print("Number of nodes (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodestop10)

        print("Number of edges between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nedges, ";")
        print("Number of edges (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nedgestop10, ";")

        nodesiip1.append(nnodes)
        nodesiip1Top10.append(nnodestop10)
        edgesiip1.append(nedges)
        edgesiip1Top10.append(nedgestop10)

        changeLogData = tmpBkupLogData

        # for debug only
        # print the edges among top10 for first release
        # print "pringing edged for reease", release_name , ":"
        # top10con = getConnectionsAmongTop10Only(uniqueConnections)
        # for edge in top10con:
        # (a,b) = edge
        # if top10con.count(edge) != 1:
        # print "ERROR:Not a single edge:"
        # print "top10con.count(edge)=[", top10con.count(edge),"] --> repeated edges"
        # print "edge in question:", edge
        # sys.exit()
        # if (b,a) in top10con:
        # print "ERROR:Not a single edge:"
        # print "top10con.count(edge)=[", top10con.count((b,a)),"] --> repeated edges (inverse relationship already accounted)"
        # print "edge in question:", edge, " and its inverse " , (b,a)
        # sys.exit()
        #
        # sys.exit()

    # Get the number of nodes and edges betwen releases i-1month and i+1
    nodesim1ip1 = []
    nodesim1ip1Top10 = []
    edgesim1ip1 = []
    edgesim1ip1Top10 = []

    releasesm1 = []
    for release in releases:
        (releasename, date) = release

        # for 4 weeks / 1 month
        # releasesm1.append((releasename, date - relativedelta(months=1)))

        # for 3 weeks
        # releasesm1.append((releasename, date - relativedelta(weeks=3)))

        # for 2 weeks
        # releasesm1.append((releasename, date - relativedelta(weeks=2)))

        # for 1 week
        releasesm1.append((releasename, date - relativedelta(weeks=1)))

    # Get the number of edges betwen releases i and i+1
    for i in range(len(releasesm1)-1):
        (release_name, release_date) = releases[i]
        prior_release_date = releasesm1[i+1][1]
        print("\t --- Filtering change log data for [" + str(
            prior_release_date) + "] <--> [" + str(release_date)+"]")
        changeLogData = filterChangeLogDataByDate(
            prior_release_date, release_date)
        reprocess()
        print("\t --- Filtering by date is done. [" + str(sizeOriginalChangeLogData-len(
            changeLogData)) + "] changeLogs removed due their change date")

        nnodes = len(
            JISA2015specificAnalysis.getNodesBetweenDatesInConnList(uniqueConnections))
        nnodestop10 = len(JISA2015specificAnalysis.getNodesBetweenDates4SelectedFirmsDatesInConnList(
            uniqueConnections, networked_affiliations, top10))

        nedges = len(uniqueConnections)
        nedgestop10 = len(JISA2015specificAnalysis.getConnectionsAmongTop10Only(
            uniqueConnections, networked_affiliations, top10))

        print ("Number of nodes between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodes)
        print ("Number of nodes (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nnodestop10)

        print ("Number of edges between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nedges, ";")
        print ("Number of edges (among TOP10 dev) between[", str(prior_release_date), "] <--> [", str(release_date), "] = ", nedgestop10, ";")

        nodesim1ip1.append(nnodes)
        nodesim1ip1Top10.append(nnodestop10)
        edgesim1ip1.append(nedges)
        edgesim1ip1Top10.append(nedgestop10)
        changeLogData = tmpBkupLogData

    # print releases name
    # Not that they are in reverse cronological order, therefore ::-1
    rname = []
    for r in releases:
        (name, nc) = r
        rname.append(name + ";")
    print( "rname", rname[::-1])

    # For all nodes
    print( "\t ALL NODES ")

    print( "nodesiip1", nodesiip1[::-1])
    print( "nodesiim1p1", nodesim1ip1[::-1])
    print( "diff capture nodes less 1 month", map(int.__sub__, nodesiip1, nodesim1ip1)[::-1])
    print( "% captured nodes less 1 month", map(float.__div__, [float(i) for i in nodesiip1], [float(i) for i in nodesim1ip1])[::-1])

    print( "edgesiip1", edgesiip1[::-1])
    print( "edgesim1ip1", edgesim1ip1[::-1])
    print( "diff edges less 1 month", map(int.__sub__, edgesiip1, edgesim1ip1)[::-1])
    print( "% captured edges less 1 month", map(float.__div__, [float(i) for i in edgesiip1], [float(i) for i in edgesim1ip1])[::-1])

    # For top 10 onlys
    print("\t TOP 10 NODES ")

    print( "nodesiip1Top10",  nodesiip1Top10[::-1])
    print( "nodesim1ip1Top10", nodesim1ip1Top10[::-1])
    print( "diff nodes top10 less 1 month", map(int.__sub__, nodesiip1Top10, nodesim1ip1Top10)[::-1])
    print( "% captured nodes less 1 month", map(float.__div__, [float(i) for i in nodesiip1Top10], [float(i) for i in nodesim1ip1Top10])[::-1])

    print( "edgesiip1Top10", edgesiip1Top10[::-1])
    print( "edgesim1ip1Top10", edgesim1ip1Top10[::-1])
    print( "diff edfes top10 less 1 month", map(int.__sub__, edgesiip1Top10, edgesim1ip1Top10)[::-1])
    print( "% captured edges less 1 month", map(float.__div__, [float(i) for i in edgesiip1Top10], [float(i) for i in edgesim1ip1Top10])[::-1])

    print("")
    print("FINNISHED " + str(datetime.now()))

    if (LOAD_MODE != 1):
        print("TOTAL TIME " + str(datetime.now() - t0))

    # Ending stats

    print("Number of analized lines [" + str(stats['nlines']) + "]")
    print(
        "Number of analized changelog blocks [" + str(stats['nBlocks']) + "]")
    print("Number of analized changelog blocks changing code files [" + str(
        stats['nBlocksChagingCode']) + "?]")
    print("Number of analized changelog blocks not changing code files (i.e. testCases)[" + str(
        stats['nBlocksNotChangingCode']) + "?]")
    print("Number of files affected by the commits reported by change log[" + str(
        stats['nChangedFiles']) + "]")


if __name__ == "__main__":
    main()
