#!/bin/bash
# Execute ZStack build and prepare test environment. 

WOODPECKER_VIRTUALENV=/var/lib/zstack/virtualenv/woodpecker
ZSTACK_TEST_ROOT=${ZSTACK_TEST_ROOT-'/usr/local/zstack'}
ZSTACK_PYPI_URL=${ZSTACK_PYPI_URL-'https://pypi.python.org/simple/'}
ZSTACK_VR_IMAGE_PATH=''
#User could define local post script, which will be executed before this deployer script exit. For example, user could copy the update virtual router image to remote http server.
USR_LOCAL_POST_BUILD_SCRIPT=/root/.zstackwoodpecker/.post_build_script.sh

help (){
    echo "Usage: $0 [options]

    Default option is -a
Options:
  -a            equal to -zuw
  -h            show this help message and exit
  -r            set zstack 'root' path, default is '/usr/local/zstack'
  -u            pull zstack-utility
  -w            pull zstack-woodpecker
  -z            pull zstack 
  -i ZSTACK_VR_IMAGE_PATH
                the path of virtual router_image
"
    exit 1
}

OPTIND=1
while getopts "r:i:azuwh" Option
do
    case $Option in
        a ) ;;
        z ) ;;
        u ) ;;
        w ) ;;
        r ) ZSTACK_TEST_ROOT=$OPTARG;;
        i ) ZSTACK_VR_IMAGE_PATH=$OPTARG;;
        h ) help;;
        * ) help;;
    esac
done
OPTIND=1

echo -e "\n - Your ZStack working folder is: $(tput setaf 14)${ZSTACK_TEST_ROOT}$(tput sgr0) - \n" 

INSTALL_REQ_PKG=$ZSTACK_TEST_ROOT/zstack-woodpecker/dailytest/install_required_pkgs.sh
BUILD_ZSTACK=$ZSTACK_TEST_ROOT/zstack-woodpecker/dailytest/build_zstack.sh
UPDATE_IMAGE_SCRIPT=$ZSTACK_TEST_ROOT/zstack-woodpecker/dailytest/update_vr_image.sh
INSTALL_WOODPECKER_ENV_SCRIPT=$ZSTACK_TEST_ROOT/zstack-woodpecker/dailytest/install_woodpecker_env.sh
$INSTALL_REQ_PKG
[ $? -ne 0 ] && echo "Check Required Packages failure. Exit." && exit 1

$BUILD_ZSTACK $@
[ $? -ne 0 ] && echo "Build ZStack failure. Exit." && exit 1

ZSTACK_ARCHIVE=$ZSTACK_TEST_ROOT/zstack_build_archive
SANITYTEST_FOLDER="$ZSTACK_TEST_ROOT/sanitytest"
SANITYTEST_CONF_FOLDER=$SANITYTEST_FOLDER/conf
ZSTACK_UTILITY=$ZSTACK_TEST_ROOT/zstack-utility
APIBINDING=$ZSTACK_UTILITY/apibinding
ZSTACKLIB=$ZSTACK_UTILITY/zstacklib

tempfolder=`mktemp -d`
/bin/cp -f $ZSTACK_ARCHIVE/latest $tempfolder
cd $tempfolder
tar zxf latest
mkdir -p $SANITYTEST_FOLDER
/bin/cp -f install.sh $SANITYTEST_FOLDER
/bin/cp -f zstack-all-in-one*.tgz $SANITYTEST_FOLDER/zstack-all-in-one.tgz
/bin/cp -f woodpecker/zstacktestagent.tar.gz $SANITYTEST_FOLDER
echo -e " - Already copy and replace $SANITYTEST_FOLDER/zstack.war $SANITYTEST_FOLDER/zstacktestagent.tar.gz\n"

if [ ! -f $SANITYTEST_FOLDER/conf/zstack.properties ];then
    mkdir -p $SANITYTEST_FOLDER/conf/
    cp woodpecker/conf/zstack.properties $SANITYTEST_FOLDER/conf/
    echo -e " - Already copy new zstack.properties to $SANITYTEST_FOLDER/conf/"
else
    if `diff -u woodpecker/conf/zstack.properties $SANITYTEST_FOLDER/conf/zstack.properties >/dev/null 2>&1`; then
        echo -e " $SANITYTEST_FOLDER/conf/zstack.properties is not changed"
    else
        echo -e "$(tput setaf 3) - WARNING: $SANITYTEST_FOLDER/conf/zstack.properties is existed and different with new config. Will not override it to keep user configuration. If need to use new configuration, please override it manually!!!$(tput sgr0)" 
    fi
fi

cd -
rm -rf $tempfolder

if [ ! -d $WOODPECKER_VIRTUALENV ]; then
    rm -rf $WOODPECKER_VIRTUALENV
    mkdir -p `dirname $WOODPECKER_VIRTUALENV`
    virtualenv --system-site-packages $WOODPECKER_VIRTUALENV
fi

#install apibinding and zstacklib in woodpecker virtualenv
. $WOODPECKER_VIRTUALENV/bin/activate

echo -e " - Install Apibinding.\n"
cd $APIBINDING; ./install.sh >/dev/null

#install woodpecker
which zstack-woodpecker
[ $? -ne 0 ] && echo "install zstack-woodpecker" && bash $INSTALL_WOODPECKER_ENV_SCRIPT 

tmpdir=`mktemp`
/bin/rm -rf $tmpdir
mkdir -p $tmpdir
tar zxf $SANITYTEST_FOLDER/zstacktestagent.tar.gz -C $tmpdir

echo -e " - Install zstacklib.\n"
pip install --ignore-installed -i $ZSTACK_PYPI_URL $tmpdir/zstacktestagent/zstacklib*.tar.gz 
[ $? -ne 0 ] && echo "Install zstacklib failure. Exit." && /bin/rm -rf $tmpdir && exit 1

echo -e " - Install testagent.\n"
pip install --ignore-installed -i $ZSTACK_PYPI_URL $tmpdir/zstacktestagent/zstacktestagent*.tar.gz
[ $? -ne 0 ] && echo "Install testagent failure. Exit." && /bin/rm -rf $tmpdir && exit 1
/bin/rm -rf $tmpdir

if [ ! -z $ZSTACK_VR_IMAGE_PATH ]; then
    echo -e " - Update Virtual Router Image.\n"
    set -x
    $UPDATE_IMAGE_SCRIPT -i $ZSTACK_VR_IMAGE_PATH -b $ZSTACK_UTILITY/virtualrouter/bootstrap/zstack-appliancevm-bootstrap.py -a $ZSTACK_UTILITY/zstackbuild/target/zstack-assemble/WEB-INF/classes/ansible/
    set +x
    [ $? -ne 0 ] && echo "Update VR image failure. Exit." && exit 1
fi

if [ -f $USR_LOCAL_POST_BUILD_SCRIPT ]; then
    echo -e " - Run User Local Post Build Script: $USR_LOCAL_POST_BUILD_SCRIPT \n"
    /bin/sh $USR_LOCAL_POST_BUILD_SCRIPT
    [ $? -ne 0 ] && echo "Run user local post build script failed. Exit." && exit 1
fi

echo -e "$(tput setaf 2) - ZStack is successfully installed. Ready for testing\n$(tput sgr0)"
