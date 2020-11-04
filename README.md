# Cisco Umbrella Internal Network Register

This repo contains a Python script that creates Internal Networks in Umbrella using a CSV file, making it easier to register mass networks.

API key and API secret of <a href="https://docs.umbrella.com/umbrella-api/docs/authentication-and-errors">Cisco Umbrella Management API</a> is also required.

Umbrella Organization ID is also required to use this script! Use <a href = "https://docs.umbrella.com/deployment-umbrella/docs/find-your-organization-id" target="_blank">esta documentação</a> to find out how to obtain your Organization ID.

If you do not have the required Python libraries configured, you will receive an error when running the script. You will need to install the "requirements.txt" file: (make sure it is in the same directory as the cloned git files):<br>
<b> pip install -r requirements.txt</b><br>

# Config file, modify with your data and credentials before running the script
<img src="screenshots/configuration.png"><br><br><br>


# How it works ??
• The script will require prompts to indicate the CSV file that will be used for registration. If not, it closes. (There is no need to add an extension for the CSV file, the script does it automatically)<br>
<img src="screenshots/informa_csv.png"><br><br><br>
• After informing the CSV, and if it exists, the script will give you two options:<br> 
    1. Create a new Site, and from the created Site, register the Internals Networks and assing to this new created Site<br>
    <img src="screenshots/criar_novo_site.png"><br>
    2. Register the Internal Networks ans assigns to a existing site, the scritp will print a list of existing Sites on Umbrella, and for that option you will use the SiteId in nexts steps<br>
    <img src="screenshots/listSites.png"><br>
    3. O CSV deve ser preenchido da seguinte forma para que o script funcione corretamente<br>
<b> ALWAYS: NAME,IP,PREFIX</b>
<img src="screenshots/csv_file.png"><br><br>

# Features
•  The script works in a totally intelligent way, does basic and advanced checks, and makes decisions correctly, including:<br>
1. Checks if the Ip's informed in the CSV are valid. It must be a Network Ip. The script tells you which IP's are incorrect in the CSV to facilitate user correction
2. Checks if a Site is already registered in Umbrella, if the option chosen by the user is to create a new Site. That's because Umbrella cannot have Sites with the same name
3. It will remove from the CSV any information that is exactly duplicated
4. It will remove from the CSV names and Networks that are the same! That's because in Umbrella, name and networs must be unique, so the script does this automatically for you if you have something duplicated in CSV
5. It will compare with what is already registered in Umbrella, and if is are already registered, the script automatically removes this data and does not send it for registration! The script will send only what is not registered in Umbrella. <b>This makes the user’s life much easier =D</b>

# Images of how script works
<img src="screenshots/invalidNetwork.png"><br>
<img src="screenshots/nothing_new.png"><br>
<b> If the user chooses the option to assign to an existing Site<b><br>
<img src="screenshots/option_assign.png"><br>
<b> If the user chooses the option to create a new Site<b>
<img src="screenshots/option_create.png"><br>
<b> Showing on Umbrella Dashboard !
<img src="screenshots/umbrella_internalnetword.png"><br>
<img src="screenshots/umbrellaSites.png"><br>
