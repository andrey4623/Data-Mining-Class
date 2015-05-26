# -*- coding: UTF-8 -*-

import vkapi
import sys

def get_friends(deep,ids):
    if deep == 0:
        return
    for id in ids:
        out.write(str(id) +' ')
        my_friends=()
        try:
            my_friends = set(api.friends.get(id))
        except:
            e = sys.exc_info()[0]
        for friend in my_friends:
            print friend
            out.write(str(friend)+' ')
            get_friends(deep-1, [friend])
        out.write('\n')
TOKEN = "a755ff3cd2ab5663cf5e9c2d69d9124b7bb08c0faa36f6e8abf5a8048acac1c898b2548eb8a29f797a8f0"

groups = [34737049] #Сколковский институт науки и технологий  https://vk.com/skoltech

api = vkapi.VKAPISession(TOKEN)

out = open("out.txt","w")

BRAM = [20334973]

get_friends(2,BRAM)
out.close()



