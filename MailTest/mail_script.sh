#!/bin/bash

# -----------------------------------------------------------------------------------------------
# This script will send mail to all authors of recently added changes in GIT and/or Mercurial.
# It look in changelog.xml for each job.
# The script should only be executed when job fails. This is trigged by “Post Build task” in Jenkins.
# These lines was added to script window in Jenkins: 
#
# umask 002
# cd osaftest
# source config/sourceme.bash
# export OSAFREPODIR=/var/lib/jenkins/jobs/Build-opensaf-default-nonRoot/workspace/opensaf-staging
# ./tools/collect-info.sh -c -d ${JENKINS_HOME}/jobs/${JOB_NAME}/builds/${BUILD_NUMBER}/

# cd $OSAFTESTDIR
# $HOME/mail_script.sh -b ${BUILD_NUMBER} -u ${BUILD_URL} -j ${JOB_NAME} -l ${JENKINS_HOME}/jobs/${JOB_NAME}/builds/${BUILD_NUMBER} -m "per.rodenvall@ericsson.com daniel.a.lundin@ericsson.com" -d -c ${DEFAULT_CONTENT}
#
# This was dropped in the end of "build" window in build job.
# This is used by sendmail_script.sh to find the latest merc build
# echo "${JOB_NAME}/builds/${BUILD_NUMBER}" > $HOME/LATESTBUILD

# -----------------------------------------------------------------------------------------------


tempMailFile=~/osafLog/mail_msg.txt

MessageArray=()
SubjectArray=()
logfileArray=()

mailRecceiver=""
defMailRecipients=""
MERC_changelog=""
GIT_changelog=""
BOUNDARY="=== This is the boundary between parts of the message. ==="
debug="True"
jenkinsHost="192.168.122.1"
ThisScrip=$0


function createMailHeader()
{
	# http://forum.codecall.net/topic/50195-sending-emails-with-sendmail-part-1/
	# http://forum.codecall.net/topic/50197-sending-emails-with-sendmail-part-2/

	# Debug
	if [ $debug == "True" ];then echo "MailRecceiver before \"force change\" was: $mailRecceiver" ; fi
	mailRecceiver="per.rodenvall@ericsson.com"
	
	if [ -z "$mailRecceiver" ] ; then 
		# $mailRecceiver var is unset"
		if [ $debug == "True" ];then echo "No mailRecceiver was defined" ; fi
		mailRecceiver="per.rodenvall@ericsson.com"
	fi

	echo "To: $mailRecceiver" > $tempMailFile
	echo "Cc: $defMailRecipients" >> $tempMailFile
	echo "From: per.rodenvall@ericsson.com" >> $tempMailFile
	
	echo -n "Subject: Failed Jenkins-jobb: $jobbName - Build # $buildNr" >> $tempMailFile
	#for msg in "${SubjectArray[@]}"; do
	#	echo -n "${msg} " >> $tempMailFile
	#done
	echo >> $tempMailFile
	
	echo "MIME-Version: 1.0" >> $tempMailFile
	
	# Mail content consist of two parts (text and attachment)
	echo "Content-Type: multipart/mixed; boundary=\"$BOUNDARY\"" >> $tempMailFile
	
	# Sending one blank line to tell mail server that here start the actual body
	echo "" >> $tempMailFile
}

function createMailBody()
{
	echo >> $tempMailFile
	echo "--${BOUNDARY}" >> $tempMailFile
	echo "Content-Type: text/plain; charset=iso-8859-1" >> $tempMailFile
	echo "Content-Disposition: inline" >> $tempMailFile
	echo >> $tempMailFile
	echo "You are receiving this mail because you are author of a new change, merged from Mercurial(opensaf) or GIT (osaftest)." >> $tempMailFile
	echo >> $tempMailFile
	echo "Following Jenkins jobb failed:" >> $tempMailFile
	echo "$jobbName - Build # $buildNr -Failure:" >> $tempMailFile
	echo "Check console output at $url to view the results." >> $tempMailFile
	echo >> $tempMailFile

	if [ -s "$GIT_changelog" ] ; then
		NrOfGitAuthors=`cat $GIT_changelog | grep author | wc -l`
		if [ $debug == "True" ];then echo "Debug: Nr of GIT authors in $GIT_changelog: $NrOfGitAuthors" ; fi
		if [ $NrOfGitAuthors -gt 0 ] ; then
			echo >> $tempMailFile
			echo "******************************************************************************" >> $tempMailFile
			echo "Content of GIT changelog ($GIT_changelog):" >> $tempMailFile
			echo "******************************************************************************" >> $tempMailFile
			cat $GIT_changelog >> $tempMailFile
			echo >> $tempMailFile
		else
			echo -e "No changes was done in GIT. No authors was found in $GIT_changelog\n" >> $tempMailFile
		fi
	else
		echo -e "No changes was done in GIT. No authors was found in $GIT_changelog\n" >> $tempMailFile
	fi
	
	if [ -s "$MERC_changelog" ] ; then
		#NrOfMercAuthors=$(cat $MERC_changelog | grep author | wc -l)
		NrOfMercAuthors=`cat $MERC_changelog | grep author | wc -l`
		if [ $debug == "True" ];then echo "Debug: Nr of Mercurial authors in $MERC_changelog: $NrOfMercAuthors" ; fi
		if [ $NrOfMercAuthors -gt 0 ] ; then
			echo >> $tempMailFile
			echo "******************************************************************************" >> $tempMailFile
			echo "Content of Mercurial changelog ($MERC_changelog):" >> $tempMailFile
			echo "******************************************************************************" >> $tempMailFile
			cat $MERC_changelog >> $tempMailFile
			echo >> $tempMailFile
		else
			echo "No changes was done in Mercurial. No authors was found in $MERC_changelog" >> $tempMailFile
		fi
	else
		echo "No changes was done in Mercurial. No authors was found in $MERC_changelog" >> $tempMailFile
	fi
}

