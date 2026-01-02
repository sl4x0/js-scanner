#!/bin/bash
# ==============================================================================
# Real-time Performance Monitor for Multi-Instance JS Scanner
# ==============================================================================
# This script monitors CPU, memory, network, and disk I/O for all running
# scanner instances and alerts when resources hit critical levels.
# ==============================================================================

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Alert thresholds
CPU_THRESHOLD=80
MEM_THRESHOLD=80
DISK_THRESHOLD=80

# Clear screen and print header
clear
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         JS Scanner Multi-Instance Performance Monitor         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}\n"

# Check if required tools are installed
command -v bc >/dev/null 2>&1 || { echo -e "${RED}Error: 'bc' is required but not installed. Install with: sudo apt install bc${NC}"; exit 1; }

# Function to get CPU usage for all jsscanner processes
get_scanner_cpu() {
    ps aux | grep "[p]ython.*jsscanner" | awk '{sum+=$3} END {printf "%.1f", sum}'
}

# Function to get memory usage for all jsscanner processes
get_scanner_mem() {
    ps aux | grep "[p]ython.*jsscanner" | awk '{sum+=$4} END {printf "%.1f", sum}'
}

# Function to get number of running scanner instances
get_instance_count() {
    ps aux | grep -c "[p]ython.*jsscanner"
}

# Function to get system-wide CPU usage
get_system_cpu() {
    top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}'
}

# Function to get system-wide memory usage
get_system_mem() {
    free | grep Mem | awk '{printf "%.1f", ($3/$2) * 100.0}'
}

# Function to get disk I/O wait percentage
get_disk_io() {
    iostat -c 1 2 | tail -1 | awk '{print $4}'
}

# Function to print colored alert
print_alert() {
    local metric=$1
    local value=$2
    local threshold=$3
    
    if (( $(echo "$value >= $threshold" | bc -l) )); then
        echo -e "${RED}⚠ WARNING: ${metric} is at ${value}% (threshold: ${threshold}%)${NC}"
    fi
}

# Function to display scanner process details
show_scanner_processes() {
    echo -e "\n${CYAN}Active Scanner Processes:${NC}"
    echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"
    ps aux | grep "[p]ython.*jsscanner" | awk '{printf "PID: %-7s CPU: %5s%% MEM: %5s%% CMD: %s\n", $2, $3, $4, substr($0, index($0,$11))}'
}

# Main monitoring loop
echo -e "${YELLOW}Press Ctrl+C to exit${NC}\n"

while true; do
    # Get current metrics
    INSTANCES=$(get_instance_count)
    
    if [ "$INSTANCES" -eq 0 ]; then
        echo -e "${RED}No scanner instances running!${NC}"
        echo -e "Start instances with: ./run_multi_instance.sh domain1.com domain2.com ..."
        exit 0
    fi
    
    SCANNER_CPU=$(get_scanner_cpu)
    SCANNER_MEM=$(get_scanner_mem)
    SYSTEM_CPU=$(get_system_cpu)
    SYSTEM_MEM=$(get_system_mem)
    
    # Check if iostat is available for disk I/O monitoring
    if command -v iostat >/dev/null 2>&1; then
        DISK_IO=$(get_disk_io)
        DISK_IO_AVAILABLE=true
    else
        DISK_IO="N/A"
        DISK_IO_AVAILABLE=false
    fi
    
    # Clear previous output (move cursor up and clear lines)
    tput cuu1 2>/dev/null || true
    
    # Display current status
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║ Running Instances: ${INSTANCES}                                           ${NC}"
    echo -e "${GREEN}╠════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${GREEN}║ Scanner Process Metrics:                                       ${NC}"
    printf "${GREEN}║${NC}   CPU Usage:    %-6s%%                                      ${GREEN}║${NC}\n" "$SCANNER_CPU"
    printf "${GREEN}║${NC}   Memory Usage: %-6s%%                                      ${GREEN}║${NC}\n" "$SCANNER_MEM"
    echo -e "${GREEN}╠════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${GREEN}║ System-Wide Metrics:                                           ${NC}"
    printf "${GREEN}║${NC}   Total CPU:    %-6s%%                                      ${GREEN}║${NC}\n" "$SYSTEM_CPU"
    printf "${GREEN}║${NC}   Total Memory: %-6s%%                                      ${GREEN}║${NC}\n" "$SYSTEM_MEM"
    if [ "$DISK_IO_AVAILABLE" = true ]; then
        printf "${GREEN}║${NC}   Disk I/O Wait: %-6s%%                                  ${GREEN}║${NC}\n" "$DISK_IO"
    fi
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}\n"
    
    # Check for alerts
    print_alert "Scanner CPU" "$SCANNER_CPU" "$CPU_THRESHOLD"
    print_alert "Scanner Memory" "$SCANNER_MEM" "$MEM_THRESHOLD"
    print_alert "System CPU" "$SYSTEM_CPU" "$CPU_THRESHOLD"
    print_alert "System Memory" "$SYSTEM_MEM" "$MEM_THRESHOLD"
    
    if [ "$DISK_IO_AVAILABLE" = true ]; then
        print_alert "Disk I/O Wait" "$DISK_IO" "$DISK_THRESHOLD"
    fi
    
    # Show process details
    show_scanner_processes
    
    echo -e "\n${YELLOW}Refreshing in 5 seconds... (Ctrl+C to exit)${NC}\n"
    sleep 5
    
    # Clear for next iteration
    clear
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║         JS Scanner Multi-Instance Performance Monitor         ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}\n"
done
