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

#######################

def start_element(name, attrs):
	global body, par
	if name == 'body':
		body = True
	if name == 'p':
		par = '';

def end_element(name):
	global body, par, book
	if name == 'body':
		body = False
	if body == False:
		return
	if name == 'p':
		par = par.strip()
		if len(par) > 0:
			book.append(par)
	if name not in ['a', 'strong', 'emphasis', 'style']:
		par = ''

def char_data(data):
	global par
	par = par + data
	par = par.replace('–', '-')

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
	for par in book:
		if len(par) > 3:
			file_name = '{0}/{0}{1:05}.mp3'.format(title, index) 
			voice.fetch_voice(par, file_name)
			index += 1

#######################

def main(book_name):
	parse_fb2(book_name)
	make_mp3(book_name)

if __name__ == '__main__':
	if len(sys.argv) > 1:
		main(sys.argv[1])
