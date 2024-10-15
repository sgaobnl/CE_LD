import time
import subprocess
import sys

nap_time = 900  # in second 
# nap_time = 120  # in seconds, uncomment if you want to use 120 seconds instead

def main():
    try:
        while True:
            print("Running top_ld.py")
            subprocess.run(["python", "top_ld.py"])
            subprocess.run(["python", "SBND_APA_ANA_v2.py"])
            subprocess.run(["python", "SBND_RMS_vs_Time.py"])
            subprocess.run(["python", "myemail.py"])
            subprocess.run(["python", "myemail2.py"])
            print("Sending femb status to EPICS")
            for crate in range(1, 5):
                for slot in range(1, 7):
                    subprocess.run(["python", "femb_status_check_n_epics.py", str(crate), str(slot)])

            print(f"Done, waiting for {nap_time} seconds")
            time.sleep(nap_time)

    except KeyboardInterrupt:
        print("\nScript interrupted by user. Resetting EPICS PVs to -1 ...")
        for crate in range(1, 5):
            for slot in range(1, 7):
                subprocess.run(["python", "femb_epics_pv_reset.py", str(crate), str(slot)])
        sys.exit(0)

if __name__ == "__main__":
    main()
