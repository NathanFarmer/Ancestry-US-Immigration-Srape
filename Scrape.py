import bs4, re, csv, math, sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# opens and logs in using credentials
browser = webdriver.PhantomJS()
browser.get("https://www.ancestry.com/secure/login")
username = browser.find_element_by_id("username")
password = browser.find_element_by_id("password")

username.send_keys("username")
password.send_keys("password")

form = browser.find_element_by_id('loginForm')
form.submit()

# reads csv names
f = open('lastnames.csv', 'r')
reader = csv.reader(f)
namesList = list(reader)
f.close()

names = [l[0] for l in namesList]

print('Names: ', names)
print(len(names))

numResults = list()

for row in names:

    # builds the URL
    url = 'http://search.ancestry.com/cgi-bin/sse.dll?db=nypl&gss=angs-d&new=1&rank=1&msT=1&MS_AdvCB=1&gsln=' + str(row) + '&gsln_x=1&MSAV=2&uidh=qf1&gl=&gst=&hc=50'
    browser.get(url)
    # tells the browser to wait until the page is fully loaded
    try:
        element = WebDriverWait(browser, 30).until(EC.presence_of_all_elements_located((By.ID, "results-main")))
    finally:
        # parses HTML and finds the total number of records
        noStarchSoup = bs4.BeautifulSoup(browser.page_source, "html.parser")
    
    resultsStr = str(noStarchSoup.select('h3[class="w50"]'))

    found = re.search('of\s(\d*)(,?)(\d+)\n', resultsStr)
    if found:
        numResults.append(found.group(1) + found.group(3))
    else:
        numResults.append(0)

# converts the total number of records from list to int        
numResults = list(map(int, numResults))
print('Results per name: ', numResults)
print(len(numResults))
print('Total Records: ' + str(sum(numResults)))

# divides and rounds up to compute the number of results pages
numPages = [math.ceil(x/50) for x in numResults]
print('Results pages per name: ', numPages)
print(len(numPages))

# computers the remainder of results left on the last results page
lastPageNum = [x%50 for x in numResults]
print('Last page results left: ', lastPageNum)
print(len(lastPageNum))

# open output file
csv_file = open("Output.csv", "w")

recordCount = int()

