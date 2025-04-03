Step 1: Add an Input Interface
Create a UI, add a text input field where users can paste a direct link to a music file (must be a .mp3 URL).

Add a button labeled something like "Influence track".

Step 2: Capture the User Input
When the button is clicked, capture the URL the user pasted.

Send this URL to your backend server via a request (e.g., a POST request with the URL in the body).

Step 3: Send the URL to Sonoteller
On the backend, take the received URL and format it for the Sonoteller API.

Send the URL to Sonoteller using the appropriate API endpoint (in this case, /lyrics_ddex).

Make sure the URL is properly encoded and the request includes your API key and headers.

Step 4: Receive and Process the Analysis
Wait for Sonoteller to respond with the music analysis data (this might include things like structure, mood, lyrics sections, tempo, etc.).

Step 5: Save the sonoteller results to a new table called "influence music"

Step 6: Handle Errors and Feedback
If the link is invalid or the analysis fails, notify the user with a friendly error message.

Optionally, add a progress indicator so users know the analysis and generation are in progress.

Python sonoteller api:
import http.client

conn = http.client.HTTPSConnection("sonoteller-ai1.p.rapidapi.com")

payload = "file=https%3A%2F%2Fstorage.googleapis.com%2Fmusikame-files%2Fthefatrat-mayday-feat-laura-brehm-lyriclyrics-videocopyright-free-music.mp3"

headers = {
    'x-rapidapi-key': "58fafc6204msh41ac38769729b59p17fbc3jsneeebeb330eb2",
    'x-rapidapi-host': "sonoteller-ai1.p.rapidapi.com",
    'Content-Type': "application/x-www-form-urlencoded"
}

conn.request("POST", "/lyrics_ddex", payload, headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))