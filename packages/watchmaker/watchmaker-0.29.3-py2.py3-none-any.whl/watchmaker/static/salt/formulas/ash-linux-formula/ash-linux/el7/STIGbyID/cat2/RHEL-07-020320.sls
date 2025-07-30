# Ref Doc:        STIG - RHEL 7 v3r11
# Finding ID:     V-204463
# STIG ID:	      RHEL-07-020320
# Version:        RHEL-07-020320_rule
# SRG ID:         SRG-OS-000480-GPOS-00227
# Finding Level:  medium
#
# Rule Summary:
#	All files and directories must have a valid owner.
#
# CCI-002165
#    NIST SP 800-53 Revision 4 :: AC-3 (4)
#
#################################################################
{%- set stig_id = 'RHEL-07-020320' %}
{%- set helperLoc = 'ash-linux/el7/STIGbyID/cat2/files' %}
{%- set skipIt = salt.pillar.get('ash-linux:lookup:skip-stigs', []) %}
{%- set nouserFiles = [] %}
{%- set nouserDirs = [] %}
{%- set localFstypes = [
                         'ext2',
                         'ext3',
                         'ext4',
                         'xfs',
                         'jfs',
                         'btrfs'
                        ] %}
{%- set mountData = salt.mount.fstab() %}

script_{{ stig_id }}-describe:
  cmd.script:
    - source: salt://{{ helperLoc }}/{{ stig_id }}.sh
    - cwd: /root

{%- if stig_id in skipIt %}
notify_{{ stig_id }}-skipSet:
  cmd.run:
    - name: 'printf "\nchanged=no comment=''Handler for {{ stig_id }} has been selected for skip.''\n"'
    - stateful: True
    - cwd: /root
{%- else %}
# Find files with no valid owner..
  {%- for mount, data in mountData.items() %}
    {%- if data['fstype'] in localFstypes %}
      {%- set foundString = salt['cmd.shell']('find ' + mount + ' -xdev -type f -nouser') %}
      {%- if foundString %}
        {%- set foundList = foundString.split('\n') %}
        {%- do nouserFiles.extend(foundList) %}
      {%- endif %}
    {%- endif %}
  {%- endfor %}

# Find directories with no valid owner..
  {%- for mount, data in mountData.items() %}
    {%- if data['fstype'] in localFstypes %}
      {%- set foundString = salt['cmd.shell']('find ' + mount + ' -xdev -type d -nouser') %}
      {%- if foundString %}
        {%- set foundList = foundString.split('\n') %}
        {%- do nouserDirs.extend(foundList) %}
      {%- endif %}
    {%- endif %}
  {%- endfor %}

# Take ownership of files
  {%- if nouserFiles %}
file_fix-{{ stig_id }}:
  file.managed:
    - names: {{ nouserFiles }}
    - user: 'root'
  {%- else %}
file_fix-{{ stig_id }}:
  cmd.run:
    - name: 'printf "\nchanged=no comment=''Found no files with missing/undefined users.''\n"'
    - stateful: True
    - cwd: /root
  {%- endif %}

# Take ownership of directories
  {%- if nouserDirs %}
dir_fix-{{ stig_id }}:
  file.directory:
    - names: {{ nouserDirs }}
    - user: 'root'
  {%- else %}
dir_fix-{{ stig_id }}:
  cmd.run:
    - name: 'printf "\nchanged=no comment=''Found no directories with missing/undefined users.''\n"'
    - stateful: True
    - cwd: /root
  {%- endif %}
{%- endif %}
