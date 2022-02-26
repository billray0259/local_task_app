# import bs4
# import requests
# import numpy as np

# mp3_links = []

# for i in range(10):
#     hostname = "https://www.myinstants.com"
#     url = "%s/trending/us/?page=%d" % (hostname, i)

#     print(mp3_links)

#     response = requests.get(url)
#     search_page = bs4.BeautifulSoup(response.text, features="lxml")

#     buttons = search_page.find_all("div", {"class": "instant"})

#     for button in buttons:
#         path = button.find("a")["href"]
#         sound_url = hostname + path
#         response = requests.get(sound_url)
#         sound_page = bs4.BeautifulSoup(response.text, features="lxml")
#         for a in sound_page.find_all("a"):
#             if a["href"][-4:] == ".mp3":
#                 mp3_links.append(hostname + a["href"])
#                 break
    

# np.savetxt("mp3_links.txt", np.array(mp3_links), fmt="%s")



import vlc
p = vlc.MediaPlayer("https://www.myinstants.com/media/sounds/movie_1.mp3")
p.play()
