
# HTS files extraction from roots  #

Repository to extract informations needed by HTS from a roots corpus. We can distinguish 3 kind of
informations :
 - the label files
 - the signal files
 - the configuration/question files

## Architecture ##
### Labels ###
To extract the label files, you should the script *labels/roots2lab.py*. The documentation of this
command is
```
usage: roots2wav.py [-h] [-v] [-p NB_PROC] corpus output_dir

positional arguments:
  corpus                roots corpus file
  output_dir            output directory

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbosity       increase output verbosity
  -p NB_PROC, --nb_proc NB_PROC
                        nb process in parallel
```

#### From full context labels to monophone labels ####

The previous scripts are just meant to extract the full context labels. However, if you want to
obtain the monophone labels, a simple shell loop coupled to a sed command will do the trick:

```sh
mkdir mono
for i in `ls -1 full/`
do
   sed 's/\([0-9]*\) \([0-9]*\).*-\([a-zA-Z]*\)+.*/\1 \2 \3/g' full/$i > mono/$i
done
```

### Signals ###
To extract the signal, you should the script *signal/roots2wav.py*. The documentation of this
command is

```
usage: roots2wav.py [-h] [-v] [-p NB_PROC] corpus output_dir

positional arguments:
  corpus                roots corpus file
  output_dir            output directory

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbosity       increase output verbosity
  -p NB_PROC, --nb_proc NB_PROC
                        nb process in parallel
```

### Questions ###
To create the question file, you should use the script *questions/roots2questions.py*. The
documentation of this command is

```
usage: roots2questions.py [-h] [-v]

optional arguments:
  -h, --help       show this help message and exit
  -v, --verbosity  increase output verbosity

```
