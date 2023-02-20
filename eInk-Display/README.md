
NEED THESE FONTS: 
sudo apt-get install fonts-roboto 
sudo apt-get install fonts-freefont-ttf 

Meteocons fonts from https://www.alessioatzeni.com/meteocons/
unzip meteocons-font.zip  
rm -rf __MACOSX
mkdir -p /usr/local/share/fonts/
 
sudo cp -var meteocons-font /usr/local/share/fonts/ 
sudo chmod -R 755 /usr/local/share/fonts

display settings: 
	Display Config B 
	Interface Config 0

need Netamo libray 
	git clone https://github.com/philippelt/netatmo-api-python.git

waveshare libry needs to be somewhere in the Pyhthon path 

