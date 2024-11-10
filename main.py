# ___IMPORTS_________________________________________________________________________________________________________
import tkinter as tk                    # TkInter GUI
from tkinter import ttk, messagebox     # TTK styling and message box
import tkinter.filedialog as fd         # file dialog
import os                               # OS paths
import re                               # Regex
import pss_pywaapi                      # PSS_PYWAAPI
from waapi import WaapiClient



# ___GLOBALS_________________________________________________________________________________________________________
import_file_list = []           # Files to be imported
source_structure = []           # Actor-Mixer structure of source template
event_source_structure = []           # Actor-Mixer structure of source template

source_location = 0             # Path to source template
source_object = 0               # Source template object
destination_location = 0        # Path to destination location
destination_object = 0          # Destination parent object
event_source_location = 0             # Path to source template
event_source_object = 0               # Source template object
event_destination_location = 0        # Path to destination location
event_destination_object = 0          # Destination parent object
event_target_location = 0
event_target_object = 0
assets_directory = 0            # Path to assets directory



# ___CLASS_________________________________________________________________________________________________________
# Custom TreeView class
class TreeviewEdit(ttk.Treeview):
    # Initialize class instance 
    def __init__(self, master, **kw):
        # Initialize super class
        super().__init__(master, **kw)



# ___FUNCTIONS_________________________________________________________________________________________________________
# On Source Template Button Click
def OnSourceButtonClick():
    # Use the global source location and object
    global source_location
    global source_object

    # Get the objects selected in Wwise
    source_objects = pss_pywaapi.getSelectedObjects()

    # If source object was selected
    if source_objects:
        # Get the first selected object
        source_object = source_objects[0]

        # Get the id of the source object and assign it to the source location
        source_location = source_object["id"]

        # Show source object path in source object entry field
        source_objectPath.set(source_object["path"])
    else:
        messagebox.showwarning("No Selection", "No objects selected in Wwise.")



# On Destination Button Click
def OnDestinationButtonClick():

    # Use the global destination location and object
    global destination_location
    global destination_object

    # Get the objects selected in Wwise
    destination_objects = pss_pywaapi.getSelectedObjects()

    # If destination object was selected
    if destination_objects:
        # Get the first selected object
        destination_object = destination_objects[0]

        # Get the id of the destination object and assign it to the destination location
        destination_location = destination_object["id"]

        # Show destination object path in destination object entry field
        destination_objectPath.set(destination_object["path"])
    else:
        messagebox.showwarning("No Selection", "No objects selected in Wwise.")



# On Asset Button Click
def OnAssetsButtonClick():
    global assets_directory

    # Open a file dialog to select a directory
    assets_directory = fd.askdirectory()

    # If an asset directory is selected set it to the asset object path
    if assets_directory:
        # Update the entry field with the selected directory path
        assets_object_path.set(assets_directory)
    else:
        print("No directory selected.")



# On Preview Template button click
def OnPreviewTemplateButtonClick():
    global source_structure

    # Clear the treeview before rebuilding it
    for item in actor_mixer_tree_view.get_children():
        actor_mixer_tree_view.delete(item)

    # Get the descendants of the selected object
    source_structure = pss_pywaapi.getDescendantObjects(
        source_object["id"],  # Start from the selected object
        returnProperties=["name", "type", "id", "path", "parent"]  # Return properties including parent ID and type
    )

    # Include the selected object in the 'sounds' list
    source_structure.insert(0, source_object)

    # Populate the treeview
    BuildTreeViewStructure(actor_mixer_tree_view, source_object, source_structure)

    if assets_directory:
        # Match .wav files with the leaf nodes in treeview
        MatchWAVFilesWithLeafNodes(actor_mixer_tree_view, assets_directory)


# On Generate Template button click
def OnGenerateTemplateButtonClick():
    # Cnce all files in this dir are added, set the import file list to be imported
    importArgs = {
        "importOperation": "replaceExisting",
        "autoAddToSourceControl": True,
        "default": {
        },
        "imports": import_file_list
    }

    # If there is a destination provided then copy the source Wwise structure to the Destation location
    if destination_objectPath.get():  
        result = pss_pywaapi.copyWwiseObject(source_location, destination_location, conflict='replace')

    # If a template name is provided then replace the TEMPLATE string in copied structure
    if template_name_object_path.get():
        ReplaceTemplateInDestinationStructure(template_name_object_path.get())

    # If the assets directory has been provided then import audio into Wwise
    if assets_directory:
        res = pss_pywaapi.importAudioFilesBatched(importArgs, 1000)
    
    print("DONE :D")



