from bs4 import BeautifulSoup
import scrapy
import re
import pymongo

client = pymongo.MongoClient()
db = client.sisrekomwisata
kode = 0
jam = ""
tiket = ""
kategori = ""
namawisata =""


class QuotesSpider(scrapy.Spider):
	name = "yogyesloc"
	# def start_requests(self):
	start_urls = [
		'https://www.yogyes.com/id/yogyakarta-tourism-object/',
	]


	def parse(self,response):
		soup = BeautifulSoup(response.text, 'lxml')
		for i in soup.find('ul', 'directory').find_all('li'):
			yield response.follow(i.a.get('href'), self.parse_tempat)

	def parse_tempat(self, response):
		soup = BeautifulSoup(response.text, 'lxml')
		for i in soup.find('ul', 'directory').find_all('li'):
			yield response.follow(i.a.get('href'), self.parse_detail)

	def parse_detail(self,response):
		global jam
		global tiket
		global kategori
		global namawisata
		soup = BeautifulSoup(response.text, 'lxml')
		for i in soup.find('div', 'not-mobile').find_all('li'):
			soup = BeautifulSoup(response.text, 'lxml')
			data = soup.find('div', 'not-mobile').find_all('li')
			kategori_temp = re.sub(r'\d',"", data[2].span.string)
			namawisata = data[3].span.string
			kategori	= re.sub(r' ',"" ,kategori_temp,1)
			try:
				hlight = soup.find('div', 'highlight').find_all('p')
				tiket_temp = re.sub(r'<br/>'," ",str(hlight[0]))
				tiket_temp2 = re.search(r'Rp..........', str(hlight[0]), re.M|re.I).group()
				print(tiket_temp2)
				tiket_temp3 = re.sub(r'Rp',"", tiket_temp2)
				jam_temp = re.sub(r'<br/>'," ",str(hlight[1]))
				jam_temp2 = re.match(r'.*</b> (.*)', jam_temp, re.M|re.I).group(1)
				tiket = re.sub(r'\D',"",tiket_temp3)
				jam = re.sub(r'</p>', "", jam_temp2)
			except :
				tiket = "0"
				jam = "Senin - Minggu: buka 24 jam"
			global kode
			kode += 1
			link_loc = soup.find('div', 'address')
			yield response.follow(link_loc.a.get('href'), self.parse_location)
			

	def parse_location(self,response):
		soup = BeautifulSoup(response.text, 'lxml')
		location = soup.find_all("li")
		tag = location[5].a
		tag_h = tag['href']
		re_loc = re.search('(?<=place/).*', tag_h, re.M|re.I).group(0)
		lng = float(re.match('.*(?=,)', re_loc).group())
		lat = float(re.search('(?<=,).*',re_loc).group())
		global kode, namaisata, kategori, tiket, jam
		post = 	{
					'kode': kode,
					'nama': namawisata,
					'kategori': kategori,
					'tiket': float(tiket),
					'jam': jam,
					'location': {
						'lng': lng,
						'lat': lat
					}
				}
		posts = db.wisata
		post_id = posts.insert_one(post).inserted_id