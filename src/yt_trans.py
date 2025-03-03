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
'''

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
# from pytube import YouTube
from yt_dlp import YoutubeDL
import requests
from bs4 import BeautifulSoup

CNT_SUCCESS = 0
CNT_NO_TRANS = 0
CNT_ERROR_MISC = 0
OUTPUT_DIR = './yt_trans_files/'


def get_title_yt_dlp(video_url):
    with YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(video_url, download=False)
        return info.get('title', 'Title not found')

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

def get_title_scrape(video_url):
    try:
        response = requests.get(video_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find("meta", {"name": "title"})["content"]
        return title
    except Exception as e:
        return f"Scraping error: {str(e)}"

# url = "https://youtube.com/watch?v=P28WviPguF8"
# print(get_title_scrape(url))

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
        # yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
        # video_title = yt.title

        url = f"https://www.youtube.com/watch?v={video_id}"
        # print(get_title_yt_dlp(url))
        video_title = get_title_yt_dlp(url)
        # video_title = get_title_scrape(url)
        
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

# # Get input from user
# video_input = input("Enter YouTube video URL or ID: ")

# # Get title and transcript
# title, result = get_youtube_transcript(video_input)

# # Print the title and transcript
# print("\nVideo Title:")
# print(title)
# print("\nTranscript:")
# print(result)

# ------------------------------------------------------------ #
# ------------------------------------------------------------ #
'''
    requirements:
        $ python3.10 -m pip install pandas
        $ python3.10 -m pip install pprint
'''

import pandas as pd
from pprint import pprint

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

        assert len(col1_data) == len(col2_data), "Columns must have the same length"
        # d_data = dict(zip(col1_data, col2_data))
        
        # Create dictionary, skipping empty keys (None in col1_data)
        # Create dictionary, skipping empty keys (None in col1_data)
        d_result = {}
        for key, value in zip(col1_data, col2_data):
            if key is not None:  # Only add if key is not empty
                d_result[key] = value
        
        # print(result_dict)
        # pprint(result_dict)
        for i,link in enumerate(d_result):
            motion = d_result[link]
            divider = "#====================================================#"
            print("\n", divider, sep="")
            print(i,link)
            print(divider, sep="")
            # Example action: Print each item with some processing
            # item = d_result[k]
            print(f"Processing Link: {link}")
            print(f"Processing Motion: {motion}")
            title, trans = get_youtube_transcript(link)
            # Print the title and transcript
            print(f"Video Title: {title}")
            print(f"Link: {link}")
            print(f"Transcript:\n {trans}")
            filename = title
            write_to_file(link, motion, title, trans, OUTPUT_DIR + f"{i}" + "_" + filename + ".txt")
            print(divider, "\n", divider, sep="")

        # # Loop through col1_data and use each item
        # print(f"\nLooping through Column {column1}:")
        # for item in col1_data:
        #     # Example action: Print each item with some processing
        #     print(f"Processing item: {item}")
        #     if item is not None:
        #         title, result = get_youtube_transcript(item)
        #         # # Print the title and transcript
        #         # print("\nVideo Title:")
        #         # print(title)
        #         print("\nTranscript:")
        #         print(result)
            
        # Print the results
        # print(f"\nColumn {column1}:")
        # pprint(col1_data)
        # print(f"\nColumn {column2}:")
        # pprint(col2_data)
        
        return col1_data, col2_data
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return None, None

# Get input from user
sheet_url = input("Enter Google Sheets URL: ")
col1 = input("Enter first column letter (e.g., 'A'): ")
col2 = input("Enter second column letter (e.g., 'B'): ")

# Run the extraction
extract_columns_from_sheets(sheet_url, col1, col2)
print('\n\n STATUS counts...')
print("CNT_SUCCESS: ", CNT_SUCCESS)
print("CNT_ERROR_MISC: ", CNT_ERROR_MISC)
print("CNT_NO_TRANS: ", CNT_NO_TRANS)
print('\n\n - DONE - \n\n')    

# '''
#     requirements:
#         $ python3.10 -m pip install gspread oauth2client
#         $ python3.10 -m pip install pprint
# '''
# import gspread
# from pprint import pprint

# def extract_columns_from_sheets(sheet_url, column1, column2):
#     try:
#         print(0)
#         # Use gspread's anonymous client for public sheets
#         gc = gspread.Client(None)  # No credentials needed
        
