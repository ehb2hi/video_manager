
import youtube_downloader
import video_spliter

if __name__ == "__main__":
    
    print(" select tool, for downloading yotube vider enter 1 for splitting video enter 2")
    
    tool = int(input())
    
    if tool == 1:
        youtube_downloader.main()
    elif tool == 2:
        video_spliter.main()
    else:
        print("the number entered is incorrect")
    
    
