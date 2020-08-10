#!/usr/bin/env python3
### Checking bed files
#
#
# run it on bioinfo
# developed under python 3.6 environment

### Usage: .py --new_bed --service --


### libraries:
import os
import sys
import argparse
import subprocess

import magic # this package requires libmagic C library. For identifying a file format

import pandas as pd # my OS X pandas version is 1.0.4
'''
### A script used in this python script
/results/Pipeline/SDGSPipeline/scripts/sorting_bed_file_and_combining_overlapping_regions.pl


### static files to be modified in this process

/results/Analysis/MiSeq/MasterBED/abbreviated_bed_names.txt

# Exception - IonTorrent brand new bed file
/netapp1/sdgs/misc_analysis/ion_trends/all_possible_broads.csv
'''
### paths
path_upcoming='/results/Analysis/MiSeq/MasterBED/upcoming_BED_files/'
path_pl_output='/home/bioinfo/bed_files_created/'
path_masterbed='/results/Analysis/MiSeq/MasterBED/'
path_masterbed_ex='/results/Analysis/MiSeq/MasterBED/exonic_files/'
path_masterbed_archived='/results/Analysis/MiSeq/MasterBED/archived_BED_files/'
path_masterbed_ex_archived='/results/Analysis/MiSeq/MasterBED/archived_BED_files/exonic/'
path_masterbed_raw='/results/Analysis/MiSeq/MasterBED/raw_region_lists/'

path_rsync_pinky = '@10.182.155.26:/sdgs/reference/bed/'
path_rsync_brain='@10.182.155.27:/sdgs/reference/bed/'

path_upcoming_test='/Users/seikomakino/Documents/201809_NHS_STP/SCH_SDGS/SDGS_Bioinfo/Projects/Checking_bed_files_202005_/'

### arguments:
parser = argparse.ArgumentParser(description='Checking a new bed file for services') # parser is a container to hold arguments
parser.add_argument('-b','--new_bed',type=str, metavar='',help='A new bed file to process.')
parser.add_argument('-s', '--service',type=str,metavar='',help='service')
parser.add_argument('-ob','--old_bed',type=str,metavar='',help='Old bed file to archive')
# positional arguments have no '-' or '--'
# metavar - A name for the argument in usage messages. If '' empty then it doesn't show anything in '-h'

# Check the file format
def check_format(path,file):
    f_format=magic.from_file(path+file)
    if 'ASCII text' in f_format: # todo: check 'ASCII text' covers all text file format
        print(file+' is a ASCII text format. Proceeding.')
    else:
        print(file+' is not a text format. Check the file.')
        print('Exiting. ')
        #exit()

def check_header(path,file,header):
    with open(path+file,'r') as bed:
        line=bed.readlines(1) # as a list
    if header in line[0]:
        print('The bed file has a header. Proceeding.')
    else:
        print('The bed file has no header. Check the file.')
        print('Exiting. ')
        #exit()

