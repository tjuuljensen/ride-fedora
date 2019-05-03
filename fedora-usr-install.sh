#!/bin/sh
# customize gnome script
# authored by.  Torsten Juul-Jensen/oct. 2015
# last edited: February 06, 2018 09:45



_gnomeConfig() {
  # add date to top bar
  gsettings set org.gnome.desktop.interface clock-show-date true

  # show week numbers in calendar drop-down
  #gsettings set org.gnome.shell.calendar show-weekdate true #deprecated from f25?!

  #enable desktop icons
  gsettings set org.gnome.desktop.background show-desktop-icons true

  # add minimize and maximize buttons to windows
  gsettings set org.gnome.desktop.wm.preferences button-layout ":minimize,maximize,close"

  # replace system locale to da_DK
  gsettings set org.gnome.system.locale region "'da_DK.UTF-8'"

  gsettings  set org.gnome.shell favorite-apps "['firefox.desktop', 'chromium-browser.desktop', 'atom.desktop', 'mozilla-thunderbird.desktop', 'vmware-workstation.desktop', 'libreoffice-writer.desktop', 'org.gnome.gedit.desktop', 'org.gnome.Nautilus.desktop', 'veracrypt.desktop', 'keepassx2.desktop', 'terminator.desktop' ]"

  # set sleep timeout to 10 minutes (600 seconds), then require login after 5 minutes (300 seconds)
  gsettings set org.gnome.desktop.session idle-delay 600
  gsettings set org.gnome.desktop.screensaver idle-activation-enabled 'true'
  gsettings set org.gnome.desktop.screensaver lock-enabled 'true'
  gsettings set org.gnome.desktop.screensaver lock-delay 300

  # add <Super>+D as show-desktop shortcut
  gsettings set org.gnome.desktop.wm.keybindings show-desktop "['<Super>d']"

  # add the list of custom shortcuts
  gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "['/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom100/','/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom101/','/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom102/']"

  # add the first shortcut - Terminal
  gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom100/ name 'Terminal'
  gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom100/ command 'gnome-terminal'
  gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom100/ binding '<Control><Alt>t'

  # add the second shortcut - Terminator
  gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom101/ name 'Terminator'
  gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom101/ command 'terminator'
  gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom101/ binding '<Super><Control>t'

  # add the second shortcut - Home
  gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom102/ name 'Nautilus - home folder'
  gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom102/ command 'nautilus'
  gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom102/ binding '<Super>e'

}

_gnomeShellExtensions(){
  # get gnome extensions
  # requires that shell-extension-install script is installed

  # install taskbar extension
  gnome-shell-extension-installer 584
  # install frippery move clock
  gnome-shell-extension-installer 2
  # restart gnome shell - CANNOT DO after wayland


  # get gnome extensions from github
  #if _confirm "Do you want to install GIT extension 'hostname-in-taskbar'? [yN] " ; then
    mkdir -p ~/git_projects
    cd ~/git_projects
    git clone git://github.com/tjuuljensen/gnome-shell-extension-hostname-in-taskbar.git
    mkdir -p ~/.local/share/gnome-shell/extensions
    cd ~/.local/share/gnome-shell/extensions
    ln -s ~/git_projects/gnome-shell-extension-hostname-in-taskbar/hostname-in-taskbar
  #fi


}





_firefoxConfig(){
  if ( command -v mozilla-extension-manager  > /dev/null 2>&1 ) ; then

    mkdir -p ~/.mozilla
    cd ~/.mozilla/firefox
    cd *.default
    mkdir extensions

    echo
    echo Install Firefox plugins
    firefox-extension-manager --install --user --url https://addons.mozilla.org/en-US/firefox/addon/ublock-origin
    firefox-extension-manager --install --user --url https://addons.mozilla.org/en-US/firefox/addon/privacy-badger17
    firefox-extension-manager --install --user --url https://addons.mozilla.org/firefox/downloads/latest/https-everywhere/addon-229918-latest.xpi
    firefox-extension-manager --install --user --url https://addons.mozilla.org/firefox/downloads/latest/noscript/addon-722-latest.xpi
    firefox-extension-manager --install --user --url https://addons.mozilla.org/en-US/firefox/addon/print-friendly-pdf/

    #firefox --new-tab https://addons.mozilla.org/en-US/firefox/addon/disable-autoplay/



  fi
}

_thunderbirdConfig(){

  echo
  echo Starting Thunderbird to create profile
  thunderbird & # start Thunderbird so profile is created
  sleep 15
  pkill thunderbird


  if ( command -v mozilla-extension-manager  > /dev/null 2>&1 ) ; then
    echo Installing enigmail plugin for thunderbird...
    mozilla-extension-manager --install https://addons.mozilla.org/thunderbird/downloads/latest/71/addon-71-latest.xpi
    echo Installing other Thunderbird plugins
    mozilla-extension-manager --install https://addons.mozilla.org/thunderbird/downloads/latest/google-search-for-thunderbi/addon-370540-latest.xpi
    mozilla-extension-manager --install https://addons.mozilla.org/thunderbird/downloads/latest/provider-for-google-calendar/addon-4631-latest.xpi
    mozilla-extension-manager --install https://addons.mozilla.org/thunderbird/downloads/latest/thunderkeep/addon-464405-latest.xpi
    mozilla-extension-manager --install https://addons.mozilla.org/thunderbird/downloads/latest/dansk-ordbog/addon-3596-latest.xpi
    #mozilla-extension-manager --install https://addons.mozilla.org/thunderbird/downloads/latest/exquilla-exchange-web-services/platform:2/addon-244848-latest.xpi
    #mozilla-extension-manager --install https://github.com/Ericsson/exchangecalendar/releases/download/v3.8.0/exchangecalendar-v3.8.0.xpi
    # Install ExchangeCalendar plugin for Thunderbird - see more at https://github.com/ExchangeCalendar/exchangecalendar/releases
    mozilla-extension-manager --install https://github.com/ExchangeCalendar/exchangecalendar/releases/download/v4.0.0-beta5/exchangecalendar-v4.0.0-beta5.xpi --user --thunderbird
    #cd ~/git_projects
    #git clone --recursive git://github.com/Ericsson/exchangecalendar.git
    #cd exchangecalendar
    #chmod +x build.sh
    #./build.sh -u
  fi
}

_makeCustomizations(){
  # Create /home/user/bin directory
  mkdir -p ~/bin

  #wget -O ~/Downloads/wallpapers.zip https://dl.dropboxusercontent.com/u/2997933/wallpapers.zip
}

########## MAIN ##############

# must be run as a regular user and NOT root
# exit if the user is root

[ "$UID" -eq 0 ] && { echo Do no run as root - script will exit.; exit ;}
