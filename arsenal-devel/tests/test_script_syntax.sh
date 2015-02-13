#!/bin/bash

num_failed=0
display_result() {
    if [ $1 == 0 ]; then
        echo "pass ${2} ${3}"
    else
        echo "FAIL ${2} ${3}"
	num_failed=$(( num_failed + 1 ))
    fi
}

ignorable() {
    for ext in '~' '~c' .pyc .o ; do
        if [ ${file_name%${ext}} != ${file_name} ]; then
            return 0
        fi
    done
    return 1
}

# Basic syntax checking
for script in scripts/* hooks/* ; do
    file_type=$(file -b ${script})
    file_name=$(basename $script)

    # Compiled objects and other cruft
    if ignorable ${file_name} ; then
        continue
    fi

    # Bash
    case ${file_type} in
        *troff*)
            ;;
        *byte-compiled*)
            ;;
        *bash*)
            bash -n $script >/dev/null 2>&1
            display_result $? 'bash' ${script}
            ;;
        *Bourne*)
            bash -n $script >/dev/null 2>&1
            display_result $? 'bash' ${script}
            ;;
        *perl*)
            perl -c $script >/dev/null 2>&1
            display_result $? 'perl' ${script}
            ;;
        *python*script*)
            python -m py_compile ${script}
            display_result $? 'python' ${script}
	    if [ -e ${script}c ]; then
		rm ${script}c
	    fi
            ;;
        *) echo "Unknown script type '${file_type}'"
            display_result 1 ${script}
    esac
done
exit $num_failed
