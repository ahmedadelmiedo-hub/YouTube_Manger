# File 71 publisher (scaffold, not pushed)
Plan: reuse the KIDS_FACTORY engine (generator -> renderer -> uploader) with a case-file visual layer
(title cards with dates, timeline and map graphics, text scenes, Arabic captions). 
Safety: dry run by default on manual runs, unlisted uploads, one real upload per day, history saved only after upload.
Needs before going live: scripts/video_publish.py (port of engine), requirements.txt, GitHub secrets
GEMINI_API_KEY, YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN (for the File 71 channel), variable FILE71_ENABLED=true.

Dry runs only until FILE71_ENABLED=true.
