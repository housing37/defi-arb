__fname = 'yt_trans'
__filename = __fname + '.py'
cStrDivider = '#================================================================#'
print('', cStrDivider, f'GO _ {__filename} -> starting IMPORTs & declaring globals', cStrDivider, sep='\n')

# ------------------------------------------------------------ #
# solution requirements
# ------------------------------------------------------------ #
'''
sub: r/forhire
user: Immediate-Bar-1300

[Hiring]Python Developer Needed for YouTube Transcript Automation.
I need a script to automatically download transcripts from 
4,000 YouTube videos and save them as individual documents (.txt or .docx). 

Tasks include:
    1) Use YouTube API to fetch existing transcripts.
    2) For videos without transcripts: Download audio and transcribe using Whisper/AWS Transcribe.
    3) Save outputs to organized, named files.

Requirements:
    - Proficiency in Python, YouTube API, and speech-to-text tools (e.g., Whisper).
    - Experience with bulk data processing and file automation.

Budget: $300–$600 (negotiable based on approach).

Additional:
    quick question, would it be possible to change the document name 
    according to the video title/motion type so it'd be easier for me to find 
    https://docs.google.com/spreadsheets/d/1GRn0N5dAAKEfI92fneBJN4Wgc1kIWprzO0PGKGyZBG4/htmlview
'''

'''
    requirements:
        $ python3.10 -m pip install youtube_transcript_api
        $ python3.10 -m pip install pytube
        $ python3.10 -m pip install yt-dlp
        $ python3.10 -m pip install pandas
        $ python3.10 -m pip install pprint
'''

# ------------------------------------------------------------ #
# library support / imports
# ------------------------------------------------------------ #
# from pprint import pprint
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import pandas as pd

# support options for getting video titles
# from pytube import YouTube
# import requests
# from bs4 import BeautifulSoup
from yt_dlp import YoutubeDL

# ------------------------------------------------------------ #
# global counters
# ------------------------------------------------------------ #
CNT_SUCCESS = 0
CNT_NO_TRANS = 0
CNT_ERROR_MISC = 0
OUTPUT_DIR = './yt_trans_files/'
PRINT_TRANS_TO_COSOLE = False

# ------------------------------------------------------------ #
# support functions
# ------------------------------------------------------------ #
# get title via "yt_dlp" library support
def get_title_yt_dlp(video_url):
    with YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(video_url, download=False)
        return info.get('title', 'Title not found')

# get title via bs4/BeautifulSoup scraping support
def get_title_scrape(video_url):
    try:
        response = requests.get(video_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find("meta", {"name": "title"})["content"]
        return title
    except Exception as e:
        return f"Scraping error: {str(e)}"

def get_youtube_transcript(video_input):
    global CNT_SUCCESS, CNT_NO_TRANS, CNT_ERROR_MISC
    # Extract video ID from URL if a full URL is provided
    if "youtube.com" in video_input or "youtu.be" in video_input:
        if "v=" in video_input:
            video_id = video_input.split("v=")[1].split("&")[0]
        elif "youtu.be" in video_input:
            video_id = video_input.split("/")[-1].split("?")[0]
        else:
            video_id = video_input
    else:
        video_id = video_input  # Assume it's already a video ID

    # Get video title using pytube
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"

        # option 1: get title via "yt_dlp" library support (testing shows better results than BeautifulSoup)
        #   requires: from yt_dlp import YoutubeDL
        video_title = get_title_yt_dlp(url)

        # option 2: get title via bs4/BeautifulSoup scraping support (testing show some failures)
        #   requires: from bs4 import BeautifulSoup & import requests
        # video_title = get_title_scrape(url)

        # option 3: get title via "pytube" library support (testing shows all failures)
        #   requires: # from pytube import YouTube
        # yt = YouTube(url)
        # video_title = yt.title

    except Exception as e:
        video_title = f"Could not fetch title: {str(e)}"

    # Get the transcript
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_transcript = " ".join([entry['text'] for entry in transcript])
        CNT_SUCCESS += 1
        return video_title, full_transcript
    except (TranscriptsDisabled, NoTranscriptFound):
        CNT_NO_TRANS += 1
        return video_title, "No transcript available"
    except Exception as e:
        CNT_ERROR_MISC += 1
        return video_title, f"Error: {str(e)}"

def write_to_file(link, motion, title, transcript, filename):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Video Link: {link}\n\n")
            f.write(f"Video Motion: {motion}\n\n")
            f.write(f"Video Title: {title}\n\n")
            f.write(f"Transcript:\n {transcript}")
        print(f"\nOutput written to {filename}")
    except Exception as e:
        print(f"Error writing to file: {str(e)}")

# ------------------------------------------------------------ #
# ------------------------------------------------------------ #
def extract_columns_from_sheets(sheet_url, column1, column2):
    try:
        # Convert the URL to CSV export format
        sheet_id = sheet_url.split("/d/")[1].split("/")[0]
        export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        
        # Read the sheet into a DataFrame
        df = pd.read_csv(export_url)
        
        # Convert column letters to indices (e.g., 'A' -> 0, 'B' -> 1)
        col1_idx = ord(column1.upper()) - ord('A')
        col2_idx = ord(column2.upper()) - ord('A')
        
        # Extract columns as lists, replacing NaN with None
        col1_data = df.iloc[:, col1_idx].replace(pd.NA, None).tolist()
        col2_data = df.iloc[:, col2_idx].replace(pd.NA, None).tolist()

        # validate the lengths of both columns are the same
        assert len(col1_data) == len(col2_data), "Columns must have the same length"
        
        # Create dictionary, skipping empty keys (None in col1_data)
        d_result = {}
        for key, value in zip(col1_data, col2_data):
            if key is not None:  # Only add if key is not empty
                d_result[key] = value
        
        # debug print consolidated columns dict
        # print(d_result)
        # pprint(d_result)

        # loop through columns dict, console print & write to file
        for i,link in enumerate(d_result):
            # debug print to console
            motion = d_result[link]
            divider = "#====================================================#"
            print("\n", divider, sep="")
            print(i,link)
            print(divider, sep="")
            print(f"Processing Link: {link}")
            print(f"Processing Motion: {motion}")

            # get transcript for each column link + console print
            title, trans = get_youtube_transcript(link)
            print(f"Video Title: {title}")
            print(f"Link: {link}")
            if PRINT_TRANS_TO_COSOLE: print(f"Transcript:\n {trans}")
            else: print("Transcript: [print to console disabled]")

            # write transcript + meta to file
            filename = title
            write_to_file(link, motion, title, trans, OUTPUT_DIR + f"{i}" + "_" + filename + ".txt")
            print(divider, "\n", divider, sep="")

        return col1_data, col2_data
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return None, None

# ------------------------------------------------------------ #
# main execution
# ------------------------------------------------------------ #
# Get input from user
sheet_url = input("Enter Google Sheets URL: ")
col1 = input("Enter first column letter (e.g., 'A|a'): ")
col2 = input("Enter second column letter (e.g., 'B|b'): ")

# Run the extraction (prints console output + write to file)
extract_columns_from_sheets(sheet_url, col1, col2)

# print exit/completion status
print('\n\n STATUS counts...')
print("CNT_SUCCESS: ", CNT_SUCCESS)
print("CNT_ERROR_MISC: ", CNT_ERROR_MISC)
print("CNT_NO_TRANS: ", CNT_NO_TRANS)
print('\n\n - DONE - \n\n')    
