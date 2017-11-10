Monitor Device42 and having performance data

### pre-requisites ###
python
pip install python-requests
pip install python-params

### parameters ###

- -i instance to check
- -m metric to check
- -w warning
- -c critical
- -p port (default is 4343)
- -s http or https (default is https)

### metrics ###
- dbsize
- cpu_used_percent
- backup_status
- disk_used_percent
- memtotal
- cached
- swapfree
- swaptotal
- swapfreepercent
- memfree
- memfreepercent
- buffers

### tresholds ###
Guidelines were taken from https://nagios-plugins.org/doc/guidelines.html#THRESHOLDFORMAT

- regular tresholds: just add as regular number
- percentual treshold: just add as regular number

If the values like memfree and swapfree need to be checked for amount left, then the warning and critical values need to be checked differently. As in 'if lower then', instead of 'if higher then'.
This can be achieved by adding a ':' after the number.

If the metric doesn't have a numeric value to check add tresholds w and c as 0. (-w 0 -c 0)