# nested for loops cycle through every result and scrape data
for x in names:
    for y in range(0,numPages[names.index(x)]):
        # builds the URL
        if (y==0):
            url = 'http://search.ancestry.com/cgi-bin/sse.dll?_phsrc=plt29&_phstart=successSource&usePUBJs=true&db=nypl&gss=angs-d&new=1&rank=1&msT=1&MS_AdvCB=1&gsln=' + str(x) + '&gsln_x=1&MSAV=2&uidh=qf1&gl=&gst='
            browser.get(url)
        else:
            nextPage = browser.find_element_by_css_selector('.ancBtn.sml.green.icon.iconArrowRight')
            nextPage.click()
            browser.get(browser.current_url) 
        
        # tells the browser to wait until the page is fully loaded
        try:
            element = WebDriverWait(browser, 30).until(EC.presence_of_all_elements_located((By.ID, "results-main")))
        finally:
            noStarchSoup = bs4.BeautifulSoup(browser.page_source, "html.parser")
        
        
        if (y == numPages[names.index(x)]-1) and (lastPageNum[names.index(x)] != 0):
            for z in range(0,lastPageNum[names.index(x)]):
                # parses HTML and finds the total number of records
                findTag = 'tr[id="sRes-' + str(z) + '"]'
                resultsStr = str(noStarchSoup.select(findTag))
                soup = bs4.BeautifulSoup(resultsStr, "html.parser")
                
                found = re.search('srchHit">(.+)\s<span\sclass=', resultsStr)
                if found:
                    with open("Output.csv", "a") as myfile:
                        myfile.write("\n" + x + ",")
                        myfile.write(found.group(1) + ",")
                        recordCount += 1
                        #print("Record: " + str(recordCount) + " of " + str(sum(numResults)) + " [" + str(round(recordCount/sum(numResults)*100,2)) + " % Complete]")
                else:
                    with open("Output.csv", "a") as myfile:
                        myfile.write("\n" + x + ",")
                        myfile.write(", ")
                        recordCount += 1
                        #print("Record: " + str(recordCount) + " of " + str(sum(numResults)) + " [" + str(round(recordCount/sum(numResults)*100,2)) + " % Complete]")
                        
                found = soup('td', limit=9)[2].contents[0]
                if found:
                    with open("Output.csv", "a") as myfile:
                        myfile.write(str(soup('td', limit=9)[2].contents[0]) + ",")
                else:
                    with open("Output.csv", "a") as myfile:
                        myfile.write(",")
                        
                found = soup('td', limit=9)[3].contents[0]
                if found:
                    with open("Output.csv", "a") as myfile:
                        myfile.write(str(soup('td', limit=9)[3].contents[0]) + ",")
                else:
                    with open("Output.csv", "a") as myfile:
                        myfile.write(",")
                
                found = soup('td', limit=9)[4].contents[0]
                if found:
                    with open("Output.csv", "a") as myfile:
                        removeComma = re.sub(',', '', str(soup('td', limit=9)[4].contents[0]))
                        myfile.write(removeComma + ",")
                else:
                    with open("Output.csv", "a") as myfile:
                        myfile.write(",")
                
                found = soup('td', limit=9)[5].contents[0]
                if found:
                    with open("Output.csv", "a") as myfile:
                        myfile.write(str(soup('td', limit=9)[5].contents[0]) + ",")
                else:
                    with open("Output.csv", "a") as myfile:
                        myfile.write(",")
                
                found = soup('td', limit=9)[6].contents[0]
                if found:
                    with open("Output.csv", "a") as myfile:
                        myfile.write(str(soup('td', limit=9)[6].contents[0]))
                        
        else:
            for z in range(0,50):
                # parses HTML and finds the total number of records
                findTag = 'tr[id="sRes-' + str(z) + '"]'
                resultsStr = str(noStarchSoup.select(findTag))
                soup = bs4.BeautifulSoup(resultsStr, "html.parser")
                
                found = re.search('srchHit">(.+)\s<span\sclass=', resultsStr)
                if found:
                    with open("Output.csv", "a") as myfile:
                        myfile.write("\n" + x + ",")
                        myfile.write(found.group(1) + ",")
                        recordCount += 1
                        #print("Record: " + str(recordCount) + " of " + str(sum(numResults)) + " [" + str(round(recordCount/sum(numResults)*100,2)) + " % Complete]")
                else:
                    with open("Output.csv", "a") as myfile:
                        myfile.write("\n" + x + ",")
                        myfile.write(",")
                        recordCount += 1
                        #print("Record: " + str(recordCount) + " of " + str(sum(numResults)) + " [" + str(round(recordCount/sum(numResults)*100,2)) + " % Complete]")  
                
                found = soup('td', limit=9)[2].contents[0]
                if found:
                    with open("Output.csv", "a") as myfile:
                        myfile.write(str(soup('td', limit=9)[2].contents[0]) + ",")
                else:
                    with open("Output.csv", "a") as myfile:
                        myfile.write(",")
                        
                found = soup('td', limit=9)[3].contents[0]
                if found:
                    with open("Output.csv", "a") as myfile:
                        myfile.write(str(soup('td', limit=9)[3].contents[0]) + ",")
                else:
                    with open("Output.csv", "a") as myfile:
                        myfile.write(",")
                
                found = soup('td', limit=9)[4].contents[0]
                if found:
                    with open("Output.csv", "a") as myfile:
                        removeComma = re.sub(',', '', str(soup('td', limit=9)[4].contents[0]))
                        myfile.write(removeComma + ",")
                else:
                    with open("Output.csv", "a") as myfile:
                        myfile.write(",")
                
                found = soup('td', limit=9)[5].contents[0]
                if found:
                    with open("Output.csv", "a") as myfile:
                        myfile.write(str(soup('td', limit=9)[5].contents[0]) + ",")
                else:
                    with open("Output.csv", "a") as myfile:
                        myfile.write(",")
                
                found = soup('td', limit=9)[6].contents[0]
                if found:
                    with open("Output.csv", "a") as myfile:
                        myfile.write(str(soup('td', limit=9)[6].contents[0]))
        
        print("Record: " + str(recordCount) + " of " + str(sum(numResults)) + " [" + str(round(recordCount/sum(numResults)*100,2)) + "% Complete]")  
                

csv_file.close()
browser.close()
sys.exit()