# Iterates through the treeview and assets_directory looking for matching names
def MatchWAVFilesWithLeafNodes(treeview, assets_directory):
    # Get the leaf nodes from the treeview
    leaf_nodes = GetLeafNodes(treeview)

    # Get the template name from the entry field
    template_name = template_name_object_path.get()

    # Define a pattern for "_1P_Local", "_1p_Local", "_3P_Enemy", etc.
    pattern = r'_(1P|1p|3P|3p)_(Local|Enemy|Friendly)'

    # Get path to Wwise Project Folder
    pathToWwiseDir = pss_pywaapi.getPathToWwiseProjectFolder()

    # Returns the absolute path of the Wwise Project Folder
    defaultDirectory = os.path.abspath(os.path.dirname(pathToWwiseDir))

    # Walk through the selected directory and subdirectories to find .wav files
    for root, dirs, files in os.walk(assets_directory):

        for file in files:
            if file.endswith(".wav"):
                # Combine path and audio file name to create path including file name
                audioFile = os.path.join(root, file)

                # Set path of the audio file
                audioFilePath = root

                # Set name of the audio file
                audioFileName = file

                # Set relative path and relative directory
                relativePath = os.path.relpath(audioFilePath, defaultDirectory)
                relativeDir = os.path.dirname(relativePath)

                # Get the file name without extension
                file_name_without_ext = os.path.splitext(file)[0]
                
                # Remove the trailing "_XX" (ie _01, _02, _03)
                file_name_without_ext = re.sub(r'_\d{2}$', '', file_name_without_ext)

                # Check if the file name (without extension) matches any leaf node name
                for leaf in leaf_nodes:
                    # Remove 1p/3p/Local/Enemy like "_1P_Local", "_3p_Enemy", etc.
                    leaf_name_cleaned = re.sub(pattern, '', leaf[1])

                    # Initialize modified_leaf_name
                    modified_leaf_name = ""

                    # Replace "TEMPLATE" string with the actual template name
                    if template_name_object_path.get():
                        modified_leaf_name = leaf_name_cleaned.replace("TEMPLATE", template_name)

                    # Perform the comparison after replacement
                    if modified_leaf_name == file_name_without_ext:
                        # Add the .wav file as a child of the corresponding leaf node
                        treeview.insert(leaf[0], 'end', text=file, values=("wav",))

                        # Set source and destination template path
                        template_path = source_objectPath.get()
                        destination_path = destination_objectPath.get()
                        
                        # Find the last occurrence of the double backslashes
                        last_double_backslash = template_path.rfind("\\")

                        # If double backslashes are found remove any part of the path after that
                        if last_double_backslash != -1:
                            template_path = template_path[:last_double_backslash]

                        # Get object path and type from leaf
                        object_path = leaf[2]
                        object_type = leaf[3]
                        
                        # Replate the source template path with the destination path
                        object_path = object_path.replace(template_path, destination_path)
                        
                        # If there is a template name available then replace the TEMPLATE string with the template name
                        if template_name_object_path.get():
                            object_path = object_path.replace("TEMPLATE", template_name)
                        
                        # Append the audio file to the import file list
                        AppendImportFileList(audioFile, file, object_path, object_type, relativeDir, False)



# Get all leaf nodes from the treeview
def GetLeafNodes(treeview, parent=""):
    # initialize leaf_node
    leaf_nodes = []
    
    # check if a parent node has children 
    for item in treeview.get_children(parent):
        values = treeview.item(item)["values"]

        # initialize variables to make sure they are not null if they do not exits in 'values'
        object_path = ""
        object_type = ""
        
        # Ensure there are at least two elements in the 'values' list
        if len(values) > 1:
            # Retrieve the object type and path
            object_type = values[0]
            object_path = values[1]

        # Check if the node has no children, which means it's a leaf
        if not treeview.get_children(item):
            leaf_nodes.append((item, treeview.item(item)["text"], object_path, object_type))
        else:
            # Recursively get leaf nodes for the children
            leaf_nodes.extend(GetLeafNodes(treeview, item))

    return leaf_nodes