function searchForChangelog()
{
	# Search for changelog files from git and mercurial

	# Search for GIT changelog.xml (create GIT_changelog env)
	if [ -r "${HOME}/jobs/${jobbName}/builds/${buildNr}/changelog.xml" ] ; then
		GIT_changelog="${HOME}/jobs/${jobbName}/builds/$buildNr/changelog.xml"
	# This is used for KVM setup
	elif [ -r "${HOME}/jobHome/${jobbName}/builds/${buildNr}/changelog.xml" ] ; then
		GIT_changelog="${HOME}/jobHome/${jobbName}/builds/${buildNr}/changelog.xml"
	else
		echo "No changelog.xml where found"
	fi
	
	# Search for Mercurial changelog.xml (create MERC_changelog env)
	if [ -r "${HOME}/jobs/${latestBuild}/changelog.xml" ] ; then
		MERC_changelog="${HOME}/jobs/${latestBuild}/changelog.xml"
	# This is used for KVM setup
	elif [ -r "${HOME}/jobHome/${latestBuild}/changelog.xml" ] ; then
		MERC_changelog="${HOME}/jobHome/${latestBuild}/changelog.xml"
	else
		echo "No changelog.xml where found"
	fi	
}

# This function is never used...
#function createlogFileArray()
#{
#	# This function create a array with all *.tgz files in one directory
#	local logdir=$1
#	local logfile="*.tgz"
#	currdir=$PWD
#
#	if [ ! -d "$logdir" ]; then
#		echo "Warning: attachment $logdir not found, skipping" >&2
#	else
#		# Create a logfileArray with all *.tgz files
#		cd $logdir
#		for i in $(ls $logfile >&2); do
#			logfileArray+=($i)
#		done
#	fi
#	cd $currdir
#}

function addAttachment()
{
	local logdir=$1
	local logfile="*.tgz"
	local logfileArray=()
	currdir=$PWD

	# This function add a attachment to mail
	if [ ! -d "$logdir" ]; then
		echo "Warning: attachment $logdir not found, skipping"
	else
		# Create a logfileArray with all attachments
		cd $logdir
		for i in $(ls $logfile 2> /dev/null); do
			logfileArray+=($i)
		done
		
		# now loop over the attachments, guess the type
		# and produce the corresponding part, encoded base64
		for file in "${logfileArray[@]}"; do
	
			if [ $debug == "True" ];then echo "Debug: Attached file = $file" ; fi
			[ ! -f "$file" ] && echo "Warning: attachment $file not found, skipping" >&2 && continue
			mimetype=$(get_mimetype "$file") 

			echo >> $tempMailFile
			echo "--${BOUNDARY}" >> $tempMailFile
			echo "Content-Type: $mimetype; charset=iso-8859-1; name=\"$(basename $file)\"" >> $tempMailFile
			echo "Content-Disposition: attachment; filename=\"$file\"" >> $tempMailFile
			echo "Content-Transfer-Encoding: base64" >> $tempMailFile
			echo >> $tempMailFile
			base64 $file >> $tempMailFile
		done

		if [ $debug == "True" ];then echo "Debug: mimetype=$mimetype" ; fi
		
		echo >> $tempMailFile
		echo "--${BOUNDARY}--" >> $tempMailFile
		cd $currdir
	fi
}

