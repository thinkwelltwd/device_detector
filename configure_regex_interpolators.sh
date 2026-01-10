#!/bin/bash

# Replace $1 / $2 regex interpolation placeholders
# with \g<1>, \g<2> for native regex substitution
for i in 1 2 3 4 5;
  do
    grep -rl --include=*.yml "\$$i" device_detector/regexes | xargs sed -i "s#\$$i#\\\g<$i>#g" 2> /dev/null
done

MALFORMED=$(grep -rl --include=*.yml "eZee'Tab\\\g<1>" device_detector/regexes)

if [ $MALFORMED ]; then
   echo "Invalid yaml value found in '${MALFORMED}'"
   echo "Manually convert 'eZee'Tab\g<1>' to 'eZee'Tab\\\g<1>"
fi