# Appends the relevent data about WAV files to the import file list to be imported later
def AppendImportFileList(audioFile, audioFileName, objectPath, objecteType, relativeDir, streamingEnabled):
    import_file_list.append(
    {
        "audioFile": audioFile,
        "objectType": objecteType,
        "objectPath": objectPath + "\\" + "<Sound>" + audioFileName,
        "originalsSubFolder": template_name_object_path.get(),
        "@IsStreamingEnabled": streamingEnabled,
        "@IsZeroLatency": streamingEnabled,
        "@PreFetchLength": 1000
    })


    # Replate the TEMPLATE string with the provided template name
def ReplaceTemplateInDestinationStructure(template_name):
    # Get the descendants of the destination path
    destination_structure = pss_pywaapi.getDescendantObjects(
        destination_object["id"],  # Start from the selected object
        returnProperties=["name", "type", "id", "path", "parent"]  # Return properties including parent ID and type
    )

    # Include the desitination object in the 0th position of the 'sounds' list
    destination_structure.insert(0, destination_object)

    # Iterate through the descendants and replace TEMPLATE with the actual template name
    for destination in destination_structure:
        # Replace TEMPLATE in the name
        new_name = re.sub(r'TEMPLATE', template_name, destination["name"])
        
        # Only update if the name actually changess
        if new_name != destination["name"]:
            # Set the updated name for the object in Wwise
            args = {
                "object": destination["id"],  # Use the ID of the object
                "value": new_name
            }

            # Call Waapi setName with arguments
            pss_pywaapi.call("ak.wwise.core.object.setName", args) 


# ___EVENT FUNCTIONS_________________________________________________________________________________________________________
# On Source Event Template Button Click
def OnSourceEventButtonClick():
    # Use the global event source lcation and object
    global event_source_location
    global event_source_object

    # Get the objects selected in Wwise
    event_source_objects = pss_pywaapi.getSelectedObjects()

    # If an object was selected in Wwise
    if event_source_objects:
        # Get the first selected object
        event_source_object = event_source_objects[0]

        # Get the id of the source object and assign it to the source location
        event_source_location = event_source_object["id"]

        # Show selected object path in the source event entry field
        event_source_path.set(event_source_object["path"])
    else:
        messagebox.showwarning("No Selection", "No objects selected in Wwise.")


# On Destination Event Button Click
def OnDestinationEventButtonClick():

    # Use the global event destination location and object
    global event_destination_location
    global event_destination_object

    # Get the objects selected in Wwise
    event_destination_objects = pss_pywaapi.getSelectedObjects()

    # If an object was selected in Wwise
    if event_destination_objects:
        # Get the first selected object
        event_destination_object = event_destination_objects[0]

        # Get the id of the destination object and assign it to the destination location
        event_destination_location = event_destination_object["id"]

        # Show selected object path in the destination event entry field
        event_destination_path.set(event_destination_object["path"])
    else:
        messagebox.showwarning("No Selection", "No objects selected in Wwise.")


# On Target Event Button Click
def OnTargetEventButtonClick():

    # Use the global Actor-Mixer target location and object
    global event_target_location
    global event_target_object

    # Get the objects selected in Wwise
    event_target_objects = pss_pywaapi.getSelectedObjects()

    # If object is selected in Wwise
    if event_target_objects:
        # Get the first selected object
        event_target_object = event_target_objects[0]

        # Get the id of the destinatevent target object and assign it to the evetn target location
        event_target_location = event_target_object["id"]

        # Show event target object path in event target path entry field
        event_target_path.set(event_target_object["path"])
    else:
        messagebox.showwarning("No Selection", "No objects selected in Wwise.")



