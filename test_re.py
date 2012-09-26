'''

just test my re here
not useful at all actually
not a part of the crawler

'''
import re

def get_randomNum(txt):
    re1='(password)'    # Word 1
    re2='(_)'   # Any Single Character 1
    re3='(\\d)' # Any Single Digit 1
    re4='(\\d)' # Any Single Digit 2
    re5='(\\d)' # Any Single Digit 3
    re6='(\\d)' # Any Single Digit 4
    rg = re.compile(re1+re2+re3+re4+re5+re6,re.DOTALL)
    m = rg.search(txt)
    random_num = '1234'
    if m:
        word1=m.group(1)
        c1=m.group(2)
        d1=m.group(3)
        d2=m.group(4)
        d3=m.group(5)
        d4=m.group(6)
        random_num = d1+d2+d3+d4
        print word1+c1+random_num
    return random_num


def get_vk_by_randomNum(random_num, txt):
    """docstring for get_vk_by_randomNum"""
    start_str = "%s_" % random_num
    print "start_str: ", start_str
    start_index = txt.find(start_str)
    print "start_index: ", start_index
    end_index = start_index + txt[start_index:].find('"')
    print "end_index: ", end_index
    return txt[start_index:end_index]


def main():
    txt = open("test.html","r").read()
    random_num = get_randomNum(txt)
    print get_vk_by_randomNum(random_num,txt)


if __name__ == '__main__':
    main()

