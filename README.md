## Canvas Glossary

This Python package helps create tool tips in a Canvas course, if there is a page called "Global Glossary" with HTML description lists.

### Installation

You can install the released version of Uppraisal from GitHub with:

```shell 
$ pip install https://github.com/cisglee/canvasglossary/zipball/master
```

Afterwards, go to the package folder and install the dependencies:

```shell
$ pip install -r requirements.txt
```

### Usage
### `retrieve_glossary`

```python
from retrieve_glossary import retrieve_glossary

glossary = retrieve_glossary(course_id=12345)

print(glossary)
# {'Term 1': 'Definition 1', 'Term 2': 'Definition 2', ...}
```

### `set_tool_tips`
```python
from retrieve_glossary import set_tool_tips

# html = '<p>This is a sentence about Term 1.</p'
glossary = {'Term 1': 'Description 1', 'Term 2': 'Description 2'}

result = set_tool_tips(glossary_dict=glossary)

print(result)
# '<p>This is a sentence about <span title="Description 1">Term 1</a>.</span>'

```

### License

This project is licensed under the MIT License - see the LICENSE file for details.

### Acknowledgments

* Based on the [RMIT University Glossary Tool](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwjust3K6b_9AhWOoaQKHVHhCucQFnoECAwQAQ&url=https%3A%2F%2Fwww.rmit.edu.au%2Fcontent%2Fdam%2Frmit%2Fdocuments%2Fstaff-site%2FLearning_and_Teaching%2FLearning-and-Teaching-Design%2FGlossaryTool.pdf&usg=AOvVaw1oVec6RbF8-62RbxZmVqwt).
* The tool uses the [Canvas LMS REST API](https://canvas.instructure.com/doc/api/).
