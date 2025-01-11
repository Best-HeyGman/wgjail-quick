# wgjail-quick
Wgjail-quick gives you the ability to create a "Wireguard jail", i.e. a network namespace where a program that is running inside that namespace can only see and use the one wireguard connection you have given it. There are two main reasons why you would want to do this:
1. For split tunneling, which means that only some of the programs on your pc shall use the wireguard vpn, while the rest just uses your normal network connection
2. To prevent a program from using your normal internet connection in case the wireguard vpn connection is shut down / crashes (a killswitch).
  
Wgjail-quick is based on the ideas of wgjailr (https://github.com/moismailzai/wgjailr), many thanks to Mo Ismailzai for writing wgjailr.  
So, why wgjail-quick then? Because I wanted something that:
1. Has a similar syntax to wg-quick, because people already use wg-quick and are used to that syntax.
2. Can be packaged for a Linux distribution (wgjailr can't really, because it needs some variables to be set in the script file itself)

# Dependencies
TLDR:  
`socat wireguard-tools bubblewrap`
- You need wireguard-tools.  
- If you want to forward a port into the namespace, you also need socat.
- If you want to use the exec command, you also need bubblewrap (bwrap), which is necessary to map the resolv.conf file with the ip of your wireguard vpn's dns server to the correct location where programs expect it (/etc/resolv.conf). Bubblewrap is not needed for a cmd-service, as systemd itself can map the resolv.conf file to the correct location. Why this added complexity? Well, I doubt you would want a dns leak. This is why. I got your back.   
- Everything else should already be on your system.

# Installing
## Manual Install / Uninstall
Just copy the "`wgjail-quick`" file to `/usr/bin` and make sure it is executable.  
To unistall, just: `rm /usr/bin/wgjail-quick`

## Distribution Packages
I wrote wgjail-quick with packaging for Linux Distributions in mind, so please feel free to do so for whatever distribution you would like.  
I myself want to make a Fedora/Epel RPM, when I have the time to do so. If you, however, are already a Fedora package maintainer, I won't complain about less work :)  

# Usage
`wgjail-quick [ up | down ] [ CONFIG_FILE | INTERFACE ]`  
`wgjail-quick exec [ CONFIG_FILE | INTERFACE ] USERNAME CMD_LINE`  
`wgjail-quick portforward [ CONFIG_FILE | INTERFACE ] LISTEN_ADDRESS FORWARDED_PORT [ DESTINATION_PORT ]`  
`wgjail-quick generate-jail-service [ CONFIG_FILE | INTERFACE ]`  
`wgjail-quick generate-cmd-service [ CONFIG_FILE | INTERFACE ] CMD_LINE`  
`wgjail-quick generate-portforward-service [ CONFIG_FILE | INTERFACE ] LISTEN_ADDRESS FORWARDED_PORT [ DESTINATION_PORT ]`

CONFIG_FILE is a path to a wireguard configuration file. Using an absolute path is a good idea.  

INTERFACE is a wireguard config file that is in /etc/wireguard  
Which means, you only have to write, for example, "p2p" to use the wireguard config file /etc/wireguard/p2p.conf

The portion of the config files basename before the .conf is the name that will be given to:
1. the network namespace (the "wireguard jail") and
2. The wireguard interface inside the network namespace.

CMD_LINE is a command with command line arguments that you want to execute in the namespace.

# Commands
## up
Creates a new network namespace with a wireguard interface defined in the given config file.

## down
Removes the given network namespace.

## exec
Executes a command in the given network namespace.  
USERNAME is the username or uid of the user that shall execute the given command.

## portforward
Forwards a port into the network namespace. You have to specify on which Address to listen and which port to forward. Use 0.0.0.0 to listen everywhere.  
Optionally you can also define a destination port inside of the network namespace that is different from the port on which the host system listens. If not given, the same port is used.

## generate-jail-service
Generates a systemd service that creates a network namespace, like with the up command. Result will be saved to the current directory (`./wgjail-NAMESPACE.service`).  
This service will expect to find the configuration file at the same absolute path on every start. Make sure you generate the service either with the absolute path to where the config file will be permanently or, if you plan to put the config file into '/etc/wireguard/CONFIG_FILE.conf', it is enough to give the filename before the '.conf' without any path.

## generate-cmd-service
Generates a systemd template service that starts the given command inside the given network namespace, like the exec keyword.  
When you start this service, make sure you append the username that shall run the command after the '@' symbol, e.g. '`systemctl start wgjail-NAMESPACE-CMD@myuser.service`'. Result will be saved to the current directory (`./wgjail-NAMESPACE-CMD@.service`).  
CMD will be substituted by the name of the command. The parameters will not be inserted into the filename. If you want to create multiple services for the same command you have to rename them manually.  
The network namespace this service references has to also be started via a systemd service (e.g. with a service generated by the "generate-jail-service" command), so that systemd can make sure that the jail already exists before it tries to execute this command inside the jail. This cmd service will bind to the jail service and will automatically be stopped if the jail service is stopped.

## generate-portforward-service
Generates a systemd template service that forwards a port into the network namespace (the wireguard jail).  
Result will be saved to the current directory('`wgjail-NAMESPACE-portforward-LISTEN_ADDRESS-FORWARDED_PORT.service`').  
Optionally you can also define a destination port inside of the network namespace that is different from the port on which the host system listens. If not given, the same port is used.  
The network namespace this service references has to also be started via a systemd service (e.g. with a service generated by the "generate-jail-service" command), so that systemd can make sure that the jail already exists before it tries to execute this command inside the jail. This cmd service will bind to the jail service and will automatically be stopped if the jail service is stopped.


# Usage Examples
## Temporary
If you want to, for example, just quickly torrent an iso of Hannah Montana Linux, which is not a metaphor for something else, and you want to make sure your torrent client only uses a vpn connection and under no circumstances your normal internet connection, while the rest of your system continues just as normal, you can do it this way:  
`sudo wgjail-quick up /path/to/<wireguard_config>.conf`  
`sudo wgjail-quick exec /path/to/<wireguard_config>.conf <your_username> qbittorrent`  
When you're done, close the qbittorrent window, then:  
`sudo wgjail-quick down /path/to/<wireguard_config>.conf`  
Done, very easy.

## Permanently via systemd services
If you now, for example, have set up a dedicated server to seed your Hannah Montana Linux iso image, you can, with wgjail-quick, create systemd files that automatically, on boot:
1. create the wireguard jail, then
2. start qbittorrent-nox (nox means webUI, so that you can connect to your server via a webbrowser and can use qbittorrent this way), then
3. forward a port into the wireguard jail, so that you can access the webinterface of qbittorrent:

`wgjail-quick generate-jail-service /path/to/<wireguard_config>.conf`  
`wgjail-quick generate-cmd-service /path/to/<wireguard_config>.conf /usr/bin/qbittorrent-nox -d --webui-port=6969`  
`wgjail-quick generate-portforward-service /path/to/<wireguard_config>.conf 0.0.0.0 6969` 
 
Now you can copy these systemd files to `/etc/systemd/system` and enable them. The filenames are different depending on how you named your wireguard conf file (just like wg-quick sets the name of the interface it creates according to the filename of the .conf file). If, for example, your wireguard config file was named "my-wg.conf" and the username with which you want to start the qbittorrent server is "myuser", then you can copy and start the services, for example, like this:  
`sudo cp wgjail-my-wg.service wgjail-my-wg-qbittorrent-nox@.service wgjail-my-wg-portforward-0.0.0.0-6969.service /etc/systemd/system`
`sudo systemctl enable --now wgjail-my-wg.service wgjail-my-wg-qbittorrent-nox@myuser.service wgjail-my-wg-portforward-0.0.0.0-6969.service`

# Todo
- Make a manpage
	+ It should probably be enough to convert the "commands" and "usage" portion of this readme to manpage syntax. Maybe there is even a way to do this conversion automatically.
- Maybe make a "exec-gui" command
	+ Some gui applications will not work / not work properly when started with the exec command inside a wgjail. The problems for gui programs are:
		* No connection to dbus
		* Audio does not work
	+ Some applications are ok with that, like qbittorrent. Others, like Firefox, won't even start.
	+ So, I would like to keep the "exec" command the way it works right now and not pile a lot of magic on top, but adding an "exec-gui" command that does that magic would probably be a nice thing to have for many users.



SPDX-License-Identifier: CC0-1.0+  
© 2024-2025 Stephan Hegemann