# On Preview event Template button click
def OnPreviewEventTemplateButtonClick():
    global event_source_structure

    # Clear the treeview before rebuilding it
    for item in events_tree_view.get_children():
        events_tree_view.delete(item)

    # Get the descendants of the selected object
    event_source_structure = pss_pywaapi.getDescendantObjects(
        event_source_object["id"],  # Start from the selected object
        returnProperties=["name", "type", "id", "path", "parent"]  # Return properties including parent ID and type
    )

    # Include the selected object in the 'sounds' list
    event_source_structure.insert(0, event_source_object)

    # Retrieve the template name to use for replacements
    template_replacement = event_template_name_entry.get()
    
    # for each event source in the event source structure
    for event_source in event_source_structure:
        # Replace TEMPLATE string in the name
        event_source["name"] = re.sub(r'TEMPLATE', template_replacement, event_source["name"])

        # Replace TEMPLATE string in the path
        event_source["path"] = re.sub(r'TEMPLATE', template_replacement, event_source["path"])

    # Populate the event treeview
    BuildTreeViewStructure(events_tree_view, event_source_object, event_source_structure)


# On Generate Template button click
def OnGenerateEventTemplateButtonClick():

    # If there is an event destination provided then copy the source Wwise structure to the destation location
    if event_destination_path.get():  
        result = pss_pywaapi.copyWwiseObject(event_source_location, event_destination_location, conflict='replace')

    # If a template name is provided then replace the TEMPLATE string in copied structure
    if  event_template_name_entry.get():
        ReplaceTemplateInDestinationEventStructure(event_template_name_entry.get())
    
    print("DONE :D")



# Replate the TEMPLATE string with the provided template name, and retarget actions
def ReplaceTemplateInDestinationEventStructure(template_name):
    # Get the descendants of the event destination path
    event_destination_structure = pss_pywaapi.getDescendantObjects(
        event_destination_object["id"],  # Start from the selected object
        returnProperties=["name", "type", "id", "path", "parent"]  # Return properties including parent ID and type
    )


    # Get the descendants of the event target path
    event_target_structure = pss_pywaapi.getDescendantObjects(
        event_target_object["id"],  # Start from the selected object
        returnProperties=["name", "type", "id", "path", "parent"]  # Return properties including parent ID and type
    )

    # Iterate through the descendants of the event destination struction 
    for event_destination in event_destination_structure:
        # Replace any instance of the string TEMPLATE in the event destination name
        new_name = re.sub(r'TEMPLATE', template_name, event_destination["name"])

        # Remove any trailing underscore and digits (e.g., _01, _99) at the end of the name
        new_name = re.sub(r'_\d+$', '', new_name)
        
        # Only update if the name actually changess
        if new_name != event_destination["name"]:
            # Create arguments to set the name of event_destination["id"]
            args = {
                "object": event_destination["id"],  # Use the ID of the object
                "value": new_name
            }

            # Call Waapi setName with arguments
            pss_pywaapi.call("ak.wwise.core.object.setName", args)

        # if the current event_destination is an Action and has a path
        if event_destination["type"] == "Action" and event_destination["path"]:

            try:
                # Create arguments to get the name, ActionType, and Target, from the event destination id
                args = {
                    "from": {"id": [event_destination["id"]]},
                    "options": {
                        "return": ["name", "@ActionType", "@Target"]  # Retrieve name, ActionType, and Target properties
                    }
                }
                # Make WAAPI call to retrieve the values of name, ActionType and Target
                result = pss_pywaapi.call("ak.wwise.core.object.get", args)

                # Make a copy of `result["return"]` to avoid issues with changes during iterations
                return_items = list(result.get("return", [])) 

                # Ensure result is valid and contains "return" before iterating
                for index, item in enumerate(return_items):
                    # Debugging output to monitor each item
                    # print(f"Iteration {index}, item: {item}") 

                    # If item is None or not a dictionary then skip
                    if item is None or not isinstance(item, dict):
                        print(f"Skipping unexpected item at index {index}: {item}")
                        # Skip any items that aren't dictionaries
                        continue  

                    # Get the id of the Target of the current Action
                    target_id = item.get('@Target')

                    # If target_id is a dictionary and contains "id"
                    if isinstance(target_id, dict) and "id" in target_id:

                        # # Debugging output for the ID only
                        # print("target_id:", target_id["id"])  
                        # print("target_id:", target_id)

                        # Get the target_id name
                        target_name = target_id.get("name", None)

                        # If there is a target_name
                        if target_name:

                            # Find any instance of the string TEMPLATE with the event template name
                            modified_target_name = target_name.replace("TEMPLATE", event_template_name_entry.get())
                            
                            # For each descendant of the event target structure check if the descendants name is equal to the modified_target_name
                            target_descendant = next((desc for desc in event_target_structure if desc["name"] == modified_target_name), None)
                            
                            # If a target descendant if found to have the same name as the modified_target_name
                            if target_descendant:

                                # Set the id of the Target of event_destination["id"] with the target_descendant id
                                result = pss_pywaapi.setReference(
                                    objectID=event_destination["id"],
                                    reference="Target",
                                    value=target_descendant["id"],
                                    platform=None
                                )
                                # print(f"Updated target ID to {target_descendant['id']} for {event_destination['id']}")
                            else:
                                print(f"No matching descendant found for modified target name: {modified_target_name}")
                        else:
                            print("Target name not retrieved or no modification needed.")
                    else:
                        print(f"No @Target found for object: {event_destination['name']}")
                # else:
                #     print("Error: 'result' is None or does not contain 'return' key.")
            except Exception as e:
                print(f"Error retrieving ActionType and Target for {event_destination['name']}: {e}")



