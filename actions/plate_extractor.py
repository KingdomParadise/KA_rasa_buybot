from concurrent.futures import ThreadPoolExecutor

try:
    from data import words
except ImportError:
    from .data import words
from PyDictionary import PyDictionary
import re
dictionary=PyDictionary()




def GET_PLATES(message):
    pattern = "[" +'!@#$%^&*()[]+=/*.,|{}\\\'\"~`' + "]"
    message = re.sub(pattern, "", message).replace('{','').replace('}','').replace('[','').replace(']','')

    message = message.split()
    for x in words:
        if x in message:message.remove(x)
    data2 = []
    # def get_meaning(word):
    #     res = dictionary.meaning(word)
    #     data2.append([word,res]) 
    # with ThreadPoolExecutor(max_workers=100) as executor:
    #     executor.map(get_meaning, message) 
    # data2 = [x for x in data2 if x[-1]]
    # data2 = [x[0] for x in data2]

    # for x in data2:
    #     if x in message:message.remove(x)
    return message






 