#!/bin/bash
# Basic script to get demovibes running on a Ubuntu 9.10+ server
# Modified from Terrasque's original Debian script by FishGuy876
# It is expected you have a clean formatted system at the time you run this,
# And don't forget to run as root/sudo!!

# Remember to add a djrandom user; otherwise when you start icecaster.sh you'll get:
# No handlers could be found for logger "pyAdder"
# Error: Could not import module pyAdder

# Ubuntu Notes:
#
# Ubuntu 9.10 seems to have multiverse already enabled for the liblame stuff, so
# We call it as a normal apt-get in this script.
#
# Not sure if its just Ubuntu related, but the script fails to install python-mysqldb
# On Debian version. Added here and there to be sure its installed (eliminates problems)

cd ..

if [ -f "demovibes/settings.py" ]
then
  echo "settings.py exist! Aborting!"
  exit 1
fi

if [ ! -f "demovibes/urls.py" ]
then
 echo "Run from wrong directory. Very confused. Quitting"
 exit 1
fi

echo "Warning! This will do no error checking, will install a lot of software on your system,"
echo "         is made specifically for Ubuntu 9.10+ machines, and will alter your database"
echo "         and apache settings. It will also cause an existing Demovibes install to stop working!"
echo
echo "         This script is meant to be run as root on a clean install"
echo
echo "         If this is not what you want, hit CTRL-C now! Otherwise, press enter to continue."

read

echo "If you have a dns/domain name you want it to answer to, please input it here. Blank line assumes that all incoming connections to this server is for demovibes."
echo -n "Please input hostname : "
read hostn

#Packages to install
database="mysql-server"
web="libapache2-mod-wsgi apache2"
python="python-imaging python-django python-mysqldb python-flup python-pymad python-setuptools python-openid"
memcache="python-memcache memcached"
lame_support="libmp3lame0 libmp3lame-dev"
icecast="icecast2"
ices_compile="build-essential python-dev libshout3-dev"
demosauce_compile="build-essential lame libboost-dev libicu-dev"

django = "http://www.djangoproject.com/download/1.1.1/tarball/"
south="http://www.aeracode.org/releases/south/south-0.6.2.tar.gz"
ices="http://downloads.us.xiph.org/releases/ices/ices-0.4.tar.gz"

curdir=$(pwd)
dbname="demovibes"
dbuser="demovibes"

#Setting up various passwords
random=$(dd if=/dev/urandom bs=30 count=1  2>/dev/null | base64 -w 0)
dbpw=$(dd if=/dev/urandom bs=8 count=1  2>/dev/null | base64 -w 0)
ice_admin=$(dd if=/dev/urandom bs=8 count=1  2>/dev/null | base64 -w 0)
ice_relay=$(dd if=/dev/urandom bs=8 count=1  2>/dev/null | base64 -w 0)
ice_source=$(dd if=/dev/urandom bs=8 count=1  2>/dev/null | base64 -w 0)


echo -e "\n\n\nInstalling packages $python $web $database $icecast $lame_support $ices_compile $memcache \n\n\n"
#apt-get update
apt-get install -y $python $web $database $icecast $lame_support $ices_compile $memcache $demosauce_compile


# Because not all mirrors carry the very latest security release of Django...
echo -e "\n\n\nInstalling Django 1.1.1 [Security Release]\n\n\n"
wget $django
tar -zxvf Django-1.1.1.tar.gz > /dev/null
cd Django-1.1.1
python setup.py install > /dev/null
cd ..
rm -rf Django-1.1.1


echo -e "\n\n\nInstalling Django South from $south\n\n\n"
wget $south
tar -xzf south-0.6.2.tar.gz > /dev/null
rm south-0.6.2.tar.gz
cd south
python setup.py install > /dev/null
cd ..
rm -rf south


