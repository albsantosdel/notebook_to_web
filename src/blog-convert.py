import os
from subprocess import Popen
import sys
from bs4 import BeautifulSoup
import re
import yaml

def read_yaml(yaml_file):
    content = None
    with open(yaml_file, 'r') as stream:
        try:
            content = yaml.load(stream)
        except yaml.YAMLError as err:
            raise yaml.YAMLError("The yaml file {} could not be parsed. {}".format(yaml_file, err))
    return content

def read_html_file(notebook_html):
    soup = BeautifulSoup(notebook_html, "lxml")
    
    return soup

def get_menu_items(soup, element='h2'):
    menu_items = [el.get_text()[0:-1] for el in soup.find_all(element)]

    return menu_items

def get_title(soup):
    title = soup.find('title').get_text()

    return title

def read_file(additional_file):
    with open(additional_file, 'r') as f:
        txt = f.read()

    return txt

def add_menu_items(nb_txt, menu_items):
    additional_txt = '<a class="dropdown-item" href="#{MENU_ITEM_ID}">{MENU_ITEM_NAME}</a><div class="dropdown-divider"></div>'
    add_lines = []
    for menu_item in menu_items:
        add_lines.append(additional_txt.replace('{MENU_ITEM_ID}', menu_item.replace(' ', '-')).replace('{MENU_ITEM_NAME}', menu_item))
    
    nb_txt = nb_txt.replace("{MENU_ITEMS}", "\n".join(add_lines))

    return nb_txt

def complement_html(soup, vp_txt, nb_txt, st_txt, about_txt):
    new_html = []
    for line in str(soup).split('\n'):
        if '<div class="prompt output_prompt">' not in line and '<link href="custom.css" rel="stylesheet"/>' not in line:
            if line.strip().startswith('<title>'):
                regex = r"(<title>.+<\/title>)"
                matches = re.search(regex,line.strip())
                if matches:
                    line = matches.group(1)
                    new_html.append(line)
                new_html.append(vp_txt)
            elif line.strip().startswith('<body>'):
                new_html.append(line)
                new_html.append(nb_txt)
            elif line.strip().startswith('<!-- Custom'):
                new_html.append(line)
                new_html.append(st_txt)
            elif line.strip().startswith('</body>'):
                new_html.extend([about_txt,line.strip()])
            else:
                new_html.append(line)

    return "\n".join(new_html)


def read_img_txt(img_txt_files):
    img_txt = {}
    for img_name in img_txt_files:
        f = img_txt_files[img_name]
        img_txt[img_name] = read_yaml(f)

    return img_txt

def add_yml(text, yml_txt):
    for name in yml_txt:
        for key in yml_txt[name]:
            r = '{%s_%s}' % (name.upper(), key.upper())
            r_by = yml_txt[name][key]
            text = text.replace(r, r_by)
    return text

if __name__ == "__main__":
    vp_file = "./assets/viewport.txt"
    nb_file = "./assets/navbar.txt"
    st_file = "./assets/custom_stylesheet.txt"
    about_file = "./assets/aboutus.txt"
    about_yml_file = './assets/aboutus.yml'
    img_yml_files = {"logo":"./assets/img/logo.yml"}
    new_file = sys.argv[1]
    notebook_html = read_file(new_file)
    soup = read_html_file(notebook_html)
    menu_items = get_menu_items(soup)
    nb_txt = read_file(nb_file)
    title = get_title(soup)
    img_txt = read_img_txt(img_yml_files)
    nb_txt = nb_txt.replace('{TITLE}', title.title())
    nb_txt = add_yml(nb_txt, img_txt)
    nb_txt = add_menu_items(nb_txt, menu_items)
    vp_txt = read_file(vp_file)
    st_txt = read_file(st_file)

    about_txt = read_file(about_file)
    
    new_html = complement_html(soup, vp_txt, nb_txt, st_txt, about_txt)
    with open(new_file+".new.html", 'w') as out:
        out.write(new_html)