# ___COMMON FUNCTIONS_________________________________________________________________________________________________________

# Builds the treeView from the source object and its descendants (source_structure)
def BuildTreeViewStructure(tree, source_object, source_structure):
    # Create a dictionary to store parent-child relationships
    tree_nodes = {}

    # Set the source objects name to the rootname
    rootname = source_object["name"]

    # If there is a template name available the replate the TEMPLATE string with the template name
    if template_name_object_path.get():
        rootname = rootname.replace("TEMPLATE", template_name_object_path.get())

    # Insert rootname into the tree and return the id
    root_id = tree.insert('', 'end', text=rootname, values=(source_object["type"],))
    
    # Add root id to tree nodes at source object id
    tree_nodes[source_object["id"]] = root_id

    # Iterate over the descendants to build the hierarchical tree structure
    for source in source_structure:
        
        # Get Actor-Mixer name and path from source
        path = source.get("path", "")
        name = source.get("name", "Unknown")
        
        # If there is a template name provided then replace the TEMPLATE string with the template name
        if template_name_object_path.get():
            name = name.replace("TEMPLATE", template_name_object_path.get())
        
        # Get the object type
        object_type = source.get("type", "Unknown")  

        # Extract the parent ID (assuming it's a dictionary, we need to access its "id" key)
        parent = source.get("parent", {})

        # Access the parent ID
        parent_id = parent.get("id", "")  

        # Check if the parent ID exists in the tree
        if parent_id in tree_nodes:
            # Insert each sound under its parent node with its type and path
            node_id = tree.insert(tree_nodes[parent_id], 'end', text=name, values=(object_type, path))
            
            # Set the node id to the tree nodes at source id
            tree_nodes[source["id"]] = node_id







# ___MAIN_________________________________________________________________________________________________________

# Connect to Wwise API
result = pss_pywaapi.connect(8081)

# Connect (default URL)
client = WaapiClient()



#___GUI setup________________________________________________________________________

# Create the main window
root = tk.Tk()
root.title("Wwise Template Importer")

# Configure row and columns in root
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Setup TTK theme styling
style = ttk.Style(root)
root.tk.call("source", "forest-light.tcl")
root.tk.call("source", "forest-dark.tcl")
style.theme_use("forest-dark")

# Create a Notebook (Tabbed interface)
notebook = ttk.Notebook(root)
notebook.grid(row=0, column=0, sticky="nsew")

# Create two frames to be used as tabs
audio_tab = ttk.Frame(notebook)
events_tab = ttk.Frame(notebook)

audio_tab.grid_columnconfigure(0, weight=1)
audio_tab.grid_rowconfigure(11, weight=1)

events_tab.grid_columnconfigure(0, weight=1)
events_tab.grid_rowconfigure(11, weight=1)

# Add frames as tabs
notebook.add(audio_tab, text="Actor-Mixer")
notebook.add(events_tab, text="Events")