echo -e "\n\n\nCreating database. Need to input database server root password\n\n\n"
sql="CREATE DATABASE __DBNAME__; GRANT ALL ON __DBNAME__.* TO __DBUSER__@localhost IDENTIFIED BY '__PASS__';"
echo $sql | sed -e "s!__PASS__!$dbpw!g" -e "s/__DBNAME__/$dbname/g" -e "s/__DBUSER__/$dbuser/g" | mysql -u root -p


echo -e "\n\n\nSetting up demovibes..\n\n\n"
cd static
mkdir media
chmod a+rwX media

# Creates compilation folder and ensures www-data owns it for apache reasons. AAK
cd media
mkdir compilations
chmod a+rwX compilations
chown www-data:www-data compilations

# Create a folder for artist avatars
mkdir artists
chmod a+rwX artists
chown www-data:www-data artists

# Create a folder for label/producer avatars
mkdir labels
chmod a+rwX labels
chown www-data:www-data labels

# And now the same for group artwork
mkdir groups
chmod a+rwX groups
chown www-data:www-data groups
cd ..

cd ..
cd demovibes
sed -e "s!__PATH__!$curdir!g" -e "s!__PASS__!$dbpw!g" -e "s!__RANDOM__!$random!g" -e "s/__DBNAME__/$dbname/g" -e "s/__DBUSER__/$dbuser/g" ../contrib/settings.py.example > settings.py
python manage.py syncdb
echo "Running DB migrate.."
python manage.py migrate > django-migrate.log
cd ..


echo -e "\n\n\nCreating WSGI file\n\n\n"
mkdir apache
sed -e "s!__PATH__!$curdir!g" contrib/demovibes.wsgi > apache/demovibes.wsgi


echo -e "\n\n\nSetting up apache\n\n\n"
echo "Finding django media path.. might take some time"
mediapath=$( find /usr/ -name media -type d | grep django)
echo "Found at $mediapath"
sed -e "s!__PATH__!$curdir!g" -e "s!__MEDIA_PATH__!$mediapath!g" contrib/demovibes.apache > /etc/apache2/sites-available/demovibes
# Get hostname?
# Enable the site?
if [ -z "$hostn" ]
then
	a2dissite default
else
	sed -i -e "s!#PLACEHOLDER#!ServerName $hostn!g" /etc/apache2/sites-available/demovibes
fi
a2ensite demovibes
/etc/init.d/apache2 reload


echo -e "\n\n\nInstalling ices0 (some warnings are common)\n\n\n"
wget $ices
tar -xzf ices-0.4.tar.gz
rm ices-0.4.tar.gz
cd ices-0.4
./configure --with-python > configure-log.txt
make > make-log.txt
cd ..

sed -e "s!__PATH__!$curdir!g" -e "s!__URL__!$hostn!g" contrib/icecaster.sh > demovibes/icecaster.sh
chmod a+x demovibes/icecaster.sh
echo -n $ice_source > demovibes/icepw.txt

# Configure icecast2
# $ice_admin $ice_source $ice_relay and enable
# <source-password>hackme</source-password> <relay-password>hackme</relay-password> <admin-password>hackme</admin-password>
echo -e "\n\n\nConfiguring IceCast\n\n\n"
icefile="/etc/icecast2/icecast.xml"
sed -i -e "s!<source-password>hackme</source-password>!<source-password>$ice_source</source-password>!g" $icefile
sed -i -e "s!<relay-password>hackme</relay-password>!<relay-password>$ice_relay</relay-password>!g" $icefile
sed -i -e "s!<admin-password>hackme</admin-password>!<admin-password>$ice_admin</admin-password>!g" $icefile
sed -i -e "s!ENABLE=false!ENABLE=true!g" /etc/default/icecast2
/etc/init.d/icecast2 restart



echo "Icecast passwords :"
echo " Admin  : $ice_admin"
echo " Relay  : $ice_relay"
echo " Source : $ice_source"
echo
echo "You can start the streamer by changing to the folder $curdir/demovibes and run ./icecaster.sh"
