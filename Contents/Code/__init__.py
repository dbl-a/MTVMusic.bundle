"""
        -API VIDEO PLAYER IS NOT SEEMING RELIABLE...  MIGHT NEED TO CHANGE TO "OVERDRIVE"
         CHECK IF PLAYLISTS HAVE AN INTERNATIONAL PLAYER
        
"""

# PMS plugin framework
import re, string, datetime
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

####################################################################################################

VIDEO_PREFIX = "/video/mtvmusic"

NAMESPACES = {'atom':'http://www.w3.org/2005/Atom','media':'http://search.yahoo.com/mrss/', 'mtvn':'http://developer.mtvnservices.com'}


MTV_ROOT            = "http://www.mtvmusic.com"
MTV_TOP_100         = "http://community.mtvmusic.com/top100/?SortOrder=numberOfViews:today&Category=&StartIndex=1&MaxResults=100"
API_ARTIST_BROWSE   = "http://api.mtvnservices.com/1/artist/browse/"
MTV_JUST_ADDED      = "http://www.mtvmusic.com/featured/just%20added/3598"
MTV_VINTAGE         = "http://www.mtvmusic.com/featured/vintage%20videos/3594"
MTV_MARQUEE         = "http://www.mtvmusic.com/featured/marquee%20videos/3599"
MTV_AMTV            = "http://www.mtvmusic.com/featured/amtv/3600"
LIVE_HD             = "http://www.mtvmusic.com/sitewide/dataservices/playlistXML/?playlistID=17747&showComments=off"
UNPLUGGED           = "http://www.mtvmusic.com/unplugged/"
PLAYER_ROOT         = "http://www.mtv.com/overdrive/?vid="
US_PLAYER_ROOT      = "http://media.mtvnservices.com/mgid:uma:video:api.mtvnservices.com:"
MTV_MUSIC_PLAYER    = "http://media.mtvnservices.com/mgid:uma:video:mtvmusic.com:"
IMAGE_ROOT          = "http://mtvmusic.mtvnimages.com/uri/mgid:uma:video:mtvmusic.com:"
SEARCH_ROOT         = "http://api.mtvnservices.com/1/artist/search/?term="


NAME = L('Title')
COUNTRY = Locale.Geolocation()

# make sure to replace artwork with what you want
# these filenames reference the example files in
# the Contents/Resources/ folder in the bundle
ART           = 'art-default.png'
ICON          = 'icon-default.png'

####################################################################################################

def Start():
  Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, "MTV Music", "icon-default.png", "art-default.jpg")
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  MediaContainer.art = R('art-default.jpg')
  MediaContainer.title1 = 'MTV Music'
  DirectoryItem.thumb=R("icon-default.png")
  
####################################################################################################
def MainMenu():
    dir = MediaContainer(mediaType='video') 
    dir.Append(Function(DirectoryItem(TopPage, "Top 100"), pageUrl = MTV_TOP_100))
    dir.Append(Function(DirectoryItem(FeaturedMenu, "Featured ")))
    dir.Append(Function(DirectoryItem(MTVBrowse, "Browse Artists")))
    #dir.Append(Function(DirectoryItem(Unplugged, "Unplugged"), pageUrl = UNPLUGGED))
    dir.Append(Function(DirectoryItem(APIBrowse, "Browse API")))
    #dir.Append(Function(DirectoryItem(Yearbook, "Yearbook"))) #YEARBOOK IS UNDER DEVELOPEMENT
    dir.Append(Function(InputDirectoryItem(APISearch, "API Search...", "Artist to search for", thumb=R(ICON), art=R(ART))))
    return dir
    
####################################################################################################
def FeaturedMenu(sender):
    dir = MediaContainer(title2=sender.itemTitle)
    dir.Append(Function(DirectoryItem(FeaturedPage, "Just Added"), pageUrl = MTV_JUST_ADDED))
    dir.Append(Function(DirectoryItem(FeaturedPage, "Vintage Videos"), pageUrl = MTV_VINTAGE))
    dir.Append(Function(DirectoryItem(FeaturedPage, "Marquee Videos"), pageUrl = MTV_MARQUEE))
    dir.Append(Function(DirectoryItem(FeaturedPage, "AMtv"), pageUrl = MTV_AMTV))
    dir.Append(Function(DirectoryItem(LiveHD, "Live HD"), pageUrl = LIVE_HD))
    return dir
    
