from retrieve_glossary import set_tool_tips


def retrieve_and_apply_glossary(course_id, glossary_dict, canvas_glossary_page):
    set_tool_tips(course_id, glossary_dict, canvas_glossary_page)  # Press Ctrl+F8 to toggle the breakpoint.


if __name__ == '__main__':
    course_id = 29625
    glossary_dict = {'Term 1': 'Definition 1', 'Term 2': 'Definition 2'}
    canvas_glossary_page = 'Global Glossary'
    retrieve_and_apply_glossary(course_id, glossary_dict, canvas_glossary_page)
