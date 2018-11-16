import requests
from bs4 import BeautifulSoup as bs
import time
import csv
from os import path
from os import mkdir
import urllib

username = #Enter username here#
password = #Enter password here#
degree = "Dual Degree"
filename = 'companies.csv'
foldername = "Companies"
filepath = foldername+"/"+filename
shortfilepath = foldername+"/"+"slist.txt"
download_description = True

url_login = "http://placement.iitm.ac.in/students/login.php"
url_companies = "http://placement.iitm.ac.in/students/comp_list.php"
url_base = "http://placement.iitm.ac.in/students/"
url_base_attachment = "http://placement.iitm.ac.in/"
url_app_comp = "http://placement.iitm.ac.in/students/app_comp.php"

clist_saved = []

if not path.exists(foldername):
	mkdir(foldername)

if path.exists(filepath):
	csvfile = open(filepath, 'r')
	reader = csv.reader(csvfile)
	for row in reader:
		clist_saved.append(row)
	csvfile.close()

def print_data(data):
	col_width = max(len(word) for row in data for word in row) + 2
	for row in data:
	    print "".join(word.ljust(col_width) for word in row)
	
def gettext(component):
	if component is None:
		return ''
	else:
		return component.text.lstrip().rstrip()

def getlink(pcs,component):
	if component is None:
		return ''
	else:
		link = url_base_attachment + component['href'][2::]
		global download_description
		if download_description:
			download(pcs,link)
		return link
		
def getfilename(link):
	out = link.rsplit('/',1)
	return out[1]

def getformattedlink(link):
	out = link.rsplit('/',1)
	init = out[0]
	fin = out[1]
	fin = urllib.quote(fin)
	return init+"/"+fin
		
def getformat(text):
	return text.rsplit('-',1)
	
def download(pcs,component):
	r = pcs.get(getformattedlink(component), stream=True)
	filename = foldername+"/"+getfilename(component)
	if not path.exists(filename):
		print filename
		with open(filename, 'wb') as f:
        		for chunk in r.iter_content(1024):
            			f.write(chunk)

pcs = requests.Session()
login_data = {"rollno": username,"pass":password,"submit":"Login"}
pc_login = pcs.post(url_login,login_data)
pc_home = pcs.get(url_companies)
soup = bs(pc_home.text,'html.parser')
companies = soup.find_all("a",href=True,onclick=True)
details_companies = []
header = ['Company Name','Designation','Offer Type','Job Details','Currency','CTC','Gross Taxable Income','Basic Pay','Extras']
details_companies.append(header)
for company in companies:
	if not 'view_profile' in company['href']:
		continue
	details_company = []
	pc_comp = pcs.get(url_base+company['href'])
	csoup = bs(pc_comp.text,'html.parser')
	title = csoup.find("div",class_="style5")
	details_company.extend(getformat(gettext(title)))
	type_offer = csoup.find("td",valign="top",width="380")
	details_company.append(gettext(type_offer))
	descr = csoup.find("a",href=True)
	details_company.append(getlink(pcs,descr))
	currency = csoup.find("td",width="464",valign="top")
	details_company.append(gettext(currency))
	deg_find = csoup.find_all("tr")
	for deg in deg_find:
		if(degree in deg.text and deg.find("strong") is not None):
			ctc = deg.find("td",width="14%")
			details_company.append(gettext(ctc))
			gti = deg.find("td",width="13%")
			details_company.append(gettext(gti))
			ex = deg.find_all("td",width="16%")
			basic = ex[0]
			details_company.append(gettext(ex[0]))
			extras = ex[1]
			details_company.append(gettext(ex[1]))
	#print details_company
	if not details_company in clist_saved:
		print details_company[0]
	details_companies.append(details_company)

csvfile = open(filepath,'w')
writer = csv.writer(csvfile)
for details_company in details_companies:
	writer.writerow(details_company)
csvfile.close()
print "DONE"

apco = pcs.get(url_app_comp)
noc = apco.text.count("<font color=red>No</font>")
yec = apco.text.count("<font color=green>yes</font>")
outstr = str(noc)+","+str(yec)
slfile = open(shortfilepath,'r')
instr = slfile.read()
slfile.close()
if not (outstr in instr):
	slfile = open(shortfilepath,'w')
	slfile.write(outstr)
	slfile.close()
	print "New shortlists out"
else:
	print "No new shortlists"