####################################################################################################
def TopPage(sender, pageUrl):
    dir = MediaContainer(title2=sender.itemTitle)
    content = XML.ElementFromURL(pageUrl, True).xpath('//li[@class="list1"]')
    c = 1
    for item in content:
        link = item.xpath('.//a[@class="F_blue videoTitle"]')[0].get('href')
        title = ''.join(item.xpath('.//a[@class="F_blue videoTitle"]/text()')) #CONCATS LIST OF STRINGS
        title = "#" + str(c) + ": " + title
        thumb = item.xpath('.//a//img')[0].get('src')
        dir.Append(Function(WebVideoItem(TopId, title, thumb=thumb), pageUrl=link))
        c += 1
    return dir
 
####################################################################################################
def TopId(sender, pageUrl):
    #GET VIDEO ID FOR TOP 100 VIDEO
    link = XML.ElementFromURL(pageUrl, True).xpath("//link[4]")
    vid = link[0].get('href')
    #ISOLATE VID
    vid = vid.split(":")[5]
    if COUNTRY == 'US':
        vid = US_PLAYER_ROOT + vid.split("?")[0]
    else:
        vid = PLAYER_ROOT + vid.split("?")[0]
    return Redirect(WebVideoItem(vid))
          
####################################################################################################
def FeaturedPage(sender, pageUrl):
    dir = MediaContainer(title2=sender.itemTitle)
    content = XML.ElementFromURL(pageUrl, True).xpath("id('contentMiddle')/div/ul/li/div[2]/div")
    c = 0
    for item in content:
        link = MTV_ROOT + item.xpath("./p/a")[0].get('href')
        #CLEAN LINK
        if COUNTRY == 'US':
            link = US_PLAYER_ROOT + link.split("/")[6]
        else:
            link = PLAYER_ROOT + link.split("/")[6]
        thumb = item.xpath("//div/a/div[2]/img")[c].get('src')
        title = item.xpath("./p/a")[1].text + " - " + '"' + item.xpath("./p/a")[0].text + '"'
        c += 1
        dir.Append(WebVideoItem(link, title=title, thumb=thumb))
    return dir

####################################################################################################
def APISearch(sender, query):
    dir = MediaContainer(title2=sender.itemTitle)
    query = query.replace(' ', '+')  #NEED FULL URL-ESCAPING
    for item in XML.ElementFromURL(SEARCH_ROOT + query, True).xpath('//author'):
        url = item.xpath('./uri')[0].text + "videos"
        title = item.xpath('./name')[0].text
        dir.Append(Function(DirectoryItem(Artist, title), pageUrl = url))
    return dir

####################################################################################################
"""YEARBOOK IS UNDER DEVELOPEMENT BY MTV
def Yearbook(sender):
    dir = MediaContainer(title2=sender.itemTitle)
    for year in XML.ElementFromURL(MTV_VIDEO_YEARBOOK, True).xpath("id('sidebar')/ul/li/a"):
        link = MTV_ROOT + year.get('href')
        title = year.text.replace(' Videos of ','')
        dir.Append(Function(DirectoryItem(YearPage, title), pageUrl = link))
    return dir
   
####################################################################################################
def YearPage(sender, pageUrl):
    dir = MediaContainer(title2=sender.itemTitle)
    for video in XML.ElementFromURL(pageUrl, True).xpath("//div[@class='thumb']"):
        url = MTV_ROOT + video.xpath('a')[0].get('href')
        img = video.xpath('a/img')[1]
        title = img.get('alt').strip('"').replace('- "','- ').replace(' "',' - ')
        thumb = MTV_ROOT + img.get('src')
        link = re.sub('#.*','', url)
        dir.Append(WebVideoItem(link, title=title, thumb=thumb))
    return dir
"""
####################################################################################################
def MTVBrowse(sender):
    dir = MediaContainer(title2=sender.itemTitle)
    for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ-':
        dir.Append(Function(DirectoryItem(MTVArtists, ch), ch = ch))
    return dir
    
