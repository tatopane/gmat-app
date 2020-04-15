from flask import Flask, render_template

app = Flask(__name__)

import requests as r
from bs4 import BeautifulSoup
import random

def get_random_question(section=None, difficulty=None):
	urls = {
		"PS": {
			"700": "https://gmatclub.com/forum/search.php?search_tags=all&selected_search_tags%5B%5D=187",
			"600": "https://gmatclub.com/forum/search.php?search_tags=all&selected_search_tags%5B%5D=216",
			"500": "https://gmatclub.com/forum/search.php?search_tags=all&selected_search_tags%5B%5D=217",
			},
		"DS": {
			"700": "https://gmatclub.com/forum/search.php?search_tags=all&selected_search_tags%5B%5D=180",
			"600": "https://gmatclub.com/forum/search.php?search_tags=all&selected_search_tags%5B%5D=222",
			"500": "https://gmatclub.com/forum/search.php?search_tags=all&selected_search_tags%5B%5D=223",
			},
		"CR": {
			"700": "https://gmatclub.com/forum/search.php?search_tags=all&selected_search_tags%5B%5D=168",
			"600": "https://gmatclub.com/forum/search.php?search_tags=all&selected_search_tags%5B%5D=226",
			"500": "https://gmatclub.com/forum/search.php?search_tags=all&selected_search_tags%5B%5D=227",
			},
		"SC": {
			"700": "https://gmatclub.com/forum/search.php?search_tags=all&selected_search_tags%5B%5D=172",
			"600": "https://gmatclub.com/forum/search.php?search_tags=all&selected_search_tags%5B%5D=231",
			"500": "https://gmatclub.com/forum/search.php?search_tags=all&selected_search_tags%5B%5D=232",
			},
		"RC": {
			"700": "https://gmatclub.com/forum/search.php?search_tags=all&selected_search_tags%5B%5D=162",
			"600": "https://gmatclub.com/forum/search.php?search_tags=all&selected_search_tags%5B%5D=228",
			"500": "https://gmatclub.com/forum/search.php?search_tags=all&selected_search_tags%5B%5D=229",
			},
	}

	if section == None:
		section = random.choice(urls.keys())
	if difficulty == None:
		difficulty = random.choice(urls[section].keys())

	start_num = random.randint(0,20)
	url = urls[section][difficulty] + "&start=%s" % (start_num,)
	print(url)
	page = r.get(url)
	soup = BeautifulSoup(page.content, "lxml")
	row_num = random.randint(0,49)
	url = soup.find_all("td", class_="topicsName")[row_num].find_all("a")[1]["href"]
	return url

def parse_question(url=None):
	print(url)
	page = r.get(url)
	soup = BeautifulSoup(page.content, "lxml")
	question = soup.select("#posts > tbody:nth-of-type(1) > tr:nth-of-type(1) > td.right > div.item.text")[0]
	
	## find OA
	oa = question.find('div', class_='item twoRowsBlock')
	if oa is not None:
		oa = oa.extract()

	## find attachment
	attachment = question.find('div', class_='attachcontent')
	if attachment is not None:
		attachment = attachment.extract()

	## remove non interesting data like footers
	[q.decompose() for q in question.find_all("div")]
	[q.decompose() for q in question.find_all("p")]
	
	## append again OA
	if attachment is not None:
		question.insert(1,attachment)
	if oa is not None:
		question.append(soup.new_tag('br'))
		question.append(soup.new_tag('br'))
		question.append(oa)

	## fix images
	for img in question.find_all("img"):
		img['src'] = "https://gmatclub.com/forum" + img['src'][1:]

	return question

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/question")
def question():
	#url = "https://gmatclub.com/forum/the-value-of-a-precious-stone-is-directly-proportional-to-the-cube-of-its-weight-253866.html"
	#url = "https://gmatclub.com/forum/sam-and-david-agreed-to-complete-a-work-in-14-days-253828.html"
	url = get_random_question()
	q = parse_question(url + "?kudos=1")
	return render_template('question.html', question=q, question_url=url)

if __name__ == "__main__":
    app.run()