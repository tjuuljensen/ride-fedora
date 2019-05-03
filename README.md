# bootstrap-fedora
Bootstrap installation of fedora system

## Usage
usage: bootstrap-loader.sh [--include <function library file>] [--preset <filename>] [[_]actionname]

### Example

bootstrap-loader.sh  --include fedora-install-functions.sh --include serialnumbers.config --preset default.preset actionFunction1 actionFunction2

### FAQ
What is an action?
An action is a name of one of the functions referenced in either one of the included file
