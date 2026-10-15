<h2 align="center">Brand Engine - AI-Powered Brand Name Generator</h2>
<p align="center">
	<img src="logo.png" width="80" alt="BrandEngine Logo">
</p>
A sophisticated brand name generator with domain availability checking, scoring, and export capabilities.

## Features
-  **Modern GUI** - Built with CustomTkinter for a polished look
-  **Smart Generation** - Multiple naming styles (compound, abstract, animal, nature)
-  **Domain Checking** - Real-time WHOIS/RDAP domain availability
-  **Intelligent Scoring** - Scores names based on phonetics, memorability, and brand appeal
- **Similarity Filtering** - Removes duplicate and similar names
-  **Database Storage** - SQLite database for persistence
-  **Export Options** - CSV, JSON, and Excel export
-  **Multi-threaded** - Fast generation without UI freezing
- **Live Filtering** - Search and filter results in real-time

## Installation
> [!IMPORTANT]
> If you prefer not to customize the repository files, you can simply download the standalone bundled executable file for BrandEngine [here](https://github.com/yavotu/BrandEngine/releases).


1. Clone the repository:
```bash
git clone https://github.com/Lewismwaz/BrandEngine.git
cd BrandEngine
```

2. Create icon for BrandEngine executable file.
- Open PowerShell from `\BrandEngine`:
- If Pillow isn't installed, run:
```powershell
python -m pip install Pillow
```
- Then run:
```powershell
python -c "from PIL import Image; img = Image.open('assets/logo.png').convert('RGBA'); img.save('assets/icon.ico', sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])"
```

Verify it worked:
```powershell
Get-Item assets\icon.ico | Select-Object Name, Length
```
![Create exe icon](icon.png)

3. Ensure you have latest `pip` and Python 3.10+ installed, and both are added to PATH, then double click to open the `build.bat` or well known as `build` Windows Batch File and let it install all the required Python dependencies and also generate the executable file.
![Build Complete](Complete.png)

![Build Complete](0.png)

5. Locate the exe file `dist\BrandEngine.exe` and open it.

## User Interface
![Build Complete](1.png)

![Build Complete](1a.png)


## License
This project is licensed under the GNU License. View License [here](https://github.com/Yavotu/BrandEngine/blob/main/LICENSE).  
More details about the MIT License can be found [here.](https://choosealicense.com/licenses/mit/)

## Contact
For any inquiries, please contact:
- Email - <yavotu@gmail.com> or <eappointmaster@gmail.com>
- GitHub - [@Yavotu](https://github.com/Yavotu) or [@Lewismwaz](https://github.com/Lewismwaz)

[Brand Engine](https://github.com/Yavotu/BrandEngine) **©** 2026, All Rights Reserved