#___Audio Tab________________________________________________________________________
# Create LabelFrame for each section
source_frame = ttk.LabelFrame(audio_tab, text="Select Source Template")
source_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

destination_frame = ttk.LabelFrame(audio_tab, text="Select Destination Location")
destination_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

assets_frame = ttk.LabelFrame(audio_tab, text="Select WAV Assets")
assets_frame.grid(row=6, column=0, padx=20, pady=10, sticky="ew")

teamplate_name_frame = ttk.LabelFrame(audio_tab, text="Find & Replace TEMPLATE Name")
teamplate_name_frame.grid(row=9, column=0, padx=20, pady=10, sticky="ew")

# Configure row and column to expand within each LabelFrame
source_frame.grid_columnconfigure(0, weight=1)
destination_frame.grid_columnconfigure(0, weight=1)
assets_frame.grid_columnconfigure(0, weight=1)
teamplate_name_frame.grid_columnconfigure(0, weight=1)

# Create entry fields to show strings to paths selected in Wwise
source_objectPath = tk.StringVar()
source_object_entry = ttk.Entry(source_frame, textvariable=source_objectPath, state="readonly", width=50)
source_object_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

destination_objectPath = tk.StringVar(value="")
destination_objectEntry = ttk.Entry(destination_frame, textvariable=destination_objectPath, state="readonly", width=50)
destination_objectEntry.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

assets_object_path = tk.StringVar()
assets_entry = ttk.Entry(assets_frame, textvariable=assets_object_path, state="readonly", width=50)
assets_entry.grid(row=7, column=0, padx=10, pady=5, sticky="ew")

template_name_object_path = tk.StringVar(value="")
template_name_entry = ttk.Entry(teamplate_name_frame, textvariable=template_name_object_path, state="readwrite", width=50)
template_name_entry.grid(row=10, column=0, padx=10, pady=5, sticky="ew")

# Create source button that calls OnSourceButtonClick()
source_button = ttk.Button(source_frame, text="Select Source", command=OnSourceButtonClick)
source_button.grid(row=1, column=1, padx=10, pady=10, sticky="w")

# Create destination button that calls OnDestinationButtonClick()
destination_button = ttk.Button(destination_frame, text="Select Destination", command=OnDestinationButtonClick)
destination_button.grid(row=4, column=1, padx=10, pady=10, sticky="w")

# Create assets button that calls OnAssetsButtonClick()
assets_button = ttk.Button(assets_frame, text="Select Folder", command=OnAssetsButtonClick)
assets_button.grid(row=7, column=1, padx=10, pady=10, sticky="w")

# Create preview_template button that calls OnPreviewTemplateButtonClick()
preview_template_button = ttk.Button(teamplate_name_frame, text="Preview Template", command=OnPreviewTemplateButtonClick)
preview_template_button.grid(row=10, column=1, padx=10, pady=10, sticky="w")

# Create generate_template button that calls GenerateTemplateButtonClick()
generate_template_button = ttk.Button(teamplate_name_frame, text="Generate Template", command=OnGenerateTemplateButtonClick)
generate_template_button.grid(row=10, column=2, padx=10, pady=10, sticky="w")

# Setup frame that will contain the treView
actor_mixer_tree_frame = ttk.Frame(audio_tab)
actor_mixer_tree_frame.grid(row=11, column=0, sticky="nsew")

# Add scroll bar to treeFrame
actor_mixer_tree_scroll = ttk.Scrollbar(actor_mixer_tree_frame)
actor_mixer_tree_scroll.pack(side="right", fill="y")

# Define three columns: Wwise Object (name), Wwise ObjectType, Actor-Mixer Path
column_names = ("Wwise Object", "Type", "Path")

# Define the treeview with 3 columns
actor_mixer_tree_view = TreeviewEdit(actor_mixer_tree_frame, columns=column_names)

# Set up the column headers
actor_mixer_tree_view.heading("#0", text="Wwise Object")  # This is the first column for the object names
actor_mixer_tree_view.heading("#1", text="Type")  # This is the second column for the object types
actor_mixer_tree_view.heading("#2", text="Path")  # This is the second column for the object types

# Config scrollbar to be up/down (y) 
actor_mixer_tree_scroll.config(command=actor_mixer_tree_view.yview)   