#         print(1)
#         # Extract the spreadsheet ID from the URL
#         sheet_id = sheet_url.split("/d/")[1].split("/")[0]
        
#         print(2)
#         # Open the spreadsheet as public
#         sheet = gc.open_by_key(sheet_id).sheet1  # Assumes data is in the first sheet
        
#         print(3)
#         # Get all data from the sheet
#         data = sheet.get_all_values()
        
#         print(4)
#         # Convert column letters to indices (e.g., 'A' -> 0, 'B' -> 1)
#         col1_idx = ord(column1.upper()) - ord('A')
#         col2_idx = ord(column2.upper()) - ord('A')
        
#         print(5)
#         # Check if the indices are valid
#         if col1_idx >= len(data[0]) or col2_idx >= len(data[0]):
#             raise ValueError("Column letter exceeds sheet dimensions")
        
#         print(6)
#         # Extract the specified columns
#         col1_data = [row[col1_idx] for row in data]
#         col2_data = [row[col2_idx] for row in data]
        
#         print(7)
#         # Print the results
#         print(f"\nColumn {column1}:")
#         pprint(col1_data)
#         print(f"\nColumn {column2}:")
#         pprint(col2_data)
        
#         return col1_data, col2_data
    
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return None, None

# # Get input from user
# sheet_url = input("Enter Google Sheets URL: ")
# col1 = input("Enter first column letter (e.g., 'A'): ")
# col2 = input("Enter second column letter (e.g., 'B'): ")

# # Run the extraction
# extract_columns_from_sheets(sheet_url, col1, col2)






# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
# from pprint import pprint

# # Define the scope and credentials
# scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# # Replace with the path to your JSON key file (downloaded from Google Cloud Console)
# creds = ServiceAccountCredentials.from_json_keyfile_name("your-credentials.json", scope)
# client = gspread.authorize(creds)

# def extract_columns_from_sheets(sheet_url, column1, column2):
#     try:
#         # Extract the spreadsheet ID from the URL
#         sheet_id = sheet_url.split("/d/")[1].split("/")[0]
        
#         # Open the spreadsheet
#         sheet = client.open_by_key(sheet_id).sheet1  # Assumes data is in the first sheet
        
#         # Get all data from the sheet
#         data = sheet.get_all_values()
        
#         # Convert column letters to indices (e.g., 'A' -> 0, 'B' -> 1)
#         col1_idx = ord(column1.upper()) - ord('A')
#         col2_idx = ord(column2.upper()) - ord('A')
        
#         # Extract the specified columns
#         col1_data = [row[col1_idx] for row in data]
#         col2_data = [row[col2_idx] for row in data]
        
#         # Print the results
#         print(f"\nColumn {column1}:")
#         pprint(col1_data)
#         print(f"\nColumn {column2}:")
#         pprint(col2_data)
        
#         return col1_data, col2_data
    
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return None, None

# # Get input from user
# sheet_url = input("Enter Google Sheets URL: ")
# col1 = input("Enter first column letter (e.g., 'A'): ")
# col2 = input("Enter second column letter (e.g., 'B'): ")

# # Run the extraction
# extract_columns_from_sheets(sheet_url, col1, col2)


# ------------------------------------------------------------ #
# ------------------------------------------------------------ #
# from youtube_transcript_api import YouTubeTranscriptApi
# from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

# def get_youtube_transcript(video_input):
#     # Extract video ID from URL if a full URL is provided
#     if "youtube.com" in video_input or "youtu.be" in video_input:
#         if "v=" in video_input:
#             video_id = video_input.split("v=")[1].split("&")[0]
#         elif "youtu.be" in video_input:
#             video_id = video_input.split("/")[-1].split("?")[0]
#         else:
#             video_id = video_input
#     else:
#         video_id = video_input  # Assume it's already a video ID

#     try:
#         # Get the transcript
#         transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
#         # Combine all text segments
#         full_transcript = " ".join([entry['text'] for entry in transcript])
#         return full_transcript
        
#     except (TranscriptsDisabled, NoTranscriptFound):
#         return "No transcript available"
#     except Exception as e:
#         return f"Error: {str(e)}"

# # Get input from user
# video_input = input("Enter YouTube video URL or ID: ")

# # Get and print the transcript
# result = get_youtube_transcript(video_input)
# print("\nTranscript:")
# print(result)