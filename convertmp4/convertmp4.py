from moviepy.editor import VideoFileClip

# Load the .mp4 file
video = VideoFileClip("C:\Users\mark\Downloads\Madonna - Vogue (Official Video).mp4")

# Extract the audio and write to .mp3
video.audio.write_audiofile("output_audio.mp3")

# Close the resources
video.close()
