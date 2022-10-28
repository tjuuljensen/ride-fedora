# bootstrap installation
Bootstrap installation of fedora system.  
Can be initated using these commands:
```
$ wget https://tjuuljensen.github.io/bootstrap-fedora/ -O bootstrap.sh
$ chmod +x bootstrap.sh
$ ./bootstrap.sh --default
```
...or just use the one-liner:  
```
$ wget https://tjuuljensen.github.io/bootstrap-fedora/ -O bootstrap.sh && chmod +x bootstrap.sh && ./bootstrap.sh  --default
```

This way the one-liner will allow you to customize your install by *editing* the preset file before installing:  
```
$ wget https://tjuuljensen.github.io/bootstrap-fedora/ -O bootstrap.sh && chmod +x bootstrap.sh && ./bootstrap.sh --edit
```

You can also *halt the installation* process when the source has been downloaded.
The source will be left in a subdirectory to current directory:
```
$ wget https://tjuuljensen.github.io/bootstrap-fedora/ -O bootstrap.sh && chmod +x bootstrap.sh && ./bootstrap.sh --stop
```

The bootstrap installer also accepts the full input for the ride.sh script.
Everything after --ride will be parsed to the ride installer.
```
$ ./bootstrap.sh --ride --help
```

### Optional loading of variables
usage: `bootstrap.sh --ride --include lib-fedora.sh --include serialnumbers.config --preset default.preset actionFunction1 actionFunction2`

### FAQ
**Q:** What is an action?  
**A:** An action is a name of one of the functions referenced in either one of the included file  

**Q:** The preset function could easily have been included the same way as the function libraries. Why not source everything?  
**A:** For readability purposes, I have chosen this solution because it is easy to see which functions are mutually connected.  

**Q:** Are there dependencies between actions?  
**A:** I have strived to keep each action atomic, having no dependencies to other actions. A few exclusions apply though; 1) rpmfusion repos are required for a lot of the installations 2) CERT Forensic repo is required for all functions in that section.
