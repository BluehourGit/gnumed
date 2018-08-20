#!/bin/bash

# bash completions for GNUmed


_gnumed_completion()
{
	COMPREPLY=()
	OPTS="--quiet --debug --slave --override-schema-check --local-import --help --version -V -h -? --tool= --text-domain= --log-file= --conf-file= --lang-gettext= --ui= --wxp="
	CURR="${COMP_WORDS[COMP_CWORD]}"
	PREV="${COMP_WORDS[COMP_CWORD-1]}"
	PREVPREV="${COMP_WORDS[COMP_CWORD-2]}"

	case "${CURR}" in
		"=")
			case "${PREV}" in
				"--tool")
					TOOLS="check_enc_epi_xref export_pat_emr_structure"
					COMPREPLY=($(compgen -W "${TOOLS}"))
					return 0
				;;
			esac
		;;
	esac

	case "${PREV}" in
		"=")
			case "${PREVPREV}" in
				"--tool")
					TOOLS="check_enc_epi_xref export_pat_emr_structure"
					COMPREPLY=($(compgen -W "${TOOLS}" -- ${CURR}))
					return 0
				;;
			esac
		;;
	esac

	COMPREPLY=($(compgen -W "${OPTS}" -- ${CURR}))
	return 0
}


complete -o nospace -F _gnumed_completion gnumed