function findGitMailRecceivers()
{
	# Search all authors in GIT changelog.xml.
	# Return one string with all authors.

	# newMailRecceiver is needed to prevent function return of a mailRecceiver that already was
	# defined.
	local newMailRecceiver=""

	if [ -f -a "$1" ] ; then
		file=$1
		while read line
		do
		   if [[ $line =~ (.*author.*<)(.*)(>.*)$ ]]; then
		     mailRecceiver+="${BASH_REMATCH[2]} "
		     newMailRecceiver=$mailRecceiver
		   fi
		done < $file

	# This echo is needed for return value from function
	echo "$newMailRecceiver"
	fi
}

function findMercurialMailRecceivers()
{
	# Search all authors in Mercurial changelog.xml.
	# Return one string with all authors.

	# newMailRecceiver is needed to prevent function return of a mailRecceiver that already was
	# defined.
	local newMailRecceiver=""

	if [ -f -a "$1" ] ; then
		file=$1
		while read line
		do
		if [[ $line =~ (.*author.*\&lt;)(.*)(\&gt;.*)$ ]]; then
		     mailRecceiver+="${BASH_REMATCH[2]} "
		     newMailRecceiver=$mailRecceiver
		   fi
		done < $file

	# This echo is needed for return value from function
	echo "$newMailRecceiver"
	fi
}

function get_mimetype()
{
	# warning: assumes that the passed file exists
	file --mime-type "$1" | sed 's/.*: //' 
}

function sendSimpleMail()
{
	/usr/sbin/sendmail -i -t < $tempMailFile
}

#------------------------------------
#------------------------------------
# Main 
#------------------------------------
#------------------------------------

echo ">*>*>*>*> Info: Start script $0"

# Parse all arguments
while [ $# -ne 0 ]; do
    case "$1" in
      --help|-h)
          echo "	Help message:"
          echo "	-h or --help	# This message"
          echo "	-b		# Build nr"
		  echo " 	-c) 	# Jenkins content for output"
		  echo "	-d		# Debug printouts"
          echo "	-u		# Url"
		  echo "	-j		# Jobbname"
		  echo "	-k) 	# KVM host"
          echo " 	-l 		# Opensaf logfiles. Directory where logfiles are stored"
		  echo "	-m		# Default Jenkins mail recipients"
          exit 0
      ;;

    -b) # Jenkins build nr
        if [ -n "$2" ] ; then
        	buildNr=$2
			MessageArray+=$buildNr
        	SubjectArray+=$buildNr
          	shift
	fi
        ;;

    -d) # Debug printouts
        if [ -n "$1" ] ; then
        	debug="True"
		fi
        ;;

    -u) # Jenkins URL
        if [ -n "$2" ] ; then
        	MessageArray+=$2
		 url=$2
          	shift
	fi
        ;;

    -j) # Jenkins jobbname
        if [ -n "$2" ] ; then
			jobbName=$2
        	MessageArray+=$jobbName
        	SubjectArray+=$jobbName
          	shift
	fi
        ;;

    -k) # KVM host
	# If KVM_host is defined Jenkins execute test on external KVM
        if [ -n "$2" ] ; then
		 KVM_host=$2
          	shift
	fi
        ;;

    -c) # Jenkins content for output
        if [ -n "$2" ] ; then
        	MessageArray+=$2
        	#echo $2
          	shift
	fi
        ;;

    -l) # Opensaf logfiles
        if [ -n "$2" ] ; then
        	openSafLogDir=$2
        	MessageArray+=$2
          	shift
	fi
        ;;

    -m) # Default Jenkins mail recipients
        if [ -n "$2" ] ; then
        	defMailRecipients=$2
          	shift
	fi
        ;;

        *)
          echo "Parameter is not supported"
          exit 1
        ;;
    esac
    shift
done

#if [ -z "$defMailRecipients" ] || [ -z "$buildNr" ] || [ -z "$url" ] || [ -z "$jobbName" ] || [ -z "$openSafLogDir" ] ; then
if [ -z "$defMailRecipients" ] || [ -z "$buildNr" ] || [ -z "$url" ] || [ -z "$jobbName" ] ; then
	echo "All needed parameters was not defined"
	if [ $debug == "True" ];then
		echo "Debug: script parameter defMailRecipients (-m) = $defMailRecipients"
		echo "Debug: script parameter buildNr (-b) = $buildNr"
		echo "Debug: script parameter url (-u) = $url"
		echo "Debug: script parameter jobbName (-j) = $jobbName"
		echo "Debug: script parameter openSafLogDir (-l) = $openSafLogDir"
	fi
	exit 1
else
	if [ $debug == "True" ];then echo "All parameters successfully parsed" ; fi
fi