def run_perl_script(file, file_bed_mod):
    # 4.1 run the perl script
    p_pl=subprocess.Popen(['/results/Pipeline/SDGSPipeline/scripts/sorting_bed_file_and_combining_overlapping_regions.pl', path_upcoming + file, path_pl_output + file, path_pl_output + f_bed_modifications], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    # 4.2 check the output
    pl_stdout=p_pl.stdout.read() # getting the stdout in bytes
    pl_stdout_str=pl_stdout.decode('utf-8') # the line ending is \n
    #b'8 regions were read in\nThere were 0 regions that were listed with different names\nThere were 0 regions that were duplicated\nThere were 0 regions that were contained within another\nThere were 0 regions that were concatenated with another\n'
    pl_stderr=p_pl.stderr.read()
    pl_stderr_str=pl_stderr.decode('utf-8')
    
    if pl_stderr==b'':
        print('The stdout of \'sorting_bed_file_and_combining_overlapping_regions.pl\': ')
        for i in pl_stdout_str.split('\n'):
            print(i)
    else:
        print('The perl script gave an error. ')
        pl_stderr_str=pl_stderr.decode('utf-8')
        print('The stderr of \'sorting_bed_file_and_combining_overlapping_regions.pl\': ')
        for i in pl_stderr_str.split('\n'):
            print(i)
        print('Check the error and the bed file: '+file+' ')
        print('Exiting. ')
        #exit()

def cmd_bed(cmd,file,path_org,path_dest):
    try:
        subprocess.run(cmd +' ' + path_org + file + ' ' + path_dest + file, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(e.output)
        print(cmd+' error for ' + file + ' to '+path_dest+' happened. Something wrong. ')
        print('Exiting. ')
        # exit()
args = parser.parse_args()
# dummy args for pytest - dnw
#args = parser.parse_args(['Haems_mini_SLC40A1_v2.bed','NGD','Haems_mini_SLC40A1_v1.bed'])

# todo: add try...except statement for checking the presence of the new bed file
f_new_bed=args.new_bed
n_service=args.service
f_old_bed=args.old_bed # some are brand new bed files # Todo: make sure no old_bed argument cause no error

f_bed_modifications= str(n_service) + '_BED_file_modifications.txt'

'''
/results/Analysis/MiSeq/MasterBED/upcoming_BED_files/<bed_file_name>
/home/bioinfo/bed_files_created/<service>_BED_file_modifications.txt # <service> is variable
/results/Analysis/MiSeq/MasterBED/<old_bed_file_name>
/results/Analysis/MiSeq/MasterBED/exonic_files/<old_exonic_file_name>
'''

### steps
# todo: check if bioinfo, pinky and brain are not immutable, or include it in the SOP?


### 1.Check that each panel has an exonic BED file and both are in the upcoming folder.
# 1.1 exonic file name check

idx=f_new_bed.index('.bed')
n_new_bed = f_new_bed[:idx]
# n_new_bed=f_new_bed[:f_new_bed.index('.bed')]

f_new_bed_ex=n_new_bed+'_exonic.bed' # the exonic bed file name has to be in this format

if os.path.isfile(path_upcoming_test+f_new_bed_ex):
    print('1. Exonic bed file has a correct file name: '+f_new_bed_ex)
    print('Proceeding.')
else:
    print('1. Exonic bed file does not exist or its name is not correct. Check the files.')
    print('Exiting.')
    #exit()

check_format(path_upcoming_test,f_new_bed)
check_format(path_upcoming_test,f_new_bed_ex)

### 2.Check each file has a header in the correct format (#chr	start	end	name)
# test to open the bed file
# test file: /Users/seikomakino/Documents/201809_NHS_STP/SCH_SDGS/SDGS_Bioinfo/Projects/Checking_bed_files_202005_/Haems_mini_SLC40A1_v2.bed
#with open(path_upcoming_test + f_new_bed, 'r') as new_bed:
header='#chr\tstart\tend\tregion'

check_header(path_upcoming_test,f_new_bed,header)
check_header(path_upcoming_test,f_new_bed_ex,header)


### 3.Check that the regions in the exonic bed file differ by 20 bases to the regions in the main bed file.
# If this is not the case, check this with the bed file author.
# todo
#
# 3.1 read in the whole files using pandas.read_table()
#with open(path_upcoming_test+f_new_bed) as f:
#    lines=f.readlines()

tbl_main=pd.read_table(path_upcoming_test + f_new_bed,index_col='region')
tbl_ex=pd.read_table(path_upcoming_test+f_new_bed_ex,index_col='region')

tbl_main=pd.read_table(path_upcoming + f_new_bed,index_col='region')
tbl_ex=pd.read_table(path_upcoming+f_new_bed_ex,index_col='region')

# 3.2 check the number of lines between two files - it has to be the same
# check the shapes of the tables. The number of rows in the exonic >= that of in the main bed is ok?
print('Comparing the number of regions between the exonic and the main bed files. ')
if tbl_ex.shape[0] == tbl_main.shape[0]:
    print('The numbers of the regions in the exonic and the main bed files are equal. ')
elif tbl_ex.shape[0] > tbl_main.shape[0]:
    print('The number of the regions in the exonic bed file is larger than the main bed file. Check if this is expected with the author. ')
    #todo: add user input if ok to proceed
    while True:
        ans_proceeding = input('Is it ok to proceed? Type Yes or No: ')
        ans = ans_proceeding.lower() # convert it to case insensitive
        if ans=='yes':
            print('Proceeding. ')
            break
        elif ans=='no':
            print('Exiting. ')
            #exit()
        else:
            print('Type Yes or No: ')
else:
    print('Check the numbers of the regions in the bed files with the author. ')
    print('Exiting. ')
    # exit()


# 3.3 Check the difference between - it has to be 20bp different

## match the region names
## subtract 'start - start' and 'end - end' positions
## check 20bp difference or not

for i_main in tbl_main.index:
    for i_ex in tbl_ex.index:
        if i_main == i_ex:
            dif_start = tbl_main.loc[i_main,'start'] - tbl_ex.loc[i_ex,'start']
            dif_end = tbl_main.loc[i_main,'end'] - tbl_ex.loc[i_ex,'end']
            if dif_start == -20 and dif_end == 20:
                print('The start and end positions are both 20bp apart. ')
            elif dif_start == -20 or dif_end == 20: # Todo: test with dummy bed files.
                print('Either start or end position is not 20bp apart. Check the region: '+i_main)
            else: # Todo: test with dummy bed files.
                print('Check the start and/or end positions between the main and exonic bed files.')


### 4.Use the following command on Bioinfo to complete the check for the main bed file and the exonic file.
# todo: rewrite with run()

p_pl_test=subprocess.Popen(['/Users/seikomakino/PycharmProjects/SDGS/SDGSPipeline/scripts/sorting_bed_file_and_combining_overlapping_regions.pl',path_upcoming_test+f_new_bed,path_upcoming_test+'local_destination_folder'+f_new_bed,path_upcoming_test+'local_destination_folder'+f_bed_modifications],stdout=subprocess.PIPE,stderr=subprocess.PIPE)

run_perl_script(f_new_bed,f_bed_modifications)
run_perl_script(f_new_bed_ex,f_bed_modifications)

### 5.The script will output any errors and tell you how many regions have been read into the program and which ones, if any, were merged.
# Todo: what is an output if merged? Run test

### 6.Once you are happy that the files are correct, use the following commands to copy the files to the correct folder on the server
# 6. cp in bioinfo and check
print('Copying the '+f_new_bed+' and '+f_new_bed_ex +' to '+path_masterbed+' and '+path_masterbed_ex)

## test on my mac how to catch error (2020/07/22)
'''
p_cp_main_test=subprocess.Popen(['cp','-v',path_upcoming_test+f_new_bed,path_upcoming_test+'local_destination_folde'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
lis_test=parse_stdout_stderr(p_cp_main_test)
# or
out,err=p_cp_main.communicate() # bytes

subprocess.check_call(p_cp_main_test.args) # this prints out the args and code.
returned_code=subprocess.check_call(p_cp_main_test.args) # this prints out the args and saves the code to an object
# use run() instead of Popen(). run() is more recommended to use.
p_cp_run_test=subprocess.run('cp -v' +path_upcoming_test+f_new_bed+' '+path_upcoming_test+' local_destination_folde',shell=True,check=True)
# I was trying to create an error to the folder name which doesn't exist. cp does copy the file to the file name 'local_destination_folde'! That's why it was not an error...
# help with LS below:
try:
    subprocess.run('cp ' +path_upcoming_test+f_new_bed+' '+path_upcoming_test+'local_destination_folder/'+f_new_bed,shell=True,check=True)
except subprocess.CalledProcessError as e:
    print(e.output)
    print('Copy error happened. Something wrong. ')
    print('Exiting. ')
    #exit()
'''

# non zero exit code means some process happened.
# 'NOT zero, 0' means the process is failed.

''' # my failed try:
# function  parse stdout and stderr from subprocess.PIPE
def parse_stdout_stderr(process):
    p_stdout=process.stdout.read()
    p_stdout_str=p_stdout.decode('utf-8')
    p_stderr=process.stderr.read()
    p_stderr_str=p_stderr.decode('utf-8')
    return[p_stdout_str,p_stderr_str]

p_cp_main=subprocess.Popen(['cp',path_pl_output+f_new_bed,path_masterbed],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
# todo: what to do if failed? try...exception??
if os.path.exists(path_masterbed+f_new_bed):
    print('cp to '+path_masterbed+'successful. ')
p_cp_ex=subprocess.Popen(['cp',path_pl_output+f_new_bed_ex,path_masterbed_ex],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
if os.path.exists(path_masterbed_ex+f_new_bed_ex):
    print('cp to '+path_masterbed_ex+'successful. ')
'''

# use run()
'''
try:
    subprocess.run('cp ' +path_pl_output+f_new_bed+' '+path_masterbed+f_new_bed,shell=True,check=True)
except subprocess.CalledProcessError as e:
    print(e.output)
    print('Copy error for '+f_new_bed+' happened. Something wrong. ')
    print('Exiting. ')
    #exit()

try:
    subprocess.run('cp ' +path_pl_output+f_new_bed_ex+' '+path_masterbed_ex+f_new_bed_ex,shell=True,check=True)
except subprocess.CalledProcessError as e:
    print(e.output)
    print('Copy error for '+f_new_bed_ex+' happened. Something wrong. ')
    print('Exiting. ')
    #exit()
'''

cmd_bed('cp',f_new_bed,path_pl_output,path_masterbed)
cmd_bed('cp',f_new_bed_ex,path_pl_output,path_masterbed_ex)

### 7.If the BED file is a new version and the old one is no longer needed, it needs to be moved to the archive folder using the following commands
if f_old_bed=='None':
    print('No archiving. ')
else:
    print('Archiving the old bed files. ')
    idx=f_old_bed.index('.bed')
    f_old_bed_ex=f_old_bed[:idx]+'_exonic.bed'
    # main bed
    cmd_bed('mv',f_old_bed,path_masterbed,path_masterbed_archived)
    cmd_bed('mv',f_old_bed_ex,path_masterbed_ex,path_masterbed_ex_archived)


### 8.If any regions have been merged move the original files from the upcoming folder to the raw regions folder with the following command, otherwise they can be deleted
# todo: how to find if bed files modified by the perl script? - comparing the line numbers??
tbl_main_pl = pd.read_table(path_pl_output + f_new_bed, index_col='region')
tbl_ex_pl = pd.read_table(path_pl_output + f_new_bed_ex, index_col='region')
# compare the line numbers with tbl_main and tbl_ex respectively. _pl should have fewer lines

if not tbl_main_pl.shape[0] == tbl_main.shape[0]:
    print('Moving the raw bed file. ')
    cmd_bed('mv',f_new_bed,path_upcoming,path_masterbed+'raw_region_lists/')
if not tbl_ex_pl.shape[0] == tbl_ex.shape[0]:
    print('Moving the raw bed file. ')
    cmd_bed('mv', f_new_bed_ex, path_upcoming, path_masterbed + 'raw_region_lists/')

### 9.If the panel is new, add the filename to the bottom of the abbreviated_bed_names file and choose an abbreviation – this will be what the results folder is named during the pipeline. The panel file name and the abbreviation must be separated by a tab.
# If the panel is a new version and the old version has been archived, just change the name of the existing BED in the abbreviations file. If the old version is still in use, both BEDs must be in the abbreviations file but they can have the same abbreviation.

# 9.1 test if the bed file is a brand new or not
n_new_bed_lower=n_new_bed.lower()
file_version=n_new_bed[n_new_bed_lower.index('_v'):]

str_to_remove= file_version+'.bed'
line_to_append=f_new_bed +'\t'+f_new_bed[:f_new_bed.index(str_to_remove)]+'\n'

if '_v1' in n_new_bed_lower:
    print(f_new_bed+' is a new bed file. Appending the filename to the abbreviated_bed_names.txt. ')
    # 9.2 if brand new, append a new line
    # read the file
    # append a new line
    # save and close
    with open(path_masterbed + 'abbreviated_bed_names.txt', 'r') as f_abv:
        txt = f_abv.readlines()

    with open(path_masterbed + 'abbreviated_bed_names.txt', 'a') as f_abv:
        if not txt.endswith('\n'):
            f_abv.writelines('\n')
            f_abv.writelines(line_to_append)
        else:
            f_abv.writelines(line_to_append)

elif '_v1' not in n_new_bed_lower:
    if '_v' in n_new_bed_lower:
        print(f_new_bed+' is a new version. Editing the file version. ')
        # 9.3 if a new version, modify the old version
        # read the file
        with open(path_masterbed+'abbreviated_bed_names.txt','r') as f_abv:
            txt=f_abv.readlines()
            for c, i in enumerate(txt):
                if f_old_bed in i: # find the line to edit,
                    idx_to_edit=c
                if f_old_bed in txt[idx_to_edit]: # check if the name matches
                    txt[idx_to_edit]=line_to_append
                else:
                    print('abbreviated_bed_names.txt cannot find '+f_old_bed +'to edit.')
                    #exiting
        # edit the line
        with open(path_masterbed+'abbreviated_bed_names.txt','w') as f_abv:
            f_abv.writelines(txt)


### 10.All the files must be checked for windows line endings. Run the following commands to check all the files in the folder.
# todo: test the commands
#for file in `ls /results/Analysis/MiSeq/MasterBED/*.bed`; do mv $file $file.dos; awk '{ sub("\r$", ""); print }' $file.dos > $file; rm $file.dos; done;
#dos_to_unix='for file in `ls /results/Analysis/MiSeq/MasterBED/*.bed`; do mv $file $file.dos; awk \'{ sub("\r$", ""); print }\' $file.dos > $file; rm $file.dos; done;'
cmd_dos_to_unix='for file in `ls'+ path_masterbed+'*.bed`; do mv $file $file.dos; awk \'{ sub("\r$", ""); print }\' $file.dos > $file; rm $file.dos; done;'
subprocess.run(cmd_dos_to_unix)
#for file in `ls /results/Analysis/MiSeq/MasterBED/exonic_files/*.bed`; do mv $file $file.dos; awk '{ sub("\r$", ""); print }' $file.dos > $file; rm $file.dos; done;
cmd_dos_to_unix='for file in `ls'+ path_masterbed_ex+'*.bed`; do mv $file $file.dos; awk \'{ sub("\r$", ""); print }\' $file.dos > $file; rm $file.dos; done;'
subprocess.run(cmd_dos_to_unix)

# testing wildcard
subprocess.run('cat * | ls', shell=True) # this works

### 11.Copy the final bed files over to Pinky
### 12.Copy over the edited abbreviated bed text file over to Pinky
user=input('Type the user name for pinky: ')
#user+path_rsync_pinky

# 11 and 12 rsync to pinky
# 11 and 12 check if rsync was successful or not
cmd_bed('rsync',f_new_bed,path_masterbed,user+path_rsync_pinky)
cmd_bed('rsync',f_new_bed_ex,path_masterbed_ex,user+path_rsync_pinky)
cmd_bed('rsync','abbreviated_bed_names.txt',path_masterbed,user+path_rsync_pinky)


### 13.Copy the final bed files over to Brain
### 14.Copy over the edited abbreviated bed text file over to Brain
user=input('Type the user name for brain: ')
cmd_bed('rsync',f_new_bed,path_masterbed,user+path_rsync_brain)
cmd_bed('rsync',f_new_bed_ex,path_masterbed_ex,user+path_rsync_brain)
cmd_bed('rsync','abbreviated_bed_names.txt',path_masterbed,user+path_rsync_brain)


# then the manual step:
### 15.The BED file needs to be added to StarLims.
print('Add or edit the bed file to StarLIMS.')

# The special case:
### 16. If a brand new broad BED file has been created for the Ion Torrent, this
# a file to edit: /netapp1/sdgs/misc_analysis/ion_trends/all_possible_broads.csv
# Todo: run as a separate script
# 16.1 log onto pinky or brain
# 16.2 make the file mutable/unprotected
# 16.3 Append the name of the new broad BED file to this file with the version number and ‘.bed’ removed.
# The name should be enclosed in double quotes and separated from other names with a comma e.g. “Haems_mini_25_v1.bed” would become “Haems_mini_25”
# 16.4 save the file and make it immutable again