####################################################################################################
def MTVArtists(sender, ch):
    dir = MediaContainer(title2=sender.itemTitle)
    url = MTV_ROOT + "/browse/" + string.lower(ch)
    content = XML.ElementFromURL(url, True).xpath("//li[@class='list1']")
    for artist in content:
        url = MTV_ROOT + artist.xpath(".//div/div/p/a")[0].get('href')
        title = artist.xpath(".//div/div/p/a")[0].text
        dir.Append(Function(DirectoryItem(MTVArtist, title), pageUrl = url))
    return dir
    
####################################################################################################
def SimilarArtists(sender, pageUrl):
    dir = MediaContainer(title2=sender.itemTitle)
    content = XML.ElementFromURL(pageUrl, True).xpath("//ul[@class='leftColumn'][2]/li//a")
    for artist in content:
        link = MTV_ROOT + artist.get('href')
        title = artist.text
        dir.Append(Function(DirectoryItem(MTVArtist, title), pageUrl = link))
    return dir
####################################################################################################
def MTVArtist(sender, pageUrl):
    content = XML.ElementFromURL(pageUrl, True)
    #APIcontent = 
    playall_content = HTTP.Request(pageUrl)
    ArtistImage = content.xpath("//div[@class='artistImage']/img")[0].get('src')
    #for listing in APIcontent
    try:
        summary = content.xpath("//ul[@class='leftColumn']/p")[0].text
        dir = MediaContainer(art=ArtistImage, viewGroup="Details", title2=sender.itemTitle)
    except:
        summary = ""
        dir = MediaContainer(art=ArtistImage, title2=sender.itemTitle)
    thumb = ArtistImage
    for item in content.xpath("//div[@id='videoGroup1']"):
        dir.Append(Function(DirectoryItem(MTVArtistVideo, "Music Videos", summary=summary, thumb=thumb), pageUrl=pageUrl, path="//div[@id='videoGroup1']"))
    for item in content.xpath("//div[@id='videoGroup2']"):
        dir.Append(Function(DirectoryItem(MTVArtistVideo, "Live Performances", summary=summary, thumb=thumb), pageUrl=pageUrl, path="//div[@id='videoGroup2']"))
    for item in content.xpath("//div[@id='videoGroup3']"):
        dir.Append(Function(DirectoryItem(MTVArtistVideo, "Interviews", summary=summary, thumb=thumb), pageUrl=pageUrl, path="//div[@id='videoGroup3']"))
    for item in content.xpath("//div[@id='videoGroup4']"):
        dir.Append(Function(DirectoryItem(MTVArtistVideo, "Other", summary=summary, thumb=thumb), pageUrl=pageUrl, path="//div[@id='videoGroup4']"))
    for item in content.xpath("//div[@id='videoGroup5']"):
        dir.Append(Function(DirectoryItem(MTVArtistVideo, "Featured On", summary=summary, thumb=thumb), pageUrl=pageUrl, path="//div[@id='videoGroup5']"))
    for item in content.xpath("//h4[@class='grey titleSmall'][2]"):
        dir.Append(Function(DirectoryItem(SimilarArtists, "Similar Artists", summary=summary, thumb=thumb), pageUrl=pageUrl))
    return dir
####################################################################################################
def MTVArtistVideo(sender, pageUrl, path):
    dir = MediaContainer(title2=sender.itemTitle)
    content = XML.ElementFromURL(pageUrl, True).xpath(path)
    playlist = []
    for item in content[0].xpath("./ul/li[@class='list1']"):
        link = item.xpath(".//a[@class='blue videoTitle']")[0].get('href')
        link = link.split('/')[4]
        playlist.append(link + ",")
        player = ''.join(playlist)
        link = US_PLAYER_ROOT + link
        title = item.xpath(".//a[@class='blue videoTitle']")[0].text
        thumb = item.xpath(".//div[@class='videoLinkThumb']/img")[0].get('src')
        dir.Append(WebVideoItem(link, title=title, thumb=thumb))
    playlist = MTV_ROOT + "/playlists/playAll/?i=%s&t=all" % (player)
    Log(playlist)
    dir.Append(WebVideoItem(playlist, title="Play All"))
    return dir