# Add treeview to treeframe
actor_mixer_tree_view.pack(fill=tk.BOTH, expand=True)


#___Event Tab________________________________________________________________________
# Create LabelFrame for each section
event_source_frame = ttk.LabelFrame(events_tab, text="Select Source Template")
event_source_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

event_destination_frame = ttk.LabelFrame(events_tab, text="Select Destination Location")
event_destination_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

event_target_frame = ttk.LabelFrame(events_tab, text="Select Target Actor-Mixer")
event_target_frame.grid(row=6, column=0, padx=20, pady=10, sticky="ew")

event_template_name_frame = ttk.LabelFrame(events_tab, text="Find & Replace TEMPLATE Name")
event_template_name_frame.grid(row=9, column=0, padx=20, pady=10, sticky="ew")

# Configure row and column to expand within each LabelFrame
event_source_frame.grid_columnconfigure(0, weight=1)
event_destination_frame.grid_columnconfigure(0, weight=1)
event_target_frame.grid_columnconfigure(0, weight=1)
event_template_name_frame.grid_columnconfigure(0, weight=1)


# Event Fields
event_source_path = tk.StringVar()
event_source_entry = ttk.Entry(event_source_frame, textvariable=event_source_path, state="readonly", width=50)
event_source_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

event_destination_path = tk.StringVar()
event_destination_entry = ttk.Entry(event_destination_frame, textvariable=event_destination_path, state="readonly", width=50)
event_destination_entry.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

event_target_path = tk.StringVar()
event_target_entry = ttk.Entry(event_target_frame, textvariable=event_target_path, state="readonly", width=50)
event_target_entry.grid(row=7, column=0, padx=10, pady=5, sticky="ew")

event_template_name = tk.StringVar()
event_template_name_entry = ttk.Entry(event_template_name_frame, textvariable=event_template_name, state="readwrite", width=50)
event_template_name_entry.grid(row=13, column=0, padx=10, pady=5, sticky="ew")


# Event Buttons
event_source_button = ttk.Button(event_source_frame, text="Select Source", command=OnSourceEventButtonClick)
event_source_button.grid(row=1, column=1, padx=10, pady=10, sticky="w")

event_destination_button = ttk.Button(event_destination_frame, text="Select Destination", command=OnDestinationEventButtonClick)
event_destination_button.grid(row=4, column=1, padx=10, pady=10, sticky="w")

event_target_button = ttk.Button(event_target_frame, text="Select Actor-Mixer", command=OnTargetEventButtonClick)
event_target_button.grid(row=7, column=1, padx=10, pady=10, sticky="w")

event_preview_template_button = ttk.Button(event_template_name_frame, text="Preview Template", command=OnPreviewEventTemplateButtonClick)
event_preview_template_button.grid(row=13, column=1, padx=10, pady=10, sticky="w")

event_generate_template_button = ttk.Button(event_template_name_frame, text="Generate Template", command=OnGenerateEventTemplateButtonClick)
event_generate_template_button.grid(row=13, column=2, padx=10, pady=10, sticky="w")

# Setup frame that will contain the event treeView
events_tree_frame = ttk.Frame(events_tab)
events_tree_frame.grid(row=14, column=0, sticky="nsew")

# Add scroll bar to treeFrame
events_tree_scroll = ttk.Scrollbar(events_tree_frame)
events_tree_scroll.pack(side="right", fill="y")

# Define three columns: Wwise Object (name), Wwise ObjectType, Actor-Mixer Path
column_names = ("Wwise Object", "Type", "Path")

# Define the treeview with 3 columns
events_tree_view = TreeviewEdit(events_tree_frame, columns=column_names)

# Set up the column headers
events_tree_view.heading("#0", text="Wwise Object")  # This is the first column for the object names
events_tree_view.heading("#1", text="Type")  # This is the second column for the object types
events_tree_view.heading("#2", text="Path")  # This is the second column for the object types

# Config scrollbar to be up/down (y) 
events_tree_scroll.config(command=events_tree_view.yview)   

# Add treeview to treeframe
events_tree_view.pack(fill=tk.BOTH, expand=True)

# Main Loop
root.mainloop()
