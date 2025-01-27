# WwiseTemplateBuilder
![WwiseTemplateBuilder](/screenshots/WwiseTemplateBuilder.gif?raw=true "WwiseTemplateBuilder")
**WwiseTemplateBuilder** is a Python-based tool for importing audio into a pre-existing Wwise templates for easy and consistent setup of actor-mixer structures and events. The tool allows users to streamline the process of setting up complex Wwise project structures, making it easier to manage consistent audio  across large-scale Wwise projects. 

Do you find yourself building similar structures over and over again in Wwise? Do you work with large amount of content that is set up in a similar way (skins, foley, materials)? Do you work with an awesome team of audio folks who need to focus more time creating great sound design and not waste time setting up large or complex Wwise structures?

Instead you can point this tool at a template Wwise structure, a destination location in Wwise, and your folder of files. WwiseTemplateBuilder will recreate the actor-mixer/event structure in Wwise, then intelligently scan the file names and place them accordingly in the mixer structure. The tool does rely on the file naming to be the same as the intended template for placement of the audio in the actor-mixer structure.

Why not just use the template feature built into Wwise when importing audio?
- Doesn't require saving files in particular folders, or mapping folders to Wwise objects
- Uses file name matching to find proper location for audio in template actor-mixer structure
- Not just for the actor-mixer setup, Event can be templated to complete a full setup 

## Features

- **Actor-Mixer Templates**: Create new actor-mixer structures based on re-usable template
- **Event Templates**: Event templates can reference actor-mixer templates to complete a full setup
- **String Replacement**: Find and replace strings in templates with user-specified values
- **Create Template in Wwise**: Create as many templates as needed directly in Wwise
- **Cross-Platform Compatibility**: Works on Windows and MacOS environments.

## Installation

### Prerequisites

- **Python 3.8+**
- **Wwise SDK**: Ensure the Wwise Authoring API (WAAPI) is enabled in your Wwise project.
- **Dependencies**: 
	- pss-waapi - https://pypi.org/project/pss-pywaapi/

### Steps

1. Clone the repository:
    
    `git clone https://github.com/LathamAudio/WwiseTemplateBuilder.git`
    
2. Navigate to the project directory:
    
    `cd WwiseTemplateBuilder`
    
3. Install the pss-waapi dependencies:
    
	`pip install pss-pywaapi
    

## Configuration

### Setting up Wwise and WAAPI

Ensure WAAPI is enabled in Wwise:

1. Open Wwise.
2. Go to **Project Settings > Advanced > WAAPI**.
3. Enable **WAAPI** and confirm it's set to port 8081 (can be changed in script).

## Usage

0. **Run the Script**:
    
    `python WwiseTemplateBuilder.py`
    
1. **Choose Source Template**: 
    - In Wwise select the actor-mixer structure that will act as the template
    - In the WwiseTemplateBuilder tool press the 'Select Source' button to set the path to the source template 
    
2. **Choose Destination Location**: 
    - In Wwise select the actor-mixer object that will act as the destination for the template (typically a folder or work unit)
    - In the WwiseTemplateBuilder tool press the 'Select Destination' button to set the path to the detination location
    
3. Select WAV assets
	- Press the 'Select Folder' button in the WwiseTemplateBuilder tool and select the folder of audio assets to import in to the template actor-mixer structure
	
4.  Set the `TEMPLATE` string
	- In the 'Find & Replace `TEMPLATE` string' field type the string that will replace `TEMPLATE` in the template name
    - The application will automatically replace instances of `TEMPLATE` in the template names and paths with specified names, adapting them to your project structure.
    
5. Preview template
	- Pressing the 'Preview Template' button populates the preview pane below with a preview of how the template will look in Wwise
	- This will show a preview of the actor-mixer structure will the new names and placement of audio assets in the structure
	
6. Generate Template
	- Pressing the 'Generate Template' button will create the new actor-mixer structure in the destination location that matches the original source structure. The string `TEMPLATE` will be replaces with the provided replacement string. The audio assets are imported into Wwise and placed into the matching actor-mixer structure locations.

7. **Event Template**:
	- Switch to the 'Events' tab to use event templates for that reference the actor-mixer templates
    - Select the location of the source event template in Wwise and press 'Select Source'
    - Select the location of the destination event template in Wwise and press 'Select Destination'
    - Select the destination location of target actor-mixer in Wwise and press 'Select Actor-Mixer', this will set the destination actor-mixer as the target of the event actions instead of the original template to replace the defaults set
    - Set the same `TEMPLATE` string to replace in the events and actions
    - Pressing 'Preview Template' with show a preview of the event template before generation
    - Pressing 'Generate Template' will create the resulting event structure in Wwise, replacing any instance of the `TEMPLATE` string found, and re-targeting event actions to the destination template actor-mixer structure

## Contributing

Contributions are welcome! If you’d like to help improve WwiseTemplateBuilder, please follow these steps:

1. Fork the repository.
2. Create a new branch with a descriptive name.
3. Make your changes and submit a pull request.


## License

This project is licensed under the MIT License

## Acknowledgements

- Special thanks to 
	- **Audiokinetic** for Wwise and WAAPI.
	- Simon Gumbleton for [pss_pywaapi](https://github.com/some_repo), a Python-WAAPI integration.


## Contact
	email: chris@lathamaudio.com
	linkedin: http://www.linkedin.com/in/lathamaudio
	twitter: @latham_audio
