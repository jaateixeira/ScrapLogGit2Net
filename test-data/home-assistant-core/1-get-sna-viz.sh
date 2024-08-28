commit fedf18f37b2b967ec54eacba0ca33627cef6095a
Author: apolinex <jose.teixeira@abo.fi>
Date:   Wed Aug 28 09:27:19 2024 +0300

    renamed get cs

diff --git a/test-data/home-assistant-core/get_network_visualizations.sh b/test-data/home-assistant-core/get_network_visualizations.sh
deleted file mode 100755
index a93d86b..0000000
--- a/test-data/home-assistant-core/get_network_visualizations.sh
+++ /dev/null
@@ -1,36 +0,0 @@
-#!/bin/bash
-
-
-if [ ! "$BASH_VERSION" ] ; then
-    echo "Please do not use sh to run this script ($0), just execute it directly" 1>&2
-    exit 1
-fi
-
-
-
-if [ ! "$BASH_VERSION" ] ; then
-    exec /bin/bash "$0" "$@"
-fi
-
-
-source config.cfg
-
-
-echo  -e "Invoking the $FFV_NO_FI_GRAPHML_SCRIPT with --save_graphML so we can later transform it"
-
-CMD="$FFV_NO_FI_GRAPHML_SCRIPT  $INPUT -pl -oi $COMPANIES_TO_IGNORE --save_graphML" 
-
-
-echo -e "Excecutiong:\n  $CMD \n"
-
-eval $CMD
-
-echo -e "TESTED" "Worked" "\n"
-
-echo -e "Filtered file saved at $FILTERED_FILE" "\n"
-
-
-du -sh $INPUT
-du -sh $FILTERED_FILE
-
-
