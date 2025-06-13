import os
import requests
from bs4 import BeautifulSoup
import re
from PIL import Image
from io import BytesIO
import numpy as np


class getSiStripDiff:
    def __init__(self):
        
        self.cookies = {
            "mod_auth_openidc_session": "0f421504-8168-42f3-90f5-83dc324a17b1",
            "d46a5d9babbb50527bceb0b5e7b82c14": "3572ee32cc1b99a6344fff2b9596db19",
            "_ga": "GA1.2.19335179.1734258879",
            "_ga_898DH11X5B": "GS1.1.1734258878.1.0.1734258886.0.0.0",
            "rl_user_id": '""'
            }
        
        self.baseUrl = "https://tkmaps.web.cern.ch/tkmaps/files/data/users/event_display/Data2025/Beam/"
        self.runDictionary = {}
        self.getOnlineDirectoryDictionary()
        self.diffImage()

    def diffImage(self):
        pathMBC=f"{self.baseUrl}/393/393126/HLT/MergedBadComponentsTkMap.png"
        pathNTC=f"{self.baseUrl}/393/393126/StreamExpress/NumberOfOnTrackCluster.png"
        
        plotMBC=self.requestImage(url=pathMBC)
        plotNTC=self.requestImage(url=pathNTC)


        whiteMask = np.all(plotMBC == [255, 255, 255], axis=-1)            
        copyMBC = plotMBC.copy()

        copyMBC[whiteMask] = plotNTC[whiteMask]
        diffImage = Image.fromarray(copyMBC)
        diffImage.save('diffImage.png')
        print("Image saved successfully as 'diffImage.png'")


    def requestImage(self, url):
        return np.array(Image.open(BytesIO(requests.get(url, cookies=self.cookies).content)))


    def getOnlineDirectoryDictionary(self):
        print("getting the directory dictionary.. \n")
        top_dirs = self.getOnlineDirectory(self.baseUrl)
        for top_dir in top_dirs:
            print(f"{top_dir} \n")
            full_url = f"{self.baseUrl}{top_dir}/"
            subdirs = self.getOnlineDirectory(full_url)
            self.runDictionary[top_dir] = subdirs


    def getOnlineDirectory(self, url):
        response = requests.get(url, cookies=self.cookies)
        soup = BeautifulSoup(response.text, "html.parser")
        dirs = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if re.match(r"^\d+/$", href):  # e.g., 390/ or 390950/
                dirs.append(href.strip("/"))
        return dirs



    def createDirectory(self, directory_name):
        try:
            os.mkdir(directory_name)
            print(f"Directory '{directory_name}' created successfully.")
        except FileExistsError:
            print(f"Directory '{directory_name}' already exists.")
        except PermissionError:
            print(f"Permission denied: Unable to create '{directory_name}'.")
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == '__main__':
    gg = getSiStripDiff()
