#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Denis Maltsev
# 21.01.2016

import sys, os
import xml.parsers.expat
import pyvona

book = []
par = ''
body = False
ignore = True

#######################

def modify(str):
	return str.strip().replace('\n', ' ').replace('–', '-').replace('—', '-')

def start_element(name, attrs):
	global body, par, ignore
	if name == 'body':
		body = True
	if name == 'p':
		par = '';
		ignore = False

def end_element(name):
	global body, par, book, ignore
	if name == 'body':
		body = False
	if body == False:
		return
	if name == 'p':
		ignore = True
		par = modify(par)
		if len(par) > 0:
			book.append(par)
		par = ''

def char_data(data):
	if not ignore:
		global par
		par = par + data

def parse_fb2(book_name):
	book_file = open(book_name, 'rb')
	p = xml.parsers.expat.ParserCreate()
	p.StartElementHandler = start_element
	p.EndElementHandler = end_element
	p.CharacterDataHandler = char_data
	p.Parse(book_file.read(), True)

#######################

def make_mp3(book_name):
	global book

	voice = pyvona.create_voice('GDNAICTDMLSLU5426OAA', '2qUFTF8ZF9wqy7xoGBY+YXLEu+M2Qqalf/pSrd9m')
	voice.codec = 'mp3'
	voice.region = 'ru-RU'
	voice.speech_rate = 'medium' # x-slow, slow, medium, fast, x-fast
	voice.voice_name = 'Tatyana' # Tatyana, Maxim 

	title = os.path.splitext(book_name)[0]
	if not os.path.exists(title):
		os.makedirs(title)

	index = 0
	percent = 10
	count = len(book)
	for i, par in enumerate(book):
		if len(par) > 3:
			file_name = '{0}/{0}{1:05}.mp3'.format(title, index) 
			voice.fetch_voice(par, file_name)
			index += 1
		# progress bar
		if i >= percent * count / 100:
			sys.stdout.write('{0}%...'.format(percent))
			sys.stdout.flush()
			percent += 10
	print('100%')

#######################

# def log_file(book_name):
# 	title = os.path.splitext(book_name)[0]
# 	f = open('_{0}.log'.format(title), 'w', encoding='utf-8')
# 	for par in book:
# 		f.write('{0}\n'.format(par))
# 	f.close()

#######################

def main(book_name):
	parse_fb2(book_name)
	make_mp3(book_name)

if __name__ == '__main__':
	if len(sys.argv) > 1:
		main(sys.argv[1])
