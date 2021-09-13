# bootstrap-fedora
Bootstrap installation of fedora system
can be initated using these commands:
```
$ wget https://tjuuljensen.github.io/bootstrap-fedora/ -O bootstrap.sh
$ chmod +x bootstrap.sh
$ ./bootstrap.sh
```
...or just use the one-liner:  
```
$ wget https://tjuuljensen.github.io/bootstrap-fedora/ -O bootstrap.sh && chmod +x bootstrap.sh && ./bootstrap.sh
```
## Usage
usage: run-command.sh [--include \<function library file>] [--preset \<filename>] [[_]actionname]

### Example
usage: run-command.sh  --include lib-fedora.sh --include serialnumbers.config --preset default.preset actionFunction1 actionFunction2

### FAQ
**Q:** What is an action?
**A:** An action is a name of one of the functions referenced in either one of the included file

**Q:** The preset function could easily have been included the same way as the function libraries. Why not source everything?
**A:** For readability purposes, I have chosen this solution because it is easy to see which functions are mutually connected.
