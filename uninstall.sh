# OpenTap uninstall
#
error=0
OS="/"unknown/""

# must be run as root
if [ $EUID -ne 0 ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# remove OpenTap directories
rm -rf /opt/openmeasure

#-------------------DONE----------
echo ""
echo "OpenMeasure has been successfully uninstalled."
echo "Sorry to see you go!"	
echo ""
