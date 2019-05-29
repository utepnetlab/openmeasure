# OpenMeasure install
error=0
OS="/"unknown/""

# must be run as root
if [ $EUID -ne 0 ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# check for dependencies:
echo ""
echo "Checking for dependencies..." 
echo ""

# python3
hash python3 &> /dev/null
if [ $? -eq 1 ]; then
    echo ""
    echo >&2 "***** DEPENDENCY ERROR *****" 
    echo "\"python3\" is required, please run the installation script again after installing this dependency..."
    echo ""
    exit 1
else
    echo "...python3 found!"
fi

# ping
hash ping &> /dev/null
if [ $? -eq 1 ]; then
    echo ""
    echo >&2 "***** DEPENDENCY ERROR *****" 
    echo "\"ping\" is required, please run the installation script again after installing this dependency..."
    echo ""
    exit 1
else
    echo "...ping found!"
fi

# iperf3
hash iperf3 &> /dev/null
if [ $? -eq 1 ]; then
    echo ""
    echo >&2 "***** DEPENDENCY ERROR *****" 
    echo "\"iperf3\" is required, please run the installation script again after installing this dependency..."
    echo ""
    exit 1
else
    echo "...iperf3 found!"
fi

# numpy
if python3 -c 'import pkgutil; exit(not pkgutil.find_loader("numpy"))'; then
    echo '...numpy found!'
else
    echo ""
    echo >&2 "***** DEPENDENCY ERROR *****" 
    echo "\"numpy\" python module is required, please run the installation script again after installing this dependency..."
    echo ""
    exit 1
fi

# pandas
if python3 -c 'import pkgutil; exit(not pkgutil.find_loader("pandas"))'; then
    echo '...pandas found!'
else
    echo ""
    echo >&2 "***** DEPENDENCY ERROR *****" 
    echo "\"pandas\" python module is required, please run the installation script again after installing this dependency..."
    echo ""
    exit 1
fi

# flask
if python3 -c 'import pkgutil; exit(not pkgutil.find_loader("flask"))'; then
    echo '...flask found!'
else
    echo ""
    echo >&2 "***** DEPENDENCY ERROR *****" 
    echo "\"flask\" python module is required, please run the installation script again after installing this dependency..."
    echo ""
    exit 1
fi

# requests
if python3 -c 'import pkgutil; exit(not pkgutil.find_loader("requests"))'; then
    echo '...requests found!'
else
    echo ""
    echo >&2 "***** DEPENDENCY ERROR *****" 
    echo "\"requests\" python module is required, please run the installation script again after installing this dependency..."
    echo ""
    exit 1
fi

# create OpenMeasure directories
mkdir /opt/openmeasure

# copy over OpenMeasure files
cp -rf ./* /opt/openmeasure

#-------------------DONE----------
echo ""
echo "OpenMeasure has been successfully installed!"
echo "To start OpenMeasure, run \"sudo python3 /opt/openmeasure.py\""
echo "The OpenMeasure python API is located at /opt/openmeasure/libs"
echo ""
