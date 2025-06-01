
#!/bin/bash

# Considering only top10

VIZ=''../../../formatFilterAndViz-nofo-GraphML.py''
VIZ_ARG='-sl'

KOHA_NET_GraphML_PATH="../JASIST-2024-wp-networks-graphML"

echo TRANSFORMER=$TRANSFORMER
echo FILTER_ARG=$FILTER_ARG
echo KOHA_NET_GraphML_PATH=$KOHA_NET_GraphML_PATH

cho Loop through files in the developer networks directory
for file in "$KOHA_NET_GraphML_PATH"/*; do
  if [ -f "$file" ]; then
    echo "$file"

    if [[ $file == *.graphML ]]       #  this is the snag
              then
                    echo "Getting top10 for"  $file ":"
                    CMD="$FILTER $FILTER_ARG $file"

                    echo CMD = $CMD

                    eval $CMD

              fi

  fi
done


