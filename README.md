The given tool can extract usernames, picture captions, likes, date of upload from pictures under a Hashtag.
To use this tool follow the below given steps:
1. Clone the repository
2. Open your terminal
3. Setup a virtual environment:
>py -m virtualenv 'anyname'
4. Install the requirements.txt file (this is a one time process) using the following syntax on your system
>py -m pip install -r requirements.txt
5. After installation the tool is read to use. 
>py Instagram_Scraper.py -l 'your username' -p 'your password' -s 'the tag you want to scrap' -n 2 -o 'any name you want'.csv

The tool will extract the data and save a csv file in the same repository or folder

Beware, Instagram keeps updating their interface and that could cause this tool to not work if you end up using it. There is a quick fix and that is to update the xpaths for all the components in the code.
It is very easy to do.
Here is how you can update the xpaths to the files:
Take an example of likes.
1. Go to your desired post and click inspect/inspect element.
2. Press ctrl+shift+c. This nnow lets you inspect specific elements.
3. Hover over the likes, double click them and their HTML code is highlighted. You can copy this code as an xpath and update it for your use in the future.

This particular code is in large parts written by https://github.com/hugozanini/hugozanini and my effort into it is minimal. The original tool that he made public is https://github.com/hugozanini/instagram-bot.
I have updated all the parameters to work seemlessly with newer versions of selenium.

CAUTION: You would be required to install python 3.9 series as there are speciic libraries in the requirements.txt that need it and are not compatible with newer versions of python.
