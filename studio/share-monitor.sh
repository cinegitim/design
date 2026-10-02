#!/bin/bash
# Brand Studio share monitor: keeps local servers + Quick Tunnels alive,
# records the current public URL per brand. No secrets involved.
ROOT="/Users/serdaryurt/Documents/OpenCode/Design/brands"
UIDN=$(id -u)
check_brand() { # $1 slug, $2 port, $3 log-suffix (optional), $4 agent-suffix (optional, default "-$slug")
  local slug="$1"
  local port="$2"
  local suffix="$3"
  local agent="com.brandstudio.${4:-$slug}.server"
  local agent_t="com.brandstudio.${4:-$slug}.tunnel"
  local rt="$ROOT/$slug/share-runtime"
  local clog="$rt/cloudflared${suffix}.log"
  local url_file="$rt/public-url${suffix}.txt"
  # 1. local server
  if ! curl -s -o /dev/null -m 10 "http://localhost:$port/" ; then
    echo "$(date '+%F %T') [$slug] local server down -> kickstart" >> "$rt/monitor.log"
    launchctl kickstart "gui/$UIDN/$agent" >> "$rt/monitor.log" 2>&1
    sleep 8
  fi
  # 2. public URL freshness
  local url
  url=$(grep -o -E 'https://[a-z0-9-]+\.trycloudflare\.com' "$clog" 2>/dev/null | tail -1)
  if [ -z "$url" ] || ! curl -s -o /dev/null -m 25 "$url/" ; then
    echo "$(date '+%F %T') [$slug] tunnel down -> kickstart" >> "$rt/monitor.log"
    launchctl kickstart "gui/$UIDN/$agent_t" >> "$rt/monitor.log" 2>&1
    sleep 20
    url=$(grep -o -E 'https://[a-z0-9-]+\.trycloudflare\.com' "$clog" 2>/dev/null | tail -1)
  fi
  if [ -n "$url" ] && curl -s -o /dev/null -m 25 "$url/" ; then
    echo -n "$url" > "$url_file"
    echo "$(date '+%F %T') [$slug] OK $url" >> "$rt/monitor.log"
  else
    echo "$(date '+%F %T') [$slug] STILL DOWN" >> "$rt/monitor.log"
  fi
}
check_brand "asya-egitim" 8787
check_brand "asyada-egitim" 8788
check_brand "asyada-egitim" 8789 "-seal" "asyada-seal"
