from unittest import TestCase

from htmlmin import minify

import retrieve_glossary


class TestRetrieveGlossary(TestCase):
    def setUp(self):
        self.glossary_html = '''
        <dl>
          <dt>Python</dt>
          <dd>A high-level programming language.</dd>
          <dt>web development</dt>
          <dd>The process of building websites and web applications.</dd>
          <dt>data analysis</dt>
          <dd>The process of cleaning, transforming, and modeling data in order to discover useful information.</dd>
        </dl>
        '''
        self.glossary_html = minify(self.glossary_html, remove_empty_space=True)
        self.html = '''
        <html>
          <head>
            <title>HTML Example</title>
          </head>
          <body>
            <p>Python is a programming language that is easy to learn and use.</p>
            <p>It is often used for web development, scientific computing, data analysis, artificial intelligence, and more.</p>
          </body>
        </html>
        '''
        self.html = minify(self.html, remove_empty_space=True)
        self.html_lowercase = self.html.lower()
        self.html_to_update = '''
        <html>
          <head>
            <title>HTML Example</title>
          </head>
          <body>
            <p><span title="A type of snake">Python</span> is a programming language that is easy to learn and use.</p>
            <p>It is often used for web development, scientific computing, data analysis, artificial intelligence, and more.</p>
          </body>
        </html>
        '''
        self.html_to_update = minify(self.html_to_update, remove_empty_space=True)
        self.html_to_expect = '''
        <html>
          <head>
            <title>HTML Example</title>
          </head>
          <body>
            <p><span title="A high-level programming language.">Python</span> is a programming language that is easy to learn and use.</p>
            <p>It is often used for <span title="The process of building websites and web applications.">web development</span>, scientific computing, <span title="The process of cleaning, transforming, and modeling data in order to discover useful information.">data analysis</span>, artificial intelligence, and more.</p>
          </body>
        </html>
        '''
        self.html_to_expect = minify(self.html_to_expect, remove_empty_space=True)
        self.glossary_dict = {
            'Python': 'A high-level programming language.',
            'web development': 'The process of building websites and web applications.',
            'data analysis': 'The process of cleaning, transforming, and modeling data in order to discover useful information.',
        }

    def test_retrieve_glossary(self):
        result = retrieve_glossary.parse_html_glossary(self.glossary_html)
        self.assertEqual(self.glossary_dict, result)

    def test_enrich_with_glossary(self):
        result = retrieve_glossary.enrich_html_with_glossary(self.html, self.glossary_dict)
        result = minify(result, remove_empty_space=True)
        self.assertEqual(self.html_to_expect, result)

        result = retrieve_glossary.enrich_html_with_glossary(self.html_lowercase, self.glossary_dict)
        self.assertEqual(self.html_to_expect.lower(), result.lower(),
                         msg="enrich_page_with_glossary appears to be case-sensitive.")

    def test_update_with_glossary(self):
        result = retrieve_glossary.enrich_html_with_glossary(self.html_to_update, self.glossary_dict)
        result = minify(result, remove_empty_space=True)
        self.assertEqual(self.html_to_expect, result)
