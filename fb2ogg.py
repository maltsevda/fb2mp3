import sys
import requests
import xml.parsers.expat

# https://cloud.yandex.ru/docs/speechkit/tts/request
folder_id = "FOLDER_ID"
iam_token = "IAM_TOKEN"

# -- Chapter -------------------------------------------------------------------

class Chapter:

    def __init__(self):
        self.title = ''
        self.content = []

    def print(self):
        print(self.title)
        for p in self.content:
            print(p)
        print('')

    def add_title(self, text):
        self.title += text

    def add_paragraph(self, text):
        self.content.append(text)

    def get_plaintext(self):
        if self.title:
            text = self.title + '\n'
        for p in self.content:
            if p: text += p + '\n'
        return text

# -- Parser for FB2 ------------------------------------------------------------

class ParserFB2:

        def __init__(self):
            self.body = False
            self.section = False
            self.title = False
            self.ignore = True
            self.text = ''
            self.chapter = None
            self.book = []

            self.parser = xml.parsers.expat.ParserCreate()
            self.parser.CharacterDataHandler = self.handleCharData
            self.parser.StartElementHandler = self.handleStartElement
            self.parser.EndElementHandler = self.handleEndElement

        def parse(self, file_name):
            self.book = []
            with open(file_name, 'rb') as file:
                self.parser.Parse(file.read(), True)

        def handleCharData(self, data):
            if not self.ignore:
                self.text = self.text + data

        def handleStartElement(self, name, attrs):
            if name == 'body':
                self.body = True
                if ('name' in attrs) and (attrs['name'] == 'notes'):
                    self.body = False
            if name == 'section' and self.body:
                self.chapter = Chapter()
                self.section = True
            if name == 'title' and self.section:
                self.title = True
            if name == 'p' and self.section:
                self.ignore = False
                self.text = ''

        def handleEndElement(self, name):
            if name == 'p':
                self.ignore = True
                if self.title:
                    self.chapter.add_title(self.text)
                elif self.section:
                    self.chapter.add_paragraph(self.text)
            if name == 'title':
                self.title = False
            if name == 'section' and self.section:
                self.section = False
                self.book.append(self.chapter)
                self.chapter = None
            if name == 'body':
                self.body = False

# -- Functions -----------------------------------------------------------------

def utf8len(str):
    return len(str.encode('utf-8'))

def split_by_size(text, max_size):
    result = []
    block_text = ''
    block_size = 0
    for sentence in text.split('.'):
        sentence += '.'
        sentence_size = utf8len(sentence)
        if block_size + sentence_size < max_size:
            block_size += sentence_size
            block_text += sentence
        else:
            result.append(block_text)
            block_size = sentence_size
            block_text = sentence
    if block_text:
        result.append(block_text[:-1])
    return result

# -- Yandex --------------------------------------------------------------------

def synthesize(folder_id, iam_token, text):
    url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
    headers = {
        'Authorization': 'Bearer ' + iam_token,
    }
    data = {
        'text': text,
        'voice': 'ermil',
        'emotion': 'neutral',
        'format': 'oggopus',
        'folderId': folder_id,
    }
    resp = requests.post(url, headers=headers, data=data)
    if resp.status_code != 200:
        raise RuntimeError("Invalid response received: code: %d, message: %s" % (resp.status_code, resp.text))
    return resp.content

# -- Entry ---------------------------------------------------------------------

def main(in_file_name, folder_id, iam_token):
    max_size = 8 * 1024
    out_file_format = 'chapter_{}_{}.ogg'

    parser = ParserFB2()
    parser.parse(in_file_name)

    chapter_index = 1+15
    chapters_count = len(parser.book)
    for chapter in parser.book[15:]:
        block_index = 1
        text = chapter.get_plaintext()
        for block in split_by_size(text, max_size):
            print("Chapter {} / {}. Block {}.".format(chapter_index, chapters_count, block_index), end = '\r')
            audio_content = synthesize(folder_id, iam_token, block)
            out_file_name = out_file_format.format(chapter_index, block_index)
            with open(out_file_name, 'wb') as file:
                file.write(audio_content)
            block_index += 1
        chapter_index += 1
    print()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1], folder_id, iam_token)