# LATESTBUILD is created in Jenkins build step, see below
# 	echo "${JOB_NAME}/builds/${BUILD_NUMBER}" > $HOME/LATESTBUILD
# It is created because Jenkins test job didn't know who was the initiator of the test job.
latestBuild=$(cat $HOME/LATESTBUILD)
if [ -z latestBuild ] ; then
	
	echo "ERROR $ThisScrip need $HOME/LATESTBUILD file to work. It is created by prior Jenkins jobb. This should be added to Execute Shell on Jenkins:  echo \"\${JOB_NAME}/builds/\${BUILD_NUMBER}\" > $HOME/LATESTBUILD"
	exit 1
fi


searchForChangelog

# Include all recent GIT authors in mail reply
echo "Debug content of GIT_changelog = echo ${GIT_changelog[*]}"
if [ -f -a "$GIT_changelog" ] ; then
	mailRecceiver+="$(findGitMailRecceivers $GIT_changelog)"
fi

# Include all recent Mercurial authors in mail reply
echo "Debug content of MERC_changelog = $(echo $MERC_changelog)"
if [ -f -a "$MERC_changelog" ] ; then
	mailRecceiver+="$(findMercurialMailRecceivers $MERC_changelog)"
fi

if [ $debug == "True" ];then echo "mailRecceiver from GIT and Mercurial authors = $mailRecceiver" ; fi

createMailHeader

createMailBody

# Compress and add Jenkins log from build and test job
jobbOpenSafBuildName=$(cat ${HOME}/LATESTBUILD | awk -F "/" '{print $1}')

if [ $debug == "True" ];then echo "Debug: Latest opensaf build name = $jobbOpenSafBuildName" ; fi

## Compress files and add to mail

# If KVM_host is defined then Jenkins job is done on a separate KVM
if [ -n "$KVM_host" ] ; then
	#scp osaftest@jenkinsHost:${HOME}/jobs/${jobbName}/builds/${buildNr}/log ${HOME}/log_test
	
	# Create log.tgz where KVM is used (Jenkins test job)
	if [ -f ${HOME}/jobHome/${jobbName}/builds/${buildNr}/log ]; then
		tar -czvhf ${HOME}/osafLog/Jenkins_${jobbName}_log.tgz -C ${HOME}/jobHome/${jobbName}/builds/${buildNr}/ log
		# Copy files back to Jenkins server
		if [ $debug == "True" ];then echo "Jenkins logfile for ${jobbName} compressed and stored on KVM ${jenkinsHost} in ${HOME}/osafLog/Jenkins_${jobbName}_log.tgz" ; fi
	fi

	# Create log.txz where KVM is used (Jenkins build job)
	if [ -f ${HOME}/jobHome/${latestBuild}/log ]; then
		tar -czvhf ${HOME}/osafLog/Jenkins_${jobbOpenSafBuildName}_log.tgz -C ${HOME}/jobHome/${latestBuild}/ log
		if [ $debug == "True" ];then echo "Jenkins logfile for ${jobbName} compressed and stored in ${HOME}/osafLog/Jenkins_${jobbOpenSafBuildName}_log.tgz" ; fi
	fi

# Jenkins jobs are executed on Jenkins server
else
	if [ -f ${HOME}/jobs/${jobbName}/builds/${buildNr}/log ]; then
		tar -czvf ${HOME}/jobs/${jobbName}/builds/${buildNr}/Jenkins_${jobbName}_log.tgz -C ${HOME}/jobs/${jobbName}/builds/$buildNr/ log
		if [ $debug == "True" ];then echo "Jenkins logfile for ${jobbName} compressed and stored in ${HOME}/jobs/${jobbName}/builds/${buildNr}/Jenkins_${jobbName}_log.tgz" ; fi
	fi

	if [ -f ${HOME}/jobs/${latestBuild}/log ]; then
		tar -czvf ${HOME}/jobs/${jobbName}/builds/${buildNr}/Jenkins_${jobbOpenSafBuildName}_log.tgz -C ${HOME}/jobs/$latestBuild/ log
		if [ $debug == "True" ];then echo "Jenkins logfile for ${jobbName} compressed and stored in ${HOME}/jobs/${jobbName}/builds/$buildNr/Jenkins_${jobbOpenSafBuildName}_log.tgz" ; fi
	fi
fi

# Files that will be attached to mail need to be stored in $openSafLogDir
cp $openSafLogDir/*.tgz ${HOME}/osafLog/. 2>/dev/null

addAttachment $openSafLogDir

sendSimpleMail
cd $currdir

# Copy files back from Jenkins server to KVM ... with plugin
#if [ -n "$KVM_host" ] ; then
#	scp 
#fi

# Clean up files
#rm -rf ${HOME}/osafLog/log_test
#rm -rf ${HOME}/osafLog/log_build
#rm -rf ${HOME}/osafLog/*.tgz
#rm -rf ${HOME}/osafLog/${tempMailFile}
#rm -rf ${HOME}/LATESTBUILD

echo "<*<*<*<*< Info: Finisched script $0"
