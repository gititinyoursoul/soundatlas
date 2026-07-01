# Bash completion for SoundAtlas backend maintenance scripts.

_soundatlas_backend_script_completion() {
  local cur prev script helper
  COMPREPLY=()

  cur="${COMP_WORDS[COMP_CWORD]}"
  prev="${COMP_WORDS[COMP_CWORD - 1]}"
  helper="/workspace/backend/scripts/completion.py"

  if [ ! -f "$helper" ]; then
    return 0
  fi

  for word in "${COMP_WORDS[@]}"; do
    case "$word" in
      backend/scripts/*.py|./backend/scripts/*.py|scripts/*.py|./scripts/*.py|*/backend/scripts/*.py)
        script="${word##*/}"
        break
        ;;
    esac
  done

  if [ -z "${script:-}" ]; then
    return 0
  fi

  case "$prev" in
    --event-id|--route-id|--kind|--provider|--query-planner)
      mapfile -t COMPREPLY < <(python3 "$helper" values "$prev" "$cur")
      return 0
      ;;
  esac

  if [[ "$cur" == --* ]]; then
    mapfile -t COMPREPLY < <(python3 "$helper" options "$script" "$cur")
  fi
}

complete -F _soundatlas_backend_script_completion uv
complete -F _soundatlas_backend_script_completion python
complete -F _soundatlas_backend_script_completion python3
