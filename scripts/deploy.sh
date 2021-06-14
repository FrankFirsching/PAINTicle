#!/bin/bash

usage() { echo "Usage: $0 -s <source> -t <target>" 1>&2; exit 1; }

while getopts "s:t:" o; do
    case "${o}" in
        s)
            s=${OPTARG}
            ;;
        t)
            t=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

if [ -z "${s}" ] || [ -z "${t}" ]; then
    usage
fi

# Remove a potential trailing slash
s=${s/%\//}

# Create a temporary directory
WORK_DIR=`mktemp -d`

# check if tmp dir was created
if [[ ! "$WORK_DIR" || ! -d "$WORK_DIR" ]]; then
  echo "Could not create temp dir"
  exit 1
fi

# A utility function we can add in the cleanup function to debug deployments
function pause(){
 read -s -n 1 -p "Press any key to continue . . ."
 echo ""
}

# deletes the temp directory
function cleanup {      
  rm -rf "$WORK_DIR"
}

# register the cleanup function to be called on the EXIT signal
trap cleanup EXIT

# Start the deployment logic
module_name=`basename ${s}`
script_dir=`dirname $0`

rsync -av "${s}" "$WORK_DIR/" --exclude '__pycache__'
rsync -av "${script_dir}/../LICENSE.md" "$WORK_DIR/$module_name/"

# On Linux strip the binary module to get a smaller size
machine=`uname -s`
if [[ "$machine" == "Linux" ]]; then
  echo "Stripping native python modules"
  find "$WORK_DIR/" -name "*.so" -exec strip {} \;
fi

deployment_version_file="$WORK_DIR/$module_name/deployment-version.txt"

git describe --always --long --match 'v*' > $deployment_version_file

echo "Zipping addon:"
target_abs=`realpath ${t}`
if [[ -f ${target_abs} ]]; then
  rm "${target_abs}" # Remove if zip exists, otherwise zip call would merge contents
fi
cd "$WORK_DIR"  && zip -9 -r ${target_abs} "$module_name"

echo ""
echo "Deployed version"
cat $deployment_version_file
