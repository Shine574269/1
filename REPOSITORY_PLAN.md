# Separate repositories

Proposed:
- mengxuan-portfolio (HTML site, images, compressed/small videos)
- memtl-edge-computing (thesis + code if later supplied)
- ground-air-dungeon-shooter (Unity project; Windows build via release)
- aiva-app-design (original PPTX, prototype design assets and explanatory documents)
- ted-talks-retrieval (Python source + dataset; online search embedded in site)
- dailysense-android (cleaned Android Studio source; supply your own API credential)
- cpt205-opengl (2D birthday card + 3D castle subfolders)

Do not commit API credentials, student-number cover sheets, 184MB videos or large binaries directly to git. Prefer GitHub Releases / external video hosting for large downloads and use HTTPS for the deployed website.

If the full DailySense video is not available on deployment, upload it to an external video host and replace the HTML video src / download link accordingly. For local preview: python3 -m http.server 8000 in the site folder.