####################################################################################################
def LiveHD(sender, pageUrl):
    dir = MediaContainer(title2=sender.itemTitle)
    content = HTTP.Request(pageUrl)
    m = re.compile('"title":".+"|"artist":".+"|"videoID":".+"|"videoThumb":".+"').findall(content)
    c = 0
    for content in m:
        item = content.split("\n")
        item = item[0].split('"')[3]
        if c == 0:
            item = item.replace("&apos;", "'")
            item = item.replace("&quot;", '"')
            title = item
            Log(title)
        if c == 1:
            title = item + " - " + title
            Log(title)
        if c == 2:
            link = US_PLAYER_ROOT + item
            Log(link)
        if c == 3:
            thumb = item
            Log(thumb)
            dir.Append(WebVideoItem(link, title=title, thumb=thumb))
            c = -1
        c += 1
    return dir

####################################################################################################
def Unplugged(sender, pageUrl, path):
    dir = MediaContainer(title2=sender.itemTitle)
    content = XML.ElementFromURL(pageUrl, True).xpath(path)
    for item in content[0].xpath("./ul/li[@class='list1']"):
        link = item.xpath(".//a[@class='blue videoTitle']")[0].get('href')
        link = link.split('/')[4]
        link = US_PLAYER_ROOT + link
        title = item.xpath(".//a[@class='blue videoTitle']")[0].text
        thumb = item.xpath(".//div[@class='videoLinkThumb']/img")[0].get('src')
        dir.Append(WebVideoItem(link, title=title, thumb=thumb))
    return dir

####################################################################################################
def APIBrowse(sender):
    dir = MediaContainer(title2=sender.itemTitle)
    for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ-':
        dir.Append(Function(DirectoryItem(Artists, ch), ch = ch))
    return dir

####################################################################################################
def Artists(sender, ch):
    dir = MediaContainer(title2=sender.itemTitle)
    url = API_ARTIST_BROWSE + ch
    content = XML.ElementFromURL(url, cacheTime=None)
    apilist = []
    mtvlist = []
    sorted_list = []
    for artist in content.xpath("//atom:entry", namespaces=NAMESPACES):
        url = artist.xpath("./atom:id", namespaces=NAMESPACES)[0].text + "videos"
        title = artist.xpath("./atom:title", namespaces=NAMESPACES)[0].text
        try:
            thumb = artist.xpath("./media:thumbnail", namespaces=NAMESPACES)[0].get('url')
        except:
            thumb = R("icon-default.png")
        apilist.append((title, thumb, url))
    #Log(apilist)
    url = MTV_ROOT + "/browse/" + string.lower(ch)
    content = XML.ElementFromURL(url, True).xpath("//li[@class='list1']")
    for artist in content:
        url = MTV_ROOT + artist.xpath(".//div/div/p/a")[0].get('href')
        title = artist.xpath(".//div/div/p/a")[0].text
        thumb = R("icon-default.png")
        mtvlist.append((title, thumb, url))
    #Log(mtvlist)
    while (apilist and mtvlist):
        Log(apilist[0])
        Log(mtvlist[0])
        if (apilist[0] <= mtvlist[0]): # Compare both heads
            item = apilist.pop(0) # Pop from the head
            sorted_list.append(item)
        else:
            item = mtvlist.pop(0)
            sorted_list.append(item)
    # Add the remaining of the lists
    sorted_list.extend(apilist if apilist else mtvlist)
    #Log(sorted_list)
    #sorted_list = list(set(sorted_list))
    for item in sorted_list:
        dir.Append(Function(DirectoryItem(Artist, title=item[0], thumb=item[1]), pageUrl = item[2]))
    return dir

####################################################################################################
def Artist(sender, pageUrl):
    dir = MediaContainer(title2=sender.itemTitle)
    content = XML.ElementFromURL(pageUrl).xpath("//atom:entry", namespaces=NAMESPACES)
    for item in content:
        restrict = item.xpath("./media:restriction", namespaces=NAMESPACES)[0].text
        Log(restrict)
        if COUNTRY in restrict or "all" in restrict:
            title = item.xpath("./media:description", namespaces=NAMESPACES)[0].text
            title = title.split('|')[0] + '-' + title.split('|')[1]
            Log(title)
            if COUNTRY == 'US':
                link = item.xpath("./media:content", namespaces=NAMESPACES)[0].get('url')
            else:
                link = item.xpath("./media:player", namespaces=NAMESPACES)[0].get('url')
            try:
                thumb = item.xpath("./media:thumbnail[last()]", namespaces=NAMESPACES)[0].get('url')
            except:
                thumb = ''
            Log(thumb)
            dir.Append(WebVideoItem(link, title=title, thumb=thumb))
    return dir
