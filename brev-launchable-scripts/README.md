# Installation Scripts

There is an entrypoint script ```installer.sh``` which will look for all the other scripts and execute then in order keeping a logic and will add a CRON job.

This is the order of execution which can be modified easily:

1. Script: ```setup-novnc.sh```
2. Script: ```setup-conda.sh```
3. Script: ```setup-isaacsim.sh```
4. Script: ```setup-isaaclab.sh```

Make sure the scripts all executable:

```bash
chmod +x installer.sh setup-novnc.sh setup-conda.sh setup-isaacsim.sh setup-isaaclab.sh setup-gr00t.sh setup-leisaac.sh
```

Run the installer

```bash
sudo ./installer.sh
```

> [!NOTE]
> There is an issue where conda fails at the ```isaaclab --install```, the fix is to run again.


Added an example of how to extend the installer to add several other things like LeIsaac and Isaac-GR00T. 

By setting the ```INSTALL_OPTIONAL=true``` it will run the additional functions the installer allowing to use more scripts to customize the project.

```bash
INSTALL_OPTIONAL=false 
```


## Connect to Instance 

Connect to instance using VNC must first get the IP:

```bash
curl ifconfig.me
```

Example: 

54.145.206.94

Then propely replace the ip into the URL:

http://<instance-public-ip>:6080/vnc.html

Example completed URL:

http://54.145.206.94:6080/vnc.html

## Debugging

There is some proto tooling to help with stability:

```bash
# Verbose output of the installer for debugging
cat /var/log/install_output.log

# Log which stage the installer is at 
cat /var/log/install_progress.log

# Rewind the progress bookmark back to desired stage 
echo "stage_name" | sudo tee /var/log/install_progress.log
```


## Making the Launchable

Repo link:

[goat_racer_collab](https://github.com/Reality-Web-Services/goat_racer_collab)

Startup Script for Private repo does not work and adding the URL with PAT wont work either.


Provide a public Repo to the Brev Launchable.

**Launchable Script**

The script is being run by Cloud-Init therefore there are limitations.

This is an example script to run the installer:

```bash
#!/bin/bash
set -e

# 1. Define where the repo will live
WORKSPACE_DIR="/home/ubuntu" 
REPO_NAME="gr00t-launchable"
REPO_PATH="$WORKSPACE_DIR/$REPO_NAME"

# 2. Navigate directly into the scripts directory
echo "Navigating to scripts directory..."
cd "$REPO_PATH/scripts"

# 2. Make the installer executable
chmod +x installer.sh setup-novnc.sh setup-conda.sh setup-isaacsim.sh setup-isaaclab.sh setup-gr00t.sh setup-leisaac.sh

# 3. Run the installer
echo "Executing installer.sh..."

# Running it with nohup so it doesn't block the rest of the Brev setup process, 
# and routing all output to a log file for easy debugging.
nohup ./installer.sh > /home/ubuntu/installer_output.log 2>&1 &

echo "=== Setup Launched Successfully ==="
```

**Networking**

Configure the Follwing ports on the Launchable:

- port = 4000
- port = 5900
- port = 6080
- port = 443
- port = 80
- port = 53
- port = 123