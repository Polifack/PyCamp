import sys
import urllib.request
import os
import eyed3
import re
import datetime
import json

def downloadAlbum(albumLink): 
	# Do the request to the url passed as argument
	with urllib.request.urlopen(albumLink) as response:
		sourceCode = response.read()
	print(("Downloading "+albumLink)) 
	
	# Get the source code of the bandcamp page
	sourceCode = sourceCode.decode("utf8")
	sourceCode = sourceCode.replace("&quot;", '"')

	# The songs are stored in the page in the json attached in <script type="application/ld+json">
	# Search the object with a REGEXP

	# flags > re.M means "try the expression each new line"
	# flags > re.I means "dont be case sensitive"
	albumData = re.search( r'<script type="application/ld\+json">\n(.*)', sourceCode, re.M|re.I)


	# If we find the json
	if albumData:
		jsonInf = albumData.group(1)
		albumInfo = json.loads(jsonInf)

		# Extract the relevant info
		albumImage = albumInfo["image"]
		albumName = albumInfo["albumRelease"][0]["name"]
		albumArtist = albumInfo["byArtist"]["name"]
		albumDate = datetime.datetime.strptime(albumInfo["datePublished"][7:], '%Y %H:%M:%S GMT')
		albumYear = albumDate.date().year
		albumTracks = albumInfo["track"]["itemListElement"]

		# Create the folder where the songs will be downloaded
		albumDownloadPath = albumArtist+" - "+albumName
		os.mkdir(albumDownloadPath)
		os.chdir(albumDownloadPath)
		
		# Download album cover
		urllib.request.urlretrieve (albumImage, "cover.jpg")		
		
		# Download the songs
		for element in albumTracks:
			# Get track data
			trackPosition = int(element["position"])
			trackName = element["item"]["name"]
			trackUrl = element["item"]["additionalProperty"][2]["value"]

			print("Downloading track",trackPosition,":",trackName)

			# Remove weird characters and set filename
			filename = trackName+".mp3"

			urllib.request.urlretrieve (trackUrl, filename)
			mp3File = eyed3.load(filename)

			# Set tags
			mp3File.tag = eyed3.id3.Tag()
			mp3File.tag.title = trackName
			mp3File.tag.artist = albumArtist
			mp3File.tag.album = albumName
			mp3File.tag.track_num = (trackPosition, None)
			mp3File.tag.original_release_date = albumYear
			
			# Set cover
			with open("./cover.jpg", "rb") as cover_art:
    				mp3File.tag.images.set(3, cover_art.read(), "image/jpeg")

			# Save
			mp3File.tag.save(version=(2, 3, 0))
			
			print("Downloaded")

	print("Download Complete")
	

if __name__ == "__main__":
	album_link = input("Paste the Bandcam link ")
	print(album_link)
	downloadAlbum(album_link)